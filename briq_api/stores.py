import logging
import os

from briq_api.config import ENV

from .chain.networks import MAINNET, TESTNET, TESTNET_LEGACY

from briq_api.genesis_data.genesis_storage import GenesisStorage
from briq_api.storage.file.backends.cloud_storage import CloudStorage
from briq_api.storage.file.backends.file_storage import FileStorage
from briq_api.storage.file.backends.legacy_cloud_storage import LegacyCloudStorage
from briq_api.indexer.storage import mongo_storage, MongoBackend
from .storage.file.file_client import FileClient

from briq_api.indexer.config import INDEXER_ID
from briq_api.memory_cache import CacheData
from briq_api.storage.file.file_client import FileStorageBackend
from briq_api.storage.multi_backend_client import StorageClient


logger = logging.getLogger(__name__)


class ThemeStorage(StorageClient[FileStorageBackend]):
    _spec = {}

    def __init__(self) -> None:
        super().__init__()

    @CacheData.memory_cache(lambda _self, chain_id: f'{chain_id}_booklet_spec', timeout=5 * 60)
    def get_booklet_spec(self, chain_id: str) -> dict[str, str]:
        if chain_id not in self._spec:
            self._spec[chain_id] = self.get_backend(chain_id).load_json("genesis_themes/booklet_spec.json")
        return self._spec[chain_id]


@CacheData.memory_cache(lambda chain_id, theme_id: f'{chain_id}_{theme_id}_auction_json_data', timeout=5 * 60)
def get_auction_json_data(chain_id: str, theme_id: str):
    if theme_id == 'ducks_everywhere':
        try:
            return file_storage.get_backend(chain_id).load_json(f"auctions/{theme_id}/auction_data.json")
        except Exception:
            # Ignore, we'll just return an empty dict
            return {}
    return {}


file_storage = FileClient()
genesis_storage = GenesisStorage()
theme_storage = ThemeStorage()


def setup_stores(local: bool, use_mock_chain: bool):
    if not local:
        logger.info("Connecting normally.")

        file_storage.connect_for_chain(TESTNET_LEGACY.id, backend=LegacyCloudStorage(TESTNET_LEGACY.storage_bucket))

        # For now, starknet-testnet is connected to the test bucket only in test env.
        if ENV != 'prod':
            cloud_storage = CloudStorage(os.getenv("CLOUD_STORAGE_BUCKET") or 'briq-bucket-test-1')
            file_storage.connect_for_chain(TESTNET.id, backend=cloud_storage)
            file_storage.connect_for_chain(MAINNET.id, backend=cloud_storage)
            theme_storage.connect_for_chain(TESTNET.id, backend=cloud_storage)
            theme_storage.connect_for_chain(MAINNET.id, backend=cloud_storage)
        else:
            cloud_storage = CloudStorage(MAINNET.storage_bucket)
            file_storage.connect_for_chain(MAINNET.id, backend=cloud_storage)
            theme_storage.connect_for_chain(MAINNET.id, backend=cloud_storage)

        if ENV != 'prod':
            mongo_storage.connect_for_chain(TESTNET.id, MongoBackend())
            mongo_storage.connect_for_chain(MAINNET.id, MongoBackend(db_name=INDEXER_ID.replace('-', '_') + '_mn'))
        else:
            mongo_storage.connect_for_chain(MAINNET.id, MongoBackend())

        if ENV != 'prod':
            genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))
        else:
            genesis_storage.connect(FileStorage("briq_api/genesis_data/mainnet/"))
    else:
        # Don't attempt connecting to the cloud in that mode,
        # we expect to run locally and it makes it faster to reload the API
        logger.info("Connecting locally.")
        file_storage.connect(FileStorage())
        theme_storage.connect(FileStorage())
        # TODO: change this
        genesis_storage.connect(FileStorage("briq_api/genesis_data/localhost/"))
        mongo_storage.connect(MongoBackend())

    if use_mock_chain:
        logger.info("Connecting for mock chain.")
        mock_storage = FileStorage()
        # Add an artificial slowdown
        mock_storage.slowdown = 0.2
        file_storage.connect_for_chain('mock', mock_storage)
