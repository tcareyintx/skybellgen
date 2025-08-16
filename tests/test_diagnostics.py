"""Test SkyBellGen coordinator."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry

from custom_components.skybellgen.const import DOMAIN
from custom_components.skybellgen.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)

from .conftest import async_init_integration
from .const import DEVICE_ID


async def test_diagnostic_config(hass, remove_platforms, bypass_get_devices):
    """Test diagnostics config entry."""
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    retval = await async_get_config_entry_diagnostics(hass, config_entry)
    assert isinstance(retval, dict)
    data = retval["devices"]
    dd = data[DEVICE_ID]
    device = dd["data"]
    assert "REDACTED" in device["account_id"]


async def test_diagnostic_device(hass, remove_platforms, bypass_get_devices):
    """Test diagnostics device entry."""
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # device should be in the device registry
    device_id = DEVICE_ID
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    assert isinstance(device_entry, DeviceEntry)

    retval = await async_get_device_diagnostics(hass, config_entry, device_entry)
    assert isinstance(retval, dict)
    data = retval["device"]
    device = data["data"]
    assert "REDACTED" in device["account_id"]
