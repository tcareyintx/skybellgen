"""Data update coordinator for the SkyBell Gen integration."""

import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import cast

from aioskybellgen import Skybell, SkybellDevice
from aioskybellgen.exceptions import SkybellException
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import SkybellConfigEntry
from .const import (
    CONF_USE_LOCAL_SERVER,
    DATA_REFRESH_CYCLE,
    DOMAIN,
    HUB_REFRESH_CYCLE,
    LOCAL_REFRESH_CYCLE,
)

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)


class SkybellHubDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Data update coordinator for a SkyBell Hub."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: SkybellConfigEntry,
        name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=name,
            update_interval=timedelta(seconds=HUB_REFRESH_CYCLE),
            always_update=True,
        )
        self.data = []  # type: ignore[assignment, var-annotated]

    async def async_check_update_interval(self, api: Skybell) -> None:
        """Check if the update_interval needs adjusted."""
        update_interval = self.update_interval  # type: ignore[has-type]
        if update_interval is None:
            update_interval = timedelta(seconds=HUB_REFRESH_CYCLE)  # pragma: no cover
        session_refresh_timestamp = api.session_refresh_timestamp
        if session_refresh_timestamp is None:
            _LOGGER.warning("No refresh session for hub: %s", api.user_id)
            return
        if session_refresh_timestamp < (datetime.now(timezone.utc) + update_interval):
            self.update_interval = session_refresh_timestamp - datetime.now(
                timezone.utc
            )
            if self.update_interval.total_seconds() < 0:
                self.update_interval = timedelta(seconds=LOCAL_REFRESH_CYCLE)

    async def _async_refresh_skybell_session(self, api: Skybell) -> None:
        """Refresh the SkyBell session if needed."""
        # If the session refresh timestamp is not None and the current time is greater
        # than the session refresh timestamp, we need to refresh the session.
        ts = api.session_refresh_timestamp
        next_update = datetime.now(timezone.utc) + cast(timedelta, self.update_interval)
        if ts is not None and (next_update >= ts):
            try:
                await api.async_refresh_session()
                _LOGGER.debug("Succesfull refresh session for %s", api.user_id)
            except SkybellException as exc:
                raise UpdateFailed(
                    translation_domain=DOMAIN,
                    translation_key="refresh_failed",
                    translation_placeholders={
                        "error": repr(exc),
                    },
                ) from exc
        self.update_interval = timedelta(seconds=HUB_REFRESH_CYCLE)
        await self.async_check_update_interval(api)

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        entry: SkybellConfigEntry = cast(SkybellConfigEntry, self.config_entry)
        api = entry.runtime_data.api
        if api is None:
            _LOGGER.warning("SkyBellGen API isn't setup, cannot refresh session")
            return

        # Check if we should refresh the tokens for the session
        await self._async_refresh_skybell_session(api)

        # Check if the update_interval needs adjusted.
        await self.async_check_update_interval(api=api)

        # Get devices
        try:
            devices: list[SkybellDevice] = await api.async_get_devices(refresh=True)
            _LOGGER.debug("Succesfull hub retrieval %s", api.user_id)
        except SkybellException as exc:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={
                    "error": repr(exc),
                },
            ) from exc

        current_device_ids = set()
        for device in devices:
            current_device_ids.add(device.device_id)

        # Remove any stale devices
        known_device_ids: set[str] = cast(set, entry.runtime_data.known_device_ids)
        if stale_device_ids := known_device_ids - current_device_ids:
            device_registry = dr.async_get(self.hass)
            for device_id in stale_device_ids:
                device_entry = device_registry.async_get_device(
                    identifiers={(DOMAIN, device_id)}
                )
                if device_entry:
                    # This action will trigger an event to remove the device
                    # from the components/registries (entity registry)
                    # listening for a "remove device" event.
                    device_registry.async_update_device(
                        device_id=device_entry.id,
                        remove_config_entry_id=entry.entry_id,
                    )
                # Clean up the config_entries runtime data
                self.remove_device_coordinators(device_id)
        entry.runtime_data.current_device_ids = current_device_ids
        self.data = devices  # type: ignore[assignment, var-annotated]
        await self.async_check_new_devices()

    def remove_device_coordinators(self, device_id: str) -> None:
        """Remove the coordinator and device info from the Hub Coordinator."""
        entry: SkybellConfigEntry = cast(SkybellConfigEntry, self.config_entry)
        cast(set, entry.runtime_data.known_device_ids).discard(device_id)
        array_index: list[int] = []
        for i, dc in enumerate(
            cast(list, entry.runtime_data.device_coordinators)
        ):  # type: ignore[var-annotated]
            if dc.device.device_id == device_id:
                array_index.append(i)
        for index in sorted(array_index, reverse=True):
            del cast(list, entry.runtime_data.device_coordinators)[index]

    async def async_check_new_devices(self) -> None:
        """Check for new devices and build the associated coordinators and platform entities."""
        entry: SkybellConfigEntry = cast(SkybellConfigEntry, self.config_entry)
        known_device_ids: set[str] = cast(set, entry.runtime_data.known_device_ids)
        current_device_ids: set[str] = cast(set, entry.runtime_data.current_device_ids)
        new_device_ids: set[str] = current_device_ids - known_device_ids
        if new_device_ids:
            known_device_ids.update(new_device_ids)
            await self.async_add_coordinators(new_device_ids)

    async def async_add_coordinators(self, new_device_ids: set[str]) -> None:
        """Build the associated device coordinators."""
        entry: SkybellConfigEntry = cast(SkybellConfigEntry, self.config_entry)
        devices: list[SkybellDevice] = self.data  # type: ignore[assignment, var-annotated]
        # Setup the device coordinators
        device_coordinators: list[
            SkybellDeviceDataUpdateCoordinator | SkybellDeviceLocalUpdateCoordinator
        ] = []
        for new_device_id in new_device_ids:
            for device in devices:
                if device.device_id == new_device_id:
                    device_coordinators.append(
                        SkybellDeviceDataUpdateCoordinator(self.hass, entry, device)
                    )

                    if entry.data.get(CONF_USE_LOCAL_SERVER, False):
                        device_coordinators.append(
                            SkybellDeviceLocalUpdateCoordinator(
                                self.hass, entry, device
                            )
                        )

        cast(list, entry.runtime_data.device_coordinators).extend(
            device_coordinators
        )  # type: ignore[assignment]

        if entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
            await asyncio.gather(
                *[
                    coordinator.async_config_entry_first_refresh()
                    for coordinator in device_coordinators
                ]
            )


class SkybellDeviceDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Data update coordinator for a SkyBell device."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: SkybellConfigEntry,
        device: SkybellDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=device.name,
            update_interval=timedelta(seconds=DATA_REFRESH_CYCLE),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        try:
            await self.device.async_update(refresh=True, get_devices=True)
            _LOGGER.debug("Succesfull update for %s", self.device.name)
        except SkybellException as exc:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={
                    "error": repr(exc),
                },
            ) from exc


class SkybellDeviceLocalUpdateCoordinator(DataUpdateCoordinator[None]):
    """Data update coordinator for a SkyBell device local information."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: SkybellConfigEntry,
        device: SkybellDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=device.name,
            update_interval=timedelta(seconds=LOCAL_REFRESH_CYCLE),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        # No need to update information from the API
