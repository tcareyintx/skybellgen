"""Button support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import (
    SkybellAccessControlException,
    SkybellException,
)
from aioskybellgen.helpers import const as CONST

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import SkybellDataUpdateCoordinator
from .entity import SkybellEntity

BUTTON_TYPES: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="device_reboot",
        translation_key="device_reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell entity."""
    async_add_entities(
        SkybellButton(coordinator, description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for description in BUTTON_TYPES
        if (
            (not coordinator.device.is_readonly)
            or (
                coordinator.device.is_readonly
                and description.key in CONST.ACL_EXCLUSIONS
            )
        )
    )


class SkybellButton(SkybellEntity, ButtonEntity):
    """A button implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize a entity for a Skybell device."""
        super().__init__(coordinator, description)

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "device_reboot":
            try:
                await self._device.async_reboot_device()
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
                    translation_key="reboot_failed",
                    translation_placeholders={
                        "key": self.entity_description.key,
                        "error": exc,
                    },
                ) from exc
