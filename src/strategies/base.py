import pandas as pd
from typing import Dict, Any

class Strategy:
    """
    Abstract base class for all trading strategies.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__

    def get_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates and adds all necessary indicators to the DataFrame.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_indicators")

    async def check_signals(self, latest_row: pd.Series, active_trades: Dict) -> Dict[str, Any]:
        """
        Checks for entry or exit signals based on the latest data.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement check_signals")
