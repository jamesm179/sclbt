import pandas as pd

class PerformanceTracker:
    def __init__(self, trade_log_file, display_manager):
        self.trade_log_file = trade_log_file
        self.display = display_manager

    def get_pair_performance(self):
        return {}

    def get_all_trade_history(self, days_limit=30):
        return pd.DataFrame()
