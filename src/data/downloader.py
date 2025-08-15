import ccxt
from src.data.models import OHLCV
from src.api_clients.bitget_client import BitgetClient
from src.api_clients.binance_client import BinanceClient
from src.api_clients.coindcx_client import CoinDCXClient
import logging

# It's better to get a logger instance than to use print
logger = logging.getLogger(__name__)

class DataDownloader:
    def __init__(self):
        """
        Initializes the DataDownloader with a prioritized list of clients.
        """
        self.primary_clients = [
            BitgetClient(),
            BinanceClient(),
            CoinDCXClient()
        ]
        # A list of exchange IDs to try with ccxt if primary clients fail
        self.fallback_exchanges = ['kraken', 'coinbase', 'kucoin']

    def download_ohlcv(self, symbol: str, timeframe: str = '1h', since: int = None, limit: int = 100) -> list[OHLCV]:
        """
        Downloads historical OHLCV data using primary direct API clients first,
        then falls back to using the ccxt library with a list of exchanges.
        """
        logger.info(f"Starting OHLCV data download for {symbol}...")

        # --- Attempt 1: Primary Direct API Clients ---
        for client in self.primary_clients:
            client_name = client.__class__.__name__
            logger.info(f"Attempting to fetch data using direct client: {client_name}")
            try:
                data = client.fetch_ohlcv(symbol, timeframe, since, limit)
                if data:
                    logger.info(f"Successfully fetched {len(data)} records from {client_name}.")
                    # The source exchange is now logged with the data itself
                    return self._to_ohlcv_objects(data, client_name.replace('Client','').lower(), symbol)
            except Exception as e:
                logger.warning(f"Direct client {client_name} failed for {symbol}. Error: {e}")
                continue

        logger.warning(f"All primary direct clients failed for {symbol}. Moving to ccxt fallback.")

        # --- Attempt 2: CCXT Fallback ---
        for exchange_id in self.fallback_exchanges:
            logger.info(f"Attempting ccxt fallback with exchange: {exchange_id}")
            try:
                exchange = getattr(ccxt, exchange_id)()
                if exchange.has['fetchOHLCV']:
                    ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                    if ohlcv_data:
                        logger.info(f"Successfully fetched {len(ohlcv_data)} records from ccxt fallback: {exchange_id}.")
                        return self._to_ohlcv_objects(ohlcv_data, exchange_id, symbol)
            except Exception as e:
                logger.warning(f"CCXT fallback for {exchange_id} failed for {symbol}. Error: {e}")
                continue

        logger.error(f"Failed to download OHLCV data for {symbol} from all available sources.")
        return []

    def _to_ohlcv_objects(self, data: list, exchange_id: str, symbol: str) -> list[OHLCV]:
        """Converts raw list-of-lists data to a list of OHLCV model objects."""
        ohlcv_objects = []
        for row in data:
            ohlcv_objects.append(OHLCV(
                exchange=exchange_id,
                symbol=symbol,
                timestamp=row[0],
                open=row[1],
                high=row[2],
                low=row[3],
                close=row[4],
                volume=row[5]
            ))
        return ohlcv_objects
