from typing import Dict
from briq_api.storage.file.file_client import FileStorageBackend
from briq_api.storage.multi_backend_client import StorageClient
from briq_api.memory_cache import CacheData

class ThemeStorage(StorageClient[FileStorageBackend]):
    _memcache: dict[str, CacheData[dict[str, str]]] = {}

    def __init__(self) -> None:
        super().__init__()
        # Decorate out of band so I can use self (so I can reset the cache).
        # (I need to reset the cache because we can upload new box/booklets)
        # (this feels kinda horrible, but alternatives have bad tradeoffs as well)
        # Guess I could just not reuse the cache decorator.
        self.get_booklet_spec = CacheData.memory_cache(lambda chain_id: f'{chain_id}_booklet_spec', timeout=5 * 60, memcache=self._memcache)(self.get_booklet_spec)
        self.get_box_spec = CacheData.memory_cache(lambda chain_id: f'{chain_id}_box_spec', timeout=5 * 60, memcache=self._memcache)(self.get_box_spec)

    def reset_cache(self):
        self._memcache.clear()

    @staticmethod
    def booklet_path():
        return "genesis_themes/booklet_spec.json"

    @staticmethod
    def box_path():
        return "genesis_themes/box_spec.json"

    def get_all_theme_object_ids(self, chain_id: str, theme_id: str) -> Dict[str, str]:
        """
        Uses the booklet spec to return all objects in a theme.
        TODO: Ultimately booklets should be abstracted as objects.
        """
        return {key: value for (key, value) in self.get_booklet_spec(chain_id).items() if key.startswith(theme_id)}

    # Booklet stuff

    def get_booklet_spec(self, chain_id: str) -> dict[str, str]:
        return self.get_backend(chain_id).load_json(self.booklet_path())

    def get_booklet_id_from_token_id(self, chain_id: str, booklet_token_id: str) -> str:
        booklet_data = self.get_booklet_spec(chain_id)
        return [booklet_id for booklet_id in booklet_data if int(booklet_data[booklet_id], 16) == int(booklet_token_id, 16)][0]

    def get_booklet_token_id_from_id(self, chain_id: str, booklet_id: str) -> str:
        return self.get_booklet_spec(chain_id)[booklet_id]

    # Box stuff

    def get_box_spec(self, chain_id: str) -> dict[str, int]:
        return self.get_backend(chain_id).load_json(self.box_path())

    def get_box_token_id(self, chain_id: str, box_id: str):
        return self.get_box_spec(chain_id)[box_id]

    def get_box_id(self, chain_id: str, box_token_id: str) -> str:
        box_data = self.get_box_spec(chain_id)
        return [box_name for box_name in box_data if box_data[box_name] == int(box_token_id, 16)][0]
