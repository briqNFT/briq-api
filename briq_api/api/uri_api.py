
import logging
from briq_api.set_identifier import SetRID

from briq_api.stores import genesis_storage

from briq_api.api.boxes import BoxRID, get_box_metadata, get_booklet_metadata
from briq_api.api.api import get_metadata

logger = logging.getLogger(__name__)


def box_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        box_id = genesis_storage.get_box_id(chain_id, token_id).split('/')
    else:
        box_id = genesis_storage.get_box_id(chain_id, hex(int(token_id))).split('/')
    return get_box_metadata(BoxRID(chain_id, *box_id))


def booklet_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        box_id = genesis_storage.get_booklet_id(chain_id, token_id).split('/')
    else:
        box_id = genesis_storage.get_booklet_id(chain_id, hex(int(token_id))).split('/')
    return get_booklet_metadata(BoxRID(chain_id, *box_id))


def set_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        set_id = token_id
    else:
        set_id = hex(int(token_id))
    return get_metadata(SetRID(chain_id=chain_id, token_id=set_id))
