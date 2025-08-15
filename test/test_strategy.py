import unittest
import pandas as pd
from src.strategies.rsi_strategy import RsiStrategy

class TestRsiStrategy(unittest.TestCase):

    def setUp(self):
        """Set up strategy with default parameters."""
        self.params = {'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30}
        self.strategy = RsiStrategy(self.params)

    def _create_test_data(self, rsi_values):
        """Creates a DataFrame with dummy close prices and a mocked RSI calculation."""
        # The length of close prices needs to be sufficient for the strategy to run
        data = pd.DataFrame({'close': [100] * len(rsi_values)})

        # Monkey-patch the _calculate_rsi method to return a predictable series
        # We need to make sure the returned series has the same index as the input data
        def mock_calculate_rsi(close_data, period):
            # The length of rsi_values should match the length of close_data
            return pd.Series(rsi_values, index=close_data.index)

        self.strategy._calculate_rsi = mock_calculate_rsi
        return data

    def test_buy_signal(self):
        """Test the BUY signal generation on oversold crossover."""
        # Simulate RSI crossing from below 30 to above 30
        rsi_series = [50] * 15 + [25, 35]
        data = self._create_test_data(rsi_series)

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, 'BUY')

    def test_sell_signal(self):
        """Test the SELL signal generation on overbought crossover."""
        # Simulate RSI crossing from above 70 to below 70
        rsi_series = [50] * 15 + [75, 65]
        data = self._create_test_data(rsi_series)

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, 'SELL')

    def test_hold_signal_middle(self):
        """Test the HOLD signal when RSI is neutral."""
        rsi_series = [50] * 17 # Stays in the middle
        data = self._create_test_data(rsi_series)

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, 'HOLD')

    def test_hold_signal_above_overbought(self):
        """Test the HOLD signal when RSI stays above overbought."""
        rsi_series = [50] * 15 + [75, 80]
        data = self._create_test_data(rsi_series)

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, 'HOLD')

    def test_hold_signal_below_oversold(self):
        """Test the HOLD signal when RSI stays below oversold."""
        rsi_series = [50] * 15 + [25, 20]
        data = self._create_test_data(rsi_series)

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, 'HOLD')

if __name__ == '__main__':
    unittest.main()
