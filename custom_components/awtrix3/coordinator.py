"""AWTRIX coordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
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
        self._client = AwtrixAPI(
            self.hass,
            self.config_entry.data[CONF_HOST],
            80,
            self.config_entry.data[CONF_USERNAME],
            self.config_entry.data[CONF_PASSWORD],
        )
        self.on_button_click = {}

    async def set_value(self, key, value):
        """Set device value."""
        await self._client.device_set_item_value(key=key, value=value)

    async def _async_update_data(self) -> AwtrixData:
        """Fetch the latest data from the source."""
        return await self._client.get_data()

    def on_press(self, key: str, action):
        """Set action on hardware button click."""
        self.on_button_click[key] = action

    def action_press(self, button, state):
        """On hardware button click."""
        # left middle right

        for btn in list(self.on_button_click.keys()) :
            if f"button_{button}" == btn.replace("select", "middle"):
                self.on_button_click[btn](state)


