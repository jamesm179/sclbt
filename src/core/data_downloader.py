import logging
import asyncio
import ccxt.async_support as ccxt
from src.api.base_client import BaseApiClient
from src.api.bitget_client import BitgetClient
from src.api.binance_client import BinanceClient
from src.api.coindcx_client import CoinDCXClient
# from src.data.models import OHLCV # This model is not fully used yet

class DataDownloader:
    def __init__(self):
        # Temporarily focus on Binance for debugging
        self.primary_clients: list[BaseApiClient] = [BinanceClient()]
        self.fallback_exchanges = [] # Disable fallback for now
        self.logger = logging.getLogger(self.__class__.__name__)

    async def download_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        self.logger.info(f"Attempting to download OHLCV for {symbol} | Timeframe: {timeframe}")

        # --- Try Primary Direct API Clients ---
        for client in self.primary_clients:
            client_name = client.__class__.__name__
            self.logger.debug(f"Trying direct client: {client_name}")
            try:
                data = await client.fetch_ohlcv(symbol, timeframe, since, limit)
                if data:
                    self.logger.info(f"SUCCESS: Fetched {len(data)} records from {client_name}.")
                    # In the future, this would return OHLCV objects
                    return data
                else:
                    self.logger.debug(f"Client {client_name} returned no data for {symbol}.")
            except Exception as e:
                self.logger.error(f"FAIL: Client {client_name} failed for {symbol}. Error: {e}", exc_info=True)
                continue

        self.logger.warning(f"All primary API clients failed for {symbol}. Falling back to ccxt.")

        # --- Fallback to CCXT ---
        for exchange_id in self.fallback_exchanges:
            self.logger.debug(f"Trying ccxt fallback: {exchange_id}")
            try:
                exchange = getattr(ccxt, exchange_id)()
                if exchange.has['fetchOHLCV']:
                    ohlcv_data = await exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                    await exchange.close() # Close the session
                    if ohlcv_data:
                        self.logger.info(f"SUCCESS: Fetched {len(ohlcv_data)} records from ccxt fallback: {exchange_id}.")
                        return ohlcv_data
                else:
                    self.logger.debug(f"CCXT exchange {exchange_id} does not support fetchOHLCV.")
            except Exception as e:
                self.logger.error(f"FAIL: CCXT fallback for {exchange_id} failed for {symbol}. Error: {e}", exc_info=True)
                if 'exchange' in locals() and exchange:
                    await exchange.close()
                continue

        self.logger.error(f"CRITICAL: Failed to download OHLCV data for {symbol} from ALL available sources.")
        return []
