"""Test SkyBellGen camera."""

# Note that the camera entity cannot be tested because of
# the import error with turbojpeg in the test environment.

import pytest

from custom_components.skybellgen.kvs import KVSEndpointData, parse_kvs_response

from .conftest import get_livestream


async def test_kvs(
    hass,
):
    """Test kvs services parser."""
    data = get_livestream()
    kvs_ep: KVSEndpointData = parse_kvs_response(data, "frontdoor")

    assert kvs_ep.region == "us-east-2"
    assert (
        kvs_ep.channel_arn
        == "arn:aws:kinesisvideo:us-east-2:"
        + "someotherstuff:channel/channel_id/client_id"
    )
    assert kvs_ep.service == "kinesisvideo"
    assert kvs_ep.channel_id == "channel_id"
    assert kvs_ep.client_id == "client_id"
    assert kvs_ep.ws_endpoint == "wss://kinesisvideo.us-east-2.amazonaws.com"
    assert kvs_ep.ice_servers.startswith(
        '[{"urls":"stun:stun.kinesisvideo.'
        + 'us-east-2.amazonaws.com:443"},{"credential":"a'
    )
    assert kvs_ep.access_key.startswith("keyid")
    assert kvs_ep.secret_key.startswith("key")
    assert kvs_ep.session_token.startswith("longtoken")
    assert kvs_ep.expiration.startswith("2025-07-")


async def test_kvs_exc(
    hass,
):
    """Test kvs services parser for exception."""
    data = get_livestream(nows=True)

    with pytest.raises(ValueError):
        assert parse_kvs_response(data, "frontdoor")
