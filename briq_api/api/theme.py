from base64 import encode
from typing import Union
from briq_api.indexer.events.common import encode_int_as_bytes
from briq_api.memory_cache import CacheData
from briq_api.stores import get_auction_json_data
from briq_api.stores import theme_storage, mongo_storage


def _list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    """Using the booklet owners, list sets of theme as hex"""
    booklets = [token for key, token in theme_storage.get_booklet_spec(chain_id).items() if key.startswith(theme_id)]
    booklet_owners = mongo_storage.get_backend(chain_id).db['booklet_tokens'].find({
        'token_id': {"$in": [encode_int_as_bytes(int(booklet_token_id, 16)) for booklet_token_id in booklets]},
        '_chain.valid_to': None,
        'quantity': {"$ne": encode_int_as_bytes(0)},
    })
    # Now get all sets matching the booklets
    sets = list(mongo_storage.get_backend(chain_id).db['set_tokens'].find({
        'token_id': {"$in": [encode_int_as_bytes(int(hex(int.from_bytes(booklet['owner'], "big")), 16)) for booklet in booklet_owners]},
        '_chain.valid_to': None,
        'quantity': {"$ne": encode_int_as_bytes(0)},
    }))
    return [hex(int.from_bytes(set['token_id'], "big")) for set in sets]


@CacheData.memory_cache(lambda chain_id: chain_id, timeout=60 * 60)
def list_duck_sets(chain_id: str) -> list[str]:
    return _list_sets_of_theme(chain_id, 'ducks_everywhere')


def list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    if theme_id != 'ducks_everywhere':
        raise NotImplementedError()
    return list_duck_sets(chain_id)


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
