"""Test SkyBellGen switch."""

from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, STATE_ON, Platform
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er
import pytest

from .conftest import async_init_integration

SWITCH = Platform.SWITCH

TEST_ENTITY = "switch.frontdoor_detect_motion"


async def test_switch(hass, remove_platforms, bypass_get_devices):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get a switch entity for detecting motion (set to on)
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off the switch
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )

    # Turn on the switch
    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )


async def test_switch_exc(
    hass, remove_platforms, bypass_get_devices, error_set_setting_exc
):
    """Test switch services with SkyBell exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get a switch entity for detecting motion (set to on)
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off the switch
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )

    # Turn on the switch
    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )


async def test_switch_acl(
    hass, remove_platforms, bypass_get_devices, error_set_setting_acl
):
    """Test switch services with ACL exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get a switch entity for detecting motion (set to on)
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off the switch
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )

    # Turn on the switch
    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )
