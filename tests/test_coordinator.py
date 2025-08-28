"""Test SkyBellGen coordinator."""

# pylint: disable=protected-access

from datetime import datetime, timedelta, timezone

from aioskybellgen import Skybell
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.skybellgen.const import DOMAIN

from .conftest import async_init_integration, get_one_device, get_two_devices
from .const import DEVICE_ID


async def test_hub_coord_exc(hass, remove_platforms, error_hub_update_exc):
    """Test hub coordinator SkyBell exception."""
    # In this case we are testing the condition where async_setup_entry keeps the
    # configuration in setup when problems occurr in the Hub coordinator.
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_device_coord_exc(
    hass, remove_platforms, bypass_get_devices, error_update_exc
):
    """Test device coordinator async update SkyBell exception."""
    # In this case we are testing the condition where async_setup_entry keeps the
    # configuration in setup when problems occurr in the Device coordinator.
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_hub_coord_stale(hass, remove_platforms, mocker):
    """Test Hub coordinator for stale devices."""
    # In this case we are testing the condition which a device exists in HA but doesn't exist
    # in the SkyBell Cloud.

    # Set up the config_entry and platform with 2 devices
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_two_devices(),
    )
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(config_entry.runtime_data.api, Skybell)
    device_id = "second_device"
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices
    old_device_entry_id = device_entry.id

    # Execute the Hub coordinators _async_update_data but patch the get_devices to only
    # return 1 device
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_one_device(),
    )
    hc = config_entry.runtime_data.hub_coordinator
    await hc.async_refresh()
    device_id = "second_device"
    assert device_id not in config_entry.runtime_data.known_device_ids
    # device should not be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert device_entry is None
    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert old_device_entry_id not in devices


async def test_hub_coord_add(hass, remove_platforms, mocker):
    """Test Hub coordinator for stale devices."""
    # In this case we are testing the condition which a device is added
    # in the SkyBell Cloud.

    # Set up the config_entry and platform with 1 device
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_one_device(),
    )
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(config_entry.runtime_data.api, Skybell)
    device_id = "012345670123456789abcdef"
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices

    # Execute the Hub coordinators _async_update_data but patch the get_devices to
    # return 2 devices
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_two_devices(),
    )
    hc = config_entry.runtime_data.hub_coordinator
    await hc.async_refresh()
    device_id = "second_device"
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices


async def test_hub_coord_refresh(
    hass, remove_platforms, mocker, freezer: FrozenDateTimeFactory, bypass_hub_refresh
):
    """Test Hub coordinator for refresh_session_timestamp."""
    freezer.move_to("2023-03-30 13:33:00+00:00")

    # In this case we are testing the logic where we have a timestamp
    # and the refresh session returns an exception but HA
    # Intercepts the update failed and reschedules the update

    # Set up the config_entry and platform with 1 device
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_one_device(),
    )
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(config_entry.runtime_data.api, Skybell)
    device_id = "012345670123456789abcdef"
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices

    # Modify the API cache
    api = config_entry.runtime_data.api
    auth_result = {
        "AccessToken": "token",
        "ExpiresIn": 3600,
        "RefreshToken": "token",
    }
    auth_result["ExpirationDate"] = datetime.now(timezone.utc) - timedelta(
        seconds=86400
    )
    api._cache["AuthenticationResult"] = auth_result

    # Refresh the hub controller
    hc = config_entry.runtime_data.hub_coordinator
    # await hc._async_refresh_skybell_session(api)
    try:
        await hc.async_refresh()
        assert True
    except UpdateFailed:  # pragma no cover
        pytest.fail("Unexpected Update failed")  # pragma no cover


async def test_hub_coord_refresh_exc(
    hass,
    remove_platforms,
    mocker,
    freezer: FrozenDateTimeFactory,
    error_hub_refresh_exc,
):
    """Test Hub coordinator for refresh_session_timestamp."""
    freezer.move_to("2023-03-30 13:33:00+00:00")

    # In this case we are testing the logic where we have a timestamp
    # and the refresh session returns an exception but HA
    # Intercepts the update failed and reschedules the update

    # Set up the config_entry and platform with 1 device
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_one_device(),
    )
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(config_entry.runtime_data.api, Skybell)
    device_id = "012345670123456789abcdef"
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices

    # Modify the API cache
    api = config_entry.runtime_data.api
    auth_result = {
        "AccessToken": "token",
        "ExpiresIn": 3600,
        "RefreshToken": "token",
    }
    auth_result["ExpirationDate"] = datetime.now(timezone.utc)
    api._cache["AuthenticationResult"] = auth_result

    # Refresh the hub controller
    hc = config_entry.runtime_data.hub_coordinator
    try:
        await hc.async_refresh()
        assert True
    except UpdateFailed:  # pragma no cover
        pytest.fail("Unexpected Update failed")  # pragma no cover


async def test_hub_coord_no_api(
    hass,
    remove_platforms,
    mocker,
    freezer: FrozenDateTimeFactory,
    error_hub_refresh_exc,
):
    """Test Hub coordinator for refresh_session_timestamp."""
    freezer.move_to("2023-03-30 13:33:00+00:00")

    # In this case we are testing the logic where the
    # SkyBell API isn't assigned for this hub controller.

    # Set up the config_entry and platform with 1 device
    mocker.patch(
        "custom_components.skybellgen.Skybell.async_get_devices",
        return_value=get_one_device(),
    )
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(config_entry.runtime_data.api, Skybell)
    device_id = DEVICE_ID
    assert device_id in config_entry.runtime_data.known_device_ids
    # device should be in the device and entity registries
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    entity_registry = er.async_get(hass)
    devices = entity_registry.async_device_ids()
    assert device_entry.id in devices

    # Modify the API
    config_entry.runtime_data.api = None

    # Refresh the hub controller
    hc = config_entry.runtime_data.hub_coordinator
    try:
        await hc.async_refresh()
        assert True
    except UpdateFailed:  # pragma no cover
        pytest.fail("Unexpected Update failed")  # pragma no cover
