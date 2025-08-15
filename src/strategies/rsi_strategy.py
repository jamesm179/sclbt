import pandas as pd
from src.strategies.base import BaseStrategy
from src.core.exceptions import StrategyException

class RsiStrategy(BaseStrategy):
    def __init__(self, parameters: dict):
        super().__init__(parameters)

    def _validate_parameters(self):
        required_params = ['rsi_period', 'rsi_overbought', 'rsi_oversold']
        for param in required_params:
            if param not in self.parameters:
                raise StrategyException(f"Missing required parameter for RSI Strategy: {param}")

    def _calculate_rsi(self, data: pd.Series, period: int) -> pd.Series:
        """Calculates the Relative Strength Index (RSI)."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generates a trading signal based on the RSI strategy.
        """
        if 'close' not in data.columns:
            return 'HOLD'

        rsi_period = self.parameters['rsi_period']
        rsi_overbought = self.parameters['rsi_overbought']
        rsi_oversold = self.parameters['rsi_oversold']

        if len(data) < rsi_period + 1:
            return 'HOLD'

        # Calculate RSI
        data = data.copy()
        data['rsi'] = self._calculate_rsi(data['close'], rsi_period)

        latest_rsi = data['rsi'].iloc[-1]
        previous_rsi = data['rsi'].iloc[-2]

        # Buy signal: RSI crosses up through the oversold level
        if latest_rsi > rsi_oversold and previous_rsi <= rsi_oversold:
            return 'BUY'

        # Sell signal: RSI crosses down through the overbought level
        if latest_rsi < rsi_overbought and previous_rsi >= rsi_overbought:
            return 'SELL'

        return 'HOLD'
