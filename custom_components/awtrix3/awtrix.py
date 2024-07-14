"""Core components of AWTRIX Light."""

import base64
from io import BytesIO
import logging

from PIL import Image
import requests

from .awtrix_api import AwtrixAPI

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

    _attr_should_poll = False

    def __init__(self,
                 hass,
                 name,
                 host,
                 user,
                 password
                 ) -> None:
        """Initialize the device."""

        self.name = name
        self.api = AwtrixAPI(hass, host, 80, user, password)

    async def push_app_data(self, data):
        """Update the application data."""

        app_id = data["name"]
        url = "custom?name=" + app_id

        data = data.get("data", {}) or {}
        msg = data.copy()

        if 'icon' in msg:
            if str(msg["icon"]).startswith(('http://', 'https://')):
                msg["icon"] = await self.hass.async_add_executor_job(getIcon, str(msg["icon"]))

        return await self.api.device_set_item_value(url, msg)

    async def switch_app(self, data):
        """Call API switch app."""

        url = "switch"
        app_id = data["name"]

        payload = {"name": app_id}
        return await self.api.device_set_item_value(url, payload)

    async def settings(self, data):
        """Call API settings."""

        url = "settings"

        data = data or {}
        msg = data.copy()

        return await self.api.device_set_item_value(url, msg)

    async def rtttl(self, data):
        """Play rtttl."""

        url = "rtttl"
        payload = data["rtttl"]

        return await self.api.device_set_item_value(url, payload)

    async def sound(self, data):
        """Play rtttl sound."""

        url = "sound"
        sound_id = data["sound"]
        payload = {"sound": sound_id}
        return await self.api.device_set_item_value(url, payload)
