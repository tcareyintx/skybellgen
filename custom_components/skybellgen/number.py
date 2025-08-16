"""Number support for the SkyBell Gen Doorbell."""

from __future__ import annotations

from aioskybellgen.exceptions import SkybellAccessControlException, SkybellException
from aioskybellgen.helpers import const as CONST
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, SENTSITIVTY_ADJ, TENTH_PERCENT_TYPES, USE_MOTION_VALUE
from .coordinator import SkybellDeviceDataUpdateCoordinator
from .entity import SkybellEntity

NUMBER_TYPES: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key=CONST.MOTION_SENSITIVITY,
        translation_key=CONST.MOTION_SENSITIVITY,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=1000,
        native_step=0.1,
    ),
    NumberEntityDescription(
        key=CONST.MOTION_HMBD_SENSITIVITY,
        translation_key=CONST.MOTION_HMBD_SENSITIVITY,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
    ),
    NumberEntityDescription(
        key=CONST.MOTION_FD_SENSITIVITY,
        translation_key=CONST.MOTION_FD_SENSITIVITY,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
    ),
    NumberEntityDescription(
        key=CONST.MOTION_PIR_SENSITIVITY,
        translation_key=CONST.MOTION_PIR_SENSITIVITY,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=100,
        native_step=0.1,
    ),
    NumberEntityDescription(
        key="location_lat",
        translation_key="location_lat",
        entity_category=EntityCategory.CONFIG,
        native_min_value=-90.0,
        native_max_value=90.0,
        native_step=0.00001,
    ),
    NumberEntityDescription(
        key="location_lon",
        translation_key="location_lon",
        entity_category=EntityCategory.CONFIG,
        native_min_value=-180.0,
        native_max_value=180.0,
        native_step=0.00001,
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
        for entity in NUMBER_TYPES:
            for coordinator in entry.runtime_data.device_coordinators:
                if (coordinator.device.device_id not in known_device_ids) and (
                    (not coordinator.device.is_readonly)
                    or (
                        coordinator.device.is_readonly
                        and entity.key in CONST.ACL_EXCLUSIONS
                    )
                ):
                    new_device_ids.add(coordinator.device.device_id)
                    entities.append(SkybellNumber(coordinator, entity))
        if entities:
            known_device_ids.update(new_device_ids)
            async_add_entities(entities)

    _check_device()

    entry.async_on_unload(
        entry.runtime_data.hub_coordinator.async_add_listener(_check_device)
    )


class SkybellNumber(SkybellEntity, NumberEntity):
    """A number implementation for SkyBell devices."""

    def __init__(
        self,
        coordinator: SkybellDeviceDataUpdateCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize a entity for a SkyBell device."""
        super().__init__(coordinator, description)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the text."""
        key = self.entity_description.key
        if key == "location_lat":
            key = CONST.LOCATION_LAT
        if key == "location_lon":
            key = CONST.LOCATION_LON
        if key in TENTH_PERCENT_TYPES:
            # Check for values 0,1,2 adjust for use motion low medium high
            if value >= 0 and value <= len(SENTSITIVTY_ADJ):
                value = SENTSITIVTY_ADJ[int(value)]
            value = int(value * 10)
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
                translation_key="motion_invalid_setting",
                translation_placeholders={
                    "key": key,
                    "value": str(value),
                },
            ) from exc

        self._attr_native_value = value

    def _handle_coordinator_update(self) -> None:
        value_fn = getattr(self._device, self.entity_description.key)
        value = value_fn
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
            self._attr_native_value = float(value / 10)
        else:
            self._attr_native_value = value
        super()._handle_coordinator_update()
