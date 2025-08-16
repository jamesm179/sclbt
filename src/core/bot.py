import asyncio
import logging
import time
import pandas as pd
from src.core.trading_engine import TradingEngine
from src.dashboard.display_manager import DisplayManager
from src.core.data_downloader import DataDownloader
from src.config.config_manager import config_manager

class HealthMonitor: # Placeholder
    def set_bot(self, bot): pass
    def check_blacklist(self): pass
    def is_pair_blacklisted(self, pair): return False
    def record_successful_cycle(self): pass
    def check_process_health(self, interval): pass

class CryptoBot:
    def __init__(self):
        self.display = DisplayManager(trading_engine=None, db_manager=None, performance_tracker=None)
        self.downloader = DataDownloader()

        self.pairs = []
        self.engine = TradingEngine(api_clients={}, pairs=self.pairs, display_manager=self.display)

        self.display.engine = self.engine
        self.health_monitor = HealthMonitor()
        # self.connectivity_monitor = ConnectivityMonitor() # This needs to be integrated properly

        self.engine.bot = self
        self.health_monitor.set_bot(self)
        # self.connectivity_monitor.set_bot(self)

        self.update_trading_pairs()
        self.running = True

    def update_trading_pairs(self):
        manual_pairs = config_manager.get('manual_trading_pairs', [])
        self.pairs = [{"symbol": s.replace('/', '_'), "color": "white"} for s in manual_pairs]
        self.engine.pairs = self.pairs
        logging.info(f"Trading pairs updated: {len(self.pairs)} pairs active.")

    async def run(self):
        logging.info("CryptoBot run loop started.")
        # self.connectivity_monitor.start_monitoring()

        while self.running:
            start_time = time.time()
            self.health_monitor.check_blacklist()
            active_pairs = [p for p in self.pairs if not self.health_monitor.is_pair_blacklisted(p["symbol"])]

            tasks = [self.process_pair(pair_info) for pair_info in active_pairs]
            await asyncio.gather(*tasks)

            self.health_monitor.record_successful_cycle()

            elapsed = time.time() - start_time
            refresh_interval = 60 # Hardcode for now
            await asyncio.sleep(max(0, refresh_interval - elapsed))

    async def process_pair(self, pair_info):
        pair_symbol = pair_info["symbol"]
        timeframe = config_manager.get('timeframe', '1h')
        try:
            # The downloader returns a list of lists, need to convert to DataFrame
            ohlcv_data = await self.downloader.download_ohlcv(pair_symbol, timeframe)
            if not ohlcv_data:
                return

            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['open_time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('open_time', inplace=True)

            strategy_dfs = await self.engine.process_data(df, pair_info)
            self.display.update_pair_data(pair_symbol, strategy_dfs)

            # signals = await self.engine.check_signals(strategy_dfs)
            # if signals: await self.engine.execute_trades(signals)

        except Exception as e:
            logging.error(f"Error processing pair {pair_symbol}: {e}", exc_info=True)

    def shutdown(self, signum=None, frame=None):
        self.running = False
        # self.connectivity_monitor.stop_monitoring()
        logging.info("Shutting down bot...")
