class BaseExchangeAPI:
    def __init__(self, credentials, display_manager, db_manager, config):
        pass

    def get_wallet_data(self):
        return [{'currency_short_name': 'USDT', 'balance': '1000.0'}]

    async def get_historical_data(self, pair_symbol, timeframe, limit=100, force_fresh=False):
        import pandas as pd
        return pd.DataFrame()

    def validate_data_freshness(self, data, pair_symbol, max_age_seconds=None):
        from datetime import datetime
        return {
            'is_fresh': True,
            'data_age_seconds': 0,
            'last_timestamp': datetime.now(),
            'circuit_breaker_active': False,
            'message': 'Data freshness validation disabled'
        }
