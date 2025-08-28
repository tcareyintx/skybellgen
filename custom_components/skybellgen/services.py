"""Services for the SkyBellGen integration."""

from __future__ import annotations

from aioskybellgen import Skybell
from homeassistant.core import HomeAssistant, ServiceCall, callback

from .const import (
    DOMAIN,
    SERVICE_START_LOCAL_EVENT_SERVER,
    SERVICE_STOP_LOCAL_EVENT_SERVER,
)


async def _start_local_event_server(call: ServiceCall) -> None:
    """Call Skybell to start the local event server."""
    Skybell.setup_local_event_server()


async def _stop_local_event_server(call: ServiceCall) -> None:
    """Call Skybell to stop the local event server."""
    Skybell.shutdown_local_event_server()


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the services for the Blink integration."""

    hass.services.async_register(
        DOMAIN,
        SERVICE_START_LOCAL_EVENT_SERVER,
        _start_local_event_server,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_LOCAL_EVENT_SERVER,
        _stop_local_event_server,
    )
