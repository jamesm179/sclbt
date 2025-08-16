import logging
import pandas as pd
from .base_client import BaseApiClient

class BinanceClient(BaseApiClient):
    def __init__(self):
        # Use the futures API base URL
        super().__init__("https://fapi.binance.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        interval_map = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d'}
        params = {
            'symbol': symbol.replace('/', '').replace('_', ''),
            'interval': interval_map.get(timeframe, timeframe),
            'limit': limit
        }
        if since:
            params['startTime'] = since

        # Use the futures kline endpoint
        response_data = await self._request('/fapi/v1/klines', params)
        if not response_data:
            return []

        # Normalization logic remains the same
        normalized_data = []
        for row in response_data:
            try:
                normalized_data.append([
                    int(row[0]), float(row[1]), float(row[2]),
                    float(row[3]), float(row[4]), float(row[5])
                ])
            except (ValueError, TypeError, IndexError) as e:
                logging.error(f"Binance client could not parse row: {row}. Error: {e}")
                continue

        return normalized_data
