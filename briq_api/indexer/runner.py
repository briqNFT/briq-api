import asyncio
import logging
import sys
from argparse import ArgumentParser

from apibara import Client, IndexerRunner, Info, NewBlock, NewEvents
from apibara.indexer.runner import IndexerRunnerConfiguration

from .config import INDEXER_ID, APIBARA_URL, MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, NETWORK_NAME, START_BLOCK
from .events.bids import process_bids, bid_filter
from .events.box import process_transfers as process_box, transfer_filters as box_filters
from .events.booklet import process_transfers as process_booklet, transfer_filters as booklet_filters
from .events.briq import process_transfers as process_briq, transfer_filters as briq_filters
from .events.set import process_transfers as process_set, transfer_filters as set_filters

logger = logging.getLogger(__name__)


async def handle_events(info: Info, block_events: NewEvents):
    block_time = block_events.block.timestamp
    logger.info("Handle block events: Block No. %(block_number)s - %(block_time)s", {
        'block_number': block_events.block.number,
        'block_time': block_time.isoformat()
    })

    bids = process_bids(info, block_events.block, [event for event in block_events.events if event.name == 'Bid'])
    boxes = process_box(info, block_events.block, [event for event in block_events.events])
    booklets = process_booklet(info, block_events.block, [event for event in block_events.events])
    briqs = process_briq(info, block_events.block, [event for event in block_events.events])
    sets = process_set(info, block_events.block, [event for event in block_events.events])
    await bids
    await boxes
    await booklets
    await briqs
    await sets


async def handle_block(info: Info, block: NewBlock):
    # Store the block information in the database.
    block = {
        "number": block.new_head.number,
        "hash": block.new_head.hash,
        "timestamp": block.new_head.timestamp.isoformat(),
    }
    await info.storage.insert_one("blocks", block)
    logger.info("Received block %(number)s", {'number': block['number']})

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
                logging.warn("Indexer deleted. Starting from beginning.")

    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            apibara_url=APIBARA_URL,
            storage_url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}"
        ),
        network_name=NETWORK_NAME,
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
        filters=bid_filter + box_filters + booklet_filters + briq_filters + set_filters,
        index_from_block=START_BLOCK,
    )

    await runner.run()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
