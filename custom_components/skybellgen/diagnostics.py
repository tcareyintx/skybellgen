"""Diagnostics support for the SkyBellGen integration."""

# pylint: disable=protected-access

from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

from aioskybellgen import Skybell, SkybellDevice
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from . import SkybellConfigEntry
from .coordinator import SkybellDeviceDataUpdateCoordinator

PARALLEL_UPDATES = 1

TO_REDACT_INFO = [
    "account_id",
    "email",
    "fname",
    "lname",
    "hd_user_id",
    "password",
    "premium",
    "user_mobile_settings",
]

TO_REDACT_DATA = [
    "account_id",
    "certificate_id",
    "client_id",
    "doorlock_id",
    "events",
    "invite_token",
    "lat",
    "lon",
    "location_id",
    "OTA_signature",
    "preview",
    "rapidsos",
]


def device_to_dict(device: SkybellDevice) -> dict:
    """Convert a SkyBellDevice to a dictionary."""
    diagnostic_data: dict[str, Any] = {}
    data: dict[str, Any] = deepcopy(device._device_json)
    data.pop("settings", None)
    red_data = async_redact_data(data, TO_REDACT_DATA)
    diagnostic_data["data"] = red_data
    data = deepcopy(device._events)
    red_data = async_redact_data(data, TO_REDACT_DATA)
    diagnostic_data["events"] = red_data
    data = deepcopy(device._snapshot_json)
    red_data = async_redact_data(data, TO_REDACT_DATA)
    diagnostic_data["snapshots"] = red_data
    red_list = []
    for activity in device._activities:
        red_data = async_redact_data(activity, TO_REDACT_DATA)
        red_list.append(red_data)
    diagnostic_data["activities"] = red_list

    return diagnostic_data


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: SkybellConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    known_devices = config_entry.runtime_data.known_device_ids
    current_devices = config_entry.runtime_data.current_device_ids
    api: Skybell = cast(Skybell, config_entry.runtime_data.api)
    dcs = config_entry.runtime_data.device_coordinators

    info: dict[str, Any] = {}
    info["known_device_ids"] = known_devices
    info["current_device_ids"] = current_devices
    api_info: dict[str, Any] = {}
    api_info["session_refresh_timestamp"] = api.session_refresh_timestamp
    api_info["session_refresh_period"] = api.session_refresh_period
    api_info["user"] = api._user
    info["api"] = api_info

    devices = {}
    for dc in dcs:
        device = device_to_dict(dc.device)
        devices[dc.device.device_id] = device

    diagnostics_data = {
        "info": async_redact_data(info, TO_REDACT_INFO),
        "devices": devices,
    }

    return diagnostics_data


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: SkybellConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    dcs = config_entry.runtime_data.device_coordinators
    devices = []
    for dc in dcs:
        devices.append(dc.device)

    # Get the device specific information
    diag_device = None
    for my_device in devices:
        for identifier in device.identifiers:
            if identifier[1] == my_device.device_id:
                diag_device = my_device
                break

    if diag_device is not None:
        diag_device = device_to_dict(cast(SkybellDevice, diag_device))
    diagnostics_data = {"device": diag_device}

    return diagnostics_data
