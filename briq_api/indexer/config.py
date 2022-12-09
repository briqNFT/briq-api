import os
from briq_api.chain.networks import get_network_metadata

NETWORK_NAME = os.getenv("NETWORK_NAME", "starknet-testnet")
NETWORK = get_network_metadata(NETWORK_NAME)

INDEXER_ID = os.getenv("INDEXER_ID", "testnet-test-3")

# TODO: proper secret management
MONGO_URL = os.getenv("MONGO_URL", "localhost:27017")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "apibara")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "apibara")

START_BLOCK = int(os.getenv("START_BLOCK", {
    "starknet-testnet": 3000,
    #"starknet-testnet": 424000,
    "starknet-mainnet": 10400,
}[NETWORK_NAME]))

APIBARA_URL = os.getenv("APIBARA_URL", {
    "starknet-testnet": "goerli-2.starknet.stream.apibara.com",
    #"starknet-testnet": "goerli.starknet.stream.apibara.com",
    "starknet-mainnet": "mainnet.starknet.stream.apibara.com",
}[NETWORK_NAME])

SET_INDEXER_URL = os.getenv("SET_INDEXER_URL", None)
