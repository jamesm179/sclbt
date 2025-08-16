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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.display = DisplayManager()
        self.downloader = DataDownloader()
        self.pairs = []
        self.engine = TradingEngine(api_clients={}, pairs=self.pairs, display_manager=self.display)
        self.display.engine = self.engine
        self.health_monitor = HealthMonitor()
        self.engine.bot = self
        self.health_monitor.set_bot(self)
        self.update_trading_pairs()
        self.running = True

    def update_trading_pairs(self):
        manual_pairs = config_manager.get('manual_trading_pairs', [])
        self.pairs = [{"symbol": s.replace('/', '_'), "color": "white"} for s in manual_pairs]
        self.engine.pairs = self.pairs
        self.logger.info(f"Trading pairs updated: {len(self.pairs)} pairs active.")

    async def run(self):
        self.logger.info("CryptoBot run loop started.")
        cycle_count = 0
        while self.running:
            cycle_count += 1
            self.logger.info(f"--- Starting Bot Cycle #{cycle_count} ---")
            start_time = time.time()

            self.health_monitor.check_blacklist()
            active_pairs = [p for p in self.pairs if not self.health_monitor.is_pair_blacklisted(p["symbol"])]

            tasks = [self.process_pair(pair_info) for pair_info in active_pairs]
            await asyncio.gather(*tasks)

            self.health_monitor.record_successful_cycle()

            elapsed = time.time() - start_time
            self.logger.info(f"--- Bot Cycle #{cycle_count} Finished ({elapsed:.2f}s) ---")

            refresh_interval = 60
            await asyncio.sleep(max(0, refresh_interval - elapsed))

    async def process_pair(self, pair_info):
        pair_symbol = pair_info["symbol"]
        timeframe = config_manager.get('timeframe', '1h')
        self.logger.debug(f"Processing pair: {pair_symbol}")
        try:
            ohlcv_data = await self.downloader.download_ohlcv(pair_symbol, timeframe)
            if not ohlcv_data:
                self.logger.warning(f"No OHLCV data returned for {pair_symbol}.")
                return

            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['open_time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('open_time', inplace=True)

            strategy_dfs = await self.engine.process_data(df, pair_info)
            self.display.update_pair_data(pair_symbol, strategy_dfs)

            self.logger.debug(f"Successfully processed pair: {pair_symbol}")

        except Exception as e:
            self.logger.error(f"CRITICAL ERROR processing pair {pair_symbol}: {e}", exc_info=True)

    def shutdown(self, signum=None, frame=None):
        self.running = False
        self.logger.info("Shutting down bot...")
