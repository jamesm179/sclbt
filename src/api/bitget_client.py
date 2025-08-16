import logging
import pandas as pd
import time
from .base_client import BaseApiClient

class BitgetClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.bitget.com")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 300) -> list:
        """
        Fetches historical OHLCV data from Bitget's V3 futures API, handling pagination.
        """
        granularity_map = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1H', '4h': '4H', '1d': '1D'}

        formatted_symbol = symbol.replace('/', '').replace('_', '')
        if not formatted_symbol.upper().endswith('USDT'):
            formatted_symbol += 'USDT'

        all_candles = []
        # Bitget V3 API has a max limit of 100 per request.
        # We need to paginate to get more data.
        max_limit_per_req = 100
        end_time = None

        while len(all_candles) < limit:
            fetch_limit = min(limit - len(all_candles), max_limit_per_req)

            params = {
                'symbol': formatted_symbol,
                'granularity': granularity_map.get(timeframe, timeframe),
                'limit': fetch_limit,
                'category': 'USDT-FUTURES'
            }
            if end_time:
                params['endTime'] = end_time

            response_data = await self._request('/api/v3/market/candles', params)

            # Check for API response structure
            if not response_data or 'data' not in response_data or not response_data['data']:
                logging.warning(f"Bitget client: No more data received for {symbol}. Got {len(all_candles)} candles.")
                break

            candles = response_data['data']
            all_candles.extend(candles)

            # Prepare for next page
            oldest_timestamp = int(candles[-1][0])
            end_time = oldest_timestamp - 1 # Avoid getting the same last candle

            # Respect rate limits
            await asyncio.sleep(0.2) # 200ms delay between paginated requests

        if not all_candles:
            return []

        # Normalize the data
        normalized_data = []
        for row in all_candles:
            try:
                normalized_data.append([
                    int(row[0]), float(row[1]), float(row[2]),
                    float(row[3]), float(row[4]), float(row[5])
                ])
            except (ValueError, TypeError, IndexError) as e:
                logging.error(f"Bitget client could not parse row: {row}. Error: {e}")
                continue

        # Data is returned newest first, so we need to reverse it
        return sorted(normalized_data, key=lambda x: x[0])
import asyncio # Add missing import for asyncio.sleep
