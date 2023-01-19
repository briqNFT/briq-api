from itertools import chain
import logging

from briq_api.indexer.storage import mongo_storage

logger = logging.getLogger(__name__)

ducks_data = {
    1: {
        'token_id': '0x7d180b4de0656c2d58237be7a77cf1403be2226f42e63a7b800000000000000',
        'minimum_bid': '1000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    },
    2: {
        'token_id': '0x210343a6ce65eaf6818b9fc8e744930e363d9a263918e94000000000000000',
        'minimum_bid': '1210',
        'growth_factor': 10,
        'start_date': 1693606220,
        'duration': 864000,
    },
    3: {
        'token_id': '0x23cb46e7f35efcb6c22c76b60dc23ffaf0bd324c43534bfb000000000000000',
        'minimum_bid': '10000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    },
    4: {
        'token_id': '0x40aacab2d004b0d8d4d95ed4dcb89b3cc0e2c66898f1a108000000000000000',
        'minimum_bid': '100000000000000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    },
    5: {
        'token_id': '0x18b440a0ced8601ce3730f544b9d22af7429296442a3e9d9000000000000000',
        'minimum_bid': '100000000000000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    },
    6: {
        'token_id': '0x791540b80c3891bffda80c230d7c8c8cec060f699ca15c88800000000000000',
        'minimum_bid': '100000000000000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    },
    7: {
        'token_id': '0x168458834a45dcae045b24600723f4f63a1355e19bea88f8000000000000000',
        'minimum_bid': '100000000000000',
        'growth_factor': 10,
        'start_date': 1673606220,
        'duration': 864000,
    }
}




def get_theme_auction_data(chain_id: str, theme_id: str):
    if theme_id == 'ducks_everywhere':
        bid_data = mongo_storage.get_backend(chain_id).db['highest_bids_ducks'].find({
            "_chain.valid_to": None,
        })
        ret = {
            'lastBlock': 0,
            'data': ducks_data.copy()
        }
        for bid in bid_data:
            auction_id = int.from_bytes(bid['auction_id'], "big")
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
        ret['data'] = {f'ducks_everywhere/{key}': value for key, value in ret['data'].items()}
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
        }).sort("_block", -1)
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
                'bid': str(int.from_bytes(bid['bid'], "big")),
                'tx_hash': hex(int.from_bytes(bid['tx_hash'], 'big')),
                'block': bid['updated_block'],
                'timestamp': bid['updated_at'],
            }
        return {f'ducks_everywhere/{key}': value for key, value in ret.items()}
    return {}
