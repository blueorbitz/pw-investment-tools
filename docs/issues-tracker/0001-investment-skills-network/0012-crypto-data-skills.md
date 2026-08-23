# 0012: Crypto-specific data skills

**What to build:** Four crypto-specific data skills. Price history is handled by the shared `data/price-history` skill (ticket 0003) which already routes crypto pairs (BTC/USD -> BTC-USD) through Yahoo Finance. This ticket covers what's unique to crypto:

1. `data/crypto-fundamentals/SKILL.md` - market cap, FDV, circulating/total/max supply, supply schedule, TVL, protocol revenue/fees, token unlock schedule. Sources: CoinGecko, DeFiLlama, TokenUnlocks.
2. `data/crypto-onchain/SKILL.md` - exchange inflows/outflows, whale wallet movements, active addresses, staking ratios. Sources: Glassnode, CryptoQuant (free tiers).
3. `data/crypto-derivatives/SKILL.md` - perpetual funding rates, open interest, liquidation levels. Source: Binance API.
4. `data/crypto-macro/SKILL.md` - DXY, stablecoin total supply, BTC ETF net flows, Fed liquidity proxy (Fed BS minus RRP minus TGA). Sources: FRED + DeFiLlama + ETF flow trackers.

**Blocked by:** None (can start immediately, but logically follows after US slice is proven).

**Status:** done

- [x] All four SKILL.md files exist under `data/` with correct naming
- [x] Each skill has: Purpose, Input, Output Format, Data Sources, Error Handling, Dependencies sections
- [x] crypto-fundamentals covers: market cap, FDV, supply breakdown, TVL, revenue, unlock schedule
- [x] crypto-onchain covers: exchange flows, whale wallets, active addresses, staking ratios
- [x] crypto-derivatives covers: funding rates, OI, liquidation levels
- [x] crypto-macro covers: DXY, stablecoin supply, ETF flows, liquidity proxy
- [x] Each documents primary source + env vars needed (API keys)
- [x] Note: crypto price history is handled by shared `data/price-history` (ticket 0003)
