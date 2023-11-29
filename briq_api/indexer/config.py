import os
from briq_api.chain.networks import get_network_metadata

NETWORK_NAME = os.getenv("NETWORK_NAME") or "starknet-testnet"
NETWORK = get_network_metadata(NETWORK_NAME)

INDEXER_ID = os.getenv("INDEXER_ID") or "localtest-0"

# TODO: proper secret management
MONGO_URL = os.getenv("MONGO_URL") or "localhost:27017"
MONGO_USERNAME = os.getenv("MONGO_USERNAME") or "apibara"
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD") or "apibara"

START_BLOCK = int(os.getenv("START_BLOCK") or {
    "starknet-testnet": 857000,
    "starknet-testnet-dojo": 910000,
    "starknet-testnet2": 3000,
    "starknet-mainnet": 10400,
    "starknet-mainnet-dojo": 445443,
}[NETWORK_NAME])

APIBARA_URL = os.getenv("APIBARA_URL") or {
    "starknet-testnet": "goerli.starknet.a5a.ch:443",
    "starknet-testnet-dojo": "goerli.starknet.a5a.ch:443",
    "starknet-testnet2": "goerli-2.starknet.a5a.ch",
    "starknet-mainnet": "mainnet.starknet.a5a.ch",
    "starknet-mainnet-dojo": "mainnet.starknet.a5a.ch",
}[NETWORK_NAME]

SET_INDEXER_URL = os.getenv("SET_INDEXER_URL")

AUTH_TOKEN = os.getenv("APIBARA_AUTH_TOKEN")
