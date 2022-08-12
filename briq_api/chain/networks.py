

from dataclasses import dataclass


@dataclass
class NetworkMetadata:
    id: str


DEVNET = NetworkMetadata(id="localhost")

TESTNET = NetworkMetadata(id="starknet-testnet")

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy")
