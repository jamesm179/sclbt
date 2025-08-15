import ccxt
import time
from src.core.config import ConfigManager
from src.core.logger import setup_logger
from src.data.database import DatabaseManager
from src.data.downloader import DataDownloader
from src.strategies.rsi_strategy import RsiStrategy
from src.strategies.base import BaseStrategy

STRATEGY_MAP = {
    'rsi': RsiStrategy,
}

class TradingBot:
    def __init__(self, args):
        self.args = args
        self.config_manager = ConfigManager(args.config)
        self.logger = setup_logger('trading_bot', 'logs/trading_bot.log')
        self.error_logger = setup_logger('error_logger', 'logs/trading_bot_error.log', level='ERROR')

        # --- Config Values ---
        self.db_url = self.config_manager.get('database.database_url', 'sqlite:///crypto_ohlcv.db')
        self.symbol = args.symbol
        self.timeframe = args.timeframe

        # --- Components ---
        self.db_manager = self._init_db()
        self.downloader = DataDownloader() # Now exchange-agnostic
        self.strategy = self._init_strategy()

    def _init_db(self):
        db_manager = DatabaseManager(self.db_url)
        db_manager.create_tables()
        self.logger.info("Database initialized and tables created.")
        return db_manager

    def _init_strategy(self) -> BaseStrategy:
        strategy_name = self.args.strategy.lower()
        strategy_class = STRATEGY_MAP.get(strategy_name)

        if not strategy_class:
            msg = f"Strategy '{strategy_name}' not found."
            self.error_logger.error(msg)
            raise ValueError(msg)

        strategy_params = self.config_manager.get(f'strategies.{strategy_name}', {})

        self.logger.info(f"Initializing strategy: {strategy_name} with params: {strategy_params}")
        return strategy_class(strategy_params)

    def _fetch_and_store_data(self):
        self.logger.info(f"Fetching historical data for {self.symbol} using multi-source downloader...")
        since = ccxt.Exchange.parse8601('2023-01-01T00:00:00Z')

        ohlcv_objects = self.downloader.download_ohlcv(self.symbol, self.timeframe, since=since, limit=1000)

        if ohlcv_objects:
            self.db_manager.store_ohlcv(ohlcv_objects)
            self.logger.info(f"Stored {len(ohlcv_objects)} new OHLCV records in the database.")
        else:
            self.logger.warning("Could not download any new data from any source.")

    def run(self):
        self.logger.info("Starting trading bot...")
        self._fetch_and_store_data()

        interval = ccxt.Exchange.parse_timeframe(self.timeframe)
        self.logger.info(f"Starting trading loop. Cycle interval: {interval} seconds.")

        while True:
            try:
                self.trading_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("Shutdown signal received. Exiting...")
                break
            except Exception as e:
                self.error_logger.error(f"Error in trading loop: {e}", exc_info=True)
                time.sleep(60)

    def trading_cycle(self):
        self.logger.info("--- New Trading Cycle ---")

        # Fetch the latest data for the symbol from any/all exchanges in the DB
        data = self.db_manager.fetch_ohlcv_as_dataframe(
            symbol=self.symbol, limit=200
        )

        if data.empty or len(data) < self.strategy.parameters.get('rsi_period', 14) + 1:
            self.logger.warning("Not enough data in DB to generate a signal. Attempting to fetch more.")
            self._fetch_and_store_data()
            return

        self.logger.info(f"Latest data loaded. Last candle: {data.index[-1]}")

        signal = self.strategy.generate_signal(data)
        self.logger.info(f"Strategy signal: {signal}")

        if signal == 'BUY':
            self.logger.info(f"ACTION: Execute BUY for {self.symbol}")
        elif signal == 'SELL':
            self.logger.info(f"ACTION: Execute SELL for {self.symbol}")
        else:
            self.logger.info("ACTION: Hold.")
