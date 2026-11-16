# Print, decoded

An interactive guide to **Pacifica Print**, written from an options desk's point of view, plus the code that produced every number in it.

- Live guide: `site/index.html` (single file, no build step, no dependencies)
- Reproduce all data: `make reproduce` (public Pacifica API only: no keys, no wallet)

## What it shows

| Finding | How it was measured |
|---|---|
| A Print Long is a sold put struck at the target, expiring at the checkpoint (a Print Short is a sold call). With the deposit cap, it's a put/call credit spread. | Payoff algebra from the Print docs |
| Print fills about **half** as often as a limit order at the same price (median fill/touch = 0.50 across 15 products): the reflection principle. | Every cycle starting at every hour, Pacifica 1h mark candles |
| At the checkpoint a filled Print becomes a normal perp, liquidated at maintenance margin (½ × 1/maxLev). At max Print leverage the real buffer can be ~half the docs formula. A real ZEC_24H order liquidated between the two lines confirms it. | Pacifica liquidation docs + public `/game/history` |
| Five real Print premiums implied 0.45–0.78× of a Black–Scholes fair value at 7-day realized vol (BTC ≈ fair). | IV solved on the capped spread; n=5, not a verdict |

## Files

- `scripts/pull.py`: 1h mark candles for every Print market (`GET /api/v1/kline/mark`) into `raw/`
- `scripts/iv.py`: implied vol of 5 real Print premiums vs realized vol
- `scripts/export.py`: fill / touch / overshoot / liquidation grids per product, side, distance and leverage into `data/dataset.json`
- `scripts/build.py`: inlines the data into `site/index.html`
- `data/example.json`: BTC 5-minute mark path for 15 Nov 2026 (the hero chart)

## Limits

Overlapping cycles (independent samples: ~528 for 24h BTC, 73 for 7d, 16 for 30d). Hourly candles approximate intraday touches. "Real" liquidation assumes the delivered position has only its own margin; spare cross-margin equity pushes the line out. Black–Scholes understates fat tails. Not financial advice.

Premium data: five orders recorded as public test fixtures in [hypurrquant/perp-cli#36](https://github.com/hypurrquant/perp-cli/pull/36).

Built by [Makabeez](https://github.com/Makabeez) ([@GeiserJoe2](https://x.com/GeiserJoe2)) for the Pacifica Educators Sprint.
