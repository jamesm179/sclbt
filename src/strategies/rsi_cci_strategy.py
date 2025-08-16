import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from .base import Strategy

class RSICCIStrategy(Strategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # ... (config parameters) ...
        self.rsi25_period = config.get('rsi25_period', 25)
        self.rsi100_period = config.get('rsi100_period', 100)
        self.cci100_period = config.get('cci100_period', 100)
        self.ema14_period = config.get('ema14_period', 14)

    def _calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period, min_periods=period).mean()
        mad = (tp - sma_tp).abs().rolling(window=period, min_periods=period).mean()
        cci = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
        return cci

    def _calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).ewm(span=period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(span=period, adjust=False).mean()
        # Avoid division by zero for rs
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        result = df.copy()

        result['rsi25'] = self._calculate_rsi(result['close'], self.rsi25_period)
        result['rsi100'] = self._calculate_rsi(result['close'], self.rsi100_period)
        result['cci100'] = self._calculate_cci(result['high'], result['low'], result['close'], self.cci100_period)
        result['ema14'] = self._calculate_ema(result['close'], self.ema14_period)

        result.ffill(inplace=True)
        result.bfill(inplace=True)
        return result

    async def check_signals(self, latest_row: pd.Series, active_trades: Dict) -> Dict[str, Any]:
        return {'signal_type': None}
