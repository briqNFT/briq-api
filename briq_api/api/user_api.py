import io
import logging
import base64

from PIL import Image

from briq_api.chain.contracts import NETWORKS

from briq_api.set_identifier import SetRID
from briq_api.stores import genesis_storage, file_storage
from briq_api.indexer.storage import mongo_storage

from briq_api.mesh.briq import BriqData

logger = logging.getLogger(__name__)


def get_user_boxes(chain_id: str, user_id: str):
    boxes = mongo_storage.get_user_boxes(chain_id, user_id)
    return {
        "box_token_ids": boxes
    }


def get_user_briqs(chain_id: str, user_id: str):
    briqs = mongo_storage.get_user_briqs(chain_id, user_id)
    ret = {}
    for briq in briqs:
        # TODO: acknowledge NFTS here
        material = hex(int.from_bytes(briq['token_id'], "big"))
        quantity = int.from_bytes(briq['quantity'], "big")
        ret[material] = {
            'ft_balance': quantity,
            'nft_ids': []
        }
    return ret
