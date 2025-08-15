import ccxt
from src.data.models import OHLCV
from src.core.exceptions import APIConnectionException
import time

class DataDownloader:
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange

    def download_ohlcv(self, symbol, timeframe='1h', since=None, limit=100):
        """
        Downloads historical OHLCV data for a given symbol and timeframe, handling pagination.
        """
        if not self.exchange.has['fetchOHLCV']:
            raise APIConnectionException(f"Exchange {self.exchange.id} does not support fetching OHLCV data.")

        if isinstance(since, str):
            since = self.exchange.parse8601(since)

        all_ohlcv = []
        try:
            while True:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                if not ohlcv:
                    break

                first_timestamp = ohlcv[0][0]
                last_timestamp = ohlcv[-1][0]

                # Check for duplicates to avoid infinite loops on exchanges that don't advance timestamp
                if len(all_ohlcv) > 0 and first_timestamp <= all_ohlcv[-1][0]:
                    break

                all_ohlcv.extend(ohlcv)

                if len(ohlcv) < limit:
                    break

                since = last_timestamp + self.exchange.parse_timeframe(timeframe) * 1000

                # Respect rate limits
                time.sleep(self.exchange.rateLimit / 1000)

        except ccxt.NetworkError as e:
            raise APIConnectionException(f"Network error while fetching OHLCV data: {e}")
        except ccxt.ExchangeError as e:
            raise APIConnectionException(f"Exchange error while fetching OHLCV data: {e}")
        except Exception as e:
            raise APIConnectionException(f"An unexpected error occurred: {e}")

        # Convert to list of OHLCV objects
        ohlcv_objects = []
        # Use a set to keep track of timestamps and avoid duplicates
        seen_timestamps = set()
        for row in all_ohlcv:
            if row[0] not in seen_timestamps:
                ohlcv_objects.append(OHLCV(
                    exchange=self.exchange.id,
                    symbol=symbol,
                    timestamp=row[0],
                    open=row[1],
                    high=row[2],
                    low=row[3],
                    close=row[4],
                    volume=row[5]
                ))
                seen_timestamps.add(row[0])

        return ohlcv_objects
