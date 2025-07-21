"""Support for the Skybell Doorbells using the Cloud GEN APIs."""

from __future__ import annotations

import asyncio

from aioskybellgen import Skybell
from aioskybellgen.exceptions import (
    SkybellAuthenticationException,
    SkybellException,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import SkybellDataUpdateCoordinator

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

type SkybellConfigEntry = ConfigEntry[SkybellData]


class SkybellData:
    """The Skybell data class for a Hub config entity."""

    api: Skybell


async def async_setup_entry(
    hass: HomeAssistant, entry: SkybellConfigEntry
) -> bool:
    """Set up Skybell from a config entry."""
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    # entry.api = None
    api = Skybell(
        username=email,
        password=password,
        disable_cache=False,
        get_devices=True,
        cache_path=hass.config.path(f"./skybellgen_{entry.unique_id}.pickle"),
        session=async_get_clientsession(hass),
    )
    try:
        devices = await api.async_initialize()
    except SkybellAuthenticationException as ex:
        await api.async_delete_cache()
        raise ConfigEntryAuthFailed from ex
    except SkybellException as ex:
        await api.async_delete_cache()
        raise ConfigEntryNotReady(
            f"Unable to connect to Skybell service: {ex}"
        ) from ex

    device_coordinators: list[SkybellDataUpdateCoordinator] = [
        SkybellDataUpdateCoordinator(hass, entry, device) for device in devices
    ]
    await asyncio.gather(
        *[
            coordinator.async_config_entry_first_refresh()
            for coordinator in device_coordinators
        ]
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device_coordinators
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.api = api
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SkybellConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
        api = entry.api
        if api is not None:
            await api.async_delete_cache()

    return unload_ok
