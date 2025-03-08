"""Platform for light integration."""

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_FLASH,
    ATTR_RGB_COLOR,
    FLASH_LONG,
    FLASH_SHORT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AwtrixCoordinator
from .entity import AwtrixEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AWTRIX light based on a config entry."""
    coordinator: AwtrixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="matrix",
            name="Matrix",
            mode={ColorMode.BRIGHTNESS},
            icon="mdi:clock-digital"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator1",
            name="Indicator 1",
            mode={ColorMode.RGB},
            icon="mdi:arrow-top-right-thick"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator2",
            name="Indicator 2",
            mode={ColorMode.RGB},
            icon="mdi:arrow-bottom-right-thick"
        ),
        AwtrixLight(
            hass=hass,
            coordinator=coordinator,
            key="indicator3",
            name="Indicator 3",
            mode={ColorMode.RGB},
            icon="mdi:arrow-bottom-right-thick"
        ),
    ]
    )


class AwtrixLight(LightEntity, AwtrixEntity):
    """Representation of a demo light."""

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
        self._available = True
        self._attr_icon = icon
        self._attr_supported_color_modes = mode
        self.mode = mode
        self._attr_supported_features = LightEntityFeature.FLASH

        super().__init__(coordinator, key)

    @property
    def available(self) -> bool:
        """Return availability."""
        # This demo light is always available, but well-behaving components
        # should implement this to inform Home Assistant accordingly.
        return self._available

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        if self.key == "bri":
            return self.coordinator.data.bri
        return None

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        if self.key == "matrix":
            return self.coordinator.data.matrix
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if self.key == "matrix":
            await self.coordinator.set_value("power", {"power": True})
            if ATTR_BRIGHTNESS in kwargs:
                self._brightness = kwargs[ATTR_BRIGHTNESS]
                await self.coordinator.set_value("settings", {"BRI": self._brightness})
        else:
            data = {"color": "#ffffff"}
            if ATTR_BRIGHTNESS in kwargs:
                self._brightness = kwargs[ATTR_BRIGHTNESS]

            if ATTR_RGB_COLOR in kwargs:
                data["color"] = kwargs[ATTR_RGB_COLOR]

            # Flash.
            if ATTR_FLASH in kwargs and self.supported_features & LightEntityFeature.FLASH:
                if kwargs[ATTR_FLASH] == FLASH_LONG:
                    data["blink"] = 1000
                elif kwargs[ATTR_FLASH] == FLASH_SHORT:
                    data["blink"] = 500
                else:
                    pass

            await self.coordinator.set_value(self.key, data)

            self.color_mode = ColorMode.RGBW
            self.rgbw_color = data["color"]

        self._state = True

        # await self.coordinator.push_state_update()
        # self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if self.key == "matrix":
            await self.coordinator.set_value("power", {"power": False})
        else:
            await self.coordinator.set_value(self.key, {"color": "0"})

        self._state = False

        # await self.coordinator.push_state_update()
        # self.async_write_ha_state()

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        value = getattr(self.coordinator.data, self.key, None)
        return "on" if value else "off"

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Flag supported color modes."""
        return {self.color_mode}

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        return list(self.mode)[0]
