"""Platform for light integration."""

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_FLASH,
    ATTR_RGB_COLOR,
    FLASH_LONG,
    FLASH_SHORT,
    LightEntity,
)
from homeassistant.components.light.const import ColorMode, LightEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AwtrixCoordinator
from .entity import AwtrixEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AWTRIX light based on a config entry."""
    coordinator: AwtrixCoordinator = entry.runtime_data.coordinator

    async_add_entities([
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="matrix",
            name="Matrix",
            mode=ColorMode.BRIGHTNESS,
            icon="mdi:clock-digital"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator1",
            name="Indicator 1",
            mode=ColorMode.RGB,
            icon="mdi:arrow-top-right-thick"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator2",
            name="Indicator 2",
            mode=ColorMode.RGB,
            icon="mdi:arrow-bottom-right-thick"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator3",
            name="Indicator 3",
            mode=ColorMode.RGB,
            icon="mdi:arrow-bottom-right-thick"
        ),
    ]
    )

PARALLEL_UPDATES = 1

class AwtrixLight(AwtrixEntity, LightEntity):
    """Representation of a Awtrix light."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator,
        key: str,
        name: str | None = None,
        mode=None,
        icon: str | None = None
    ) -> None:
        """Initialize the light."""

        self.hass = hass
        self.key = key
        self._attr_name = name or key
        self._brightness = 0
        self._state = False
        self._attr_icon = icon

        if mode is not None:
            self._attr_supported_color_modes = {mode}
            self._attr_color_mode = mode
        else:
            self._attr_supported_color_modes = set()
            self._attr_color_mode = None
        self._attr_supported_features = LightEntityFeature.FLASH

        super().__init__(coordinator, key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        self._state = True

        data = {}

        if self.key == "matrix":
            await self.coordinator.set_value("power", {"power": True})
        else:
            self.rgb_color = (255, 255, 255) if self.rgb_color is None else self.rgb_color
            data["color"] = f"#{self.rgb_color[0]:02x}{self.rgb_color[1]:02x}{self.rgb_color[2]:02x}"
            self._brightness = 255 if data["color"] == "#ffffff" else self._brightness

        if ATTR_RGB_COLOR in kwargs:
            data["color"] = kwargs[ATTR_RGB_COLOR]
            self.rgb_color = kwargs[ATTR_RGB_COLOR]

        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

            if self.key == "matrix":
                await self.coordinator.set_value("power", {"power": True})
                if ATTR_BRIGHTNESS in kwargs:
                    self._brightness = kwargs[ATTR_BRIGHTNESS]
                    await self.coordinator.set_value("settings", {"ABRI": False, "BRI": self._brightness})
            else:
                rgb_color = self.adjust_brightness(self.rgb_color, self._brightness)
                data["color"] = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"

        # Flash.
        if ATTR_FLASH in kwargs and self.supported_features & LightEntityFeature.FLASH:
            if kwargs[ATTR_FLASH] == FLASH_LONG:
                data["blink"] = 1000
            elif kwargs[ATTR_FLASH] == FLASH_SHORT:
                data["blink"] = 500
            else:
                pass

        await self.coordinator.set_value(self.key, data)

        await self.coordinator.async_refresh()


    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        self._state = False

        if self.key == "matrix":
            await self.coordinator.set_value("power", {"power": False})
        else:
            await self.coordinator.set_value(self.key, {"color": "0"})

        await self.coordinator.async_refresh()


    def adjust_brightness(self, color, brightness_percent):
        """Adjust the brightness of an RGB color."""
        # Ensure brightness_percent is between 1 and 255
        brightness_percent = max(1, min(255, brightness_percent))

        # Scale RGB values based on the brightness percentage
        scale_factor = brightness_percent / 255
        r = int(color[0] * scale_factor)
        g = int(color[1] * scale_factor)
        b = int(color[2] * scale_factor)

        # Return the new color tuple
        return (r, g, b)

    def update(self) -> None:
        """State update callback."""
        if self.key == "matrix":
            self._attr_is_on = bool(self.coordinator.data.get("matrix"))
            self._attr_brightness = int(self.coordinator.data.get("BRI", 0))
        else:
            self._attr_is_on = bool(self.coordinator.data.get(self.key))
            # color = self.coordinator.data.get("color")
            # if color:
            #     r = int(color[1:3], 16)
            #     g = int(color[3:5], 16)
            #     b = int(color[5:7], 16)
            #     self._attr_rgb_color = (r, g, b)

        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self.update()
