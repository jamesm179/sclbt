import pandas as pd
import numpy as np
import talib
import logging
from typing import Dict, Any
from .base import Strategy

class TRFStrategy(Strategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.per1 = config.get('per1', 27)
        self.mult1 = config.get('mult1', 2)
        self.per2 = config.get('per2', 55)
        self.mult2 = config.get('mult2', 3)
        self.use_long_signals = config.get('use_long_signals', True)
        self.use_short_signals = config.get('use_short_signals', True)
        self.desired_take_profit = config.get('desired_take_profit', 10.0)
        self.desired_stop_loss = config.get('desired_stop_loss', 5.0)
        self.cci_length = config.get('cci_length', 100)
        self.ema_length = config.get('ema_length', 200)
        self.cci_long_level = config.get('cci_long_level', 100)
        self.cci_short_level = config.get('cci_short_level', -100)
        self.use_trending_signals = config.get('use_trending_signals', True)
        self.use_reversal_signals = config.get('use_reversal_signals', True)

    def smooth_range(self, series, period, multiplier):
        if len(series) < period * 2:
            return pd.Series(np.zeros(len(series)), index=series.index)
        wper = period * 2 - 1
        values = series.values
        abs_diff = np.abs(np.diff(values, prepend=values[0]))
        abs_diff_series = pd.Series(abs_diff, index=series.index)
        avg_range = abs_diff_series.ewm(span=period, adjust=False, min_periods=period).mean()
        smooth_range = avg_range.ewm(span=wper, adjust=False, min_periods=wper).mean() * multiplier
        return smooth_range

    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        result = df.copy()
        required_length = max(self.per1 * 2, self.per2 * 2, self.ema_length, self.cci_length)
        if len(result) < required_length:
            logging.warning(f"Insufficient data for TRF strategy: {len(result)} candles")
            return result

        source = result['close']
        close_array = result['close'].values
        high_array = result['high'].values
        low_array = result['low'].values

        result['ema4'] = talib.EMA(close_array, timeperiod=self.ema_length)
        result['CCI'] = talib.CCI(high_array, low_array, close_array, timeperiod=self.cci_length)
        result['smrng1'] = self.smooth_range(source, self.per1, self.mult1)
        result['smrng2'] = self.smooth_range(source, self.per2, self.mult2)
        result['smrng'] = (result['smrng1'] + result['smrng2']) / 2
        result['filt'] = source.copy()

        filt_values = result['filt'].values
        source_values = source.values
        smrng_values = result['smrng'].values

        for i in range(1, len(result)):
            prev_filt = filt_values[i-1]
            curr_source = source_values[i]
            curr_range = smrng_values[i]
            if curr_source > prev_filt:
                if curr_source - curr_range < prev_filt: filt_values[i] = prev_filt
                else: filt_values[i] = curr_source - curr_range
            else:
                if curr_source + curr_range > prev_filt: filt_values[i] = prev_filt
                else: filt_values[i] = curr_source + curr_range
        result['filt'] = filt_values

        upward = np.zeros(len(result))
        downward = np.zeros(len(result))
        for i in range(1, len(result)):
            if filt_values[i] > filt_values[i-1]:
                upward[i] = upward[i-1] + 1
                downward[i] = 0
            elif filt_values[i] < filt_values[i-1]:
                upward[i] = 0
                downward[i] = downward[i-1] + 1
            else:
                upward[i] = upward[i-1]
                downward[i] = downward[i-1]
        result['upward'] = upward
        result['downward'] = downward

        long_cond = ((source > result['filt']) & (source > source.shift(1)) & (result['upward'] > 0)) | \
                    ((source > result['filt']) & (source < source.shift(1)) & (result['upward'] > 0))
        short_cond = ((source < result['filt']) & (source < source.shift(1)) & (result['downward'] > 0)) | \
                     ((source < result['filt']) & (source > source.shift(1)) & (result['downward'] > 0))

        cond_ini = np.zeros(len(result))
        for i in range(1, len(result)):
            if long_cond.iloc[i]: cond_ini[i] = 1
            elif short_cond.iloc[i]: cond_ini[i] = -1
            else: cond_ini[i] = cond_ini[i-1]
        result['cond_ini'] = cond_ini

        result['long_signal'] = long_cond & (result['cond_ini'].shift(1) == -1)
        result['short_signal'] = short_cond & (result['cond_ini'].shift(1) == 1)
        result['rlong'] = (result['close'] < result['ema4']) & (result['CCI'] > self.cci_short_level) & result['long_signal']
        result['rshort'] = (result['close'] > result['ema4']) & (result['CCI'] < self.cci_long_level) & result['short_signal']
        result['tlong'] = (result['close'] > result['ema4']) & (result['CCI'] > self.cci_short_level) & result['long_signal']
        result['tshort'] = (result['close'] < result['ema4']) & (result['CCI'] < self.cci_long_level) & result['short_signal']

        return result

    async def check_signals(self, latest_row: pd.Series, active_trades: Dict) -> Dict[str, Any]:
        signals = {'signal_type': None, 'entry_reason': '', 'exit_reason': '', 'strategy_name': self.name}
        pair_symbol = latest_row.get('symbol', '')
        close_price = latest_row['close']

        if self.use_long_signals and self.use_trending_signals and latest_row.get('tlong', False):
            signals['signal_type'] = 'long'
        elif self.use_long_signals and self.use_reversal_signals and latest_row.get('rlong', False):
            signals['signal_type'] = 'long'
        elif self.use_short_signals and self.use_trending_signals and latest_row.get('tshort', False):
            signals['signal_type'] = 'short'
        elif self.use_short_signals and self.use_reversal_signals and latest_row.get('rshort', False):
            signals['signal_type'] = 'short'
        elif self.use_long_signals and latest_row.get('long_signal', False):
            signals['signal_type'] = 'long'
        elif self.use_short_signals and latest_row.get('short_signal', False):
            signals['signal_type'] = 'short'

        if pair_symbol in active_trades:
            trade = active_trades[pair_symbol]
            is_long = trade.get('direction') == 'long'

            if (is_long and close_price < latest_row['filt']) or (not is_long and close_price > latest_row['filt']):
                signals['signal_type'] = 'exit'

        return signals
