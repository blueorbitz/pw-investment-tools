#!/usr/bin/env python3
"""Fetch historical OHLCV from Yahoo Finance and compute technical indicators."""

import sys
import os
import json
import math
from datetime import datetime

SKILLS_ROOT = os.environ.get("SKILLS_ROOT", os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(SKILLS_ROOT, "utility", "shared-lib", "scripts"))
from yahoo_cache import fetch_yahoo_cached


def ema(data, period):
    """Compute EMA."""
    if len(data) < period:
        return [None] * len(data)
    k = 2 / (period + 1)
    result = [None] * (period - 1)
    result.append(sum(data[:period]) / period)
    for i in range(period, len(data)):
        result.append(data[i] * k + result[-1] * (1 - k))
    return result


def sma(data, period):
    """Compute SMA."""
    result = [None] * (period - 1)
    for i in range(period - 1, len(data)):
        result.append(sum(data[i - period + 1:i + 1]) / period)
    return result


def rsi(closes, period=14):
    """Compute RSI."""
    if len(closes) < period + 1:
        return [None] * len(closes)
    result = [None] * period
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(round(100 - 100 / (1 + rs), 2))
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    # Last value
    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(round(100 - 100 / (1 + rs), 2))

    return result


def macd(closes, fast=12, slow=26, signal=9):
    """Compute MACD line, signal, histogram."""
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line = []
    for i in range(len(closes)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line.append(round(ema_fast[i] - ema_slow[i], 4))
        else:
            macd_line.append(None)

    # Signal line (EMA of MACD)
    valid_macd = [v for v in macd_line if v is not None]
    if len(valid_macd) < signal:
        return None, None, None

    sig = ema(valid_macd, signal)
    # Align signal back
    offset = len(macd_line) - len(valid_macd)

    last_macd = macd_line[-1]
    last_signal = sig[-1] if sig[-1] is not None else None
    last_hist = round(last_macd - last_signal, 4) if last_macd is not None and last_signal is not None else None

    return last_macd, last_signal, last_hist


def adx(candles, period=14):
    """Compute ADX (simplified)."""
    if len(candles) < period * 2:
        return None

    tr_list = []
    plus_dm_list = []
    minus_dm_list = []

    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        pc = candles[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        tr_list.append(tr)

        up = h - candles[i - 1]["high"]
        down = candles[i - 1]["low"] - l
        plus_dm_list.append(up if up > down and up > 0 else 0)
        minus_dm_list.append(down if down > up and down > 0 else 0)

    # Smoothed averages
    atr = sum(tr_list[:period]) / period
    plus_dm = sum(plus_dm_list[:period]) / period
    minus_dm = sum(minus_dm_list[:period]) / period

    dx_list = []
    for i in range(period, len(tr_list)):
        atr = (atr * (period - 1) + tr_list[i]) / period
        plus_dm = (plus_dm * (period - 1) + plus_dm_list[i]) / period
        minus_dm = (minus_dm * (period - 1) + minus_dm_list[i]) / period

        plus_di = 100 * plus_dm / atr if atr > 0 else 0
        minus_di = 100 * minus_dm / atr if atr > 0 else 0
        di_sum = plus_di + minus_di
        dx = 100 * abs(plus_di - minus_di) / di_sum if di_sum > 0 else 0
        dx_list.append(dx)

    if len(dx_list) < period:
        return None

    adx_val = sum(dx_list[:period]) / period
    for i in range(period, len(dx_list)):
        adx_val = (adx_val * (period - 1) + dx_list[i]) / period

    return round(adx_val, 2)


def obv_trend(candles, lookback=20):
    """Compute OBV direction over lookback period."""
    if len(candles) < lookback + 1:
        return "insufficient_data"

    obv = 0
    obv_values = []
    for i in range(1, len(candles)):
        if candles[i]["close"] > candles[i - 1]["close"]:
            obv += candles[i]["volume"]
        elif candles[i]["close"] < candles[i - 1]["close"]:
            obv -= candles[i]["volume"]
        obv_values.append(obv)

    if len(obv_values) < lookback:
        return "insufficient_data"

    recent = obv_values[-lookback:]
    slope = recent[-1] - recent[0]
    if slope > 0:
        return "rising"
    elif slope < 0:
        return "falling"
    return "flat"


def bollinger_position(closes, period=20, std_mult=2):
    """Where current price sits within Bollinger Bands (0=lower, 1=upper)."""
    if len(closes) < period:
        return None
    window = closes[-period:]
    mid = sum(window) / period
    std = math.sqrt(sum((x - mid) ** 2 for x in window) / period)
    if std == 0:
        return 0.5
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    pos = (closes[-1] - lower) / (upper - lower)
    return round(pos, 3)


def detect_signals(candles, closes, rsi_values, macd_hist_recent):
    """Detect basic technical signals."""
    signals = []
    n = len(candles)

    # RSI divergence (simplified: last 20 bars)
    if n > 20 and rsi_values[-1] is not None and rsi_values[-20] is not None:
        price_higher = closes[-1] > max(closes[-20:-1])
        rsi_lower = rsi_values[-1] < max(v for v in rsi_values[-20:-1] if v is not None)
        if price_higher and rsi_lower:
            signals.append("bearish_rsi_divergence")

        price_lower = closes[-1] < min(closes[-20:-1])
        rsi_higher = rsi_values[-1] > min(v for v in rsi_values[-20:-1] if v is not None)
        if price_lower and rsi_higher:
            signals.append("bullish_rsi_divergence")

    # MA cross signals
    ema21 = ema(closes, 21)
    sma50 = sma(closes, 50)
    sma200 = sma(closes, 200)

    if len(closes) > 50 and ema21[-1] and sma50[-1]:
        if ema21[-2] and sma50[-2]:
            if ema21[-2] < sma50[-2] and ema21[-1] > sma50[-1]:
                signals.append("21ema_crossed_above_50sma")
            elif ema21[-2] > sma50[-2] and ema21[-1] < sma50[-1]:
                signals.append("21ema_crossed_below_50sma")

    if len(closes) > 200 and sma50[-1] and sma200[-1]:
        if sma50[-2] and sma200[-2]:
            if sma50[-2] < sma200[-2] and sma50[-1] > sma200[-1]:
                signals.append("golden_cross_50_200")
            elif sma50[-2] > sma200[-2] and sma50[-1] < sma200[-1]:
                signals.append("death_cross_50_200")

    # 200 MA reclaim
    if sma200[-1] and len(closes) > 5:
        if closes[-5] < sma200[-5] and closes[-1] > sma200[-1]:
            signals.append("200ma_reclaim")

    # Volume surge (today vs 50-day avg)
    if n > 50:
        vol_avg = sum(c["volume"] for c in candles[-51:-1]) / 50
        if vol_avg > 0 and candles[-1]["volume"] > vol_avg * 1.5:
            signals.append("volume_surge")

    # Breakout: new 52-week high
    if n > 250:
        high_52 = max(c["high"] for c in candles[-252:-1])
        if candles[-1]["high"] > high_52:
            signals.append("52week_high_breakout")

    return signals


def assess_stage(closes, candles):
    """Simplified Weinstein stage assessment."""
    if len(closes) < 150:
        return "insufficient_data"

    sma150 = sma(closes, 150)
    current = closes[-1]
    ma_val = sma150[-1]

    if ma_val is None:
        return "insufficient_data"

    # MA slope (last 10 vs 30 bars ago)
    if sma150[-30] is None:
        return "insufficient_data"

    slope = (sma150[-1] - sma150[-30]) / sma150[-30] * 100

    if current > ma_val and slope > 0.5:
        return "Stage 2 (Advancing)"
    elif current > ma_val and -0.5 <= slope <= 0.5:
        return "Stage 3 (Topping) or late Stage 2"
    elif current < ma_val and slope < -0.5:
        return "Stage 4 (Declining)"
    elif current < ma_val and -0.5 <= slope <= 0.5:
        return "Stage 1 (Basing)"
    elif current > ma_val and slope < 0:
        return "Stage 1→2 transition"
    else:
        return "Ambiguous"


def weekly_candles(candles, count=12):
    """Aggregate daily candles into weekly (last N weeks)."""
    weeks = []
    week = None
    for c in candles:
        # Simple weekly grouping by ISO week
        dt = datetime.strptime(c["date"], "%Y-%m-%d")
        wk = dt.isocalendar()[1]
        yr = dt.isocalendar()[0]
        key = f"{yr}-W{wk:02d}"

        if week is None or week["key"] != key:
            if week:
                weeks.append(week)
            week = {
                "key": key,
                "date": c["date"],
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"]
            }
        else:
            week["high"] = max(week["high"], c["high"])
            week["low"] = min(week["low"], c["low"])
            week["close"] = c["close"]
            week["volume"] += c["volume"]

    if week:
        weeks.append(week)

    result = []
    for w in weeks[-count:]:
        result.append({
            "week": w["key"],
            "open": w["open"],
            "high": w["high"],
            "low": w["low"],
            "close": w["close"],
            "volume": w["volume"]
        })
    return result


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: ta_history.py <ticker> [period]"}))
        sys.exit(1)

    ticker = sys.argv[1].upper()
    period = sys.argv[2] if len(sys.argv) > 2 else "1y"

    try:
        candles, meta = fetch_yahoo_cached(ticker, period)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"Failed to fetch data: {e}"}))
        sys.exit(1)

    if len(candles) < 50:
        print(json.dumps({"ok": False, "error": f"Insufficient data: only {len(candles)} candles"}))
        sys.exit(1)

    closes = [c["close"] for c in candles]

    # Compute indicators
    ema21_vals = ema(closes, 21)
    sma50_vals = sma(closes, 50)
    sma150_vals = sma(closes, 150)
    sma200_vals = sma(closes, 200)
    rsi_vals = rsi(closes, 14)
    macd_val, macd_sig, macd_hist = macd(closes)
    adx_val = adx(candles)
    obv_dir = obv_trend(candles)
    bb_pos = bollinger_position(closes)
    stage = assess_stage(closes, candles)
    signals = detect_signals(candles, closes, rsi_vals, macd_hist)

    # Current price vs MAs
    current = closes[-1]
    ma_distances = {}
    for name, vals in [("21_ema", ema21_vals), ("50_sma", sma50_vals), ("150_sma", sma150_vals), ("200_sma", sma200_vals)]:
        if vals[-1] is not None:
            dist = round((current - vals[-1]) / vals[-1] * 100, 2)
            ma_distances[name] = {"value": round(vals[-1], 4), "distance_pct": dist}

    # Volume analysis
    vol_avg_50 = sum(c["volume"] for c in candles[-50:]) / 50 if len(candles) >= 50 else None
    vol_current = candles[-1]["volume"]
    vol_ratio = round(vol_current / vol_avg_50, 2) if vol_avg_50 and vol_avg_50 > 0 else None

    # Trend direction (simple: above/below 50 MA + slope)
    trend = "sideways"
    if sma50_vals[-1] and sma50_vals[-20]:
        slope_50 = (sma50_vals[-1] - sma50_vals[-20]) / sma50_vals[-20] * 100
        if current > sma50_vals[-1] and slope_50 > 0:
            trend = "uptrend"
        elif current < sma50_vals[-1] and slope_50 < 0:
            trend = "downtrend"

    # 52-week high/low
    high_52 = max(c["high"] for c in candles[-min(252, len(candles)):])
    low_52 = min(c["low"] for c in candles[-min(252, len(candles)):])

    output = {
        "ok": True,
        "ticker": ticker,
        "name": meta.get("longName") or meta.get("shortName") or ticker,
        "currency": meta.get("currency", ""),
        "period": period,
        "data_points": len(candles),
        "summary": {
            "price": current,
            "trend": trend,
            "stage": stage,
            "52wk_high": round(high_52, 4),
            "52wk_low": round(low_52, 4),
            "pct_from_52wk_high": round((current - high_52) / high_52 * 100, 2)
        },
        "ma_levels": ma_distances,
        "indicators": {
            "rsi_14": rsi_vals[-1],
            "macd": macd_val,
            "macd_signal": macd_sig,
            "macd_histogram": macd_hist,
            "adx_14": adx_val,
            "obv_trend": obv_dir,
            "bollinger_position": bb_pos
        },
        "volume": {
            "current": vol_current,
            "avg_50day": round(vol_avg_50) if vol_avg_50 else None,
            "ratio_vs_avg": vol_ratio
        },
        "signals": signals,
        "weekly_ohlcv": weekly_candles(candles, 12)
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
