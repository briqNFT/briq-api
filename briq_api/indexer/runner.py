import asyncio
import logging
import sys
from argparse import ArgumentParser

from apibara import IndexerRunner, Info, NewBlock, NewEvents
from apibara.indexer import IndexerRunnerConfiguration

from .config import INDEXER_ID, APIBARA_URL, MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, START_BLOCK
from .events.bids import process_bids, bid_filter
from .events.bids_onchain import process_bids as process_bids_onchain, bid_filter as bid_onchains_filter
from .events.box import process_transfers as process_box, process_pending_box, transfer_filters as box_filters
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
    bids_onchain = process_bids_onchain(info, block_events.block, [event for event in block_events.events if event.name == 'Bid'])
    boxes = process_box(info, block_events.block, [event for event in block_events.events])
    booklets = process_booklet(info, block_events.block, [event for event in block_events.events])
    briqs = process_briq(info, block_events.block, [event for event in block_events.events])
    sets = process_set(info, block_events.block, [event for event in block_events.events])
    await bids
    await bids_onchain
    await boxes
    await booklets
    await briqs
    await sets

    # try:
    #    await process_pending_box(info, block_events.block, [event for event in block_events.events])
    # except Exception as e:
    #    logger.warning(e, exc_info=e)


async def handle_pending_events(info: Info, block_events: NewEvents):
    block_time = block_events.block.timestamp
    logger.info("Handle pending block: Block No. %(block_number)s - %(block_time)s", {
        'block_number': block_events.block.number,
        'block_time': block_time.isoformat()
    })
    try:
        await process_pending_box(info, block_events.block, [event for event in block_events.events])
    except Exception as e:
        logger.warning(e, exc_info=e)


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

    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            apibara_url=APIBARA_URL,
            storage_url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}"
        ),
        reset_state=args.reset,
        indexer_id=INDEXER_ID,
        new_events_handler=handle_events,
    )

    # Deactivate pending block for now - not used.
    # runner.add_pending_events_handler(handle_pending_events, interval_seconds=5)

    runner.add_block_handler(handle_block)

    # Create the indexer if it doesn't exist on the server,
    # otherwise it will resume indexing from where it left off.
    #
    # For now, this also helps the SDK map between human-readable
    # event names and StarkNet events.
    runner.create_if_not_exists(
        filters=bid_filter + box_filters + booklet_filters + briq_filters + set_filters + bid_onchains_filter,
        index_from_block=START_BLOCK,
    )

    logger.info("Starting indexer from block %(block)s", {'block': START_BLOCK})

    await runner.run()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
