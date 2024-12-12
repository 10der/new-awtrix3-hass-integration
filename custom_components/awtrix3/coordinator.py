"""AWTRIX coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .awtrix_api import AwtrixAPI
from .const import DOMAIN
from .models import AwtrixData

_LOGGER = logging.getLogger(__name__)

class AwtrixCoordinator(DataUpdateCoordinator[AwtrixData]):
    """Data update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=1),
        )
        self.entry = entry
        self.client = AwtrixAPI(
            self.hass,
            self.config_entry.data[CONF_HOST],
            80,
            self.config_entry.data[CONF_USERNAME],
            self.config_entry.data[CONF_PASSWORD],
        )
        #self.device_name = self.get_device_real_name()
        self.on_button_click = {}

    @property
    def device_name(self):
        """Return the real device name."""
        return self.get_device_real_name()

    async def set_value(self, key, value):
        """Set device value."""
        await self.client.device_set_item_value(key=key, value=value)

    async def _async_update_data(self) -> AwtrixData:
        """Fetch the latest data from the source."""
        return await self.client.get_data()

    def on_press(self, key: str, action):
        """Set action on hardware button click."""
        self.on_button_click[key] = action

    def action_press(self, button, state):
        """On hardware button click."""
        # left middle right

        for btn in list(self.on_button_click.keys()) :
            if f"button_{button}" == btn.replace("select", "middle"):
                self.on_button_click[btn](state)

    def get_device_real_name(self):
        """Get real name of device."""
        device_registry = dr.async_get(self.hass)
        for device in device_registry.devices.values():
            if device.manufacturer == 'Blueforcer':
                for entry_id in device.config_entries:
                    if entry_id == self.entry.entry_id:
                        return device.name_by_user or device.name
        return None



