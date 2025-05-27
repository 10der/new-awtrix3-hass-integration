"""Global services file."""

from functools import partial

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers.service import async_set_service_schema

from .awtrix import AwtrixService
from .const import DOMAIN, SERVICE_TO_FIELDS, SERVICE_TO_SCHEMA, SERVICES


async def async_setup_services(hass: HomeAssistant) -> None:
    """Handle Integration Services."""

    async def service_handler(awtrixService, service, call: ServiceCall) -> None:
        """Handle service call."""

        func = getattr(awtrixService, service)
        if func:
            return await func(call.data)
        return None

    awtrixService = AwtrixService(hass)
    for service_name in SERVICES:
        hass.services.async_register(
            DOMAIN,
            service_name,
            partial(service_handler, awtrixService, service_name),
            schema=SERVICE_TO_SCHEMA[service_name],
            supports_response=SupportsResponse.OPTIONAL
        )

        # Register the service description
        async_set_service_schema(
            hass,
            DOMAIN,
            service_name,
            {
                "description": (
                    f"Calls the service {service_name} of the node AWTRIX"
                ),
                "fields": SERVICE_TO_FIELDS[service_name],
            },
        )
