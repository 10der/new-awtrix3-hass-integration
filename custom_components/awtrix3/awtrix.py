"""Core components of AWTRIX Light."""

import logging

from homeassistant.core import HomeAssistant

from .common import async_get_coordinator_by_device_id, getIcon
from .const import CONF_DEVICE_ID

_LOGGER = logging.getLogger(__name__)


class AwtrixService:
    """Allows to send updated to applications."""

    def __init__(self,
                 hass: HomeAssistant
                 ) -> None:
        """Initialize the device."""

        self.hass = hass

    def api(self, data):
        """Create API on the fly."""
        result = []
        for device_id in data.get(CONF_DEVICE_ID):
            try:
                coordinator = async_get_coordinator_by_device_id(self.hass, device_id)
                result.append(coordinator)
            except Exception:  # noqa: BLE001
                _LOGGER.error("Failed to coordinator for %s", device_id)
        return result

    async def call(self, func, seq):
        """Call action API."""
        result = []
        for i in seq:
            uniq_id = i.config_entry.unique_id
            try:
                res =  await func(i.api)
                result.append({uniq_id: res})
            except Exception:  # noqa: BLE001
                _LOGGER.error("Failed to call %s: action", i)
                result.append({uniq_id: False})

        return {"result" : result}

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

    async def get_settings(self, data):
        """Call API get settings."""
        return await self.call(lambda x: x.get_config(), self.api(data))

    async def get_device(self, data):
        """Call API get device."""
        return await self.call(lambda x: x.get_device(), self.api(data))

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
