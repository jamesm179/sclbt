import logging
import asyncio
import ccxt.async_support as ccxt # Use async version of ccxt
from src.api.bitget_client import BitgetClient
from src.api.binance_client import BinanceClient
from src.api.coindcx_client import CoinDCXClient
from src.data.models import OHLCV # Assuming this model exists

class DataDownloader:
    def __init__(self):
        self.primary_clients = [BitgetClient(), BinanceClient(), CoinDCXClient()]
        self.fallback_exchanges = ['kraken', 'kucoin']

    async def download_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 100) -> list:
        logging.info(f"Attempting to download OHLCV for {symbol} using direct API clients...")

        for client in self.primary_clients:
            try:
                data = await client.fetch_ohlcv(symbol, timeframe, since, limit)
                if data:
                    logging.info(f"Successfully fetched {len(data)} records from {client.__class__.__name__}.")
                    return self._to_ohlcv_objects(data, client.__class__.__name__.replace('Client','').lower(), symbol)
            except Exception as e:
                logging.warning(f"Client {client.__class__.__name__} failed: {e}")

        logging.warning("All primary API clients failed. Falling back to ccxt.")

        for exchange_id in self.fallback_exchanges:
            try:
                exchange = getattr(ccxt, exchange_id)()
                if exchange.has['fetchOHLCV']:
                    ohlcv_data = await exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                    await exchange.close()
                    if ohlcv_data:
                        logging.info(f"Successfully fetched {len(ohlcv_data)} records from ccxt fallback: {exchange_id}.")
                        return self._to_ohlcv_objects(ohlcv_data, exchange_id, symbol)
            except Exception as e:
                logging.warning(f"CCXT fallback for {exchange_id} failed: {e}")

        return []

    def _to_ohlcv_objects(self, data: list, exchange_id: str, symbol: str) -> list:
        # This should return OHLCV objects, but for now, we'll just return the raw list
        return data
