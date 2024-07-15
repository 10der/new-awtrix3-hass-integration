"""__init__.py: AWTRIX integration."""
from __future__ import annotations

import asyncio
from functools import partial
import logging

import aiohttp
from aiohttp import web

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import device_registry as dr, discovery
from homeassistant.helpers.service import async_set_service_schema
from homeassistant.helpers.typing import ConfigType

from .awtrix import AwtrixService
from .const import (
    COORDINATORS,
    DOMAIN,
    PLATFORMS,
    SERVICE_TO_FIELDS,
    SERVICE_TO_SCHEMA,
    SERVICES,
)
from .coordinator import AwtrixCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Awtrix component."""

    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN].setdefault(COORDINATORS, [])

    webhook.async_register(
        hass, DOMAIN, "Awtrix", "awtrix", handle_webhook
    )

    # common serices
    #async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Awtrix3 from a config entry."""

    coordinator = AwtrixCoordinator(hass=hass, entry=entry)
    hass.data[DOMAIN][COORDINATORS].append(coordinator)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # notification
    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {
                CONF_NAME:  get_device_real_name(hass, entry),
            },
            hass.data[DOMAIN][entry.entry_id],
        )
    )

    # individual services
    init_services(hass=hass, entry=entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def handle_webhook(hass, webhook_id, request):
    """Handle incoming webhook with Awtrix requests."""
    try:
        async with asyncio.timeout(5):
            data = dict(await request.post())
    except (TimeoutError, aiohttp.web.HTTPException) as error:
        _LOGGER.error("Could not get information from POST <%s>", error)
        return

    if webhook_id == "awtrix":
        button = data["button"]
        state = data["state"]
        for coordinator in hass.data[DOMAIN][COORDINATORS]:
            if coordinator.data.uid == request.query_string:
                coordinator.action_press(button, state)

    return web.Response(text="OK")

def init_services(hass, entry):
    """"Init services."""
    async def service_handler(entry, service, call: ServiceCall) -> None:
        """Handle service call."""

        func = getattr(entry, service)
        if func:
            await func(call.data)

    def build_service_name(entry_name, service) -> str:
        """Build a service name for a node."""
        return f"{entry_name.replace('-', '_')}_{service}"

    def register_services(entry):
        """Register Services."""
        for service in SERVICES:
            service_name = build_service_name(entry.name, service)

            hass.services.async_register(
                DOMAIN,
                service_name,
                partial(service_handler, entry, service),
                schema=SERVICE_TO_SCHEMA[service]
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
                    "fields": SERVICE_TO_FIELDS[service],
                },
            )

    ha_device_name = get_device_real_name(hass, entry) #entry.title
    # services
    entity = AwtrixService(
        hass,
        ha_device_name,
    )
    register_services(entity)

def get_device_real_name(hass, entry):
    """Get real name of device."""
    device_registry = dr.async_get(hass)
    for device in device_registry.devices.values():
        if device.manufacturer == 'Blueforcer':
            for entry_id in device.config_entries:
                if entry_id == entry.entry_id:
                    return device.name_by_user or device.name


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Awtrix integration."""

    async def service_handler(entry, service, call: ServiceCall) -> None:
        """Handle service call."""

        func = getattr(entry, service)
        if func:
            await func(call.data)

    for service in SERVICES:
        service_name = service

        entry = AwtrixService(hass, None)
        hass.services.async_register(
            DOMAIN,
            service_name,
            partial(service_handler, entry, service),
            schema=SERVICE_TO_SCHEMA[service]
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
                "fields": SERVICE_TO_FIELDS[service],
            },
        )
