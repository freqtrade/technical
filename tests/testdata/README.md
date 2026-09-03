# Divergence indicator: TradingView ground-truth fixtures

`tests/test_divergence.py` validates `technical.indicators.divergence` against
real output from the original Pine Script indicator, captured via TradingView's
Pine Logs panel. The two CSVs in this directory
(`divergence_tradingview_log_regular.csv`, `divergence_tradingview_log_hidden.csv`)
are checked into the repo as evidence: they're the actual Pine runtime's own
computed values. They're trimmed to include the leading history the indicator needs to
warm up (see WARMUP_CANDLES in the test file) plus enough bars afterward to
contain real divergence events, rather than a full multi-year export.

To independently verify or regenerate them:

## 1. Load the Pine Script

Load `divergence_indicator_v6.pine` (in this directory). It's the Pine v6 
conversion of "Divergence for many indicator v3" (source Pine Script by 
LonesomeTheBlue, MPL-2.0). This script creates the CSVs that serve as 
ground-truth for Trading View output.  

## 2. Regular-divergence export

1. Open indicator settings, "Debug" group.
2. Enable "Enable Debug CSV Log".
3. Leave "Show Hidden Divergences" **off**.
4. Set `Log Start Date` / `Log End Date` to cover the range you want to test.
   Include at least ~300 extra bars before your intended start date -- the
   indicator needs history to warm up (see WARMUP_CANDLES in the test file).
5. Download the Pine Log.
6. Copy all logged rows (first row is the CSV header) into
   `tests/testdata/divergence_tradingview_log_regular.csv`.

## 3. Hidden-divergence export

Repeat step 2, but toggle "Show Hidden Divergences" **on** this time, and save
as `tests/testdata/divergence_tradingview_log_hidden.csv`.

## 4.  Quality Control Test Inputs 
Only the `bearish_divergence`/`bullish_divergence` columns in the 
"regular" export may have nonzero values.  On the other hand, only 
`bearish_hidden_divergence`/`bullish_hidden_divergence` columns in the 
"hidden" export may have nonzero values. This ensures that each of the four 
divergence tests get exercised.

## 5. Run the tests

```bash
pytest tests/test_divergence.py -v
```

Both fixtures are independently optional -- if a CSV is deleted or replaced
with a fresh export, the tests relying on it still run against whatever's
present, or skip gracefully if it's missing entirely.
