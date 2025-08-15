from abc import ABC, abstractmethod
import requests

class BaseApiClient(ABC):
    """
    Abstract base class for API clients.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None) -> list:
        """
        Fetches OHLCV data from the exchange and normalizes it.

        :param symbol: The trading symbol (e.g., 'BTCUSDT').
        :param timeframe: The timeframe for the candles (e.g., '1h').
        :param since: The start time in milliseconds.
        :param limit: The number of candles to fetch.
        :return: A list of lists, where each inner list is [timestamp, open, high, low, close, volume].
                 Returns an empty list if the request fails or no data is available.
        """
        pass

    def _request(self, endpoint: str, params: dict = None):
        """
        Makes an HTTP GET request to the specified endpoint.
        """
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # In a real app, you'd use a logger here.
            print(f"API request failed for {url}: {e}")
            return None
