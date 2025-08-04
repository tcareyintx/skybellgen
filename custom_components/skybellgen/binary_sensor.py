"""Binary sensor support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.helpers import const as CONST
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BASIC_MOTION_GET_FUNCTION, DOMAIN
from .coordinator import SkybellDataUpdateCoordinator
from .entity import SkybellEntity

BINARY_SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key=CONST.BUTTON_PRESSED,
        translation_key=CONST.BUTTON_PRESSED,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.MOTION_DETECTION,
        translation_key=CONST.MOTION_DETECTION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.DEBUG_MOTION_DETECTION,
        translation_key=CONST.DEBUG_MOTION_DETECTION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.INDOOR_CHIME,
        translation_key=CONST.INDOOR_CHIME,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.INDOOR_DIGITAL_CHIME,
        translation_key=CONST.INDOOR_DIGITAL_CHIME,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.OUTDOOR_CHIME,
        translation_key=CONST.OUTDOOR_CHIME,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_NOTIFY,
        translation_key=CONST.BASIC_MOTION_NOTIFY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_RECORD,
        translation_key=CONST.BASIC_MOTION_RECORD,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_FD_NOTIFY,
        translation_key=CONST.BASIC_MOTION_FD_NOTIFY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_FD_RECORD,
        translation_key=CONST.BASIC_MOTION_FD_RECORD,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_HBD_NOTIFY,
        translation_key=CONST.BASIC_MOTION_HBD_NOTIFY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key=CONST.BASIC_MOTION_HBD_RECORD,
        translation_key=CONST.BASIC_MOTION_HBD_RECORD,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell binary sensor."""
    async_add_entities(
        SkybellBinarySensor(coordinator, sensor)
        for sensor in BINARY_SENSOR_TYPES
        for coordinator in hass.data[DOMAIN][entry.entry_id]
    )


class SkybellBinarySensor(SkybellEntity, BinarySensorEntity):
    """A binary sensor implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize a binary sensor for a Skybell device."""
        super().__init__(coordinator, description)

    @callback
    def _handle_coordinator_update(self) -> None:
        key = self.entity_description.key
        if key in BASIC_MOTION_GET_FUNCTION:
            key = BASIC_MOTION_GET_FUNCTION.get(key)
        value_fn = getattr(self._device, key)
        self.is_on = bool(value_fn)
        super()._handle_coordinator_update()
