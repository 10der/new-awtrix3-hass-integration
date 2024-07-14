"""Constants for Awtrix time."""

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

"""Constants used for Awtrix."""

DOMAIN = "awtrix"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.LIGHT,
                             Platform.SWITCH, Platform.BUTTON, Platform.BINARY_SENSOR]

COORDINATORS = "coordinators"

# Services
SERVICE_PUSH_APP_DATA = "push_app_data"
SERVICE_SETTINGS = "settings"
SERVICE_SWITCH_APP = "switch_app"
SERVICE_SOUND = "sound"
SERVICE_RTTTL = "rtttl"

SERVICES = [
    SERVICE_PUSH_APP_DATA,
    SERVICE_SETTINGS,
    SERVICE_SOUND,
    SERVICE_RTTTL,
    SERVICE_SWITCH_APP,
]

SERVICE_DATA = "data"
SERVICE_APP_NAME = "name"
CONF_DEVICE_ID = "device"

# Schemas
SERVICE_BASE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_DEVICE_ID): cv.string,
    },
)

SERVICE_PUSH_APP_DATA_SCHEMA = SERVICE_BASE_SCHEMA.extend(
    {
        vol.Required(SERVICE_APP_NAME): str,
        vol.Required(SERVICE_DATA, default={}): dict
    },
    # cv.has_at_least_one_key(SERVICE_APP_NAME),
)

SERVICE_SWITCH_APP_SCHEMA = SERVICE_BASE_SCHEMA.extend(
    {
        vol.Required(SERVICE_APP_NAME): str,
    },
    # cv.has_at_least_one_key(SERVICE_APP_NAME),
)

SERVICE_RTTTL_SCHEMA = SERVICE_BASE_SCHEMA.extend(
    {
        vol.Required(SERVICE_RTTTL): str,
    },
    # cv.has_at_least_one_key(SERVICE_RTTTL),
)

SERVICE_SOUND_SCHEMA = SERVICE_BASE_SCHEMA.extend(
    {
        vol.Required(SERVICE_SOUND): str,
    },
    # cv.has_at_least_one_key(SERVICE_SOUND),
)

SERVICE_SETTINGS_SCHEMA = SERVICE_BASE_SCHEMA.extend(
    {
    }
)

# Fields
SERVICE_RTTTL_FIELDS = {
    "rtttl": {
        "description": "The rtttl text",
        "required": True,
        "example": "two_short:d=4,o=5,b=100:16e6,16e6",
        "selector": {
            "text": ""
        }
    }
}

SERVICE_SOUND_FIELDS = {
    "sound": {
        "description": "The sound name",
        "required": True,
        "example": "beep",
        "selector": {
            "text": ""
        }
    }
}

SERVICE_PUSH_APP_DATA_FIELDS = {
    "name": {
        "description": "The application name",
        "required": True,
        "example": "Test",
        "selector": {
            "text": ""
        }
    },
    "data": {
        "example": 'text : "Hello, AWTRIX Light!"\nrainbow: true\nicon: "87"\nduration: 5\npushIcon: 2\nlifetime: 900\nrepeat: 1',
        "selector": {
            "object": ""
        }
    }
}

SERVICE_SWITCH_APP_FIELDS = {
    "name": {
        "description": "The application name",
        "required": True,
        "example": "Test",
        "selector": {
            "text": ""
        }
    }
}

SERVICE_SETTINGS_FIELDS = {
}

# services fields and schemas
SERVICE_TO_FIELDS = {
    SERVICE_PUSH_APP_DATA: SERVICE_PUSH_APP_DATA_FIELDS,
    SERVICE_SETTINGS: SERVICE_SETTINGS_FIELDS,
    SERVICE_SWITCH_APP: SERVICE_SWITCH_APP_FIELDS,
    SERVICE_RTTTL: SERVICE_RTTTL_FIELDS,
    SERVICE_SOUND: SERVICE_SOUND_FIELDS
}

SERVICE_TO_SCHEMA = {
    SERVICE_PUSH_APP_DATA: SERVICE_PUSH_APP_DATA_SCHEMA,
    SERVICE_SETTINGS: SERVICE_SETTINGS_SCHEMA,
    SERVICE_SWITCH_APP: SERVICE_SWITCH_APP_SCHEMA,
    SERVICE_RTTTL: SERVICE_RTTTL_SCHEMA,
    SERVICE_SOUND: SERVICE_SOUND_SCHEMA
}
