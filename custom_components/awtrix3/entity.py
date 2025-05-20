"""Entity object for shared properties of Awtrix entities."""

from propcache.api import cached_property

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AwtrixCoordinator

ENTITY_ID_FORMAT = DOMAIN + ".{}"

class AwtrixEntity(CoordinatorEntity[AwtrixCoordinator]):
    """Generic Awtrix entity (base class)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AwtrixCoordinator, key: str) -> None:
        """Initialize the AWTRIX entity."""
        super().__init__(coordinator=coordinator)
        uid = self.coordinator.data["uid"]
        self._attr_unique_id = generate_entity_id(
             ENTITY_ID_FORMAT, uid + "_" + key, hass=self.hass)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, uid)},
            name=uid,
            model="AWTRIX 3",
            sw_version=self.coordinator.data.get("version"),
            manufacturer="Blueforcer",
            configuration_url=f"http://{self.coordinator.data.get("ip_address")}",
            suggested_area="Work Room"
         )

    @cached_property
    def available(self) -> bool: # type: ignore
        """Entity gets data from ezviz API so always available."""
        return True
