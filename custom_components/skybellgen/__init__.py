"""Support for the Skybell Doorbells using the Cloud GEN APIs."""

from __future__ import annotations

from dataclasses import dataclass

from aioskybellgen import Skybell
from aioskybellgen.exceptions import SkybellAuthenticationException, SkybellException
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

# Calls to the communications driver should be serialized
PARALLEL_UPDATES = 1


@dataclass
class SkybellData:
    """The Skybell data class for a Hub config entity."""

    api: Skybell | None = None
    # Ignore typing errors due to circular imports with the data coordinator
    hub_coordinator = None  # type: ignore[assignment]
    device_coordinators = None  # type: ignore[assignment]
    known_device_ids: set[str] | None = None
    current_device_ids: set[str] | None = None


type SkybellConfigEntry = ConfigEntry[SkybellData]  # flake8: noqa: E999


async def async_setup_entry(hass: HomeAssistant, entry: SkybellConfigEntry) -> bool:
    """Set up Skybell from a config entry."""
    from .coordinator import (  # pylint: disable=import-outside-toplevel, cyclic-import
        SkybellHubDataUpdateCoordinator,
    )

    # Sign into the session and get initial devices
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    api = Skybell(
        username=email,
        password=password,
        disable_cache=False,
        get_devices=False,
        cache_path=hass.config.path(f"./skybellgen_{entry.unique_id}.pickle"),
        session=async_get_clientsession(hass),
    )
    try:
        await api.async_initialize()
    except SkybellAuthenticationException as ex:
        await api.async_delete_cache()
        raise ConfigEntryAuthFailed from ex
    except SkybellException as ex:
        await api.async_delete_cache()
        raise ConfigEntryNotReady(f"Unable to connect to Skybell service: {ex}") from ex

    # Assign the API and initialize the runtime data
    entry.runtime_data = SkybellData(api=api)
    entry.runtime_data.known_device_ids = set()
    entry.runtime_data.current_device_ids = set()
    entry.runtime_data.device_coordinators = []  # type: ignore[assignment]

    # Setup the hub coordinator
    hub_coordinator: SkybellHubDataUpdateCoordinator = SkybellHubDataUpdateCoordinator(
        hass, entry, str(entry.unique_id)
    )
    entry.runtime_data.hub_coordinator = hub_coordinator  # type: ignore[assignment]
    await hub_coordinator.async_check_update_interval(api=api)

    # Get the devices and setup the device coordinators
    await hub_coordinator.async_config_entry_first_refresh()

    # Setup the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: SkybellConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:  # pragma: no cover
    """Remove a config entry from a device."""
    remove_entry = False
    for identifier in device_entry.identifiers:
        device_id = identifier[1]
        if (
            identifier[0] == DOMAIN
            and device_id not in config_entry.runtime_data.current_device_ids
        ):
            remove_entry = True
            if device_id in config_entry.runtime_data.known_device_ids:
                del config_entry.runtime_data.known_device_ids[device_id]
    return remove_entry


async def async_unload_entry(hass: HomeAssistant, entry: SkybellConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        api = entry.runtime_data.api
        if api is not None:
            await api.async_delete_cache()

    return unload_ok
