import logging
from datetime import datetime
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

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
        if pd.isna(pl_value) or not isinstance(pl_value, (int, float)): return '#FFFFFF'
        if pl_value > 0: return '#00FF00'
        if pl_value < 0: return '#FF0000'
        return '#FFFF00'

    def create_technical_data(self):
        technicals = []
        # perf_data = self.performance_tracker.get_pair_performance() if self.performance_tracker else {}

        for pair_symbol, df in self.pair_data.items():
            if df is None or df.empty: continue

            latest = df.iloc[-1]
            close_price = latest.get('close', 0)
            filt = latest.get('filt', 0)
            upward = latest.get('upward', 0)
            downward = latest.get('downward', 0)
            cond_ini = latest.get('cond_ini', 0)

            signal = "BUY" if close_price > filt else "SELL"

            technicals.append({
                'pair': pair_symbol.replace('_', '/').replace('B-', ''),
                'price': f"{close_price:.4f}",
                'filt': f"{filt:.4f}",
                'filt_color': '#00FF00' if close_price > filt else '#FF0000',
                'up_down': f"{upward:.0f}/{downward:.0f}",
                'trend_color': '#00FF00' if upward > 0 else '#FF0000',
                'cond': f"{cond_ini:.0f}",
                'cond_color': '#00FF00' if cond_ini == 1 else '#FF0000',
                'signal': signal,
                'signal_color': '#00FF00' if signal == "BUY" else '#FF0000',
                'avg_pl': "N/A", # Placeholder for now
                'pl_color': '#FFFFFF',
                'pair_symbol': pair_symbol
            })
        return technicals

    def create_trade_data(self):
        trades = []
        if not self.engine or not self.engine.active_trades: return trades

        for symbol, trade in self.engine.active_trades.items():
            current_price = self.pair_data.get(symbol, pd.DataFrame()).iloc[-1].get('close', 0)
            if current_price == 0: continue

            entry_price = trade.get('entry_price', 0)
            is_long = trade.get('direction') == 'long'
            leverage = trade.get('leverage', 1)

            profit_pct = (((current_price - entry_price) / entry_price) * 100 * leverage) if is_long else (((entry_price - current_price) / entry_price) * 100 * leverage)

            trades.append({
                'pair': symbol.replace('_', '/').replace('B-', ''),
                'symbol': symbol,
                'direction': trade.get('direction', 'N/A').upper(),
                'dir_color': '#00FF00' if is_long else '#FF0000',
                'entry_price': f"{entry_price:.4f}",
                'current_price': f"{current_price:.4f}",
                'profit_pct': f"{profit_pct:.2f}%",
                'pl_color': self.get_pl_color(profit_pct),
                'stop_loss': f"{trade.get('stop_loss_price', 0):.4f}",
                'take_profit': f"{trade.get('take_profit_price', 0):.4f}",
                'leverage': f"{leverage}x",
                'strategy': trade.get('strategy', 'N/A'),
                'duration': "N/A"
            })
        return trades

    def create_candles_data(self):
        candles = []
        for pair_symbol, df in self.pair_data.items():
            if df is None or df.empty: continue

            # Get last 10 candles
            for _, row in df.tail(10).iterrows():
                candles.append({
                    'pair': pair_symbol.replace('_', '/').replace('B-', ''),
                    'time_ist': row.name.strftime('%H:%M:%S'),
                    'open': f"{row.get('open', 0):.4f}",
                    'high': f"{row.get('high', 0):.4f}",
                    'low': f"{row.get('low', 'N/A'):.4f}",
                    'close': f"{row.get('close', 0):.4f}",
                    'volume': f"{row.get('volume', 0):,.0f}",
                })
        return candles
