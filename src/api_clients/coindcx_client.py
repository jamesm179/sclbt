from .base_client import BaseApiClient

class CoinDCXClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://public.coindcx.com")

    def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = 500) -> list:
        # CoinDCX uses 'interval' and a special 'pair' format like 'B-BTC_USDT'
        interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
        }

        try:
            base, quote = symbol.split('/')
            pair = f"B-{base}_{quote}"
        except ValueError:
            print(f"CoinDCX client: Invalid symbol format '{symbol}'. Expected 'BASE/QUOTE'.")
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

        # Normalize the data from a list of dictionaries
        normalized_data = []
        for row in response_data:
            try:
                # The response keys are 'time', 'open', 'high', 'low', 'close', 'volume'
                normalized_data.append([
                    int(row['time']),
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close']),
                    float(row['volume'])
                ])
            except (ValueError, TypeError, KeyError) as e:
                print(f"CoinDCX client could not parse row: {row}. Error: {e}")
                continue

        # Ensure data is sorted by timestamp in ascending order
        return sorted(normalized_data, key=lambda x: x[0])
