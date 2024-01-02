import asyncio
import logging
from typing import Any

from apibara.indexer import IndexerRunnerConfiguration
from apibara.indexer import IndexerRunner, IndexerRunnerConfiguration, Info
from apibara.indexer.indexer import IndexerConfiguration
from apibara.protocol.proto.stream_pb2 import DataFinality
from apibara.starknet import EventFilter, Filter, StarkNetIndexer
from apibara.starknet.cursor import starknet_cursor
from apibara.starknet.proto.starknet_pb2 import Block

from starkware.starknet.public.abi import get_selector_from_name
from apibara.starknet import felt

from briq_api.indexer.config import AUTH_TOKEN, NETWORK, APIBARA_URL, MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD
from briq_api.indexer.events.common import decode_event, get_event_serializer


"""
To query total balance:
# auction contract
starknet call --address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 --abi cabi.json --function balanceOf --inputs 0x1712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620 --block_number
# funding wallet
starknet call --address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 --abi cabi.json --function balanceOf --inputs 0x00E838d30a24e0b7014ccd5Cf4E43B006f4Db1b122664F77fD4dfa0C6A1Ed285 --block_number

starkli call 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 balanceOf 0x00E838d30a24e0b7014ccd5Cf4E43B006f4Db1b122664F77fD4dfa0C6A1Ed285 --network mainnet

"""


# python -m asyncio
import pandas as pd
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

client = FullNodeClient(node_url="http://127.0.0.1:5055/v1/node/starknet-mainnet-dojo/rpc_local")

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

eth_token_address = 0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7

call = Call(
    to_addr=eth_token_address,
    selector=get_selector_from_name("balanceOf"),
    calldata=[0x00E838d30a24e0b7014ccd5Cf4E43B006f4Db1b122664F77fD4dfa0C6A1Ed285],
)
await client.call_contract(call, block_number=489986)

# Note that a Contract instance cannot be used here, since it needs ABI to generate the functions

# Run like so:
#  APIBARA_AUTH_TOKEN=$APIBARA_AUTH_TOKEN LOGHUMAN=1 LOGLEVEL=INFO NETWORK_NAME=starknet-mainnet python3 jobs/compta.py

START_BLOCK = 130000
END_BLOCK = 194000
INDEXER_ID = 'compta_2'
should_reset = True

logger = logging.getLogger(__name__)

mintsquare_mn = "0x079b882cb8200c1c1d20e849a2ef19124b0b8985358c1313ea6af588cfe4fec8"

print(NETWORK)

def mintsquare_filter():
    key = felt.from_int(
        get_selector_from_name("RoyaltyPayment")
    )
    return EventFilter().with_from_address(felt.from_hex(mintsquare_mn)).with_keys([key])

mintsquare_abi = get_event_serializer({
    "name": "RoyaltyPayment",
    "type": "event",
    "keys": [],
    "data": [
        {"name": "collection", "type": "felt"},
        {"name": "tokenId", "type": "Uint256"},
        {"name": "royaltyRecipient", "type": "felt"},
        {"name": "currency", "type": "felt"},
        {"name": "amount", "type": "felt"},
        {"name": "timestamp", "type": "felt"},
    ],
}, "RoyaltyPayment")

class BriqIndexer(StarkNetIndexer):

    total_amount = {}
    first_block = {}

    def indexer_id(self) -> str:
        return INDEXER_ID

    def initial_configuration(self) -> IndexerConfiguration[Filter]:
        filters = Filter().with_header(True)
        filters.add_event(mintsquare_filter())
        return IndexerConfiguration(
            filter=filters,
            starting_cursor=starknet_cursor(START_BLOCK),
            finality=DataFinality.DATA_STATUS_ACCEPTED,
        )

    async def handle_data(self, info: Info[Any, Any], data: Block):
        month = data.header.timestamp.ToDatetime().strftime('%Y-%m')
        logger.info("At block %s with %i events %s", data.header.block_number, len(data.events), month)
        if month not in self.total_amount:
            self.total_amount[month] = 0
            self.first_block[month] = data.header.block_number
        for event in data.events:
            tx_hash = felt.to_hex(event.transaction.meta.hash)
            parsed_event = decode_event(mintsquare_abi, event.event)
            if parsed_event.royaltyRecipient != 0x1712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620:
                continue
            self.total_amount[month] += parsed_event.amount

        if data.header.block_number >= END_BLOCK:
            raise Exception("Done")

briq_indexer = BriqIndexer()

async def main():
    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            stream_url=APIBARA_URL,
            storage_url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}",
            token=AUTH_TOKEN,
        ),
        reset_state=should_reset,
        client_options=[
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
    )

    logger.info("Starting indexer %(indexer)s from block %(block)s", {'indexer': INDEXER_ID, 'block': START_BLOCK})

    await runner.run(briq_indexer, ctx={"network": NETWORK.id})

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("Block dates: ", briq_indexer.first_block)
        print("Total amount: ", briq_indexer.total_amount)
