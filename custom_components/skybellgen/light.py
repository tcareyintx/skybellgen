"""Light/LED support for the SkyBell Gen Doorbell."""

from __future__ import annotations

from typing import Any, cast

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DEFAULT_BRIGHTNESS, DEFAULT_LED_COLOR, DOMAIN
from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity

LIGHT_TYPES: tuple[LightEntityDescription, ...] = (
    LightEntityDescription(
        key="light",
        translation_key="button_light",
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
    """Set up SkyBell entity."""

    known_device_ids: set[str] = set()

    def _check_device() -> None:
        entities = []
        new_device_ids: set[str] = set()
        for entity in LIGHT_TYPES:
            for coordinator in entry.runtime_data.device_coordinators:
                if not isinstance(coordinator, SkybellDeviceDataUpdateCoordinator):
                    continue
                if (coordinator.device.device_id not in known_device_ids) and (
                    (not coordinator.device.is_readonly)
                    or (
                        coordinator.device.is_readonly
                        and entity.key in CONST.ACL_EXCLUSIONS
                    )
                ):
                    new_device_ids.add(coordinator.device.device_id)
                    entities.append(SkybellLight(coordinator, entity))
        if entities:
            known_device_ids.update(new_device_ids)
            async_add_entities(entities)

    _check_device()

    entry.async_on_unload(
        entry.runtime_data.hub_coordinator.async_add_listener(_check_device)
    )


class SkybellLight(SkybellEntity, LightEntity):
    """A light implementation for SkyBell devices."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
        description: LightEntityDescription,
    ) -> None:
        """Initialize a light entity for a SkyBell device."""
        super().__init__(coordinator, description)
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_name = "Button LED"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        current_color: tuple[int, int, int] | None = None
        brightness = self.brightness
        current_color = self.rgb_color
        if current_color is None:
            current_color = DEFAULT_LED_COLOR

        if ATTR_RGB_COLOR in kwargs:
            current_color = kwargs[ATTR_RGB_COLOR]
            if brightness == 0:
                current_color = None  # pragma: no cover
        elif ATTR_BRIGHTNESS in kwargs:
            return  # pragma: no cover

        # Update the adjusted color
        rgb_value = ""
        if current_color is not None:
            rgb_value = (
                f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}"
            )
        try:
            await self._device.async_set_setting(CONST.LED_COLOR, rgb_value)
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
                    "key": CONST.LED_COLOR,
                    "value": rgb_value,
                },
            ) from exc

        # To stop bouncing issue a refresh
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        # We need to set the LED Color to a RGB value
        hex_color = ""
        try:
            await self._device.async_set_setting(CONST.LED_COLOR, hex_color)
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
                    "key": CONST.LED_COLOR,
                    "value": hex_color,
                },
            ) from exc

        # To stop bouncing issue a refresh
        await self.coordinator.async_refresh()

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._device.normal_led_is_on

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the led color value (int, int, int)."""
        if not self.is_on:
            return super().rgb_color

        hex_color = self._device.led_color
        int_array = [int(hex_color[i : i + 2], 16) for i in range(1, len(hex_color), 2)]
        return cast(tuple[int, int, int], tuple(int_array))

    @property
    def brightness(self) -> int | None:
        """Return the brightness."""
        brightness = super().brightness
        if brightness is None:
            brightness = DEFAULT_BRIGHTNESS
        return brightness
