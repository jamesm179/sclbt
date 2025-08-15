import unittest
import pandas as pd
from src.data.database import DatabaseManager
from src.data.models import OHLCV

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database for testing."""
        self.db_url = 'sqlite:///:memory:'
        self.db_manager = DatabaseManager(self.db_url)
        self.db_manager.create_tables()

    def test_store_and_fetch_ohlcv(self):
        """Test storing and fetching OHLCV data."""
        ohlcv_records = [
            OHLCV(exchange='test_ex', symbol='BTC/USDT', timestamp=1672531200000, open=16000, high=16100, low=15900, close=16050, volume=100),
            OHLCV(exchange='test_ex', symbol='BTC/USDT', timestamp=1672534800000, open=16050, high=16200, low=16000, close=16150, volume=120),
        ]
        self.db_manager.store_ohlcv(ohlcv_records)

        df = self.db_manager.fetch_ohlcv_as_dataframe(exchange='test_ex', symbol='BTC/USDT')

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['close'], 16050)
        self.assertEqual(df.index[0], pd.to_datetime('2023-01-01 00:00:00'))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df.index))


    def test_fetch_with_limit(self):
        """Test fetching with a limit."""
        ohlcv_records = [
            OHLCV(exchange='test_ex', symbol='BTC/USDT', timestamp=1672531200000 + i * 3600000, open=1, high=1, low=1, close=1, volume=1)
            for i in range(10)
        ]
        self.db_manager.store_ohlcv(ohlcv_records)

        df = self.db_manager.fetch_ohlcv_as_dataframe(exchange='test_ex', symbol='BTC/USDT', limit=5)
        self.assertEqual(len(df), 5)

    def test_deduplication_on_storage(self):
        """Test that storing the same data twice does not create duplicates."""
        ohlcv_records = [
            OHLCV(exchange='test_ex', symbol='BTC/USDT', timestamp=1672531200000, open=16000, high=16100, low=15900, close=16050, volume=100),
        ]
        # Store once
        self.db_manager.store_ohlcv(ohlcv_records)
        df_first = self.db_manager.fetch_ohlcv_as_dataframe(exchange='test_ex', symbol='BTC/USDT')
        self.assertEqual(len(df_first), 1)

        # Store again
        self.db_manager.store_ohlcv(ohlcv_records)
        df_second = self.db_manager.fetch_ohlcv_as_dataframe(exchange='test_ex', symbol='BTC/USDT')
        self.assertEqual(len(df_second), 1)


if __name__ == '__main__':
    unittest.main()
