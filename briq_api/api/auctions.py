import logging
from time import time
from briq_api.api.boxes import BoxStorage

from briq_api.indexer.storage import mongo_storage
from briq_api.memory_cache import CacheData
from briq_api.stores import file_storage

logger = logging.getLogger(__name__)


@CacheData.memory_cache(lambda chain_id, theme_id: f'{chain_id}_{theme_id}_auction_json_data', timeout=5 * 60)
def get_auction_json_data(chain_id: str, theme_id: str):
    if theme_id == 'ducks_everywhere':
        try:
            return file_storage.get_backend(chain_id).load_json(f"auctions/{theme_id}/auction_data.json")
        except Exception:
            # Ignore, we'll just return an empty dict
            return {}
    return {}


def get_theme_auction_data(chain_id: str, theme_id: str):
    if theme_id == 'ducks_everywhere':
        ducks_data = get_auction_json_data(chain_id, theme_id)
        bid_data = mongo_storage.get_backend(chain_id).db['highest_bids_ducks'].find({
            "_chain.valid_to": None,
        })
        ret = {
            'lastBlock': 0,
            'data': ducks_data.copy()
        }
        for bid in bid_data:
            auction_id = str(int.from_bytes(bid['auction_id'], "big"))
            if not auction_id in ret['data']:
                continue
            ret['data'][auction_id] = ret['data'][auction_id].copy()
            ret['data'][auction_id]['highest_bid'] = str(int.from_bytes(bid['bid'], "big"))
            ret['data'][auction_id]['highest_bidder'] = hex(int.from_bytes(bid['bidder'], "big"))
            ret['data'][auction_id]['bids'] = [{
                'bid': ret['data'][auction_id]['highest_bid'],
                'bidder': ret['data'][auction_id]['highest_bidder'],
                'tx_hash': hex(int.from_bytes(bid['tx_hash'], 'big')),
                'block': bid['updated_block'],
                'timestamp': bid['updated_at'],
            }]
            ret['lastBlock'] = max(ret['lastBlock'], bid['updated_block'])
        ret['data'] = {
            f'ducks_everywhere/{key}': value
            for key, value in ret['data'].items()
            if value['start_date'] < time()
        }
        return ret
    return {
        'last_block': 0,
        'data': {}
    }


def get_auction_bids(chain_id: str, auction_theme: str, auction_id: str):
    if auction_theme == 'ducks_everywhere':
        bids = mongo_storage.get_backend(chain_id).db['bids_ducks'].find({
            "auction_id": int(auction_id).to_bytes(32, "big"),
            "_chain.valid_to": None,
        }).sort("_timestamp", -1)
        return [
            {
                'bid': str(int.from_bytes(b['bid_amount'], "big")),
                'bidder': hex(int.from_bytes(b['bidder'], "big")),
                'tx_hash': hex(int.from_bytes(b['_tx_hash'], 'big')),
                'block': b['_block'],
                'timestamp': b['_timestamp'],
            }
            for b in bids
        ]
    return []


def get_user_bids(chain_id: str, auction_theme: str, user_id: str):
    if auction_theme == 'ducks_everywhere':
        bid_data = mongo_storage.get_backend(chain_id).db['ducks_bids_per_user'].find({
            "bidder": int(user_id, 16).to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        ret = {}
        for bid in bid_data:
            auction_id = int.from_bytes(bid['auction_id'], "big")
            ret[auction_id] = {
                'bid_amount': str(int.from_bytes(bid['bid'], "big")),
                'tx_hash': hex(int.from_bytes(bid['tx_hash'], 'big')),
                'block': bid['updated_block'],
                'timestamp': bid['updated_at'],
            }
        return {f'ducks_everywhere/{key}': value for key, value in ret.items()}
    return {}
