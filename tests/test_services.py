"""Test SkyBellGen services."""

from homeassistant.config_entries import ConfigEntryState

from custom_components.skybellgen.const import (
    DOMAIN,
    SERVICE_START_LOCAL_EVENT_SERVER,
    SERVICE_STOP_LOCAL_EVENT_SERVER,
)

from .conftest import async_init_integration


async def test_local_server(hass, remove_platforms, bypass_get_devices, mocker):
    """Test local server."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Make a service call to setup the server
    # Since the service call will create a separate thread - just mock it for
    # coverage.
    mocker.patch("aioskybellgen.Skybell.setup_local_event_server")
    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_LOCAL_EVENT_SERVER,
        None,
        blocking=True,
    )

    # Make a service call to stop the server
    # Since the service call will create a separate thread - just mock it for
    # coverage.
    mocker.patch("aioskybellgen.Skybell.shutdown_local_event_server")
    await hass.services.async_call(
        DOMAIN,
        SERVICE_STOP_LOCAL_EVENT_SERVER,
        None,
        blocking=True,
    )
