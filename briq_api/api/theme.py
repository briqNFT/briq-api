
from typing import Any, Union
from briq_api.api.auctions import get_auction_json_data
from briq_api.storage.file.file_client import FileStorageBackend
from briq_api.storage.multi_backend_client import StorageClient
from briq_api.stores import genesis_storage


class ThemeStorage(StorageClient[FileStorageBackend]):
    _spec = {}

    def __init__(self) -> None:
        super().__init__()

    def get_booklet_spec(self, chain_id: str):
        if chain_id not in self._spec:
            self._spec[chain_id] = self.get_backend(chain_id).load_json("booklet_spec.json")
        return self._spec[chain_id]


theme_storage = ThemeStorage()


def list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    if theme_id != 'ducks_everywhere':
        raise NotImplementedError()
    # Use the auction data to get a list of token IDs
    ducks_data = get_auction_json_data(chain_id, theme_id)
    return [ducks_data[d]['token_id'] for d in ducks_data]


def list_booklets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    return [key for key in theme_storage.get_booklet_spec(chain_id).keys() if key.startswith(theme_id)]


def get_booklet_id_from_token_id(chain_id: str, booklet_token_id: str) -> Union[str, None]:
    booklet_data = theme_storage.get_booklet_spec(chain_id)
    try:
        return [booklet_id for booklet_id in booklet_data if int(booklet_data[booklet_id], 16) == int(booklet_token_id, 16)][0]
    except:
        return None


def get_booklet_token_id_from_id(chain_id: str, booklet_id: str) -> Union[str, None]:
    booklet_data = theme_storage.get_booklet_spec(chain_id)
    try:
        return booklet_data[booklet_id]
    except:
        return None
