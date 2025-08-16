import logging
from datetime import datetime
import pandas as pd

class DisplayManager:
    def __init__(self, trading_engine=None, db_manager=None, performance_tracker=None):
        self.engine = trading_engine
        self.db_manager = db_manager
        self.performance_tracker = performance_tracker
        self.log_messages = []
        self.pair_data = {} # To store the latest DataFrame for each pair

    def add_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.log_messages.append(formatted_message)
        if len(self.log_messages) > 50: # Keep last 50 logs
            self.log_messages = self.log_messages[-50:]
        logging.info(message)

    def update_pair_data(self, pair_symbol, strategy_dfs):
        # For now, we'll just use the 'main_strategy' df for display
        if strategy_dfs and 'main_strategy' in strategy_dfs:
            self.pair_data[pair_symbol] = strategy_dfs['main_strategy']

    def create_technical_data(self):
        technicals = []
        for pair_symbol, df in self.pair_data.items():
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                technicals.append({
                    'pair': pair_symbol.replace('_', '/'),
                    'price': f"{latest.get('close', 0):.4f}",
                    'signal': "BUY" if latest.get('close', 0) > latest.get('ema200', 0) else "SELL",
                    # Add more technicals later
                })
        return technicals

    def create_trade_data(self):
        trades = []
        if not self.engine or not self.engine.active_trades:
            return trades
        for symbol, trade in self.engine.active_trades.items():
            # This logic needs to be fully fleshed out
            trades.append({
                'pair': symbol.replace('_', '/'),
                'direction': trade.get('direction', 'N/A'),
                'entry_price': f"{trade.get('entry_price', 0):.4f}",
                'profit_pct': "0.00%",
            })
        return trades

    def create_candles_data(self):
        candles = []
        for pair_symbol, df in self.pair_data.items():
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                candles.append({
                    'pair': pair_symbol.replace('_', '/'),
                    'time_ist': latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                    'open': f"{latest.get('open', 0):.4f}",
                    'high': f"{latest.get('high', 0):.4f}",
                    'low': f"{latest.get('low', 0):.4f}",
                    'close': f"{latest.get('close', 0):.4f}",
                    'volume': f"{latest.get('volume', 0):,.0f}",
                })
        return candles[-10:] # Return last 10 for display
