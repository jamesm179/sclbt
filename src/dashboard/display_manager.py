import logging
from datetime import datetime
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
from src.config.config_manager import config_manager

class DisplayManager:
    def __init__(self, trading_engine=None, db_manager=None, performance_tracker=None):
        self.engine = trading_engine
        self.db_manager = db_manager
        self.performance_tracker = performance_tracker
        self.log_messages = []
        self.pair_data = {}

    def add_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_messages.append(f"[{timestamp}] {message}")
        if len(self.log_messages) > 50:
            self.log_messages = self.log_messages[-50:]
        logging.info(message)

    def update_pair_data(self, pair_symbol, strategy_dfs):
        if strategy_dfs and 'main_strategy' in strategy_dfs:
            self.pair_data[pair_symbol] = strategy_dfs['main_strategy']

    def get_pl_color(self, pl_value):
        colors = config_manager.get('colors', {"positive": "#00FF00", "negative": "#FF0000", "neutral": "#FFFFFF"})
        if pd.isna(pl_value) or not isinstance(pl_value, (int, float)): return colors.get('neutral')
        if pl_value > 0: return colors.get('positive')
        if pl_value < 0: return colors.get('negative')
        return colors.get('neutral')

    def create_technical_data(self):
        technicals = []
        colors = config_manager.get('colors', {"positive": "#00FF00", "negative": "#FF0000"})
        positive_color = colors.get('positive')
        negative_color = colors.get('negative')

        for pair_symbol, df in self.pair_data.items():
            if df is None or df.empty: continue

            latest = df.iloc[-1]
            close_price = latest.get('close', 0)
            filt = latest.get('filt', 0)
            upward = latest.get('upward', 0)
            cond_ini = latest.get('cond_ini', 0)
            signal = "BUY" if close_price > filt else "SELL"

            technicals.append({
                'pair': pair_symbol.replace('_', '/').replace('B-', ''),
                'exchange': 'N/A', # Placeholder for now
                'price': f"{close_price:.4f}",
                'filt': f"{filt:.4f}",
                'filt_color': positive_color if close_price > filt else negative_color,
                'up_down': f"{upward:.0f}/{latest.get('downward', 0):.0f}",
                'trend_color': positive_color if upward > 0 else negative_color,
                'cond': f"{cond_ini:.0f}",
                'cond_color': positive_color if cond_ini == 1 else negative_color,
                'signal': signal,
                'signal_color': positive_color if signal == "BUY" else negative_color,
            })
        return technicals

    def create_trade_data(self):
        # ... (this method remains the same for now)
        return []

    def create_candles_data(self):
        # ... (this method remains the same for now)
        return []
