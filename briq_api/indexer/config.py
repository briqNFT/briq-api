import os
from briq_api.chain.networks import get_network_metadata

INDEXER_ID = os.getenv("INDEXER_ID", "testnet-test-3")
# TODO: proper secret management
MONGO_URL = os.getenv("MONGO_URL", "localhost:27017")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "apibara")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "apibara")

START_BLOCK = int(os.getenv("START_BLOCK", 3000))

APIBARA_URL = {
    "starknet-testnet": "goerli-2.starknet.stream.apibara.com",
    "starknet-mainnet": "mainnet.starknet.stream.apibara.com",
}[os.getenv("NETWORK_NAME", "starknet-testnet")]

NETWORK = get_network_metadata(os.getenv("NETWORK_NAME", "starknet-testnet"))
