"""Camera support for the SkyBell Gen Doorbell."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import cast

from aiohttp import web
from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from aioskybellgen.helpers.models import LiveStreamConnectionData
from go2rtc_client import Go2RtcRestClient
from go2rtc_client.ws import (
    Go2RtcWsClient,
    ReceiveMessages,
    WebRTCAnswer,
    WebRTCCandidate,
    WebRTCOffer,
    WsError,
)
from haffmpeg.camera import CameraMjpeg
from homeassistant.components.camera import (
    Camera,
    CameraEntityDescription,
    CameraEntityFeature,
    WebRTCAnswer as HAWebRTCAnswer,
    WebRTCCandidate as HAWebRTCCandidate,
    WebRTCError,
    WebRTCMessage,
    WebRTCSendMessage,
)
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.aiohttp_client import (
    async_aiohttp_proxy_stream,
    async_get_clientsession,
)
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from webrtc_models import RTCIceCandidateInit

from .const import DOMAIN
from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity
from .kvs import KVSEndpointData, parse_kvs_response

_LOGGER = logging.getLogger(__name__)

CAMERA_TYPES: tuple[CameraEntityDescription, ...] = (
    CameraEntityDescription(
        key=CONST.ACTIVITY,
        translation_key=CONST.ACTIVITY,
    ),
    CameraEntityDescription(
        key=CONST.SNAPSHOT,
        translation_key=CONST.SNAPSHOT,
    ),
    CameraEntityDescription(
        key="live_stream",
        translation_key="live_stream",
    ),
)

# Calls to the communications driver should be serialized
PARALLEL_UPDATES = 1


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
                    if entity.key == CONST.SNAPSHOT:
                        entities.append(SkybellCamera(coordinator, entity))
                    elif entity.key == CONST.ACTIVITY:
                        entities.append(SkybellActivityCamera(coordinator, entity))
                    else:
                        entities.append(SkybellLiveStreamCamera(coordinator, entity))
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


class SkybellLiveStreamCamera(SkybellCamera):
    """A camera implementation for SkyBell live stream activity."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a camera for a SkyBell device."""

        super().__init__(coordinator, description)
        self._kvs_ep: KVSEndpointData | None = None
        self._sessions: dict[str, Go2RtcWsClient] = {}
        self._attr_supported_features = CameraEntityFeature.STREAM

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Get the livestream camera image (avatar)."""

        return self._device.images.get(CONST.SNAPSHOT, b"")

    async def async_handle_async_webrtc_offer(
        self, offer_sdp: str, session_id: str, send_message: WebRTCSendMessage
    ) -> None:
        """Handle the async WebRTC offer."""

        self._sessions[session_id] = ws_client = Go2RtcWsClient(
            async_get_clientsession(self.hass),
            self.hass.data["go2rtc"],
            source=self.entity_id,
        )
        await self._async_register_go2rtc_stream()

        @callback
        def on_messages(message: ReceiveMessages) -> None:
            """Handle messages."""
            value: WebRTCMessage
            match message:
                case WebRTCCandidate():
                    value = HAWebRTCCandidate(RTCIceCandidateInit(message.candidate))
                case WebRTCAnswer():
                    value = HAWebRTCAnswer(message.sdp)
                case WsError():
                    value = WebRTCError("go2rtc_webrtc_offer_failed", message.error)
                    self.close_webrtc_session(session_id)

            send_message(value)

        ws_client.subscribe(on_messages)
        config = self.async_get_webrtc_client_configuration()
        await ws_client.send(WebRTCOffer(offer_sdp, config.configuration.ice_servers))

    async def async_on_webrtc_candidate(
        self, session_id: str, candidate: RTCIceCandidateInit
    ) -> None:
        """Handle the WebRTC candidate."""

        if ws_client := self._sessions.get(session_id):
            _LOGGER.debug(
                "Received candidate: %s for session %s",
                candidate.candidate,
                session_id,
            )
            await ws_client.send(WebRTCCandidate(candidate.candidate))
        else:
            _LOGGER.debug("Unknown session %s. Ignoring candidate", session_id)

    @callback
    def close_webrtc_session(self, session_id: str) -> None:
        """Close the session."""
        ws_client = self._sessions.pop(session_id, None)
        if ws_client is not None:
            self.hass.async_create_task(ws_client.close())
        if not self._sessions:
            self.hass.async_create_task(self._async_stop_livestream())
            _LOGGER.debug("session %s. Created task to stop livestream", session_id)

    def _get_go2rtc_url(self) -> str:
        """Get the WS Signed url for kvs in go2rtc format."""

        kvs_ep: KVSEndpointData = cast(
            KVSEndpointData,
            self._kvs_ep,
        )
        result = (
            "webrtc:"
            + kvs_ep.signed_ws_endpoint
            + "#format=kinesis"
            + "#client_id="
            + kvs_ep.client_id
            + "#ice_servers="
            + kvs_ep.ice_servers
        )
        return result

    async def _async_get_webrtc_signalling(self) -> str:
        """Return the webrtc signalling channel."""

        if self._kvs_ep is None:
            await self._async_start_livestream()

        # if the kvs endpoint is expired, restart the livestream
        expiration_ts = datetime.fromisoformat(
            cast(KVSEndpointData, self._kvs_ep).expiration
        )
        if expiration_ts < datetime.now(tz=timezone.utc):
            _LOGGER.info(
                "Livestream endpoint expired. Restarting livestream for %s",
            )
            await self._async_stop_livestream()
            await self._async_start_livestream()

        ss = self._get_go2rtc_url()

        return ss

    async def _async_register_go2rtc_stream(self) -> None:
        """Register the stream in go2rtc if it does not already exist."""

        rest_client = Go2RtcRestClient(
            async_get_clientsession(self.hass), self.hass.data["go2rtc"]
        )

        signed_url = await self._async_get_webrtc_signalling()

        streams = await rest_client.streams.list()
        if (stream := streams.get(self.entity_id)) is None or not any(
            signed_url == producer.url for producer in stream.producers
        ):
            await rest_client.streams.add(
                self.entity_id,
                [signed_url],
            )

    async def _async_start_livestream(self) -> None:
        """Handle starting the live stream."""

        try:
            ls: LiveStreamConnectionData = await self._device.async_start_livestream()
        except SkybellAccessControlException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_permissions",
                translation_placeholders={
                    "key": self.entity_description.key,
                },
            ) from exc
        except SkybellException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="turnon_livestream_failed",
                translation_placeholders={
                    "key": self.entity_description.key,
                    "error": repr(exc),
                },
            ) from exc
        self._kvs_ep = parse_kvs_response(ls, self._device.device_id)

    async def _async_stop_livestream(self) -> None:
        """Handle stopping the live stream."""

        try:
            await self._device.async_stop_livestream()
        except SkybellAccessControlException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_permissions",
                translation_placeholders={
                    "key": self.entity_description.key,
                },
            ) from exc
        except SkybellException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="turnoff_livestream_failed",
                translation_placeholders={
                    "key": self.entity_description.key,
                    "error": repr(exc),
                },
            ) from exc
        finally:
            self._kvs_ep = None
