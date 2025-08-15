import logging

class DisplayManager:
    def __init__(self, trading_engine=None, db_manager=None, performance_tracker=None):
        self.log_messages = []

    def add_log(self, message):
        logging.info(f"[DISPLAY LOG] {message}")

    def update_pair_data(self, pair_symbol, strategy_dfs):
        pass
