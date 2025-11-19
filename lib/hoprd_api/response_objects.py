from dataclasses import fields
from typing import Any

from api_lib.objects.response import (
    APIfield,
    APImetric,
    APIobject,
    JsonResponse,
    MetricResponse,
)

from .balance import Balance
from .channelstatus import ChannelStatus


def try_to_lower(value: Any):
    if isinstance(value, str):
        return value.lower()
    return value


@APIobject
class Addresses(JsonResponse):
    native: str


@APIobject
class Balances(JsonResponse):
    hopr: Balance
    native: Balance
    safe_native: Balance = APIfield("safeNative")
    safe_hopr: Balance = APIfield("safeHopr")


@APIobject
class Infos(JsonResponse):
    hopr_node_safe: str = APIfield("hoprNodeSafe")

    def post_init(self):
        self.hopr_node_safe = try_to_lower(self.hopr_node_safe)


@APIobject
class ConnectedPeer(JsonResponse):
    address: str
    multiaddr: str

    def post_init(self):
        self.address = try_to_lower(self.address)


@APIobject
class Channel(JsonResponse):
    balance: Balance
    id: str = APIfield("channelId")
    destination: str
    source: str
    status: ChannelStatus

    def post_init(self):
        self.destination = try_to_lower(self.destination)
        self.source = try_to_lower(self.source)


@APIobject
class OwnChannel(JsonResponse):
    id: str
    peer_address: str = APIfield("peerAddress")
    status: ChannelStatus
    balance: Balance


@APIobject
class TicketPrice(JsonResponse):
    value: Balance = APIfield("price")


@APIobject
class Configuration(JsonResponse):
    price: Balance = APIfield("hopr/protocol/outgoing_ticket_price")


@APIobject
class OpenedChannel(JsonResponse):
    channel_id: str = APIfield("channelId")
    receipt: str = APIfield("transactionReceipt", "")


@APIobject
class Metrics(MetricResponse):
    hopr_tickets_incoming_statistics: dict = APImetric(["statistic"])
    hopr_packets_count: dict = APImetric(["type"])


class Channels:
    def __init__(self, data: dict):
        self.all = [Channel(c) for c in data.get("all", [])]
        self.incoming = [OwnChannel(c) for c in data.get("incoming", [])]
        self.outgoing = [OwnChannel(c) for c in data.get("outgoing", [])]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


@APIobject
class Session(JsonResponse):
    """
    Represents an active UDP session for message relay to a peer.

    A Session encapsulates both the API-level session state and the local UDP socket
    connection used for sending/receiving messages. Sessions have a lifecycle managed
    by SessionMixin with a 60-second grace period before closure.

    Attributes:
        ip (str): IP address for socket connection (usually "127.0.0.1")
        port (int): UDP port assigned by the HOPR node API
        protocol (str): Protocol type (typically "udp")
        target (str): Peer address this session relays to
        mtu (int): Maximum transmission unit from HOPR protocol
        surb_size (int): Size of SURB (Single Use Reply Block) overhead
        socket (Optional[socket]): Local UDP socket, None if closed

    Properties:
        payload (int): Usable payload size = mtu - surb_size
        as_path (str): API path for this session
        as_dict (dict): Dictionary representation of session state

    Thread Safety:
        Socket operations are NOT thread-safe. However, this is safe in the current
        design because asyncio runs in a single thread and we avoid concurrent access
        through the snapshot pattern in maintain_sessions().

    Lifecycle:
        1. Created via NodeHelper.open_session() (API call)
        2. Socket created via create_socket()
        3. Used for send/receive operations
        4. Closed via close_socket() when peer unreachable or node stopping
        5. Removed from API via NodeHelper.close_session()
    """

    ip: str
    port: int
    protocol: str
    target: str
    mtu: int = APIfield("hoprMtu")
    surb_size: int = APIfield("surbLen")

    @property
    def payload(self):
        """
        Calculate usable payload size for messages.

        Returns:
            int: Maximum bytes available for message data (mtu - surb_size)
        """
        return self.mtu - self.surb_size

    @property
    def as_path(self):
        """
        Generate API path for this session.

        Returns:
            str: Path like "/session/udp/127.0.0.1/9001"
        """
        return f"/session/{self.protocol}/{self.ip}/{self.port}"

    @property
    def as_dict(self) -> dict:
        """
        Convert session to dictionary representation.

        Returns:
            dict: All session fields as strings
        """
        return {key: str(getattr(self, key)) for key in [f.name for f in fields(self)]}

@APIobject
class SessionFailure(JsonResponse):
    status: str = APIfield("status")
    error: str = APIfield("error")
    destination: str = APIfield("destination", "")
    relayer: str = APIfield("relayer", "")
    relayer: str = APIfield("relayer", "")
    relayer: str = APIfield("relayer", "")
