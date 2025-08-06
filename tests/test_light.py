"""Test SkybellGen light."""

from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, Platform
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er
import pytest

from .conftest import async_init_integration

LIGHT = Platform.LIGHT

TEST_ENTITY = "light.frontdoor_button_led"


async def test_light_off(hass, remove_platforms, bypass_initialize):
    """Test light services with the original off."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off
    state = hass.states.get(entity_id)
    assert state.state == STATE_OFF

    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )

    # Turn on
    rgb = (0, 255, 0)
    attrs = {ATTR_ENTITY_ID: entity_id, ATTR_RGB_COLOR: rgb}
    await hass.services.async_call(LIGHT_DOMAIN, SERVICE_TURN_ON, attrs, blocking=True)


async def test_light_on(hass, remove_platforms, bypass_initialize2):
    """Test light services from orignal state of on."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )

    # Turn on
    rgb = (0, 255, 0)
    attrs = {ATTR_ENTITY_ID: entity_id, ATTR_RGB_COLOR: rgb}
    await hass.services.async_call(LIGHT_DOMAIN, SERVICE_TURN_ON, attrs, blocking=True)


async def test_light_exc(
    hass, remove_platforms, bypass_initialize, error_set_setting_exc
):
    """Test services with Skybell exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off
    state = hass.states.get(entity_id)
    assert state.state == STATE_OFF

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )

    # Turn on
    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            LIGHT_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )


async def test_light_acl(
    hass, remove_platforms, bypass_initialize, error_set_setting_acl
):
    """Test services with ACL exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITY
    assert entity_registry.async_get(entity_id) is not None

    # Turn off
    state = hass.states.get(entity_id)
    assert state.state == STATE_OFF

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )

    # Turn on the switch
    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            LIGHT_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
        )
