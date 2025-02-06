import logging
import aiohttp
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

class BoschAPI:
    """API handler for Bosch BPT-S4 Inverter."""

    def __init__(self, hass, base_url):
        """Initialize the API."""
        self._hass = hass
        self._base_url = base_url
        self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None

    async def fetch_data(self, endpoint):
        """Fetch data asynchronously from the Bosch inverter."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"{self._base_url}{endpoint}"
        _LOGGER.debug(f"Fetching data from Bosch API: {url}")

        try:
            async with self._session.get(url, timeout=10) as response:
                if response.status == 200:
                    # Read response as text first
                    text_response = await response.text()
                    _LOGGER.debug(f"Raw text response: {text_response}")
                    
                    # Manually parse text as JSON
                    try:
                        data = json.loads(text_response)
                        _LOGGER.debug(f"Successfully parsed JSON: {data}")
                        return data
                    except json.JSONDecodeError as e:
                        _LOGGER.error(f"Failed to parse response as JSON: {e}")
                        return None
                else:
                    _LOGGER.error(f"Bosch API request failed with status: {response.status}")
                    return None
        except asyncio.TimeoutError:
            _LOGGER.error(f"Bosch API request timed out for endpoint: {endpoint}")
            return None
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Bosch API client error for endpoint {endpoint}: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error in Bosch API request: {e}")
            return None

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None