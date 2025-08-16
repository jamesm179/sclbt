import logging
import pandas as pd
from .base_client import BaseApiClient

class BinanceClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.binance.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        # Binance uses 'interval' for timeframe and a specific symbol format
        interval_map = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d'}
        params = {
            'symbol': symbol.replace('/', '').replace('_', ''),
            'interval': interval_map.get(timeframe, timeframe),
            'limit': limit
        }
        if since:
            params['startTime'] = since

        response_data = await self._request('/api/v3/klines', params)
        if not response_data:
            return []

        # Normalize the data
        normalized_data = []
        for row in response_data:
            try:
                normalized_data.append([
                    int(row[0]),      # Open time
                    float(row[1]),    # Open
                    float(row[2]),    # High
                    float(row[3]),    # Low
                    float(row[4]),    # Close
                    float(row[5])     # Volume
                ])
            except (ValueError, TypeError, IndexError) as e:
                logging.error(f"Binance client could not parse row: {row}. Error: {e}")
                continue

        return normalized_data
