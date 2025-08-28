"""Camera support for the SkyBell Gen Doorbell."""

from __future__ import annotations

from aiohttp import web
from haffmpeg.camera import CameraMjpeg
from homeassistant.components.camera import Camera, CameraEntityDescription
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity

CAMERA_TYPES: tuple[CameraEntityDescription, ...] = (
    CameraEntityDescription(
        key="activity",
        translation_key="activity",
    ),
    CameraEntityDescription(
        key="avatar",
        translation_key="avatar",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SkyBell camera."""

    known_device_ids: set[str] = set()

    def _check_device() -> None:
        entities = []
        new_device_ids: set[str] = set()
        for entity in CAMERA_TYPES:
            for coordinator in entry.runtime_data.device_coordinators:
                if not isinstance(coordinator, SkybellDeviceDataUpdateCoordinator):
                    continue
                if coordinator.device.device_id not in known_device_ids:
                    if entity.key == "avatar":
                        entities.append(SkybellCamera(coordinator, entity))
                    else:
                        entities.append(SkybellActivityCamera(coordinator, entity))
                    new_device_ids.add(coordinator.device.device_id)
        if entities:
            known_device_ids.update(new_device_ids)
            async_add_entities(entities)

    _check_device()

    entry.async_on_unload(
        entry.runtime_data.hub_coordinator.async_add_listener(_check_device)
    )


class SkybellCamera(SkybellEntity, Camera):
    """A camera implementation for SkyBell devices."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a camera for a SkyBell device."""
        super().__init__(coordinator, description)
        Camera.__init__(self)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Get the latest camera image."""
        return self._device.images.get(self.entity_description.key, b"")


class SkybellActivityCamera(SkybellCamera):
    """A camera implementation for latest SkyBell activity."""

    async def handle_async_mjpeg_stream(
        self, request: web.Request
    ) -> web.StreamResponse:
        """Generate an HTTP MJPEG stream from the latest recorded activity."""
        stream = CameraMjpeg(get_ffmpeg_manager(self.hass).binary)
        url = await self.coordinator.device.async_get_activity_video_url()
        await stream.open_camera(url, extra_cmd="-r 210")

        try:
            return await async_aiohttp_proxy_stream(
                self.hass,
                request,
                await stream.get_reader(),
                get_ffmpeg_manager(self.hass).ffmpeg_stream_content_type,
            )
        finally:
            await stream.close()
