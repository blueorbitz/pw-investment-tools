# Investment Skills Network - Tickets

All skill paths referenced in these tickets are relative to `src/`.

For example, `data/us-macro/SKILL.md` means `src/data/us-macro/SKILL.md` on disk.

## Shared vs market-specific skills

Some data skills handle all markets via internal routing (Yahoo Finance handles US, Bursa via .KL suffix, crypto via pair format). These are shared:

| Shared skill | Handles | Notes |
|---|---|---|
| `data/price-history/` | US, Bursa, Crypto | Yahoo Finance OHLCV + computed indicators |
| `data/fundamentals/` | US, Bursa | Yahoo timeseries (US) + KLSE Screener (Bursa) |

Market-specific skills stay prefixed because their data sources are single-market:

| Skill | Market | Why separate |
|---|---|---|
| `data/us-macro/` | US | FRED API (US-only indicators) |
| `data/us-filings/` | US | SEC EDGAR (US-only) |
| `data/bursa-fundamentals/` | Bursa | TradingView MY scanner, fund flow |
| `data/bursa-announcements/` | Bursa | BursaWhale API (MY insider transactions) |
| `data/crypto-*` | Crypto | CoinGecko, DeFiLlama, Glassnode, Binance |

## Environment variable

Set `SKILLS_ROOT` to point at the `src/` directory so scripts can locate each other regardless of where the workspace is cloned:

```
# PowerShell
$env:SKILLS_ROOT = "C:\path\to\investment-skills\src"

# bash/zsh
export SKILLS_ROOT="/path/to/investment-skills/src"
```

If `SKILLS_ROOT` is unset, scripts fall back to resolving relative to their own file location (works when running from within the workspace tree).

## Required env vars (per skill)

| Env Var | Used by | Source |
|---------|---------|--------|
| `SKILLS_ROOT` | all scripts with cross-skill imports | workspace path |
| `FRED_API_KEY` | data/us-macro (fed_liquidity, yield_curve, sentiment_dashboard) | https://fred.stlouisfed.org/docs/api/api_key.html |
| `SEC_EDGAR_USER_AGENT` | data/us-filings (sec_filings) | "YourName your@email.com" |
| `BURSAWHALE_CLIENT_ID` | data/bursa-announcements (bursawhale_api) | BursaWhale OAuth |
| `BURSAWHALE_CLIENT_SECRET` | data/bursa-announcements (bursawhale_api) | BursaWhale OAuth |
