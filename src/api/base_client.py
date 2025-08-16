from abc import ABC, abstractmethod
import requests
import logging

class BaseApiClient(ABC):
    """
    Abstract base class for API clients.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None) -> list:
        """
        Fetches OHLCV data from the exchange and normalizes it.
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
            logging.error(f"API request failed for {url}: {e}")
            return None
