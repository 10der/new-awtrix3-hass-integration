"""awtrix_api.py: Awtrix API for Awtrix integration."""
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class AwtrixAPI:
    """Awtrix device API."""

    def __init__(self, hass: HomeAssistant, host, port, username, password)-> None:
        """Init Awtrix."""

        self.hass = hass
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    async def device_set_item_value(self, key, value):
        """Set device item value info."""

        try:
            auth = aiohttp.BasicAuth(self.username, self.password)
            url = "http://" + self.host + "/api/" + key
            response = await async_get_clientsession(self.hass).post(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                auth=auth,
                json=value
            )
            if response.status in (401, 403):
                _LOGGER.warning("Error %s: authentication failed", self.host)
                raise ApiAuthenticationFailed

            if response.status != 200:
                return None

            return True  # noqa: TRY300
        except TimeoutError:
            _LOGGER.warning("Error fetching %s: timeout", self.host)

        raise ApiCannotConnect

    async def get_data(self) -> dict:
        """Get all actual data from device."""
        # raise ApiCannotConnect
        stats = await self.__device_info()
        if stats is None:
            stats = {}

        config = await self.__device_config()
        if config is None:
            config = {}

        return  dict(stats, **config)


    async def get_config(self) -> dict | None:
         """Get config."""
         return await self.__device_config()

    async def get_device(self) -> dict | None:
         """Get device."""
         return await self.__device_info()

    async def __device_info(self):
        """Get device info."""

        try:
            auth = aiohttp.BasicAuth(self.username, self.password)
            response = await async_get_clientsession(self.hass).get(
                "http://" + self.host + "/api/" + "stats",
                timeout=aiohttp.ClientTimeout(total=10),
                auth=auth
            )
            if response.status in (401, 403):
                _LOGGER.warning("Error %s: authentication failed", self.host)
                raise ApiAuthenticationFailed

            if response.status != 200:
                return None

            return await response.json()
        except TimeoutError:
            _LOGGER.warning("Error fetching %s: timeout", self.host)

        # raise CannotConnect()
        return None

    async def __device_config(self):
        """Get device config."""

        try:
            auth = aiohttp.BasicAuth(self.username, self.password)
            response = await async_get_clientsession(self.hass).get(
                "http://" + self.host + "/api/" + "settings",
                timeout=aiohttp.ClientTimeout(total=10),
                auth=auth
            )
            if response.status in (401, 403):
                _LOGGER.warning("Error %s: authentication failed", self.host)
                raise ApiAuthenticationFailed

            if response.status != 200:
                return None

            return await response.json()
        except TimeoutError:
            _LOGGER.warning("Error fetching %s: timeout", self.host)

        return None

class ApiCannotConnect(Exception):
    """Error to indicate we cannot connect."""

class ApiAuthenticationFailed(Exception):
    """Exception to indicate authentication failure."""
