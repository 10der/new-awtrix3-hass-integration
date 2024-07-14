"""Support for Awtrix notifications."""

import base64
from io import BytesIO
import logging

from PIL import Image
import requests

from homeassistant.components.notify import BaseNotificationService
from homeassistant.components.notify.const import ATTR_DATA
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

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

    def __init__(self, hass, uid):
        """Init the notification service for Awtrix."""

        self.hass = hass
        self.api = self.create_api(uid)

    def create_api(self, name):
        """Create API on the fly."""
        for coordinator in self.hass.data[DOMAIN][COORDINATORS]:
            if coordinator.data.uid == name:
                return coordinator.client

        raise HomeAssistantError("Could not send Awtrix action")

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

def getIcon(url):
    """Get icon by url."""
    try:
        timeout=5
        response = requests.get(url, timeout=timeout)
        if response and response.status_code == 200:
            pil_im = Image.open(BytesIO(response.content))
            pil_im = pil_im.convert('RGB')
            b = BytesIO()
            pil_im.save(b, 'jpeg')
            im_bytes = b.getvalue()
            return base64.b64encode(im_bytes).decode()
    except Exception as err:
        _LOGGER.exception(err)
