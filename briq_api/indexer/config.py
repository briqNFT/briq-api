import os

INDEXER_ID = os.getenv("INDEXER_ID", "testnet-test-2")
# TODO: proper secret management
MONGO_URL = os.getenv("MONGO_URL", "localhost:27017")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "apibara")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "apibara")

NETWORK_NAME = os.getenv("NETWORK_NAME", "starknet-goerli")
START_BLOCK = int(os.getenv("START_BLOCK", 352_600))

APIBARA_URL = os.getenv("APIBARA_URL", "goerli.starknet.stream.apibara.com")
