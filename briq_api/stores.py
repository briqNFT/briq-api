import logging

from .chain.networks import TESTNET, TESTNET_LEGACY

from briq_api.genesis_data.genesis_storage import GenesisStorage
from briq_api.storage.file.backends.cloud_storage import CloudStorage
from briq_api.storage.file.backends.file_storage import FileStorage
from briq_api.storage.file.backends.legacy_cloud_storage import LegacyCloudStorage
from .storage.file.file_client import FileClient

logger = logging.getLogger(__name__)

file_storage = FileClient()
genesis_storage = GenesisStorage()


def setup_stores(local: bool, use_mock_chain: bool):
    if not local:
        logger.info("Connecting normally.")
        file_storage.connect_for_chain(chain_id=TESTNET.id, backend=CloudStorage('briq-bucket-test-1'))
        file_storage.connect_for_chain(TESTNET_LEGACY.id, LegacyCloudStorage())
        # For now connect genesis storage to local files regardless
        genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))
    else:
        # Don't attempt connecting to the cloud in that mode,
        # we expect to run locally and it makes it faster to reload the API
        logger.info("Connecting locally.")
        file_storage.connect(FileStorage())
        # TODO: change this
        genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))

    if use_mock_chain:
        logger.info("Connecting for mock chain.")
        mock_storage = FileStorage()
        # Add an artificial slowdown
        mock_storage.slowdown = 0.2
        file_storage.connect_for_chain('mock', mock_storage)
