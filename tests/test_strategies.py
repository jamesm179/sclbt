import unittest
import pandas as pd
import numpy as np
import asyncio
from unittest.mock import patch
import sys
import os

# Add the project root to the Python path to allow for correct module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockTaLib:
    def EMA(self, real, timeperiod):
        return pd.Series(np.random.rand(len(real)))
    def CCI(self, high, low, close, timeperiod):
        return pd.Series(np.random.rand(len(high)))
    def RSI(self, real, timeperiod):
        return pd.Series(np.random.rand(len(real)))

class TestStrategies(unittest.TestCase):

    def setUp(self):
        self.long_data = pd.DataFrame({
            'open_time': pd.to_datetime(pd.date_range(start='2023-01-01', periods=300, freq='h')),
            'open': np.linspace(100, 150, 300),
            'high': np.linspace(102, 152, 300),
            'low': np.linspace(98, 148, 300),
            'close': np.linspace(101, 149, 300),
            'volume': np.random.uniform(1000, 5000, 300)
        })

    def test_emacci_strategy_indicators(self):
        with patch('src.strategies.ema_cci_strategy.talib', MockTaLib()):
            from src.strategies.ema_cci_strategy import EMACCIStrategy
            strategy = EMACCIStrategy(config={})
            df = strategy.get_indicators(self.long_data.copy())
            self.assertIn('ema50', df.columns)
            self.assertFalse(df['ema50'].isnull().all())

    def test_trf_strategy_indicators(self):
        with patch('src.strategies.trf_strategy.talib', MockTaLib()):
            from src.strategies.trf_strategy import TRFStrategy
            strategy = TRFStrategy(config={})
            df = strategy.get_indicators(self.long_data.copy())
            self.assertIn('filt', df.columns)
            self.assertFalse(df['filt'].isnull().all())

    def test_rsicci_strategy_indicators(self):
        with patch('src.strategies.rsi_cci_strategy.talib', MockTaLib()):
            from src.strategies.rsi_cci_strategy import RSICCIStrategy
            strategy = RSICCIStrategy(config={})
            df = strategy.get_indicators(self.long_data.copy())
            self.assertIn('rsi25', df.columns)
            self.assertFalse(df['rsi25'].isnull().all())

    def test_emacci_strategy_signals(self):
        async def run_test():
            with patch('src.strategies.ema_cci_strategy.talib', MockTaLib()):
                from src.strategies.ema_cci_strategy import EMACCIStrategy
                strategy = EMACCIStrategy(config={})
                df = strategy.get_indicators(self.long_data.copy())
                latest_row = df.iloc[-1]
                signals = await strategy.check_signals(latest_row, {})
                self.assertIn(signals['signal_type'], [None, 'long', 'short', 'exit'])
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
