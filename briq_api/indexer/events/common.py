from starknet_py.contract import FunctionCallSerializer
from typing import List, NamedTuple

uint256_abi = {
    "name": "Uint256",
    "type": "struct",
    "size": 2,
    "members": [
        {"name": "low", "offset": 0, "type": "felt"},
        {"name": "high", "offset": 1, "type": "felt"},
    ],
}


def decode_event(decoder: FunctionCallSerializer, data: List[bytes]) -> NamedTuple:
    data = [int.from_bytes(b, "big") for b in data]
    return decoder.to_python(data)


def encode_int_as_bytes(n: int) -> bytes:
    """Encode an integer to bytes so that it can be stored in a db."""
    return n.to_bytes(32, "big")

