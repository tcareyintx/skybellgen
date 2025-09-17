"""Test SkyBellGen button."""

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er
import pytest

from .conftest import async_init_integration

BUTTON = Platform.BUTTON

TEST_ENTITY = "button.frontdoor_reboot_doorbell"


async def test_button(
    hass,
    remove_platforms,
    bypass_get_devices,
):
    """Test button services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Press the button
    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )


async def test_button_exc(hass, remove_platforms, bypass_get_devices, error_reboot_exc):
    """Test services with SkyBell exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )


async def test_button_acl(hass, remove_platforms, bypass_get_devices, error_reboot_acl):
    """Test services with ACL exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )
