"""Test SkybellGen sensor."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
import homeassistant.helpers.entity_registry as er

from .conftest import async_init_integration

SENSOR = Platform.SENSOR

TEST_ENTITIES = [
    ["sensor.frontdoor_outdoor_chime_volume", "High"],
    ["sensor.frontdoor_speaker_volume", "Medium"],
    ["sensor.frontdoor_image_quality", "Low"],
    ["sensor.frontdoor_facial_detection_sensitivity", "53.4"],
    ["sensor.frontdoor_location_longitude", "-1.0"],
    ["sensor.frontdoor_human_detection_sensitivity", "50.0"],
]


async def test_sensor_service(hass, remove_platforms, bypass_get_devices):
    """Test sensor services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = await async_init_integration(hass)
    assert config_entry.state is ConfigEntryState.LOADED

    # Get the entity registry
    entity_registry = er.async_get(hass)

    # Loop through each test entity
    for entity in TEST_ENTITIES:
        entity_id, initial_state = entity
        assert entity_registry.async_get(entity_id) is not None

        # Assert the state
        state = hass.states.get(entity_id)
        assert state.state == initial_state


async def test_sensor_no_option_for_key(hass, remove_platforms, bypass_get_devices3):
    """Test sensor services with no options exception."""
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
