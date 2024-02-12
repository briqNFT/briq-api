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
To query total balance (auction contract)
starknet call --address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 --abi cabi.json --function balanceOf --inputs 0x1712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620 --block_number
(briq factory)
starknet call --address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 --abi cabi.json --function balanceOf --inputs 0x05b021b6743c4f420e20786baa7fb9add1d711302c267afbc171252a74687376 --block_number
(funding wallet)
starknet call --address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 --abi cabi.json --function balanceOf --inputs 0x00E838d30a24e0b7014ccd5Cf4E43B006f4Db1b122664F77fD4dfa0C6A1Ed285 --block_number
"""

"""
Run like so:
source .env.prod
APIBARA_AUTH_TOKEN=$APIBARA_AUTH_TOKEN LOGHUMAN=1 LOGLEVEL=DEBUG NETWORK_NAME=starknet-mainnet-dojo python3 jobs/compta_briq_sell_apibara.py

import pandas as pd
df = pd.read_csv('briq_price.csv')
df['date'] = pd.to_datetime(df['date'])
df['nb'] = 1
df.set_index('date').loc['2024-01'].reset_index()[['amount', 'price', 'nb']].groupby(df.date.dt.date).sum().to_csv(sep='\t')
"""


START_BLOCK = 489986
END_BLOCK = 526895 # end of jan
INDEXER_ID = 'xplorer_briq_price'
should_reset = True

logger = logging.getLogger(__name__)

# These events are only on the world contract.
factory_address = "0x1ea16366a82e211a9b9045725309a5080c0260d5caf45c58836fc61b42501f5"

def factory_filter():
    key = felt.from_int(
        0x1d38efbe2fff75bf03ddd5acd7c1c46ac2f90cdc475bad52fa0c0e7ae9c0b4f,
        #get_selector_from_name("BriqsBought")
    )
    key2 = felt.from_int(
        0x3374d4a1b4f8dc87bd680ddbd4f1181b3ec3cf5a8ef803bc4351603b063314f
    )

    return EventFilter().with_from_address(felt.from_hex(factory_address)).with_keys([key, key2])


factory_abi = get_event_serializer({
    "name": "BriqsBought",
    "type": "event",
    "keys": [],
    "data": [
        {"name": "buyer", "type": "felt"},
        {"name": "amount", "type": "felt"},
        {"name": "price", "type": "felt"},
    ],
}, "BriqsBought")

output_events = []


class BriqIndexer(StarkNetIndexer):
    def indexer_id(self) -> str:
        return INDEXER_ID

    def initial_configuration(self) -> IndexerConfiguration[Filter]:
        filters = Filter().with_header(True)
        filters.add_event(factory_filter())
        return IndexerConfiguration(
            filter=filters,
            starting_cursor=starknet_cursor(START_BLOCK),
            finality=DataFinality.DATA_STATUS_ACCEPTED,
        )

    async def handle_data(self, info: Info[Any, Any], data: Block):
        day = data.header.timestamp.ToDatetime().strftime('%Y-%m-%d')
        logger.info("At block %s with %i events %s", data.header.block_number, len(data.events), day)
        for event in data.events:
            tx_hash = felt.to_hex(event.transaction.meta.hash)
            #if event.event.keys[0] == felt.from_int(0x1d38efbe2fff75bf03ddd5acd7c1c46ac2f90cdc475bad52fa0c0e7ae9c0b4f):
            #    print("event", event.event)
            #    print("toto", [felt.to_hex(f) for f in event.event.keys])
            #    print("toto")
            try:
                parsed_event = decode_event(factory_abi, event.event)
                output_events.append({
                    'block': data.header.block_number,
                    'tx_hash': tx_hash,
                    'date': str(data.header.timestamp.ToDatetime()),
                    'buyer': hex(parsed_event.buyer),
                    'amount': parsed_event.amount,
                    'price': parsed_event.price / 10**18,
                })
            except:
                continue

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

    await runner.run(BriqIndexer(), ctx={"network": NETWORK.id})

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except:
        logger.error("Other error")

    # Save events to CSV
    with open('briq_price.csv', 'w+') as f:
        f.write('block,tx_hash,date,buyer,amount,price\n')
        for event in output_events:
            f.write(','.join([str(event['block']), event['tx_hash'], event['date'], event['buyer'], str(event['amount']), str(event['price'])]) + '\n')
