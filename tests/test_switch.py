"""Test SkybellGen switch."""

from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)

from homeassistant.const import Platform, STATE_OFF, STATE_ON, ATTR_ENTITY_ID
from homeassistant.config_entries import ConfigEntryState
import homeassistant.helpers.entity_registry as er

from .conftest import async_init_integration

SWITCH = Platform.SWITCH


async def test_switch(hass, remove_platforms):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get a switch entity for detecting motion (set to on)
    entity_registry = er.async_get(hass)
    entity_id = "switch.frontdoor_detect_motion"
    assert entity_registry.async_get(entity_id) is not None

    # Turn off the switch
    state = hass.states.get(entity_id)
    assert state.state == STATE_ON

    """
    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    """
