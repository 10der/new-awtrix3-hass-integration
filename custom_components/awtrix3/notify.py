"""Support for Awtrix notifications."""

import logging

from homeassistant.components.notify import ATTR_DATA, BaseNotificationService
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .common import getIcon
from .const import COORDINATORS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> BaseNotificationService:
    """Get the AWTRIX notification service."""

    if discovery_info is None:
        return None

    return AwtrixNotificationService(hass=hass,
                                     uid=discovery_info[CONF_NAME])


########################################################################################################

class AwtrixNotificationService(BaseNotificationService):
    """Implement the notification service for Awtrix."""

    def __init__(self, hass: HomeAssistant, uid) -> None:
        """Init the notification service for Awtrix."""

        self.hass = hass
        self.api = self.create_api(uid)

    def create_api(self, name):
        """Create API on the fly."""
        for coordinator in self.hass.data[DOMAIN][COORDINATORS]:
            if coordinator.device_name == name:
                return coordinator.client

        raise HomeAssistantError("Could not initialize Awtrix notification")

    async def async_send_message(self, message='', **kwargs):
        """Send a message to some Awtrix device."""

        data = kwargs.get(ATTR_DATA)
        return await self.notification(message, data)

    async def notification(self, message, data):
        """Handle the notification service for Awtrix."""

        data = data or {}
        msg = data.copy()
        msg["text"] = message

        if 'icon' in msg:
            if str(msg["icon"]).startswith(('http://', 'https://')):
                icon = await self.hass.async_add_executor_job(getIcon, str(msg["icon"]))
                if icon:
                    msg["icon"] = icon

        command = "notify/dismiss" if not message else "notify"
        return await self.api.device_set_item_value(command, msg)
