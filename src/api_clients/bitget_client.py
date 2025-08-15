from .base_client import BaseApiClient

class BitgetClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.bitget.com")

    def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 100) -> list:
        # Bitget's API has different endpoints for spot and futures, and uses 'granularity'
        # This is a simplified client assuming USDT futures as per the research example.

        # A simple mapping from standard timeframes to Bitget's 'granularity'
        granularity_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1H', '4h': '4H', '1d': '1D', '1w': '1W'
        }

        params = {
            'symbol': symbol.replace('/', '') + 'USDT', # e.g., 'BTC/USDT' -> 'BTCUSDT'
            'granularity': granularity_map.get(timeframe, timeframe),
            'limit': limit
        }
        # Note: The v2 history-candles endpoint is for futures. A different one is needed for spot.
        # Let's use the more general candles endpoint which might work for spot.
        # After more review, the public spot endpoint is /api/v2/spot/market/candles

        endpoint = '/api/v2/spot/market/candles'

        if since:
            # Bitget uses startTime and endTime
            params['startTime'] = since

        response_data = self._request(endpoint, params)

        if not response_data:
            return []

        # The actual data is in the root of the response list
        # Bitget response: [ [ts, open, high, low, close, volume], ... ]
        normalized_data = []
        for row in response_data:
            try:
                # Data comes as strings, so we need to cast them
                normalized_data.append([
                    int(row[0]),
                    float(row[1]),
                    float(row[2]),
                    float(row[3]),
                    float(row[4]),
                    float(row[5])
                ])
            except (ValueError, TypeError, IndexError) as e:
                print(f"Bitget client could not parse row: {row}. Error: {e}")
                continue

        # API docs say data is sorted in ascending order, so no reversal needed.
        return normalized_data
