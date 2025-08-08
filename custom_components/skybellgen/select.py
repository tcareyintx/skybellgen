"""Select support for the Skybell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, IMAGE_FIELDS, IMAGE_OPTIONS, VOLUME_FIELDS, VOLUME_OPTIONS
from .coordinator import SkybellDataUpdateCoordinator
from .entity import SkybellEntity

SELECT_TYPES: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key=CONST.OUTDOOR_CHIME_VOLUME,
        translation_key=CONST.OUTDOOR_CHIME_VOLUME,
        entity_category=EntityCategory.CONFIG,
        options=VOLUME_OPTIONS,
    ),
    SelectEntityDescription(
        key=CONST.SPEAKER_VOLUME,
        translation_key=CONST.SPEAKER_VOLUME,
        entity_category=EntityCategory.CONFIG,
        options=VOLUME_OPTIONS,
    ),
    SelectEntityDescription(
        key=CONST.IMAGE_QUALITY,
        translation_key=CONST.IMAGE_QUALITY,
        entity_category=EntityCategory.CONFIG,
        options=IMAGE_OPTIONS,
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
    async_add_entities(
        SkybellSelect(coordinator, description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for description in SELECT_TYPES
        if (
            (not coordinator.device.is_readonly)
            or (
                coordinator.device.is_readonly
                and description.key in CONST.ACL_EXCLUSIONS
            )
        )
    )


class SkybellSelect(SkybellEntity, SelectEntity):
    """A select implementation for Skybell devices."""

    def __init__(
        self,
        coordinator: SkybellDataUpdateCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize a entity for a Skybell device."""
        super().__init__(coordinator, description)

    async def async_select_option(self, option: str) -> None:
        """Set the value of the option."""
        array_options = None
        if self.entity_description.key in VOLUME_FIELDS:
            array_options = VOLUME_OPTIONS
        elif self.entity_description.key in IMAGE_FIELDS:
            array_options = IMAGE_OPTIONS

        if array_options is None:
            raise ServiceValidationError(  # pragma: no cover
                translation_domain=DOMAIN,
                translation_key="no_options_list_for_key",
                translation_placeholders={
                    "key": self.entity_description.key,
                },
            )
        try:
            value = array_options.index(option)
        except (IndexError, ValueError) as exc:  # pragma: no cover
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_option_for_key",
                translation_placeholders={
                    "key": self.entity_description.key,
                    "option": option,
                },
            ) from exc

        try:
            await self._device.async_set_setting(self.entity_description.key, value)
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
                    "value": str(value),
                },
            ) from exc

    def _handle_coordinator_update(self) -> None:
        value_fn = getattr(self._device, self.entity_description.key)
        index = value_fn
        array_options = None
        if self.entity_description.key in VOLUME_FIELDS:
            array_options = VOLUME_OPTIONS
        elif self.entity_description.key in IMAGE_FIELDS:
            array_options = IMAGE_OPTIONS

        if array_options is None:
            raise ServiceValidationError(  # pragma: no cover
                translation_domain=DOMAIN,
                translation_key="no_options_list_for_key",
                translation_placeholders={
                    "key": self.entity_description.key,
                },
            )
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

        self._attr_current_option = value
        super()._handle_coordinator_update()
