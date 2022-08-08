import asyncio
import logging
from multiprocessing.synchronize import Event
import sys
from argparse import ArgumentParser
from typing import List, NamedTuple

from starknet_py.contract import DataTransformer, identifier_manager_from_abi

from apibara import Client, IndexerRunner, Info, NewBlock, NewEvents
from apibara.indexer.runner import IndexerRunnerConfiguration
from apibara.model import EventFilter

from .config import INDEXER_ID, MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD

logger = logging.getLogger(__name__)

briqs_address = "0x04a97166c6718f85162f05270274ccede8e20e6aaa47a389f478d9df71ee6a95"

uint256_abi = {
    "name": "Uint256",
    "type": "struct",
    "size": 2,
    "members": [
        {"name": "low", "offset": 0, "type": "felt"},
        {"name": "high", "offset": 1, "type": "felt"},
    ],
}

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

bid_decoder = DataTransformer(
    abi=bid_abi,
    identifier_manager=identifier_manager_from_abi([bid_abi, uint256_abi]),
)


def decode_event(decoder: DataTransformer, data: List[bytes]) -> NamedTuple:
    data = [int.from_bytes(b, "big") for b in data]
    return decoder.to_python(data)


def encode_int_as_bytes(n: int) -> bytes:
    """Encode an integer to bytes so that it can be stored in a db."""
    return n.to_bytes(32, "big")


async def handle_events(info: Info, block_events: NewEvents):
    block_time = block_events.block.timestamp
    print(f"Handle block events: Block No. {block_events.block.number} - {block_time}")

    bids = [(decode_event(bid_decoder, event.data), event) for event in block_events.events]

    # Store each bid in Mongo
    documents = [
        {
            "bidder": encode_int_as_bytes(tr[0].bidder),
            "box_token_id": encode_int_as_bytes(tr[0].box_token_id),
            "bid_amount": encode_int_as_bytes(tr[0].bid_amount),
            "_tx_hash": tr[1].transaction_hash,
            "_timestamp": block_time,
            "_block": block_events.block.number,
        }
        for tr in bids
    ]

    await info.storage.insert_many("bids", documents)

    logger.info("Stored %(docs)s new bids", {"docs": len(documents)})

    # Compute the new highest bid on all items
    highest_bid = dict()
    for bid, _ in bids:
        if bid.box_token_id not in highest_bid or bid.box_token_id[highest_bid][1] < bid.bid_amount:
            highest_bid[bid.box_token_id] = (bid.bidder, bid.bid_amount)

    for box_token_id in highest_bid:
        existing_bid = await info.storage.find_one("highest_bids", {"box_token_id": box_token_id})
        logging.info(f"existing_bid {existing_bid}  highest {highest_bid[box_token_id]}")
        if existing_bid and existing_bid[1] >= highest_bid[box_token_id][1]:
            del highest_bid[box_token_id]

    for box_token_id, data in highest_bid.items():
        box_token_id = encode_int_as_bytes(box_token_id)
        await info.storage.find_one_and_replace(
            "highest_bids",
            {"box_token_id": box_token_id},
            {
                "box_token_id": box_token_id,
                "bidder": encode_int_as_bytes(data[0]),
                "bid": encode_int_as_bytes(data[1]),
                "updated_at": block_time,
                "updated_block": block_events.block.number,
            },
            upsert=True,
        )

    logger.info("Updated %(bids)s highest bids", {"bids": len(highest_bid)})


async def handle_block(info: Info, block: NewBlock):
    # Store the block information in the database.
    block = {
        "number": block.new_head.number,
        "hash": block.new_head.hash,
        "timestamp": block.new_head.timestamp.isoformat(),
    }
    await info.storage.insert_one("blocks", block)

# TODO: handle reorg


async def main(args):
    parser = ArgumentParser()
    parser.add_argument("--reset", action="store_true", default=False)
    args = parser.parse_args()

    if args.reset:
        async with Client.connect() as client:
            existing = await client.indexer_client().get_indexer(INDEXER_ID)
            if existing:
                await client.indexer_client().delete_indexer(INDEXER_ID)
                print("Indexer deleted. Starting from beginning.")

    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            storage_url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}"
        ),
        network_name="starknet-goerli",
        indexer_id=INDEXER_ID,
        new_events_handler=handle_events,
    )

    runner.add_block_handler(handle_block)

    # Create the indexer if it doesn't exist on the server,
    # otherwise it will resume indexing from where it left off.
    #
    # For now, this also helps the SDK map between human-readable
    # event names and StarkNet events.
    runner.create_if_not_exists(
        filters=[EventFilter.from_event_name(name="Bid", address=briqs_address)],
        index_from_block=285_000,
    )

    await runner.run()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
