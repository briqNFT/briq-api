
from briq_api.api.auctions import get_auction_json_data
from briq_api.stores import genesis_storage


def list_sets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    if theme_id != 'ducks_everywhere':
        raise NotImplementedError()
    # Use the auction data to get a list of token IDs
    ducks_data = get_auction_json_data(chain_id, theme_id)
    return [ducks_data[d]['token_id'] for d in ducks_data]


def list_booklets_of_theme(chain_id: str, theme_id: str) -> list[str]:
    return [key for key in genesis_storage.get_backend(chain_id).get_booklet_spec().keys() if key.startswith(theme_id)]
