from abc import ABC, abstractmethod
import logging
import aiohttp

class BaseApiClient(ABC):
    """
    Abstract base class for API clients using aiohttp.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None) -> list:
        """
        Fetches OHLCV data from the exchange and normalizes it.
        """
        pass

    async def _request(self, endpoint: str, params: dict = None):
        """
        Makes an asynchronous HTTP GET request to the specified endpoint.
        """
        url = self.base_url + endpoint
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"API request failed for {url}: {e}")
            return None

    async def close(self):
        """Closes the aiohttp session."""
        await self.session.close()
