from briq_api.indexer.events.common import encode_int_as_bytes
from briq_api.memory_cache import CacheData
from briq_api.stores import theme_storage, mongo_storage


async def _list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    """Using the booklet owners, list sets of theme as hex"""
    booklets = [token for key, token in theme_storage.get_booklet_spec(chain_id).items() if key.startswith(theme_id)]
    booklet_owners = mongo_storage.get_backend(chain_id).async_db['booklet_tokens'].find({
        'token_id': {"$in": [encode_int_as_bytes(int(booklet_token_id, 16)) for booklet_token_id in booklets]},
        '_chain.valid_to': None,
        'quantity': {"$ne": encode_int_as_bytes(0)},
    })
    # Now get all sets matching the booklets
    sets = mongo_storage.get_backend(chain_id).async_db['set_tokens'].find({
        'token_id': {"$in": [encode_int_as_bytes(int(hex(int.from_bytes(booklet['owner'], "big")), 16)) async for booklet in booklet_owners]},
        '_chain.valid_to': None,
        'quantity': {"$ne": encode_int_as_bytes(0)},
    })
    return [hex(int.from_bytes(set['token_id'], "big")) async for set in sets]


@CacheData.memory_cache(lambda chain_id, theme_id: f"{chain_id}_{theme_id}", timeout=60 * 60)
async def list_duck_sets(chain_id: str, theme_id: str) -> list[str]:
    return await _list_sets_of_theme(chain_id, theme_id)


async def list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    """
    List all minted NFTs belonging to a particular theme.
    """
    if theme_id not in { 'ducks_everywhere', 'ducks_frens', 'lil_ducks' }:
        raise NotImplementedError()
    return await list_duck_sets(chain_id, theme_id)
