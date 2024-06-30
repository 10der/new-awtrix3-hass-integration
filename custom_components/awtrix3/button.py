"""Demo platform that offers a fake button entity."""
from __future__ import annotations

from config.custom_components.awtrix.coordinator import AwtrixCoordinator
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AwtrixEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the demo button platform."""

    coordinator: AwtrixCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            AwtrixButton(
                hass=hass,
                coordinator=coordinator,
                key="next_app",
                name="Next app",
                icon="mdi:swap-horizontal"),
            AwtrixButton(
                hass=hass,
                coordinator=coordinator,
                key="previous_app",
                name="Previous app",
                icon="mdi:swap-horizontal"),
            AwtrixButton(
                hass=hass,
                coordinator=coordinator,
                key="dismiss_notificationn",
                name="Dismiss notification",
                icon="mdi:swap-horizontal"),
            AwtrixButton(
                hass=hass,
                coordinator=coordinator,
                key="start_update",
                name="Start Update",
                icon="mdi:swap-horizontal"),
        ]
    )

class AwtrixButton(ButtonEntity, AwtrixEntity):
    """Representation of awtrix button entity."""

    def __init__(
        self,
        hass,
        coordinator,
        key: str,
        name: str = None,
        icon: str = None
    ) -> None:
        """Initialize the Awtrix button entity."""
        self.hass = hass
        self.key = key
        self._attr_name = name or key
        self._state = False
        self._available = True
        self._attr_icon = icon

        super().__init__(coordinator, key)

    async def async_press(self) -> None:
        """Send out a persistent notification."""
        if self.key == "next_app":
            await self.coordinator.set_value("nextapp", {})
        if self.key == "previous_app":
            await self.coordinator.set_value("previousapp", {})
        if self.key == "dismiss_notificationn":
            await self.coordinator.set_value("notify/dismiss", {})
        if self.key == "start_update":
            await self.coordinator.set_value("doupdate", {})
