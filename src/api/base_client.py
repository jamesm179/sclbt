from abc import ABC, abstractmethod
import logging
import aiohttp

class BaseApiClient(ABC):
    """
    Abstract base class for API clients using aiohttp.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        # Do NOT create the session here. It must be created inside an async function.

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None) -> list:
        """
        Fetches OHLCV data from the exchange and normalizes it.
        """
        pass

    async def _request(self, endpoint: str, params: dict = None):
        """
        Makes an asynchronous HTTP GET request to the specified endpoint.
        The session is created and closed within the function to ensure thread safety.
        """
        url = self.base_url + endpoint
        try:
            # Create the session inside the async function
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"API request failed for {url}: {e}")
            return None

    # The close method is no longer needed as the session is managed by the 'with' statement.
    # async def close(self):
    #     pass
