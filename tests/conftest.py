"""Global fixtures for SkybellGen integration."""

from os import path
import json
from aioskybellgen import SkybellDevice
from unittest.mock import patch

import pytest

from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
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


# This fixture, when used, will result in calls to bypass the coordinators first refresh.
@pytest.fixture(name="bypass_first_refresh")
def bypass_first_refresh_fixture():
    """Skip calls refresh the configuration entry."""
    with patch("homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_config_entry_first_refresh"):
        yield


# This fixture, when used, will result in calls to bypass the config entry bypass.
#  We have to bypass because for some reason AddConfigEntryEntitiesCallback doesnt exist.
@pytest.fixture(name="bypass_forward_setup")
def bypass_forward_setup_fixture():
    """Skip calls forward the build to the platform."""
    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"):
        yield


# This fixture, when used, will result in calls to async_initialize to return a MOCKED device.
@pytest.fixture(name="bypass_initialize")
def bypass_initialize_fixture():
    """Skip calls to get data from API."""
    with patch("custom_components.skybellgen.Skybell.async_initialize") as init_method:
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "data/device.json"))
        with open(filepath, 'r') as file:
            data = json.load(file)
        device = SkybellDevice(device_json=data, skybell=None)
        init_method.return_value = []
        init_method.return_value.append(device)
        yield


# This fixture, when used, will result in calls to async_refresh_session.
@pytest.fixture(name="bypass_refresh_session")
def bypass_refresh_session_fixture():
    """Skip calls to get data from API."""
    with patch("custom_components.skybellgen.Skybell.async_refresh_session"):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.skybellgen.Skybell.async_initialize",
        side_effect=Exception,
    ):
        yield
