#!/usr/bin/env python3
import os
import re
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

# Shared-lib import: ISK_ROOT points at src/. A relative ISK_ROOT is ignored
# for import purposes (CWD-dependent); __file__-relative resolution is used instead.
_ROOT = os.environ.get("ISK_ROOT")
if not _ROOT or not os.path.isabs(_ROOT):
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "utility", "shared-lib", "scripts"))

from yahoo_cache import _cache_dir, load_workspace_env  # noqa: E402

load_workspace_env()

# Institutional holder patterns (compiled for performance)
_INSTITUTIONAL_PATTERN = re.compile(r'Persaraan|EPF|Trustees|Fund', re.IGNORECASE)

API_BASE_URL = os.getenv('BURSAWHALE_API_URL', 'https://bursa-whale-bi.choong.pw/backend/api')
AUTH_URL = os.getenv('BURSAWHALE_AUTH_URL', 'https://mybursabi.kinde.com/oauth2/token')
CLIENT_ID = os.getenv('BURSAWHALE_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('BURSAWHALE_CLIENT_SECRET', '')
AUDIENCE = os.getenv('BURSAWHALE_AUDIENCE', 'https://mybursabi.kinde.com/api')

# Token cache lives in ISK_CACHE (env/.env resolved), not the current directory
TOKEN_FILE = os.path.join(_cache_dir(), '.bursawhale_token.json')

def get_access_token() -> str:
    """Get OAuth2 access token from Kinde using x-www-form-urlencoded"""
    global _access_token, _access_token_expires_at
    
    # Try to load token from file first
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                _access_token = token_data.get('token')
                expires_at_str = token_data.get('expires_at')
                if expires_at_str:
                    _access_token_expires_at = datetime.fromisoformat(expires_at_str)
                
                # Check if cached token is still valid
                if _access_token and _access_token_expires_at and datetime.now() < _access_token_expires_at:
                    return _access_token
        except Exception:
            # If there's any issue with the file, continue to get a new token
            pass
    
    # No valid cached token, get a new one
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError('BURSAWHALE_CLIENT_ID and BURSAWHALE_CLIENT_SECRET must be set')

    response = requests.post(AUTH_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'audience': AUDIENCE
    }, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    response.raise_for_status()
    
    token_data = response.json()
    _access_token = token_data['access_token']
    
    # Calculate expiration time (assuming token lasts for 1 hour)
    # In a real implementation, you might get expiration info from the token or response
    _access_token_expires_at = datetime.now() + timedelta(hours=1)
    
    # Save token to file for reuse
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                'token': _access_token,
                'expires_at': _access_token_expires_at.isoformat()
            }, f)
    except Exception:
        # If we can't save the token file, that's okay - we'll just request a new one next time
        pass
    
    return _access_token

