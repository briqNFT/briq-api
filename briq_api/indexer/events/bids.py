import logging
from apibara import Info
from apibara.model import EventFilter, BlockHeader, StarkNetEvent
from starknet_py.contract import FunctionCallSerializer, identifier_manager_from_abi

from ...chain.networks import TESTNET
from .common import uint256_abi, decode_event, encode_int_as_bytes

logger = logging.getLogger(__name__)

auction_address = TESTNET.auction_address

bid_abi = {
    "name": "Bid",
    "type": "event",
    "keys": [],
    "outputs": [
        {"name": "bidder", "type": "felt"},
        {"name": "box_token_id", "type": "felt"},
        {"name": "bid_amount", "type": "felt"},
    ],
}

bid_decoder = FunctionCallSerializer(
    abi=bid_abi,
    identifier_manager=identifier_manager_from_abi([bid_abi, uint256_abi]),
)

bid_filter = [EventFilter.from_event_name(name="Bid", address=auction_address)]


def prepare_bid_for_storage(event: StarkNetEvent, block: BlockHeader):
    bid_data = decode_event(bid_decoder, event.data)
    return {
        "bidder": encode_int_as_bytes(bid_data.bidder),
        "box_token_id": encode_int_as_bytes(bid_data.box_token_id),
        "bid_amount": encode_int_as_bytes(bid_data.bid_amount),
        "_tx_hash": event.transaction_hash or f'{event.name}-{event.log_index}',
        "_timestamp": block.timestamp,
        "_block": block.number,
    }


async def process_bids(info: Info, block: BlockHeader, bids: list[StarkNetEvent]):
    block_time = block.timestamp

    # Store each bid in Mongo
    documents = [prepare_bid_for_storage(tr, block) for tr in bids]
    if (not len(documents)):
        return

    await info.storage.insert_many("bids", documents)

    logger.info("Stored %(docs)s new bids", {"docs": len(documents)})

    # Compute the new highest bid on all items
    highest_bid = dict()
    for bid in documents:
        if bid['box_token_id'] not in highest_bid or highest_bid[bid['box_token_id']][1] < int.from_bytes(bid['bid_amount'], "big"):
            highest_bid[bid['box_token_id']] = (bid['bidder'], int.from_bytes(bid['bid_amount'], "big"))

    for box_token_id in highest_bid:
        existing_bid = await info.storage.find_one("highest_bids", {"box_token_id": box_token_id})
        if existing_bid and int.from_bytes(existing_bid['bid'], "big") >= highest_bid[box_token_id][1]:
            del highest_bid[box_token_id]

    for box_token_id, data in highest_bid.items():
        await info.storage.find_one_and_replace(
            "highest_bids",
            {"box_token_id": box_token_id},
            {
                "box_token_id": box_token_id,
                "bidder": data[0],
                "bid": encode_int_as_bytes(data[1]),
                "updated_at": block_time,
                "updated_block": block.number,
            },
            upsert=True,
        )

    logger.info("Updated %(bids)s highest bids", {"bids": len(highest_bid)})
