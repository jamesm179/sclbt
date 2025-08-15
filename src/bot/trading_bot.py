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

        self.exchange_id = self.config_manager.get('exchange.id', 'binance')
        self.api_key = self.config_manager.get('exchange.api_key')
        self.secret = self.config_manager.get('exchange.secret')
        self.test_mode = args.test_mode or self.config_manager.get('exchange.test_mode', True)
        self.db_url = self.config_manager.get('database.database_url', 'sqlite:///crypto_ohlcv.db')

        self.symbol = args.symbol
        self.timeframe = args.timeframe

        self.db_manager = self._init_db()
        self.exchange = self._init_exchange()
        self.downloader = DataDownloader(self.exchange)
        self.strategy = self._init_strategy()

    def _init_db(self):
        db_manager = DatabaseManager(self.db_url)
        db_manager.create_tables()
        self.logger.info("Database initialized and tables created.")
        return db_manager

    def _init_exchange(self):
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            exchange = exchange_class({'apiKey': self.api_key, 'secret': self.secret})
            if self.test_mode:
                if 'test' in exchange.urls:
                    exchange.set_sandbox_mode(True)
                else:
                    self.logger.warning(f"Exchange {self.exchange_id} does not support sandbox mode. Live trading is active.")

            exchange.load_markets()
            self.logger.info(f"Exchange '{self.exchange_id}' initialized. Test mode: {self.test_mode}")
            return exchange
        except Exception as e:
            self.error_logger.error(f"Failed to initialize exchange: {e}")
            raise

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
        self.logger.info(f"Fetching historical data for {self.symbol}...")
        since = self.exchange.parse8601('2023-01-01T00:00:00Z')
        ohlcv_objects = self.downloader.download_ohlcv(self.symbol, self.timeframe, since=since, limit=1000)

        if ohlcv_objects:
            self.db_manager.store_ohlcv(ohlcv_objects)
            self.logger.info(f"Stored {len(ohlcv_objects)} OHLCV records.")
        else:
            self.logger.info("No new historical data found.")

    def run(self):
        self.logger.info("Starting trading bot...")
        self._fetch_and_store_data()

        interval = self.exchange.parse_timeframe(self.timeframe)
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

        data = self.db_manager.fetch_ohlcv_as_dataframe(
            exchange=self.exchange_id, symbol=self.symbol, limit=200
        )

        if data.empty or len(data) < self.strategy.parameters.get('rsi_period', 14) + 1:
            self.logger.warning("Not enough data to generate a signal. Fetching more data.")
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
