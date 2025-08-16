import logging
import pandas as pd
from .base_client import BaseApiClient

class CoinDCXClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://public.coindcx.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 500) -> list:
        interval_map = {'1m': '1m', '5m': '5m', '1h': '1h', '1d': '1d'}
        try:
            base, quote = symbol.split('/')
            pair = f"B-{base}_{quote}"
        except ValueError:
            logging.error(f"CoinDCX client: Invalid symbol format '{symbol}'. Expected 'BASE/QUOTE'.")
            return []

        params = {
            'pair': pair,
            'interval': interval_map.get(timeframe, timeframe),
            'limit': limit
        }
        if since:
            params['startTime'] = since

        response_data = self._request('/market_data/candles', params)
        if not response_data:
            return []

        normalized_data = []
        for row in response_data:
            try:
                normalized_data.append([
                    int(row['time']), float(row['open']), float(row['high']),
                    float(row['low']), float(row['close']), float(row['volume'])
                ])
            except (ValueError, TypeError, KeyError) as e:
                logging.error(f"CoinDCX client could not parse row: {row}. Error: {e}")
                continue

        return sorted(normalized_data, key=lambda x: x[0])
