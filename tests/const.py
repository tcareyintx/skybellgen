"""Constants for SkybellGen tests."""

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_EMAIL,
    Platform,
)

USERNAME = "test_email"
PASSWORD = "test_password"
USER_ID = "1234567890abcdef12345678"
DEVICE_ID = "012345670123456789abcdef"

MOCK_CONFIG = {CONF_EMAIL: USERNAME, CONF_PASSWORD: PASSWORD}

MOCK_PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]
