"""Text support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from homeassistant.components.text import TextEntity, TextEntityDescription, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import SkybellDataUpdateCoordinator
from .entity import SkybellEntity

TEXT_TYPES: tuple[TextEntityDescription, ...] = (
    TextEntityDescription(
        key=CONST.NAME,
        translation_key=CONST.NAME,
        entity_category=EntityCategory.CONFIG,
        mode=TextMode.TEXT,
        native_min=1,
        native_max=20,
    ),
    TextEntityDescription(
        key="location_place",
        translation_key="location_place",
        entity_category=EntityCategory.CONFIG,
        mode=TextMode.TEXT,
        native_min=1,
        native_max=40,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Skybell entity."""
    async_add_entities(
        SkybellText(coordinator, description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for description in TEXT_TYPES
        if (
            (not coordinator.device.is_readonly)
            or (
                coordinator.device.is_readonly
                and description.key in CONST.ACL_EXCLUSIONS
            )
        )
    )


class SkybellText(SkybellEntity, TextEntity):
    """A text implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDataUpdateCoordinator,
        description: TextEntityDescription,
    ) -> None:
        """Initialize a entity for a Skybell device."""
        super().__init__(coordinator, description)

    async def async_set_value(self, value: str) -> None:
        """Set the value of the text."""
        key = self.entity_description.key
        if key == "location_place":
            key = CONST.LOCATION_PLACE
        try:
            await self._device.async_set_setting(key, value)
        except SkybellAccessControlException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_permissions",
                translation_placeholders={
                    "key": key,
                },
            ) from exc
        except SkybellException as exc:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_setting",
                translation_placeholders={
                    "key": key,
                    "value": value,
                },
            ) from exc
        self._attr_native_value = value

    def _handle_coordinator_update(self) -> None:
        value_fn = getattr(self._device, self.entity_description.key)
        self._attr_native_value = str(value_fn)
        super()._handle_coordinator_update()
