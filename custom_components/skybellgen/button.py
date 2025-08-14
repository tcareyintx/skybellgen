"""Button support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
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
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity

BUTTON_TYPES: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="device_reboot",
        translation_key="device_reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# Calls to the communications driver should be serialized
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell entity."""

    known_device_ids: set[str] = set()

    def _check_device() -> None:
        entities = []
        new_device_ids: set[str] = set()
        for entity in BUTTON_TYPES:
            for coordinator in entry.runtime_data.device_coordinators:
                if (coordinator.device.device_id not in known_device_ids) and (
                    (not coordinator.device.is_readonly)
                    or (
                        coordinator.device.is_readonly
                        and entity.key in CONST.ACL_EXCLUSIONS
                    )
                ):
                    new_device_ids.add(coordinator.device.device_id)
                    entities.append(SkybellButton(coordinator, entity))
        if entities:
            known_device_ids.update(new_device_ids)
            async_add_entities(entities)

    _check_device()

    entry.async_on_unload(
        entry.runtime_data.hub_coordinator.async_add_listener(_check_device)
    )


class SkybellButton(SkybellEntity, ButtonEntity):
    """A button implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
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
                        "error": str(exc),
                    },
                ) from exc
