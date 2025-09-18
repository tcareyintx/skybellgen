"""Global fixtures for SkyBellGen integration."""

# pylint: disable=protected-access

import copy
import json
from os import path
from unittest.mock import patch

from aioskybellgen import SkybellDevice
from aioskybellgen.exceptions import (
    SkybellAccessControlException,
    SkybellAuthenticationException,
    SkybellException,
)
import aioskybellgen.helpers.const as CONST
from aioskybellgen.helpers.models import LiveStreamConnectionData
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.skybellgen.const import DOMAIN

from .const import MOCK_CONFIG, MOCK_PLATFORMS, USER_ID


def get_livestream(nows: bool = False) -> LiveStreamConnectionData:
    """Return two SkyBell devices."""
    filename = "data/start_livestream.json"
    if nows:
        filename = "data/start_livestream nows.json"
    data: LiveStreamConnectionData = {}
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, filename))
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_two_devices() -> list[SkybellDevice]:
    """Return two SkyBell devices."""
    devices: list[SkybellDevice] = []
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "data/device.json"))
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    device1 = SkybellDevice(device_json=data, skybell=None)
    devices.append(device1)

    device2_data = copy.deepcopy(data)
    device2 = SkybellDevice(device_json=device2_data, skybell=None)
    device2._device_id = "second_device"
    device2._device_json[CONST.DEVICE_ID] = "second_device"
    device2._device_json[CONST.NAME] = "second_device name"
    device2._device_json["serial"] = "second_device_sernum"
    device_settings = device2._device_json.get(CONST.DEVICE_SETTINGS)
    device_settings[CONST.SERIAL_NUM] = "second_device_sernum"
    device_settings[CONST.MAC_ADDRESS] = "FF:EE:DD:CC:BB:AA"
    devices.append(device2)
    return devices


def get_one_device() -> list[SkybellDevice]:
    """Return one SkyBell device."""
    devices: list[SkybellDevice] = []
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "data/device.json"))
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    device1 = SkybellDevice(device_json=data, skybell=None)
    filepath = path.abspath(path.join(basepath, "data/activity.json"))
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    activity = data
    device1._activities.append(activity)
    devices.append(device1)
    return devices


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations by default."""
    yield


# This fixture, when used, will result in calls to save cache to return None.
# This is useful to prevent the cache from being saved during tests.
@pytest.fixture(name="bypass_save_cache", autouse=True)
def bypass_save_cache():
    """Skip calls to save cache."""
    with patch("aioskybellgen.utils.async_save_cache"):
        yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will result in calls to bypass the dependency check.
@pytest.fixture(name="bypass_dependency_check", autouse=True)
def bypass_dependency_check_fixture():
    """Skip calls to check the dependencies of an integration."""
    with patch("homeassistant.setup._async_process_dependencies") as dep_method:
        dep_method.return_value = []
        yield


# This fixture, when used, will result in calls to async_get_devices to return a MOCKED device.
@pytest.fixture(name="bypass_get_devices")
def bypass_get_devices_fixture():
    """Skip calls to get data from API."""
    with patch("custom_components.skybellgen.Skybell.async_get_devices") as init_method:
        devices = get_one_device()
        init_method.return_value = []
        init_method.return_value.append(devices[0])
        yield


# This fixture, when used, will result in calls to async_get_devices to return a MOCKED device.
@pytest.fixture(name="bypass_get_devices2")
def bypass_get_devices2_fixture():
    """Skip calls to get data from API."""
    with patch("custom_components.skybellgen.Skybell.async_get_devices") as init_method:
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "data/device2.json"))
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        device = SkybellDevice(device_json=data, skybell=None)
        init_method.return_value = []
        init_method.return_value.append(device)
        yield


# This fixture, when used, will result in calls to async_get_devices to return a MOCKED device.
@pytest.fixture(name="bypass_get_devices3")
def bypass_get_devices3_fixture():
    """Skip calls to get data from API."""
    with patch("custom_components.skybellgen.Skybell.async_get_devices") as init_method:
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "data/device3.json"))
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        device = SkybellDevice(device_json=data, skybell=None)
        init_method.return_value = []
        init_method.return_value.append(device)
        yield


# Issue SkyBell exception for Hub coordinator get_devices.
@pytest.fixture(name="error_hub_update_exc")
def error_hub_update_exc_fixture():
    """Issue a SkyBellException when called."""
    with patch(
        "custom_components.skybellgen.coordinator.Skybell.async_get_devices",
        side_effect=SkybellException,
    ):
        yield


# Issue SkyBell exception for Hub coordinator get_devices.
@pytest.fixture(name="error_hub_refresh_exc")
def error_hub_refresh_exc_fixture():
    """Issue a SkyBellException when called."""
    with patch(
        "custom_components.skybellgen.coordinator.Skybell.async_refresh_session",
        side_effect=SkybellException,
    ):
        yield


# Bypess for Hub coordinator get_devices.
@pytest.fixture(name="bypass_hub_refresh")
def bypass_hub_refresh_fixture():
    """Bypass the hub refresh call."""
    with patch(
        "custom_components.skybellgen.coordinator.Skybell.async_refresh_session",
    ):
        yield


# This fixture, when used, will result in calls to async_delete_cache.
@pytest.fixture(name="bypass_delete_cache", autouse=True)
def bypass_delete_cache_fixture():
    """Skip calls to delete cache from API."""
    with patch("custom_components.skybellgen.Skybell.async_delete_cache"):
        yield


# In this fixture, we are bypassing calls to async_initialize.
@pytest.fixture(name="bypass_initialize", autouse=True)
def bypass_initialize_fixture():
    """Simulate error when retrieving data from API."""
    with patch("custom_components.skybellgen.Skybell.async_initialize"):
        yield


# In this fixture, we are forcing calls to async_initialize to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_initialize")
def error_initialize_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.skybellgen.Skybell.async_initialize",
        side_effect=SkybellException,
    ):
        yield


# In this fixture, we are forcing calls to async_initialize to raise an Auth Exception.
# This is useful for exception handling.
@pytest.fixture(name="error_initialize_auth")
def error_initialize_auth_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.skybellgen.Skybell.async_initialize",
        side_effect=SkybellAuthenticationException,
    ):
        yield


# In this fixture, we are forcing calls to async_initialize to raise an SkyBellException.
# This is useful for exception handling.
@pytest.fixture(name="error_initialize_exception")
def error_initialize_exception_fixture():
    """Simulate error when authenticating from the API."""
    with patch(
        "custom_components.skybellgen.Skybell.async_initialize",
        side_effect=Exception,
    ):
        yield


# Patch the Platform to remove platforms that cant be tested.
@pytest.fixture(name="remove_platforms")
def remove_camera_platform_fixture():
    """Remove the platforms that cannot be tested from the SkyBellGen integration."""
    with patch("custom_components.skybellgen.PLATFORMS", MOCK_PLATFORMS):
        yield


# Bypass the device async_set_setting.
@pytest.fixture(name="bypass_set_settings", autouse=True)
def bypass_set_settings_fixture():
    """Bypass the call to set settings the SkyBellGen integration."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_set_setting"
    ):
        yield


