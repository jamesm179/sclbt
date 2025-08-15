import asyncio
import logging
import time
from src.core.trading_engine import TradingEngine
from src.dashboard.display_manager import DisplayManager
from src.managers.connectivity_monitor import ConnectivityMonitor
from src.api.factory import ExchangeAPIFactory
from src.config.config_manager import config_manager

class HealthMonitor: # Placeholder
    def set_bot(self, bot): pass
    def check_blacklist(self): pass
    def is_pair_blacklisted(self, pair): return False
    def record_successful_cycle(self): pass
    def check_process_health(self, interval): pass

class CryptoBot:
    def __init__(self):
        # Use a placeholder for db_manager for now
        self.db_manager = None
        self.display = DisplayManager(trading_engine=None, db_manager=self.db_manager, performance_tracker=None)

        # Initialize API clients for all supported exchanges for flexibility
        self.api_clients = {
            name: ExchangeAPIFactory.create_api(name, {}, self.display, self.db_manager, config_manager)
            for name in ['coindcx', 'bitget', 'binance']
        }

        self.pairs = [] # Will be updated by update_trading_pairs
        self.engine = TradingEngine(self.api_clients, self.pairs, self.display)

        self.display.engine = self.engine
        self.health_monitor = HealthMonitor()
        self.connectivity_monitor = ConnectivityMonitor()

        self.engine.bot = self
        self.health_monitor.set_bot(self)
        self.connectivity_monitor.set_bot(self)

        self.update_trading_pairs() # Initial pair setup
        self.running = True

    def update_trading_pairs(self):
        # Combines default and manual pairs from config
        default_pairs = config_manager.get('default_pairs', []) # Assuming this key exists
        manual_pairs = config_manager.get('manual_trading_pairs', [])
        all_pair_symbols = sorted(list(set(default_pairs + manual_pairs)))

        self.pairs = [{"symbol": s.replace('/', '_'), "color": "white", "weight": i} for i, s in enumerate(all_pair_symbols)]
        self.engine.pairs = self.pairs
        logging.info(f"Trading pairs updated: {len(self.pairs)} pairs active.")

    async def run(self):
        logging.info("CryptoBot run loop started.")
        self.connectivity_monitor.start_monitoring()

        while self.running:
            start_time = time.time()
            self.health_monitor.check_blacklist()

            active_pairs = [p for p in self.pairs if not self.health_monitor.is_pair_blacklisted(p["symbol"])]

            # Use the currently selected exchange from config
            exchange_name = config_manager.get('selected_exchange', 'coindcx')
            api_client = self.api_clients.get(exchange_name)

            if not api_client:
                logging.error(f"Selected exchange '{exchange_name}' not available.")
                await asyncio.sleep(5)
                continue

            tasks = [self.process_pair(api_client, pair_info) for pair_info in active_pairs]
            await asyncio.gather(*tasks)

            self.health_monitor.record_successful_cycle()

            elapsed = time.time() - start_time
            refresh_interval = config_manager.get('refresh_interval', 60)
            sleep_time = max(0, refresh_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def process_pair(self, api_client, pair_info):
        pair_symbol = pair_info["symbol"]
        timeframe = config_manager.get('timeframe', '1h')
        try:
            data = await api_client.get_historical_data(pair_symbol, timeframe)
            if data.empty:
                return

            strategy_dfs = await self.engine.process_data(data, pair_info)
            self.display.update_pair_data(pair_symbol, strategy_dfs)

            signals = await self.engine.check_signals(strategy_dfs)
            if signals:
                await self.engine.execute_trades(signals)

        except Exception as e:
            logging.error(f"Error processing pair {pair_symbol}: {e}", exc_info=True)

    def shutdown(self, signum=None, frame=None):
        self.running = False
        self.connectivity_monitor.stop_monitoring()
        logging.info("Shutting down bot...")
