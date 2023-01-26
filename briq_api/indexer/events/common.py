from abc import abstractmethod
from starknet_py.serialization import PayloadSerializer
from apibara.starknet import felt
from apibara.starknet.proto.starknet_pb2 import Event
from typing import Any, List, NamedTuple

from apibara.starknet import EventFilter, felt
from starkware.starknet.public.abi import get_selector_from_name
from starknet_py.serialization import serializer_for_event
from starknet_py.abi import AbiParser
from apibara.indexer import Info
from apibara.starknet.proto.starknet_pb2 import Block


class EventIndexer:
    contract_prefix: str
    filters: list[EventFilter]

    def __init__(self, contract_prefix: str, address: str) -> None:
        self.contract_prefix = contract_prefix
        self.address = address

    @abstractmethod
    async def process_transfers(self, data: Block, info: Info[Any, Any]):
        pass


uint256_abi = {
    "name": "Uint256",
    "type": "struct",
    "size": 2,
    "members": [
        {"name": "low", "offset": 0, "type": "felt"},
        {"name": "high", "offset": 1, "type": "felt"},
    ],
}


def get_event_filter(contract_address: str, name: str) -> EventFilter:
    transfer_key = felt.from_int(
        get_selector_from_name(name)
    )
    return EventFilter().with_from_address(felt.from_hex(contract_address)).with_keys([transfer_key])


def get_event_serializer(raw_abi: dict[str, Any], name: str) -> PayloadSerializer:
    abi = AbiParser([uint256_abi, raw_abi]).parse()
    return serializer_for_event(abi.events[name])


def decode_event(event_serializer: PayloadSerializer, event: Event) -> NamedTuple:
    return event_serializer.deserialize([felt.to_int(d) for d in event.data])


def encode_int_as_bytes(n: int) -> bytes:
    """Encode an integer to bytes so that it can be stored in a db."""
    return n.to_bytes(32, "big")


def decode_bytes(n: bytes) -> int:
    """Decode bytes to an integer."""
    return int.from_bytes(n, "big")
