"""Constants for the Skybell Gen Doorbell."""

import logging
from typing import Final

from aioskybellgen.helpers.const import (
    BASIC_MOTION_FD_NOTIFY,
    BASIC_MOTION_FD_RECORD,
    BASIC_MOTION_HBD_NOTIFY,
    BASIC_MOTION_HBD_RECORD,
    BASIC_MOTION_NOTIFY,
    BASIC_MOTION_RECORD,
    IMAGE_QUALITY,
    MOTION_FD_SENSITIVITY,
    MOTION_HMBD_SENSITIVITY,
    MOTION_PIR_SENSITIVITY,
    MOTION_SENSITIVITY,
    OUTDOOR_CHIME_VOLUME,
    SPEAKER_VOLUME,
)

DEFAULT_NAME = "SkyBellGen"
DOMAIN: Final = "skybellgen"

IMAGE_AVATAR = "avatar"
IMAGE_ACTIVITY = "activity"

DEFAULT_LED_COLOR = [0, 255, 0]
DEFAULT_BRIGHTNESS = 255

ENUMERATION_VS_VALUES = [
    "Low",
    "Medium",
    "High",
]

ENUMERATION_IQ_VALUES = [
    "Low",
    "Medium",
    "High",
    "Highest",
]

ENUMERATION_TYPES = [
    OUTDOOR_CHIME_VOLUME,
    SPEAKER_VOLUME,
    IMAGE_QUALITY,
    MOTION_SENSITIVITY,
    MOTION_PIR_SENSITIVITY,
    MOTION_HMBD_SENSITIVITY,
    MOTION_FD_SENSITIVITY,
]

TENTH_PERCENT_TYPES = [
    MOTION_SENSITIVITY,
    MOTION_PIR_SENSITIVITY,
    MOTION_HMBD_SENSITIVITY,
    MOTION_FD_SENSITIVITY,
]

VOLUME_OPTIONS = ["Low", "Medium", "High"]

IMAGE_OPTIONS = ["Low", "Medium", "High", "Highest"]

BASIC_MOTION_GET_FUNCTION = {
    BASIC_MOTION_HBD_RECORD: "basic_motion_hbd_record",
    BASIC_MOTION_HBD_NOTIFY: "basic_motion_hbd_notify",
    BASIC_MOTION_FD_RECORD: "basic_motion_fd_record",
    BASIC_MOTION_FD_NOTIFY: "basic_motion_fd_notify",
    BASIC_MOTION_RECORD: "basic_motion_record",
    BASIC_MOTION_NOTIFY: "basic_motion_notify",
}

LOGGER = logging.getLogger(__package__)