def fetch_transactions(filters: Optional[Dict] = None) -> Dict:
    """Fetch transaction records from Bursa Whale API with pagination support"""
    params = filters or {}
    
    # Set default date range to last 7 days if not provided
    if 'startDate' not in params and 'endDate' not in params:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        params['startDate'] = start_date.strftime('%Y-%m-%d')
        params['endDate'] = end_date.strftime('%Y-%m-%d')
    
    params['pageSize'] = 500  # Use larger page size to reduce API calls
    token = get_access_token()
    
    all_records = []
    current_page = 1
    total_pages = 1
    
    while current_page <= total_pages:
        params['page'] = current_page
        
        response = requests.get(
            f'{API_BASE_URL}/records',
            params=params,
            headers={'Authorization': f'Bearer {token}'}
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract pagination info
        pagination = data.get('pagination', {})
        total_pages = pagination.get('total_pages', 1)
        
        # Process records from this page
        for r in data['records']:
            is_acquired = r['transaction']['type'] == 'Acquired'
            all_records.append({
                'date': r['transaction']['tx_date'],
                'ref_date': r['announcement']['ref_date'],
                'stock_code': r['announcement']['stock_code'],
                'company': r['announcement']['company'],
                'holder': r['announcement']['holder'],
                'price': r['price']['open'],
                'acquired_value': r['transaction']['value'] if is_acquired else 0,
                'disposed_value': r['transaction']['value'] if not is_acquired else 0,
                'diff_value': r['transaction']['value'] if is_acquired else -r['transaction']['value']
            })
        
        current_page += 1
    
    return {
        'records': all_records,
        'pagination': {
            'total': len(all_records),
            'total_pages': total_pages
        }
    }

def aggregate_by_stock(records: List[Dict]) -> Dict[str, Dict]:
    """Aggregate transactions by stock code"""
    stock_summary = {}
    seen_keys = set()
    
    for r in records:
        code = r['stock_code']
        if code not in stock_summary:
            stock_summary[code] = {
                'stock_code': code,
                'company': r['company'],
                'acquired_value': 0,
                'disposed_value': 0,
                'diff_value': 0,
                'price': r['price']
            }
        
        key = f"{code}_{r['ref_date']}_{int(r['diff_value'])}"
        if key not in seen_keys:
            seen_keys.add(key)
            stock_summary[code]['acquired_value'] += r['acquired_value']
            stock_summary[code]['disposed_value'] += r['disposed_value']
            stock_summary[code]['diff_value'] += r['diff_value']
    
    return stock_summary

def aggregate_by_holder(records: List[Dict]) -> Dict[str, Dict]:
    """Aggregate transactions by holder type"""
    holder_summary = {}
    
    for r in records:
        holder = r['holder']
        if holder not in holder_summary:
            holder_summary[holder] = {
                'holder': holder,
                'acquired_value': 0,
                'disposed_value': 0,
                'diff_value': 0
            }
        
        holder_summary[holder]['acquired_value'] += r['acquired_value']
        holder_summary[holder]['disposed_value'] += r['disposed_value']
        holder_summary[holder]['diff_value'] += r['diff_value']
    
    return holder_summary


def is_institutional_holder(holder_name: str) -> bool:
    """Check if a holder is an institutional investor based on name patterns.
    
    Args:
        holder_name: The name of the holder to check.
        
    Returns:
        True if the holder is institutional, False otherwise.
    """
    return bool(_INSTITUTIONAL_PATTERN.search(holder_name))


def split_institutional_holder_data(holder_data: Dict[str, Dict]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Split holder data into institutional and non-institutional categories.
    
    Args:
        holder_data: Dictionary mapping holder names to their aggregated data.
        
    Returns:
        A tuple of (institutional_holders, non_institutional_holders) dictionaries.
    """
    institutional = {}
    non_institutional = {}
    
    for holder_name, data in holder_data.items():
        if is_institutional_holder(holder_name):
            institutional[holder_name] = data
        else:
            non_institutional[holder_name] = data
    
    return institutional, non_institutional

def get_last_30_days_range() -> tuple:
    """Get date range for last 30 days based on latest record in DB"""
    # Fetch only the latest record to determine the latest date
    params = {
        'pageSize': 1
    }
    token = get_access_token()
    
    response = requests.get(
        f'{API_BASE_URL}/records',
        params=params,
        headers={'Authorization': f'Bearer {token}'}
    )
    response.raise_for_status()
    data = response.json()
    
    if not data['records']:
        # If no records found, return default range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    # Get the latest date from the record
    latest_record = data['records'][0]
    latest_date = datetime.strptime(latest_record['transaction']['tx_date'], '%Y-%m-%d')
    
    # Return range for last 30 days from the latest date
    start_date = latest_date - timedelta(days=30)
    return start_date.strftime('%Y-%m-%d'), latest_date.strftime('%Y-%m-%d')

if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python3 bursawhale_api.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'fetch':
        filters = {}
        if len(sys.argv) > 2:
            filters = json.loads(sys.argv[2])
        result = fetch_transactions(filters)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'aggregate_stock':
        records = []
        if len(sys.argv) > 2:
            records = json.loads(sys.argv[2])
        result = aggregate_by_stock(records)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'aggregate_holder':
        records = []
        if len(sys.argv) > 2:
            records = json.loads(sys.argv[2])
        result = aggregate_by_holder(records)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'get_dates':
        # This command outputs the date range in the format needed by scan.sh
        start_date, end_date = get_last_30_days_range()
        print(f"{start_date} {end_date}")
