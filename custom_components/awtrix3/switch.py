"""Platform for switch integration."""
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AwtrixCoordinator
from .entity import AwtrixEntity

ENTITY_ID_FORMAT = DOMAIN + ".{}"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    coordinator: AwtrixCoordinator = entry.runtime_data.coordinator
    async_add_entities([
        AwtrixSwitch(
            hass=hass,
            coordinator=coordinator,
            key="ATRANS",
            name="Transition",
            icon="mdi:swap-horizontal"),
        AwtrixSwitch(
            hass=hass,
            coordinator=coordinator,
            key="ABRI",
            name="Brightness mode",
            icon="mdi:brightness-auto")
    ])

PARALLEL_UPDATES = 1

class AwtrixSwitch(AwtrixEntity, SwitchEntity):
    """Representation of a Awtrix switch."""

    #_attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator,
        key: str,
        name: str | None = None,
        icon: str | None = None
    ) -> None:
        """Initialize the switch."""

        self.hass = hass
        self.key = key
        self._attr_name = name or key
        self._state = False
        self._available = True
        self._attr_icon = icon

        super().__init__(coordinator, key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.key == "ATRANS":
            await self.coordinator.set_value("settings", {"ATRANS": True})
        if self.key == "ABRI":
            await self.coordinator.set_value("settings", {"ABRI": True})

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self.key == "ATRANS":
            await self.coordinator.set_value("settings", {"ATRANS": False})
        if self.key == "ABRI":
            await self.coordinator.set_value("settings", {"ABRI": False})

        await self.coordinator.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self._attr_is_on = bool(self.coordinator.data.get(self.key))
        self.async_write_ha_state()
