"""Core components of AWTRIX Light."""

import base64
from io import BytesIO
import logging

from PIL import Image
import requests

#from homeassistant.exceptions import HomeAssistantError
from .const import CONF_DEVICE_ID, COORDINATORS, DOMAIN

"""Support for AWTRIX service."""

_LOGGER = logging.getLogger(__name__)


def getIcon(url):
    """Get icon by url."""
    try:
        timeout = 5
        response = requests.get(url, timeout=timeout)
        if response and response.status_code == 200:
            pil_im = Image.open(BytesIO(response.content))
            pil_im = pil_im.convert('RGB')
            b = BytesIO()
            pil_im.save(b, 'jpeg')
            im_bytes = b.getvalue()
            return base64.b64encode(im_bytes).decode()
    except Exception:
        pass


class AwtrixService:
    """Allows to send updated to applications."""

    def __init__(self,
                 hass,
                 name
                 ) -> None:
        """Initialize the device."""

        self.hass = hass
        self.name = name
        self._api = None
        if name is not None:
            self._api = self.create_api(name)

    def api(self, data):
        """Create API on the fly."""
        result = []
        for device_id in data.get(CONF_DEVICE_ID):
            api = self.create_api(device_id)
            if api:
                result.append(api)
        return result

    def create_api(self, name):
        """Create API on the fly."""
        if self._api:
            return self._api

        for coordinator in self.hass.data[DOMAIN][COORDINATORS]:
            if coordinator.data.uid == name:
                return coordinator.client

        _LOGGER.error("Failed to call %s: device not found", name)
        return None

        #raise HomeAssistantError("Could not find Awtrix device %s", name)

    async def call(self, func, seq):
        """Call action API."""
        for i in seq:
            try:
                await func(i)
            except Exception:
                _LOGGER.error("Failed to call %s: action", i)

        return True

    async def push_app_data(self, data):
        """Update the application data."""

        app_id = data["name"]
        url = "custom?name=" + app_id

        action_data = data.get("data", {}) or {}
        payload = action_data.copy()
        payload.pop(CONF_DEVICE_ID, None)

        if 'icon' in payload:
            if str(payload["icon"]).startswith(('http://', 'https://')):
                payload["icon"] = await self.hass.async_add_executor_job(getIcon, str(payload["icon"]))

        return await self.call(lambda x: x.device_set_item_value(url, payload), self.api(data))

    async def switch_app(self, data):
        """Call API switch app."""

        url = "switch"
        app_id = data["name"]

        payload = {"name": app_id}
        return await self.call(lambda x: x.device_set_item_value(url, payload), self.api(data))

    async def settings(self, data):
        """Call API settings."""

        url = "settings"

        data = data or {}
        payload = data.copy()
        payload.pop(CONF_DEVICE_ID, None)

        return await self.call(lambda x: x.device_set_item_value(url, payload), self.api(data))

    async def rtttl(self, data):
        """Play rtttl."""

        url = "rtttl"
        payload = data["rtttl"]
        return await self.call(lambda x: x.device_set_item_value(url, payload), self.api(data))

    async def sound(self, data):
        """Play rtttl sound."""

        url = "sound"
        sound_id = data["sound"]
        payload = {"sound": sound_id}
        return await self.call(lambda x: x.device_set_item_value(url, payload), self.api(data))
