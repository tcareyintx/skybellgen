"""Constants for SkyBellGen tests."""

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform

from custom_components.skybellgen.const import CONF_USE_LOCAL_SERVER

USERNAME = "test_email"
PASSWORD = "test_password"
USER_ID = "1234567890abcdef12345678"
DEVICE_ID = "012345670123456789abcdef"
USE_LOCAL_SERVER = True

MOCK_CONFIG = {
    CONF_EMAIL: USERNAME,
    CONF_PASSWORD: PASSWORD,
    CONF_USE_LOCAL_SERVER: USE_LOCAL_SERVER,
}

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
