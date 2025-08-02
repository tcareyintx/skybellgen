"""Data update coordinator for the Skybell Gen integration."""

from datetime import datetime, timedelta

from aioskybellgen import SkybellDevice
from aioskybellgen.exceptions import SkybellException
from aioskybellgen.helpers.const import REFRESH_CYCLE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER


class SkybellDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Data update coordinator for the Skybell integration."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: SkybellDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            config_entry=config_entry,
            name=device.name,
            update_interval=timedelta(seconds=REFRESH_CYCLE),
        )
        self.device = device

    async def _async_refresh_skybell_session(self) -> None:  # pragma: no cover
        """Refresh the Skybell session if needed."""
        # If the session refresh timestamp is not None and the current time is greater
        # than the session refresh timestamp, we need to refresh the session.
        ts = self.device.skybell.session_refresh_timestamp
        if (ts is not None and (datetime.now() > ts)):
            try:
                await self.device.skybell.async_refresh_session()
            except SkybellException as exc:
                raise UpdateFailed(
                    translation_domain=DOMAIN,
                    translation_key="refresh_failed",
                    translation_placeholders={
                        "error": exc,
                    },
                ) from exc

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        # Check if we should refresh the tokens for the ses
        await self._async_refresh_skybell_session()

        # Update the device
        try:
            await self.device.async_update(refresh=True, get_devices=True)
        except SkybellException as exc:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={
                    "error": exc,
                },
            ) from exc
