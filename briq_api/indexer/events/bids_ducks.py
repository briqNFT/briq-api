import logging
from apibara import Info
from apibara.model import EventFilter, BlockHeader, StarkNetEvent
from starknet_py.contract import FunctionCallSerializer, identifier_manager_from_abi

from .common import uint256_abi, decode_event, encode_int_as_bytes
from ..config import NETWORK

logger = logging.getLogger(__name__)

# This file needs updating if I reuse it
contract_address = NETWORK.auction_ducks

bid_abi = {
    "name": "Bid",
    "type": "event",
    "keys": [],
    "outputs": [
        {"name": "bidder", "type": "felt"},
        {"name": "bid_amount", "type": "felt"},
        {"name": "auction_id", "type": "felt"},
    ],
}

bid_decoder = FunctionCallSerializer(
    abi=bid_abi,
    identifier_manager=identifier_manager_from_abi([bid_abi, uint256_abi]),
)

bid_filter = [EventFilter.from_event_name(name="Bid", address=contract_address)]

def prepare_bid_for_storage(event: StarkNetEvent, block: BlockHeader):
    bid_data = decode_event(bid_decoder, event.data)
    return {
        "bidder": encode_int_as_bytes(bid_data.bidder),
        "bid_amount": encode_int_as_bytes(bid_data.bid_amount),
        "auction_id": encode_int_as_bytes(bid_data.auction_id),
        "_tx_hash": event.transaction_hash,
        "_timestamp": block.timestamp,
        "_block": block.number,
    }


async def process_bids(info: Info, block: BlockHeader, bids: list[StarkNetEvent]):
    block_time = block.timestamp

    # Store each bid in Mongo
    documents = [prepare_bid_for_storage(tr, block) for tr in bids if int.from_bytes(tr.address, 'big') == int(contract_address, 16)]
    if (not len(documents)):
        return

    await info.storage.insert_many("bids_ducks", documents)

    logger.info("Stored %(docs)s new bids", {"docs": len(documents)})

    # Compute the new highest bid on all items
    highest_bid = dict()
    for bid in documents:
        await info.storage.find_one_and_replace(
            "ducks_bids_per_user",
            {"auction_id": bid['auction_id'], "bidder": bid['bidder']},
            {
                "auction_id": bid['auction_id'],
                "bidder": bid['bidder'],
                "bid": bid['bid_amount'],
                "tx_hash": bid['_tx_hash'],
                "updated_at": block_time,
                "updated_block": block.number,
            },
            upsert=True,
        )

        if bid['auction_id'] not in highest_bid or highest_bid[bid['auction_id']][1] < int.from_bytes(bid['bid_amount'], "big"):
            highest_bid[bid['auction_id']] = (bid['bidder'], int.from_bytes(bid['bid_amount'], "big"), bid)

    skips = []
    for auction_id in highest_bid:
        existing_bid = await info.storage.find_one("highest_bids_ducks", {"auction_id": auction_id})
        if existing_bid and int.from_bytes(existing_bid['bid'], "big") >= highest_bid[auction_id][1]:
            skips.append(auction_id)

    for auction_id, data in highest_bid.items():
        if auction_id in skips:
            continue
        await info.storage.find_one_and_replace(
            "highest_bids_ducks",
            {"auction_id": auction_id},
            {
                "auction_id": data[2]['auction_id'],
                "bidder": data[2]['bidder'],
                "bid": data[2]['bid_amount'],
                "tx_hash": data[2]['_tx_hash'],
                "updated_at": block_time,
                "updated_block": block.number,
            },
            upsert=True,
        )

    logger.info("Updated %(bids)s highest bids", {"bids": len(highest_bid)})
