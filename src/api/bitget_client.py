import logging
import pandas as pd
import time
import asyncio
from .base_client import BaseApiClient

class BitgetClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.bitget.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        """
        TEMPORARY DEBUGGING VERSION: Fetches tickers to discover correct symbol format.
        """
        params = {'category': 'USDT-FUTURES'}

        # Call the tickers endpoint to see the symbol list
        response_data = await self._request('/api/v3/market/tickers', params)

        # Print the response to the console/log for inspection
        logging.info(f"BITGET TICKERS RESPONSE: {response_data}")

        # Return an empty list to prevent further processing for now
        return []
