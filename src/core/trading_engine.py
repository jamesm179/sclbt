import os
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.notifications.telegram_notifier import TelegramNotifier
from src.loggers.async_trade_logger import AsyncTradeLogger
from src.managers.performance_tracker import PerformanceTracker
from src.strategies.base import Strategy
from src.strategies.ema_cci_strategy import EMACCIStrategy
from src.strategies.trf_strategy import TRFStrategy
from src.strategies.rsi_cci_strategy import RSICCIStrategy
from src.core.kill_switch import EmergencyKillSwitch
from src.config.config_manager import config_manager # Import the instance
from src.dashboard.display_manager import DisplayManager

def get_strategy(strategy_name: str, config: Dict[str, Any]) -> Strategy:
    strategies = {
        'main_strategy': EMACCIStrategy,
        'rsi_cci_strategy': RSICCIStrategy,
        'trf_strategy': TRFStrategy
    }
    strategy_class = strategies.get(strategy_name)
    if not strategy_class:
        raise ValueError(f"Unsupported strategy: {strategy_name}")
    return strategy_class(config)

class TradingEngine:
    def __init__(self, api_clients: Dict, pairs: list, display_manager: DisplayManager):
        self.api_clients = api_clients
        self.active_trades = {}
        self.telegram = TelegramNotifier(display_manager)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.trade_log_file = os.path.join('logs', f'trades_{timestamp}.csv')
        self.async_trade_logger = AsyncTradeLogger(self.trade_log_file)
        self.performance_tracker = PerformanceTracker(self.trade_log_file, display_manager)
        self.display = display_manager
        self.bot_start_time = datetime.now()
        self.signals_today = 0

        # Use the config_manager
        self.strategies = {
            strat: get_strategy(strat, config_manager.get('strategies', {}).get(strat, {}))
            for strat in config_manager.get('active_strategies', [])
        }
        self.pairs = pairs
        self.balance = 1000.0
        self.bot = None
        self.emergency_kill_switch = EmergencyKillSwitch(self)

    async def process_data(self, data, pair_info=None):
        """
        Process market data with all active strategies.
        """
        if data.empty:
            return None

        pair_name = pair_info["symbol"] if pair_info else "UNKNOWN_PAIR"

        try:
            strategy_dfs = {}
            # Process with each active strategy
            for strat_name, strategy in self.strategies.items():
                df_strat = strategy.get_indicators(data.copy())
                strategy_dfs[strat_name] = df_strat

            return strategy_dfs
        except Exception as e:
            self.display.add_log(f"Error processing {pair_name}: {e}")
            logging.error(f"Error processing data for {pair_name}: {e}", exc_info=True)
            return None

    async def check_signals(self, strategy_dfs):
        # Simplified for now
        return {}

    async def execute_trades(self, signals):
        # Simplified for now
        return False

    def log_trade(self, exchange, action, pair, price, amount, balance, profit_pct, reason, direction, stop_loss_price=None, take_profit_price=None, trade_id=None, status="Active"):
        asyncio.create_task(
            self.async_trade_logger.log_trade_async(
                exchange, action, pair, price, amount, balance, profit_pct, reason, direction,
                stop_loss_price, take_profit_price, trade_id, status
            )
        )
