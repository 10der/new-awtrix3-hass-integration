"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import LIGHT_LUX, PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utcnow

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
    async_add_entities(
        [
            DeviceTemperatureSensor(hass=hass, coordinator=coordinator),
            DeviceHumiditySensor(hass=hass, coordinator=coordinator),
            BatteryChargeSensor(hass=hass, coordinator=coordinator),
            LuxSensor(hass=hass, coordinator=coordinator),
            # CommmonSensor(hass=hass, coordinator=coordinator,
            #                 key="app", name="Current app"),
            CommmonSensor(hass=hass, coordinator=coordinator,
                            entity_category=EntityCategory.DIAGNOSTIC,
                            key="version", prefix="v", name="Version"),
            CommmonSensor(hass=hass, coordinator=coordinator, key="wifi_signal",
                            state_class=SensorStateClass.MEASUREMENT,
                            name="Wifi Signal",
                            entity_category=EntityCategory.DIAGNOSTIC,
                            icon="mdi:wifi"),
            CommmonSensor(hass=hass, coordinator=coordinator, key="ip_address",
                            name="IP Address",
                            #state_class=SensorStateClass.MEASUREMENT,
                            entity_category=EntityCategory.DIAGNOSTIC,
                            icon="mdi:wan"),
            CommmonSensor(hass=hass, coordinator=coordinator, key="uptime", name="Uptime",
                            device_class=SensorDeviceClass.TIMESTAMP,
                            entity_category=EntityCategory.DIAGNOSTIC,
                            value_fn=lambda data: utcnow() - timedelta(seconds=data)),
            CommmonSensor(hass=hass, coordinator=coordinator, key="ram", name="Free ram",
                            measurement="B",
                            entity_category=EntityCategory.DIAGNOSTIC,
                            state_class=SensorStateClass.MEASUREMENT,
                            icon="mdi:memory")
        ]
    )

PARALLEL_UPDATES = 1

class CommmonSensor(AwtrixEntity, SensorEntity):
    """Representation of a common Sensor."""

    def __init__(self,
                 hass: HomeAssistant,
                 coordinator,
                 key,
                 name=None,
                 device_class=None,
                 state_class=None,
                 icon=None,
                 measurement=None,
                 entity_category=None,
                 value_fn=None,
                 prefix="",
                 suffix="") -> None:
        """Initialize the entity."""
        self._attr_name = name or key
        self.hass = hass
        self.key = key
        self.prefix = prefix
        self.suffix = suffix
        self.value_fn = value_fn

        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = measurement
        self._attr_entity_category = entity_category

        super().__init__(coordinator, key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        value = self.coordinator.data.get(self.key)
        if value is not None:
            if self.value_fn is not None:
                value = self.value_fn(value)
            if self.prefix or self.suffix:
                self._attr_native_value = self.prefix + str(value) + self.suffix
            else:
                self._attr_native_value = value

        self.async_write_ha_state()


class DeviceTemperatureSensor(AwtrixEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator, "temperature")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self._attr_native_value = self.coordinator.data.get("temp", 0)
        self.async_write_ha_state()

class DeviceHumiditySensor(AwtrixEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Humidity"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator, "humidity")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self._attr_native_value = self.coordinator.data.get("hum", 0)
        self.async_write_ha_state()

class LuxSensor(AwtrixEntity, SensorEntity):
    """Representation of an Awtric Lux sensor."""

    _attr_name = "Illuminance"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_device_class = SensorDeviceClass.ILLUMINANCE

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator, "lux")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self._attr_native_value = self.coordinator.data.get("lux", 0)
        self.async_write_ha_state()


class BatteryChargeSensor(AwtrixEntity, SensorEntity):
    """Representation of an Awtrix charge sensor."""

    _attr_name = "Battery"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator, "battery")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""

        self._attr_native_value = self.coordinator.data.get("bat", 0)
        self.async_write_ha_state()
