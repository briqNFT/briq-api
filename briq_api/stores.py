import logging

from briq_api.config import ENV

from .chain.networks import MAINNET, TESTNET, TESTNET_LEGACY

from briq_api.genesis_data.genesis_storage import GenesisStorage
from briq_api.storage.file.backends.cloud_storage import CloudStorage
from briq_api.storage.file.backends.file_storage import FileStorage
from briq_api.storage.file.backends.legacy_cloud_storage import LegacyCloudStorage
from briq_api.indexer.storage import mongo_storage, MongoBackend
from .storage.file.file_client import FileClient

logger = logging.getLogger(__name__)

file_storage = FileClient()
genesis_storage = GenesisStorage()


def setup_stores(local: bool, use_mock_chain: bool):
    if not local:
        logger.info("Connecting normally.")
        # For now, starknet-testnet is connected to the test bucket only in test env.
        if ENV != 'prod':
            file_storage.connect_for_chain(TESTNET.id, backend=CloudStorage('briq-bucket-test-1'))
        file_storage.connect_for_chain(TESTNET_LEGACY.id, backend=LegacyCloudStorage('briq-bucket-prod-1'))
        file_storage.connect_for_chain(MAINNET.id, backend=CloudStorage('briq-bucket-prod-1'))

        if ENV != 'prod':
            mongo_storage.connect_for_chain(TESTNET.id, MongoBackend())
        else:
            mongo_storage.connect_for_chain(TESTNET.id, MongoBackend())

        if ENV != 'prod':
            genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))
        else:
            genesis_storage.connect(FileStorage("briq_api/genesis_data/mainnet/"))
    else:
        # Don't attempt connecting to the cloud in that mode,
        # we expect to run locally and it makes it faster to reload the API
        logger.info("Connecting locally.")
        file_storage.connect(FileStorage())
        # TODO: change this
        genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))
        mongo_storage.connect_for_chain(TESTNET.id, MongoBackend())

    if use_mock_chain:
        logger.info("Connecting for mock chain.")
        mock_storage = FileStorage()
        # Add an artificial slowdown
        mock_storage.slowdown = 0.2
        file_storage.connect_for_chain('mock', mock_storage)
