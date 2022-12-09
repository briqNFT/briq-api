import os
from briq_api.chain.networks import get_network_metadata

NETWORK = get_network_metadata(os.getenv("NETWORK_NAME") or "starknet-testnet")
