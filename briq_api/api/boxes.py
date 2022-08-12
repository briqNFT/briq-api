from dataclasses import dataclass
import logging

from briq_api.chain.contracts import NETWORKS

from briq_api.storage.multi_backend_client import StorageClient
from briq_api.stores import genesis_storage, file_storage

logger = logging.getLogger(__name__)


@dataclass
class BoxRID:
    chain_id: str  # NB: this is not the same as the 'chain ID', since we'll plan ahead for cross-chain support.
    theme_id: str
    box_id: str


class BoxStorage:
    storage: StorageClient
    PREFIX = "genesis_themes"

    def __init__(self, storage: StorageClient) -> None:
        self.storage = storage

    def box_path(self, rid: BoxRID):
        return f"{BoxStorage.PREFIX}/{rid.theme_id}/{rid.box_id}"

    def metadata_path(self, rid: BoxRID):
        return f"{self.box_path(rid)}/shape.json"

    def load_metadata(self, rid: BoxRID):
        return self.storage.get_backend(rid.chain_id).load_json(self.metadata_path(rid))

    def step_image_path(self, rid: BoxRID, step: int):
        return f"{self.box_path(rid)}/step_{step}.png"

    def load_step_image(self, rid: BoxRID, step: int):
        return self.storage.get_backend(rid.chain_id).load_bytes(self.step_image_path(rid, step))

    def load_cover_item(self, rid: BoxRID):
        return self.storage.get_backend(rid.chain_id).load_bytes(f"{self.box_path(rid)}/cover_item.png")

    def load_cover_box(self, rid: BoxRID):
        return self.storage.get_backend(rid.chain_id).load_bytes(f"{self.box_path(rid)}/cover_box.png")

    def load_box_texture(self, rid: BoxRID):
        return self.storage.get_backend(rid.chain_id).load_bytes(f"{self.box_path(rid)}/box_texture.png")

    # Themes

    def list_themes(self, chain_id: str):
        return self.storage.get_backend(chain_id).list_paths(f"{BoxStorage.PREFIX}/")

    def list_boxes_of_theme(self, chain_id: str, theme_id: str):
        return [x for x in self.storage.get_backend(chain_id).list_paths(f"{BoxStorage.PREFIX}/{theme_id}/") if not x.endswith('data.json')]

    def get_theme_data(self, chain_id: str, theme_id: str):
        return self.storage.get_backend(chain_id).load_json(f"{BoxStorage.PREFIX}/{theme_id}/data.json")


box_storage = BoxStorage(file_storage)


def get_box_metadata(rid: BoxRID):
    metadata = box_storage.load_metadata(rid)
    box_data = genesis_storage.get_backend(rid.chain_id).load_json("box_spec.json")
    auction_data = genesis_storage.get_backend(rid.chain_id).load_json("auction_spec.json")
    metadata['token_id'] = box_data[f'{rid.theme_id}/{rid.box_id}']
    metadata['auction_id'] = list(auction_data.keys()).index(f'{rid.theme_id}/{rid.box_id}')
    return metadata


def get_box_saledata(rid: BoxRID):
    # TODO: on chain query
    import time
    if rid.box_id == 'spaceman':
        return {
            'quantity_left': 24,
            'total_quantity': 80,
            'price': 0.4,
            'sale_start': time.time() - 60 if 'ongoing' in rid.theme_id else time.time() + 24*60*60*10,
            'sale_duration': 24*3600*6,
        }
    return {
        'quantity_left': 1,
        'total_quantity': 1,
        'price': 0.4,
        'sale_start': time.time() - 60 if 'ongoing' in rid.theme_id else time.time() + 24*60*60*10,
        'sale_duration': 3600*2,
    }


def list_themes(chain_id: str):
    return box_storage.list_themes(chain_id)


def list_boxes_of_theme(chain_id: str, theme_id: str):
    # TODO -> change this?
    return [f"{theme_id}/{box}" for box in box_storage.list_boxes_of_theme(chain_id, theme_id)]

def get_theme_data(chain_id: str, theme_id: str):
    return box_storage.get_theme_data(chain_id, theme_id)

def get_box_step_image(rid: BoxRID, step: int):
    return box_storage.load_step_image(rid, step)


def get_box_cover_item(rid: BoxRID):
    return box_storage.load_cover_item(rid)


def get_box_cover_box(rid: BoxRID):
    return box_storage.load_cover_box(rid)


def get_box_texture(rid: BoxRID):
    return box_storage.load_box_texture(rid)
