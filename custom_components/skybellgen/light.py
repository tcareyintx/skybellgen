"""Light/LED support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import (
    SkybellAccessControlException,
    SkybellException,
)
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
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)
from typing import Any

from .const import DEFAULT_BRIGHTNESS, DEFAULT_LED_COLOR, DOMAIN
from .coordinator import SkybellDataUpdateCoordinator
from .entity import SkybellEntity


LIGHT_TYPES: tuple[LightEntityDescription, ...] = (
    LightEntityDescription(
        key="light",
        translation_key="button_light",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell entity."""
    async_add_entities(
        SkybellLight(coordinator, description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for description in LIGHT_TYPES
        if (
            (not coordinator.device.is_readonly)
            or (
                coordinator.device.is_readonly
                and description.key in CONST.ACL_EXCLUSIONS
            )
        )
    )


class SkybellLight(SkybellEntity, LightEntity):
    """A light implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDataUpdateCoordinator,
        description: LightEntityDescription,
    ) -> None:
        """Initialize a light entity for a Skybell device."""
        super().__init__(coordinator, description)
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_name = "Button LED"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = self.brightness
        current_color = self.rgb_color
        if current_color is None:
            current_color = DEFAULT_LED_COLOR
        else:
            current_color = list(current_color)

        if ATTR_RGB_COLOR in kwargs:
            current_color = list(kwargs[ATTR_RGB_COLOR])
            if brightness == 0:
                current_color = []
        elif ATTR_BRIGHTNESS in kwargs:
            return

        # Update the adjusted color
        rgb_value = ""
        if len(current_color) > 0:
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
        await self._device.async_set_setting(CONST.LED_COLOR, hex_color)
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
        return tuple(int_array)

    @property
    def brightness(self) -> int | None:
        """Return the brightness."""
        brightness = super().brightness
        if brightness is None:
            brightness = DEFAULT_BRIGHTNESS
        return brightness
