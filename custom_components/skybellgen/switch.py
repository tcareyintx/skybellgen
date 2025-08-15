"""Switch support for the Skybell Gen Doorbell."""

from __future__ import annotations

from typing import Any, cast

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BASIC_MOTION_GET_FUNCTION, DOMAIN
from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity

SWITCH_TYPES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key=CONST.BUTTON_PRESSED,
        translation_key=CONST.BUTTON_PRESSED,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.MOTION_DETECTION,
        translation_key=CONST.MOTION_DETECTION,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.DEBUG_MOTION_DETECTION,
        translation_key=CONST.DEBUG_MOTION_DETECTION,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.INDOOR_CHIME,
        translation_key=CONST.INDOOR_CHIME,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.INDOOR_DIGITAL_CHIME,
        translation_key=CONST.INDOOR_DIGITAL_CHIME,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.OUTDOOR_CHIME,
        translation_key=CONST.OUTDOOR_CHIME,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_HBD_RECORD,
        translation_key=CONST.BASIC_MOTION_HBD_RECORD,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_HBD_NOTIFY,
        translation_key=CONST.BASIC_MOTION_HBD_NOTIFY,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_RECORD,
        translation_key=CONST.BASIC_MOTION_RECORD,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_NOTIFY,
        translation_key=CONST.BASIC_MOTION_NOTIFY,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_FD_RECORD,
        translation_key=CONST.BASIC_MOTION_FD_RECORD,
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key=CONST.BASIC_MOTION_FD_NOTIFY,
        translation_key=CONST.BASIC_MOTION_FD_NOTIFY,
        entity_category=EntityCategory.CONFIG,
    ),
)

# Calls to the communications driver should be serialized
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Skybell switch."""

    known_device_ids: set[str] = set()

    def _check_device() -> None:
        entities = []
        new_device_ids: set[str] = set()
        for entity in SWITCH_TYPES:
            for coordinator in entry.runtime_data.device_coordinators:
                if (coordinator.device.device_id not in known_device_ids) and (
                    (not coordinator.device.is_readonly)
                    or (
                        coordinator.device.is_readonly
                        and entity.key in CONST.ACL_EXCLUSIONS
                    )
                ):
                    new_device_ids.add(coordinator.device.device_id)
                    entities.append(SkybellSwitch(coordinator, entity))
        if entities:
            known_device_ids.update(new_device_ids)
            async_add_entities(entities)

    _check_device()

    entry.async_on_unload(
        entry.runtime_data.hub_coordinator.async_add_listener(_check_device)
    )


class SkybellSwitch(SkybellEntity, SwitchEntity):
    """A switch implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize a binary sensor for a Skybell device."""
        super().__init__(coordinator, description)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        try:
            await self._device.async_set_setting(self.entity_description.key, True)
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
                translation_key="invalid_setting",
                translation_placeholders={
                    "key": self.entity_description.key,
                    "value": str(True),
                },
            ) from exc
        # To stop bouncing issue a refresh
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        try:
            await self._device.async_set_setting(self.entity_description.key, False)
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
                translation_key="invalid_setting",
                translation_placeholders={
                    "key": self.entity_description.key,
                    "value": str(False),
                },
            ) from exc

        # To stop bouncing issue a refresh
        await self.coordinator.async_refresh()

    @property
    def is_on(self) -> bool:
        """Return true if entity is on."""
        key = self.entity_description.key
        if key in BASIC_MOTION_GET_FUNCTION:
            key = BASIC_MOTION_GET_FUNCTION[key]
        return cast(bool, getattr(self._device, key))
