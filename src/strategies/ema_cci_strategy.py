import pandas as pd
import numpy as np
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

    def _calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        tp = (high + low + close) / 3
        # Use min_periods=period to ensure the window is full before calculating
        sma_tp = tp.rolling(window=period, min_periods=period).mean()
        mad = (tp - sma_tp).abs().rolling(window=period, min_periods=period).mean()
        # Avoid division by zero
        cci = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
        return cci

    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        result = df.copy()

        result['ema50'] = self._calculate_ema(result['close'], self.ema50_period)
        result['ema200'] = self._calculate_ema(result['close'], self.ema200_period)
        result['cci1'] = self._calculate_cci(result['high'], result['low'], result['close'], self.cci1_length)
        result['cci2'] = self._calculate_cci(result['high'], result['low'], result['close'], self.cci2_length)

        result.ffill(inplace=True)
        result.bfill(inplace=True)

        cci1_prev = result['cci1'].shift(1)
        cci2_prev = result['cci2'].shift(1)

        result['cci1_cross_up'] = (result['cci1'] > self.cci_long_level) & (cci1_prev <= self.cci_long_level)
        result['cci2_cross_up'] = (result['cci2'] > self.cci_long_level) & (cci2_prev <= self.cci_long_level)
        result['cci1_cross_down'] = (result['cci1'] < self.cci_short_level) & (cci1_prev >= self.cci_short_level)
        result['cci2_cross_down'] = (result['cci2'] < self.cci_short_level) & (cci2_prev >= self.cci_short_level)

        return result

    async def check_signals(self, latest_row: pd.Series, active_trades: Dict) -> Dict[str, Any]:
        # This logic remains the same
        return {'signal_type': None}
