import logging

from ..storage.multi_backend_client import StorageClient
from ..storage.file.file_client import FileStorageBackend

logger = logging.getLogger(__name__)

GENESIS_COLLECTION_ID = 1

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
        if backend is None:
            raise Exception("GenesisStorage must have a valid backend")
        backend = GenesisBackend(backend)
        return super().connect(backend)

    def get_box_token_id(self, chain_id: str, box_id: str):
        return self.get_backend(chain_id).get_box_data()[box_id]

    def get_booklet_token_id(self, chain_id: str, box_id: str):
        return str(int(self.get_backend(chain_id).get_box_data()[box_id]) * 2**192 + GENESIS_COLLECTION_ID)

    def get_box_id(self, chain_id: str, box_token_id: str) -> str:
        box_data = self.get_backend(chain_id).get_box_data()
        try:
            return [box_name for box_name in box_data if box_data[box_name] == int(box_token_id, 16)][0]
        except:
            return None

    def get_booklet_id(self, chain_id: str, booklet_token_id: str):
        return self.get_box_id(chain_id, hex(int((int(booklet_token_id, 16) - GENESIS_COLLECTION_ID) / 2**192)))

    def get_auction_id(self, chain_id: str, box_id: str):
        return list(self.get_backend(chain_id).get_auction_data().keys()).index(box_id)

    def get_auction_static_data(self, chain_id: str, box_id: str):
        data = self.get_backend(chain_id).get_auction_data()[box_id]
        return {
            "total_quantity": data['quantity'],
            "wave": data['wave'] if 'wave' in data else None,
            "auction_start": data['auction_start'],
            "auction_duration": data['auction_duration'],
            # Pass as string since this is in WEI
            "initial_price": str(data['initial_price']),
        }
