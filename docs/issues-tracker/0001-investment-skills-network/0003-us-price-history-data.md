# 0003: Shared price history data skill

**What to build:** `data/price-history/SKILL.md` that instructs the agent to fetch OHLCV data and computed indicators for any market. The script routes internally via `yahoo_cache.py`: US tickers as-is, Bursa (numeric -> .KL), crypto (BTC/USD -> BTC-USD). Outputs computed indicators (RSI, MACD, MA levels, ADX, OBV, Bollinger, stage assessment) rather than raw candles.

Existing scripts: `price_history.py` (full indicator suite + stage detection) and `sector_rs.py` (relative strength comparison vs any benchmark) already handle all markets.

Default timeframes: 1Y daily for equities, 6M daily for crypto. Configurable via argument.

**Blocked by:** None (can start immediately). Scripts already working.

**Status:** done

- [x] `data/price-history/SKILL.md` exists with sections: Purpose, Input (ticker, optional period override), Output Format, Data Sources (Yahoo Finance via shared cache), Error Handling, Dependencies
- [x] Skill documents that it handles all three markets via ticker format routing
- [x] Skill documents computed output: 50/200 MA, RSI 14, MACD, ADX, OBV trend, Bollinger position, Weinstein stage, 52-week range, volume ratio
- [x] Skill references both scripts: `price_history.py` (indicators) and `sector_rs.py` (RS comparison)
- [x] Default timeframes documented: 1Y daily equities, 6M daily crypto
- [x] Error handling documents fallback behavior
