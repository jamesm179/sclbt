import pandas as pd
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self, trade_log_file, display_manager):
        self.trade_log_file = trade_log_file
        self.display = display_manager

    def get_pair_performance(self):
        # This can be fleshed out later
        return {}

    def get_all_trade_history(self, days_limit=30):
        """
        Generates a sample DataFrame of historical trades for testing.
        """
        now = datetime.now()
        data = {
            'Timestamp': [now - timedelta(days=x) for x in range(5)],
            'Pair': ['BTC/USDT', 'ETH/USDT', 'BTC/USDT', 'SOL/USDT', 'ETH/USDT'],
            'Action': ['SELL', 'SELL', 'BUY', 'SELL', 'BUY'],
            'Direction': ['long', 'long', 'short', 'long', 'short'],
            'Price': [45000, 3000, 44000, 150, 2950],
            'Amount': [100, 50, 100, 20, 50],
            'P/L%': [5.5, -2.1, 3.2, 8.0, -1.5],
            'Strategy': ['main_strategy', 'trf_strategy', 'main_strategy', 'rsi_cci_strategy', 'trf_strategy'],
            'Reason': ['Take Profit Hit', 'Stop Loss Hit', 'Take Profit Hit', 'Take Profit Hit', 'Stop Loss Hit'],
            'Status': ['Closed', 'Closed', 'Closed', 'Closed', 'Closed']
        }
        df = pd.DataFrame(data)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
