import logging
import pandas as pd
from .base_client import BaseApiClient

class BitgetClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.bitget.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        granularity_map = {'1m': '1m', '5m': '5m', '1h': '1H', '1d': '1D'}

        formatted_symbol = symbol.replace('/', '').replace('_', '')
        if not formatted_symbol.upper().endswith('USDT'):
            formatted_symbol += 'USDT'

        params = {
            'symbol': formatted_symbol,
            'granularity': granularity_map.get(timeframe, timeframe),
            'limit': limit,
            'productType': 'usdt-futures'
        }
        if since:
            params['startTime'] = since

        response_data = await self._request('/api/v2/mix/market/history-candles', params)
        if not response_data:
            return []

        normalized_data = []
        for row in response_data:
            try:
                normalized_data.append([
                    int(row[0]), float(row[1]), float(row[2]),
                    float(row[3]), float(row[4]), float(row[5])
                ])
            except (ValueError, TypeError, IndexError) as e:
                logging.error(f"Bitget client could not parse row: {row}. Error: {e}")
                continue

        return normalized_data
