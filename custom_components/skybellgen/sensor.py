"""Sensor support for Skybell Gen  Doorbells."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from aioskybellgen import SkybellDevice
from aioskybellgen.helpers import const as CONST
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    IMAGE_FIELDS,
    IMAGE_OPTIONS,
    SENTSITIVTY_ADJ,
    TENTH_PERCENT_TYPES,
    USE_MOTION_VALUE,
    VOLUME_FIELDS,
    VOLUME_OPTIONS,
)
from .entity import DOMAIN, SkybellEntity


@dataclass(frozen=True, kw_only=True)
class SkybellSensorEntityDescription(SensorEntityDescription):
    """Class to describe a Skybell sensor."""

    value_fn: Callable[[SkybellDevice], StateType | datetime]


SENSOR_TYPES: tuple[SkybellSensorEntityDescription, ...] = (
    SkybellSensorEntityDescription(
        key="last_button_event",
        translation_key="last_button_event",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda device: device.latest_doorbell_event_time,
    ),
    SkybellSensorEntityDescription(
        key="last_motion_event",
        translation_key="last_motion_event",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda device: device.latest_motion_event_time,
    ),
    SkybellSensorEntityDescription(
        key="last_livestream_event",
        translation_key="last_livestream_event",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda device: device.latest_livestream_event_time,
    ),
    SkybellSensorEntityDescription(
        key=CONST.DEVICE_LAST_SEEN,
        translation_key=CONST.DEVICE_LAST_SEEN,
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.last_seen,
    ),
    SkybellSensorEntityDescription(
        key=CONST.LAST_CONNECTED,
        translation_key=CONST.LAST_CONNECTED,
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.last_connected,
    ),
    SkybellSensorEntityDescription(
        key=CONST.LAST_DISCONNECTED,
        translation_key=CONST.LAST_DISCONNECTED,
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.last_disconnected,
    ),
    SkybellSensorEntityDescription(
        key=CONST.WIFI_SSID,
        translation_key="wifi_ssid",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.wifi_ssid,
    ),
    SkybellSensorEntityDescription(
        key=CONST.WIFI_LINK_QUALITY,
        translation_key="wifi_link_quality",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.wifi_link_quality,
    ),
    SkybellSensorEntityDescription(
        key=CONST.OUTDOOR_CHIME_VOLUME,
        translation_key=CONST.OUTDOOR_CHIME_VOLUME,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.outdoor_chime_volume,
    ),
    SkybellSensorEntityDescription(
        key=CONST.SPEAKER_VOLUME,
        translation_key=CONST.SPEAKER_VOLUME,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.speaker_volume,
    ),
    SkybellSensorEntityDescription(
        key=CONST.IMAGE_QUALITY,
        translation_key=CONST.IMAGE_QUALITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.image_quality,
    ),
    SkybellSensorEntityDescription(
        key=CONST.MOTION_SENSITIVITY,
        translation_key=CONST.MOTION_SENSITIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.motion_sensitivity,
    ),
    SkybellSensorEntityDescription(
        key=CONST.MOTION_HMBD_SENSITIVITY,
        translation_key=CONST.MOTION_HMBD_SENSITIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.hmbd_sensitivity,
    ),
    SkybellSensorEntityDescription(
        key=CONST.MOTION_FD_SENSITIVITY,
        translation_key=CONST.MOTION_FD_SENSITIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.fd_sensitivity,
    ),
    SkybellSensorEntityDescription(
        key=CONST.MOTION_PIR_SENSITIVITY,
        translation_key=CONST.MOTION_PIR_SENSITIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.pir_sensitivity,
    ),
    SkybellSensorEntityDescription(
        key=CONST.LOCATION_LAT,
        translation_key="location_lat",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.location_lat,
    ),
    SkybellSensorEntityDescription(
        key=CONST.LOCATION_LON,
        translation_key="location_lon",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.location_lon,
    ),
    SkybellSensorEntityDescription(
        key=CONST.LOCATION_PLACE,
        translation_key="location_place",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.location_place,
    ),
    SkybellSensorEntityDescription(
        key=CONST.NAME,
        translation_key=CONST.NAME,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.name,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell sensor."""
    async_add_entities(
        SkybellSensor(coordinator, description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for description in SENSOR_TYPES
    )


class SkybellSensor(SkybellEntity, SensorEntity):
    """A sensor implementation for Skybell devices."""

    entity_description: SkybellSensorEntityDescription

    @property
    def native_value(self) -> StateType | datetime:
        """Return the state of the sensor."""
        value = self.entity_description.value_fn(self._device)

        # Check the fields with select options
        array_options = None
        if self.entity_description.key in VOLUME_FIELDS:
            array_options = VOLUME_OPTIONS
        elif self.entity_description.key in IMAGE_FIELDS:
            array_options = IMAGE_OPTIONS

        if array_options is not None:
            index = value
            try:
                value = array_options[index]
            except (IndexError, ValueError) as exc:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="no_option_for_key",
                    translation_placeholders={
                        "key": self.entity_description.key,
                        "option": index,
                    },
                ) from exc

        # Check the fields with number adjustments
        if self.entity_description.key in TENTH_PERCENT_TYPES:
            # Check for values 0,1,2 adjust for low medium high
            if value >= 0 and value <= len(SENTSITIVTY_ADJ):
                value = SENTSITIVTY_ADJ[value] * 10
            elif (
                self.entity_description.key in USE_MOTION_VALUE
                and value == CONST.USE_MOTION_SENSITIVITY
            ):
                value_fn = getattr(self._device, CONST.MOTION_SENSITIVITY)
                value = value_fn
            # Set the value returned by the function
            value = float(value / 10)

        return value
