from .base_client import BaseApiClient

class BinanceClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://api.binance.com")

    def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 500) -> list:
        # Binance uses 'interval' for timeframe
        interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
        }

        params = {
            'symbol': symbol.replace('/', ''),
            'interval': interval_map.get(timeframe, timeframe),
            'limit': limit
        }
        if since:
            params['startTime'] = since

        response_data = self._request('/api/v3/klines', params)

        if not response_data:
            return []

        # Normalize the data
        # Binance response format:
        # [ open_time, open, high, low, close, volume, ... ]
        normalized_data = []
        for row in response_data:
            try:
                normalized_data.append([
                    int(row[0]),      # Open time (timestamp)
                    float(row[1]),    # Open
                    float(row[2]),    # High
                    float(row[3]),    # Low
                    float(row[4]),    # Close
                    float(row[5])     # Volume
                ])
            except (ValueError, TypeError, IndexError) as e:
                print(f"Binance client could not parse row: {row}. Error: {e}")
                continue

        return normalized_data
