"""Test SkybellGen number."""

import pytest

from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
    ATTR_VALUE
)

from homeassistant.const import Platform, ATTR_ENTITY_ID
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er

from .conftest import async_init_integration

NUMBER = Platform.NUMBER

TEST_ENTITIES = [
    ["number.frontdoor_facial_detection_sensitivity", "53.4", 50.0],
    ["number.frontdoor_location_latitude", "1.0", 1.0],
    ["number.frontdoor_location_longitude", "-1.0", 1.0],
    ["number.frontdoor_human_detection_sensitivity", "50.0", 1],
]


async def test_number_service(hass, remove_platforms, bypass_initialize):
    """Test number services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get the entity registry
    entity_registry = er.async_get(hass)

    # Loop through each test entity
    for entity in TEST_ENTITIES:
        entity_id, initial_state, expected_value = entity
        assert entity_registry.async_get(entity_id) is not None

        # Assert the state
        state = hass.states.get(entity_id)
        assert state.state == initial_state

        attr = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: expected_value,
        }

        await hass.services.async_call(
            NUMBER_DOMAIN, SERVICE_SET_VALUE, attr, blocking=True
        )


async def test_number_exc(hass, remove_platforms, bypass_initialize, error_set_setting_exc):
    """Test services with Skybell exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITIES[0][0]
    assert entity_registry.async_get(entity_id) is not None

    # Assert the state
    state = hass.states.get(entity_id)
    assert state.state == TEST_ENTITIES[0][1]

    attr = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: TEST_ENTITIES[0][2],
    }

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            NUMBER_DOMAIN, SERVICE_SET_VALUE, attr, blocking=True
        )


async def test_number_acl(hass, remove_platforms, bypass_initialize, error_set_setting_acl):
    """Test switch services with ACL exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITIES[0][0]
    assert entity_registry.async_get(entity_id) is not None

    # Assert the state
    state = hass.states.get(entity_id)
    assert state.state == TEST_ENTITIES[0][1]

    attr = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_VALUE: TEST_ENTITIES[0][2],
    }

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            NUMBER_DOMAIN, SERVICE_SET_VALUE, attr, blocking=True
        )
