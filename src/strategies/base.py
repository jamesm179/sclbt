from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    def __init__(self, parameters: dict):
        self.parameters = parameters
        self._validate_parameters()

    @abstractmethod
    def _validate_parameters(self):
        """
        Validates the parameters required for the strategy.
        Should be implemented by each subclass.
        """
        pass

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generates a trading signal based on the input data.

        :param data: A pandas DataFrame with OHLCV data.
        :return: A string signal: 'BUY', 'SELL', or 'HOLD'.
        """
        pass

    def backtest(self, data: pd.DataFrame, initial_balance=10000, commission=0.001):
        """
        A simple backtesting implementation.
        This can be expanded later.
        """
        if 'close' not in data.columns:
            raise ValueError("Data must contain 'close' column for backtesting.")

        balance = initial_balance
        position = 0  # 0 for no position, 1 for long position
        trades = []

        for i in range(1, len(data)):
            # We need at least some data to generate signals
            historical_data = data.iloc[:i]
            signal = self.generate_signal(historical_data)

            if signal == 'BUY' and position == 0:
                # Buy at the close price of the current candle
                entry_price = data['close'].iloc[i]
                position = balance / entry_price
                balance = 0
                trades.append({'entry_date': data.index[i], 'entry_price': entry_price})


            elif signal == 'SELL' and position > 0:
                # Sell at the close price of the current candle
                exit_price = data['close'].iloc[i]
                balance = position * exit_price * (1 - commission)
                position = 0
                trade = trades[-1]
                trade['exit_date'] = data.index[i]
                trade['exit_price'] = exit_price
                trade['pnl'] = (trade['exit_price'] - trade['entry_price']) / trade['entry_price']

        # If still in position at the end, sell at the last close price
        if position > 0:
            balance = position * data['close'].iloc[-1]

        return {
            "final_balance": balance,
            "performance_pct": (balance / initial_balance - 1) * 100,
            "trades": trades
        }
