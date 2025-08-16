import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BaseExchangeAPI:
    def __init__(self, credentials, display_manager, db_manager, config):
        pass

    def get_wallet_data(self):
        return [{'currency_short_name': 'USDT', 'balance': '1000.0'}]

    async def get_historical_data(self, pair_symbol, timeframe, limit=200, force_fresh=False):
        """
        Generates realistic sample OHLCV data for testing purposes.
        """
        end_time = datetime.now()
        # Create a date range ending now
        dates = pd.to_datetime(pd.date_range(end=end_time, periods=limit, freq='h'))

        # Generate some plausible price data
        price = 100 + np.random.randn(limit).cumsum()

        df = pd.DataFrame({
            'open_time': dates,
            'open': price,
            'high': price + np.random.uniform(0, 5, size=limit),
            'low': price - np.random.uniform(0, 5, size=limit),
            'close': price + np.random.uniform(-2, 2, size=limit),
            'volume': np.random.uniform(1000, 5000, size=limit)
        })

        # Ensure high is the highest and low is the lowest
        df['high'] = df[['high', 'open', 'close']].max(axis=1)
        df['low'] = df[['low', 'open', 'close']].min(axis=1)

        return df

    def validate_data_freshness(self, data, pair_symbol, max_age_seconds=None):
        return {
            'is_fresh': True,
            'data_age_seconds': 0,
            'last_timestamp': datetime.now(),
            'circuit_breaker_active': False,
            'message': 'Data freshness validation disabled (using sample data)'
        }
