# General Usage

After installation, technical can be imported and used in your code.

We recommend to import freqtrade.indicators as ftt to avoid conflicts with other libraries, and to help determining where indicator calculations came from.

```python
import technical.indicators as ftt

# The indicator calculations can now be used as follows:

dataframe['cmf'] = ftt.chaikin_money_flow(dataframe)
```

## Indicator functions

All built in indicators are designed to work with a pandas DataFrame as provided by freqtrade, containing the standard columns: open, high, low, close and volume.
This dataframe should be provided as the first argument to the indicator function.
Depending on the indicator, additional parameters may be required.

### Return type

Depending on the indicator, the return type may be a pandas Series, a tuple of pandas Series, or a pandas DataFrame.

## Resample to interval

The helper methods `resample_to_interval` and `resampled_merge` are used to resample a dataframe to a higher timeframe and merge the resampled dataframe back into the original dataframe.
This is an alternative approach to using informative pairs and reduces the amount of data needed from the exchange (you don't need to download 4h candles in the below example).

```python
from pandas import DataFrame
from technical.util import resample_to_interval, resampled_merge
import technical.indicators as ftt

timeframe = '1h'

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

    # Resampling to 4h:
    dataframe_long = resample_to_interval(dataframe, 240)  # 240 = 4 * 60 = 4h

    dataframe_long['cmf'] = ftt.chaikin_money_flow(dataframe_long)
    # Combine the 2 dataframes
    dataframe = resampled_merge(dataframe, dataframe_long, fill_na=True)

    
    # The resulting dataframe will have 5 resampled columns in addition to the regular columns,
    # following the template resample_<interval_in_minutes>_<orig_column_name>.
    # So in the above example:
    # ['resample_240_open', 'resample_240_high', 'resample_240_low','resample_240_close', 'resample_240_cmf']

    return dataframe
```
