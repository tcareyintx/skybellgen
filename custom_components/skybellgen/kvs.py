"""AWS Kinesis WebRTC support for the SkyBell Gen Doorbell cameras."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging

from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

_LOGGER = logging.getLogger(__name__)


@dataclass
class KVSEndpointData:  # pylint: disable=too-many-instance-attributes
    """Data for KVS endpoint."""

    service: str = ""
    region: str = ""
    ws_endpoint: str = ""
    signed_ws_endpoint: str = ""
    channel_arn: str = ""
    channel_id: str = ""
    client_id: str = ""
    ice_servers: str = ""
    access_key: str = ""
    secret_key: str = ""
    session_token: str = ""
    expiration: str = ""


def sign_ws_endpoint(kvs_endpoint: KVSEndpointData) -> str:
    """Return the signed websocket endpoint."""

    auth_credentials = Credentials(
        access_key=kvs_endpoint.access_key,
        secret_key=kvs_endpoint.secret_key,
        token=kvs_endpoint.session_token,
    )
    sigv4 = SigV4QueryAuth(
        auth_credentials, kvs_endpoint.service, kvs_endpoint.region, 299
    )
    aws_request = AWSRequest(
        method="GET",
        url=kvs_endpoint.ws_endpoint,
        params={
            "X-Amz-ChannelARN": kvs_endpoint.channel_arn,
            "X-Amz-ClientId": kvs_endpoint.client_id,
        },
    )
    sigv4.add_auth(aws_request)
    prepared_request = aws_request.prepare()

    url = prepared_request.url
    _LOGGER.debug("WSS Endpoint: %s", url)

    return url


def parse_kvs_response(data: dict, device: str) -> KVSEndpointData:
    """Parse the Livestream KVS response into KVSEndpointData."""

    kvs_endpoint = KVSEndpointData()
    kvs_endpoint.region = data["aws_region"]

    # parse the channel ARN
    kvs_endpoint.channel_arn = data["channelARN"]
    _LOGGER.debug(
        "Livestream Channel ARN for %s is %s", device, kvs_endpoint.channel_arn
    )
    channel_arn = kvs_endpoint.channel_arn.split(":")
    assert channel_arn[0] == "arn"
    assert channel_arn[1] == "aws"
    assert channel_arn[2] == "kinesisvideo"

    kvs_endpoint.service = channel_arn[2]
    channel_parts = channel_arn[-1].split("/")
    assert channel_parts[0] == "channel"

    kvs_endpoint.channel_id = channel_parts[1]
    kvs_endpoint.client_id = channel_parts[2]

    # get the ICE servers
    kvs_endpoint.ice_servers = json.dumps(data["ice"], separators=(",", ":"))
    _LOGGER.debug(
        "Livestream ICE Servers for %s is %s", device, kvs_endpoint.ice_servers
    )

    # credentials and expiration
    credentials = data["credentials"]
    kvs_endpoint.expiration = credentials["Expiration"]
    expiration_ts = datetime.fromisoformat(kvs_endpoint.expiration)
    time_offset = expiration_ts - datetime.now(tz=timezone.utc)
    expiration_period = int(time_offset.total_seconds())
    _LOGGER.debug(
        "Livestream expiration period for %s is %d seconds", device, expiration_period
    )
    kvs_endpoint.access_key = credentials["AccessKeyId"]
    kvs_endpoint.secret_key = credentials["SecretAccessKey"]
    kvs_endpoint.session_token = credentials["SessionToken"]

    # get the ws endpoint
    kvs_endpoint.ws_endpoint = ""
    endpoints = data["endpoints"]
    for endpoint in endpoints:
        if endpoint["Protocol"] == "WSS":
            kvs_endpoint.ws_endpoint = endpoint["ResourceEndpoint"]
            break

    if not kvs_endpoint.ws_endpoint:
        raise ValueError("No WS endpoint found in KVS response")

    # get the signed ws endpoint
    kvs_endpoint.signed_ws_endpoint = data["signedWSS"]
    signed_url = sign_ws_endpoint(kvs_endpoint)
    if signed_url != kvs_endpoint.ws_endpoint:
        _LOGGER.debug("Signed url is different than WSS endpoint. Using signed url.")
        kvs_endpoint.signed_ws_endpoint = signed_url

    return kvs_endpoint
