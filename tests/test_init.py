"""Test SkybellGen setup process."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.skybellgen import async_setup_entry, async_unload_entry
from custom_components.skybellgen.const import DOMAIN
from custom_components.skybellgen.coordinator import (
    SkybellDeviceDataUpdateCoordinator,
    SkybellHubDataUpdateCoordinator,
)

from .conftest import async_init_integration
from .const import MOCK_CONFIG


async def test_setup_and_unload_entry(
    hass,
    remove_platforms,
    bypass_get_devices,
):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    # Set up the entry and assert that the values set during setup are where we expect
    # them to be.
    # Because we have patched the following calls:
    #    Skybell.async_initialize
    #    Skybell.async_get_devices (HubCoordinator)
    #    Skybell.async_refresh_session (HubCoordinator)
    #    SkybellDevice.async_update(refresh=True, get_devices=True) (DataCoordinator)
    # No APIs to the Skybell Cloud (aioskybellgen) actually runs.
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Check that the device registry has been loaded
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(
        identifiers={(DOMAIN, "012345670123456789abcdef")}
    )
    assert isinstance(device_entry, dr.DeviceEntry)
    # We have to reload the platforms because the test auto tears down the integration
    # after the test is done.
    hc = config_entry.runtime_data.hub_coordinator
    assert isinstance(hc, SkybellHubDataUpdateCoordinator)
    dc = config_entry.runtime_data.device_coordinators
    assert isinstance(dc[0], SkybellDeviceDataUpdateCoordinator)

    # Execute the Unload the entry
    assert await async_unload_entry(hass, config_entry)


async def test_setup_entry_exception(hass, error_initialize):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_initialize` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


async def test_setup_entry_auth_exception(hass, error_initialize_auth):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryAuthFailed using the `error_iniitalize_auth` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryAuthFailed):
        assert await async_setup_entry(hass, config_entry)