# In this fixture, we are forcing calls to async_set_setting to raise a SkyBellException.
# This is useful for exception handling.
@pytest.fixture(name="error_set_setting_exc")
def error_set_setting_exc_fixture():
    """Simulate error from the API."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_set_setting",
        side_effect=SkybellException,
    ):
        yield


# In this fixture, we are forcing calls to async_set_setting to raise a SkyBellSCLException.
# This is useful for exception handling.
@pytest.fixture(name="error_set_setting_acl")
def error_set_setting_acl_fixture():
    """Simulate error from the API."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_set_setting",
        side_effect=SkybellAccessControlException,
    ):
        yield


# Bypass the device async_set_setting.
@pytest.fixture(name="bypass_device_reboot", autouse=True)
def bypass_device_reboot_fixture():
    """Bypass the call to set settings the SkyBellGen integration."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_reboot_device"
    ):
        yield


# In this fixture, we are forcing calls to async_reboot_device to raise a SkyBellException.
# This is useful for exception handling.
@pytest.fixture(name="error_reboot_exc")
def error_reboot_exc_fixture():
    """Simulate error from the API."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_reboot_device",
        side_effect=SkybellException,
    ):
        yield


# In this fixture, we are forcing calls to async_reboot_device to raise a SkyBellACLException.
# This is useful for exception handling.
@pytest.fixture(name="error_reboot_acl")
def error_reboot_acl_fixture():
    """Simulate error from the API."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_reboot_device",
        side_effect=SkybellAccessControlException,
    ):
        yield


# Bypass the device async_update.
@pytest.fixture(name="bypass_device_update", autouse=True)
def bypass_device_update_fixture():
    """Bypass the call to update the SkyBellGen device."""
    with patch("custom_components.skybellgen.coordinator.SkybellDevice.async_update"):
        yield


# Issue SkyBell exception for async_update.
@pytest.fixture(name="error_update_exc")
def error_update_exc_fixture():
    """Issue a SkyBellException when called."""
    with patch(
        "custom_components.skybellgen.coordinator.SkybellDevice.async_update",
        side_effect=SkybellException,
    ):
        yield


# This function is used to create a mock config entry for the SkyBellGen integration.
def create_entry(hass) -> MockConfigEntry:
    """Create fixture for adding config entry in Home Assistant."""
    entry = MockConfigEntry(
        domain=DOMAIN, entry_id=USER_ID, unique_id=USER_ID, data=MOCK_CONFIG
    )
    entry.add_to_hass(hass)
    return entry


# This function initializes the SkyBellGen integration in Home Assistant.
async def async_init_integration(hass) -> MockConfigEntry:
    """Set up the skybellgen integration in Home Assistant."""
    config_entry = create_entry(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    return config_entry
