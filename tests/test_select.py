"""Test SkybellGen select."""

from homeassistant.components.select import (
    ATTR_OPTION,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.entity_registry as er
import pytest

from .conftest import async_init_integration

SELECT = Platform.SELECT

TEST_ENTITIES = [
    ["select.frontdoor_outdoor_chime_volume", "High", "Low"],
    ["select.frontdoor_speaker_volume", "Medium", "Low"],
    ["select.frontdoor_image_quality", "Low", "High"],
]


async def test_select_service(hass, remove_platforms, bypass_initialize):
    """Test select services."""
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
            ATTR_OPTION: expected_value,
        }

        await hass.services.async_call(
            SELECT_DOMAIN, SERVICE_SELECT_OPTION, attr, blocking=True
        )


async def test_select_exc(
    hass, remove_platforms, bypass_initialize, error_set_setting_exc
):
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
        ATTR_OPTION: TEST_ENTITIES[0][2],
    }

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SELECT_DOMAIN, SERVICE_SELECT_OPTION, attr, blocking=True
        )


async def test_select_acl(
    hass, remove_platforms, bypass_initialize, error_set_setting_acl
):
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
        ATTR_OPTION: TEST_ENTITIES[0][2],
    }

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SELECT_DOMAIN, SERVICE_SELECT_OPTION, attr, blocking=True
        )


async def test_select_no_option_for_key(hass, remove_platforms, bypass_initialize3):
    """Test switch services with ACL exception."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get an entity
    entity_registry = er.async_get(hass)
    entity_id = TEST_ENTITIES[2][0]  # This is the image quality select
    assert entity_registry.async_get(entity_id) is not None

    # Assert the state
    state = hass.states.get(entity_id)
    assert (
        state is None
    )  # The state should not be set since the image quality is not valid from device.json3

    attr = {
        ATTR_ENTITY_ID: entity_id,
        ATTR_OPTION: "The very highest",  # This is not a valid option for image quality
    }

    with pytest.raises(ServiceValidationError):
        assert await hass.services.async_call(
            SELECT_DOMAIN, SERVICE_SELECT_OPTION, attr, blocking=True
        )
