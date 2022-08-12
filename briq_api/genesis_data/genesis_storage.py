import logging

from ..storage.multi_backend_client import StorageClient
from ..storage.file.file_client import FileStorageBackend

logger = logging.getLogger(__name__)


class GenesisBackend():
    def __init__(self, file_storage: FileStorageBackend) -> None:
        self._storage = file_storage
        self.box_data = file_storage.load_json("box_spec.json")
        self.auction_data = file_storage.load_json("auction_spec.json")

    def get_box_data(self):
        return self.box_data

    def get_auction_data(self):
        return self.auction_data


class GenesisStorage(StorageClient[GenesisBackend]):

    def connect(self, backend):
        if backend:
            backend = GenesisBackend(backend)
        return super().connect(backend)

    def get_box_token_id(self, chain_id: str, box_id: str):
        return self.get_backend(chain_id).get_box_data()[box_id]

    def get_auction_id(self, chain_id: str, box_id: str):
        return list(self.get_backend(chain_id).get_auction_data().keys()).index(box_id)
