import asyncio
import logging
from typing import Any

from apibara.indexer import IndexerRunnerConfiguration
from apibara.indexer import IndexerRunner, IndexerRunnerConfiguration, Info
from apibara.indexer.indexer import IndexerConfiguration, Reconnect
from apibara.indexer.info import Info
from apibara.protocol.proto.stream_pb2 import Cursor, DataFinality
from apibara.starknet import EventFilter, Filter, StarkNetIndexer, TransactionFilter
from apibara.starknet.cursor import starknet_cursor
from apibara.starknet.proto.starknet_pb2 import Block

from .config import AUTH_TOKEN, NETWORK, INDEXER_ID, APIBARA_URL, MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, START_BLOCK

from .events.set import SetIndexer
from .events.box import Erc1155Indexer

logger = logging.getLogger(__name__)

set_indexer = SetIndexer(NETWORK.set_address)
box_indexer = Erc1155Indexer("box", NETWORK.box_address)
booklet_indexer = Erc1155Indexer("booklet", NETWORK.booklet_address)
briq_indexer = Erc1155Indexer("briq", NETWORK.briq_address)


class BriqIndexer(StarkNetIndexer):
    def indexer_id(self) -> str:
        return INDEXER_ID

    def initial_configuration(self) -> IndexerConfiguration[Filter]:
        filters = Filter().with_header(True)
        for filter in set_indexer.filters + box_indexer.filters + booklet_indexer.filters + briq_indexer.filters:
            filters = filters.add_event(filter)
        return IndexerConfiguration(
            filter=filters,
            starting_cursor=starknet_cursor(START_BLOCK),
            finality=DataFinality.DATA_STATUS_PENDING,
        )

    async def handle_data(self, info: Info[Any, Any], data: Block):
        logger.info("Handle block events: Block No. %(block_number)s - %(block_time)s", {
            'block_number': data.header.block_number,
            'block_time': data.header.timestamp.ToDatetime().isoformat(),
        })

        await set_indexer.process_transfers(data, info)
        await box_indexer.process_transfers(data, info)
        await booklet_indexer.process_transfers(data, info)
        await briq_indexer.process_transfers(data, info)

    async def handle_pending_data(self, info: Info[Any, Filter], data: Block):
        # TODO
        pass

    # Temporarily override this to help with k8s crashing issues.
    async def handle_reconnect(self, exc: Exception, retry_count: int) -> Reconnect:
        await asyncio.sleep(min(30, retry_count * 5))
        return Reconnect(reconnect=retry_count < 20)


async def main():
    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            stream_url=APIBARA_URL,
            storage_url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}",
            token=AUTH_TOKEN,
        ),
        reset_state=False,
        client_options=[
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
    )

    logger.info("Starting indexer %(indexer)s from block %(block)s", {'indexer': INDEXER_ID, 'block': START_BLOCK})

    await runner.run(BriqIndexer(), ctx={"network": NETWORK.id})

if __name__ == "__main__":
    asyncio.run(main())
