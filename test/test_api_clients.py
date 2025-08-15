import unittest
from unittest.mock import patch, MagicMock
import requests

from src.api_clients.binance_client import BinanceClient
from src.api_clients.bitget_client import BitgetClient
from src.api_clients.coindcx_client import CoinDCXClient

class TestApiClients(unittest.TestCase):

    # --- BinanceClient Tests ---
    @patch('src.api_clients.base_client.requests.get')
    def test_binance_client_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [1672531200000, '16000', '16100', '15900', '16050', '100.0']
        ]
        mock_get.return_value = mock_response

        client = BinanceClient()
        data = client.fetch_ohlcv('BTC/USDT', '1h', limit=1)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][1], 16000.0)
        mock_get.assert_called_once()
        self.assertIn('api.binance.com', mock_get.call_args[0][0])

    @patch('src.api_clients.base_client.requests.get')
    def test_binance_client_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")
        client = BinanceClient()
        data = client.fetch_ohlcv('BTC/USDT', '1h')
        self.assertEqual(data, [])

    # --- BitgetClient Tests ---
    @patch('src.api_clients.base_client.requests.get')
    def test_bitget_client_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            ['1672531200000', '16000', '16100', '15900', '16050', '100.0']
        ]
        mock_get.return_value = mock_response

        client = BitgetClient()
        data = client.fetch_ohlcv('BTC/USDT', '1h', limit=1)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][2], 16100.0)
        mock_get.assert_called_once()
        self.assertIn('api.bitget.com', mock_get.call_args[0][0])

    # --- CoinDCXClient Tests ---
    @patch('src.api_clients.base_client.requests.get')
    def test_coindcx_client_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {'time': 1672531200000, 'open': 16000, 'high': 16100, 'low': 15900, 'close': 16050, 'volume': 100.0}
        ]
        mock_get.return_value = mock_response

        client = CoinDCXClient()
        data = client.fetch_ohlcv('BTC/USDT', '1h', limit=1)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][4], 16050.0)
        mock_get.assert_called_once()
        self.assertIn('public.coindcx.com', mock_get.call_args[0][0])

    def test_coindcx_client_invalid_symbol(self):
        client = CoinDCXClient()
        data = client.fetch_ohlcv('BTC-USDT', '1h') # Invalid format
        self.assertEqual(data, [])

if __name__ == '__main__':
    unittest.main()
