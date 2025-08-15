import pandas as pd
import numpy as np
import talib
import logging
from typing import Dict, Any
from .base import Strategy

class EMACCIStrategy(Strategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ema50_period = config.get('ema50_period', 50)
        self.ema200_period = config.get('ema200_period', 200)
        self.cci1_length = config.get('cci1_length', 100)
        self.cci2_length = config.get('cci2_length', 40)
        self.cci_long_level = config.get('cci_long_level', 100)
        self.cci_short_level = config.get('cci_short_level', -100)
        self.use_long_signals = config.get('use_long_signals', True)
        self.use_short_signals = config.get('use_short_signals', True)
        self.use_cci1 = config.get('use_cci1', True)
        self.use_cci2 = config.get('use_cci2', True)
        self.desired_take_profit = config.get('desired_take_profit', 7.0)
        self.desired_stop_loss = config.get('desired_stop_loss', 5.0)

    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        result = df.copy()
        required_length = max(self.ema200_period, self.cci1_length)
        if len(result) < required_length:
            logging.warning(f"Insufficient data for EMACCI indicators: {len(result)} candles")
            return result

        required_cols = ['high', 'low', 'close']
        if result[required_cols].isna().any().any():
            result[required_cols] = result[required_cols].fillna(method='ffill')
            if result[required_cols].isna().any().any():
                result[required_cols] = result[required_cols].fillna(method='bfill')
            if result[required_cols].isna().any().any():
                result = result.dropna(subset=required_cols)
                if len(result) < required_length:
                    logging.warning(f"After dropping NaNs, insufficient data: {len(result)} candles")
                    return result

        close_array = result['close'].values
        high_array = result['high'].values
        low_array = result['low'].values

        result['ema50'] = talib.EMA(close_array, timeperiod=self.ema50_period)
        result['ema200'] = talib.EMA(close_array, timeperiod=self.ema200_period)
        result['cci1'] = talib.CCI(high_array, low_array, close_array, timeperiod=self.cci1_length)
        result['cci2'] = talib.CCI(high_array, low_array, close_array, timeperiod=self.cci2_length)

        result[['ema50', 'ema200', 'cci1', 'cci2']] = result[['ema50', 'ema200', 'cci1', 'cci2']].ffill().bfill()

        cci1_prev = result['cci1'].shift(1)
        cci2_prev = result['cci2'].shift(1)

        result['cci1_cross_up'] = (result['cci1'] > self.cci_long_level) & (cci1_prev <= self.cci_long_level)
        result['cci2_cross_up'] = (result['cci2'] > self.cci_long_level) & (cci2_prev <= self.cci_long_level)
        result['cci1_cross_down'] = (result['cci1'] < self.cci_short_level) & (cci1_prev >= self.cci_short_level)
        result['cci2_cross_down'] = (result['cci2'] < self.cci_short_level) & (cci2_prev >= self.cci_short_level)

        return result

    async def check_signals(self, latest_row: pd.Series, active_trades: Dict) -> Dict[str, Any]:
        signals = {'signal_type': None, 'entry_reason': '', 'exit_reason': '', 'strategy_name': self.name}
        pair_symbol = latest_row.get('symbol', '')
        close_price = latest_row['close']
        ema50 = latest_row.get('ema50', 0)
        ema200 = latest_row.get('ema200', 0)
        cci1_cross_up = latest_row.get('cci1_cross_up', False)
        cci2_cross_up = latest_row.get('cci2_cross_up', False)
        cci1_cross_down = latest_row.get('cci1_cross_down', False)
        cci2_cross_down = latest_row.get('cci2_cross_down', False)

        long_ema_condition = close_price > ema50 and close_price < ema200
        short_ema_condition = close_price < ema50 and close_price > ema200

        long_cci_condition = (self.use_cci1 and cci1_cross_up) or (self.use_cci2 and cci2_cross_up)
        short_cci_condition = (self.use_cci1 and cci1_cross_down) or (self.use_cci2 and cci2_cross_down)

        if self.use_long_signals and long_ema_condition and long_cci_condition:
            signals['signal_type'] = 'long'
        elif self.use_short_signals and short_ema_condition and short_cci_condition:
            signals['signal_type'] = 'short'

        if pair_symbol in active_trades:
            trade = active_trades[pair_symbol]
            is_long = trade.get('direction') == 'long'
            take_profit_price = trade.get('take_profit_price', 0)
            stop_loss_price = trade.get('stop_loss_price', 0)

            if (is_long and close_price >= take_profit_price) or (not is_long and close_price <= take_profit_price):
                signals['signal_type'] = 'exit'
            elif (is_long and close_price <= stop_loss_price) or (not is_long and close_price >= stop_loss_price):
                signals['signal_type'] = 'exit'
            elif (is_long and short_ema_condition and short_cci_condition) or (not is_long and long_ema_condition and long_cci_condition):
                signals['signal_type'] = 'exit'

        return signals
