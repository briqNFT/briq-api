from typing import Any, Sequence
import logging
import requests

from apibara.starknet import felt
from apibara.starknet.proto.types_pb2 import FieldElement
from briq_api.indexer.config import NETWORK, SET_INDEXER_URL

from .common import (
    Block, Info, EventIndexer, decode_event, encode_int_as_bytes, get_event_serializer, get_event_filter
)

logger = logging.getLogger(__name__)


class SetIndexer(EventIndexer):
    def __init__(self, address: str) -> None:
        super().__init__("set", address)
        self.filters = [get_event_filter(address, "Transfer")]
        self.event_serializer = get_event_serializer({
            "name": "Transfer",
            "type": "event",
            "keys": [],
            "data": [
                {"name": "from_", "type": "felt"},
                {"name": "to_", "type": "felt"},
                {"name": "token_", "type": "Uint256"},
            ],
        }, "Transfer")

    def _prepare_transfer_for_storage(self, event_data: dict[str, str], tx_hash: str, data: Block):
        return {
            "from": encode_int_as_bytes(event_data.from_),
            "to": encode_int_as_bytes(event_data.to_),
            "token_id": encode_int_as_bytes(event_data.token_),
            "value": encode_int_as_bytes(1),
            "_tx_hash": encode_int_as_bytes(int(tx_hash, 16)),
            "_timestamp": data.header.timestamp.ToDatetime(),
            "_block": data.header.block_number,
        }

    async def process_transfers(self, data: Block, info: Info[Any, Any]):
        block_time = data.header.timestamp.ToDatetime()
        block_number = data.header.block_number

        tx_processed = set()

        documents = []
        for event_with_tx in data.events:
            if felt.to_int(event_with_tx.event.from_address) != int(self.address, 16):
                continue
            tx_hash = felt.to_hex(event_with_tx.transaction.meta.hash)
            parsed_event = decode_event(self.event_serializer, event_with_tx.event)
            document = self._prepare_transfer_for_storage(parsed_event, tx_hash, data)
            documents.append(document)
            if SET_INDEXER_URL is not None:
                if tx_hash not in tx_processed:
                    tx_processed.add(tx_hash)
                    self.send_to_set_indexer(tx_hash, event_with_tx.transaction.invoke_v1.calldata)

        if (not len(documents)):
            return

        await info.storage.insert_many(f'{self.contract_prefix}_transfers', documents)

        logger.info("Stored %(docs)s new %(prefix)s transfers", {"docs": len(documents), "prefix": self.contract_prefix})

        # TODO -> this can be optimised a bit
        for transfer in documents:
            # Update from
            if int.from_bytes(transfer['from'], "big") != 0:
                og_ownership = await info.storage.find_one(f"{self.contract_prefix}_tokens", {
                    "token_id": transfer['token_id'],
                    "owner": transfer['from'],
                })
                og_amount = int.from_bytes(og_ownership['quantity'], "big") if og_ownership else 0
                await info.storage.find_one_and_replace(
                    f"{self.contract_prefix}_tokens",
                    {
                        "token_id": transfer['token_id'],
                        "owner": transfer['from'],
                    },
                    {
                        "token_id": transfer['token_id'],
                        "owner": transfer['from'],
                        "quantity": encode_int_as_bytes(og_amount - int.from_bytes(transfer['value'], 'big')),
                        "updated_at": block_time,
                        "updated_block": block_number,
                    },
                    upsert=True,
                )

            # Update to
            if int.from_bytes(transfer['to'], "big") != 0:
                to_ownership = await info.storage.find_one(f"{self.contract_prefix}_tokens", {
                    "token_id": transfer['token_id'],
                    "owner": transfer['to'],
                })
                to_amount = int.from_bytes(to_ownership['quantity'], "big") if to_ownership else 0
                await info.storage.find_one_and_replace(
                    f"{self.contract_prefix}_tokens",
                    {
                        "token_id": transfer['token_id'],
                        "owner": transfer['to'],
                    },
                    {
                        "token_id": transfer['token_id'],
                        "owner": transfer['to'],
                        "quantity": encode_int_as_bytes(to_amount + int.from_bytes(transfer['value'], 'big')),
                        "updated_at": block_time,
                        "updated_block": block_number,
                    },
                    upsert=True,
                )

        logger.info("Updated %(prefix)s token owners", {"prefix": self.contract_prefix})

    def send_to_set_indexer(self, tx_hash: str, calldata: Sequence[FieldElement]):
        """Find all assembly transactions and send them to the set indexer."""
        try:
            # Need to decode the transaction to find the right offset. There might be several.
            assembly_calls = []
            calls = felt.to_int(calldata[0])
            for i in range(calls):
                callarray = calldata[1 + i * 4: 1 + (i + 1) * 4]
                if felt.to_int(callarray[0]) == int(self.address, 16):
                    # Check the selector matches 'assemble_'
                    if felt.to_int(callarray[1]) == 0x2f2e26c65fb52f0e637c698caccdefaa2a146b9ec39f18899efe271f0ed83d3:
                        assembly_calls.append([felt.to_int(x) for x in callarray[2:4]])  # offset, length
            # Now send all transactions to the set indexer
            # We don't care if there are repeats, the indexer handles that.
            for call in assembly_calls:
                set_calldata = calldata[calls * 4 + 2 + call[0]:calls * 4 + 2 + call[0] + call[1]]
                # Request storage in the set indexer. Short timeout, we don't care outrageously if this fails.
                req = requests.post(f"http://{SET_INDEXER_URL}:5432/store", json={
                    "chain_id": NETWORK.id,
                    "transaction_data": [felt.to_int(x) for x in set_calldata],
                }, timeout=1)
                try:
                    req.raise_for_status()
                except Exception as e:
                    logger.warn("Error while storing set data for TX %(tx)s.", {
                        "tx": tx_hash,
                        "call": call,
                    }, exc_info=e)

        except Exception as f:
            logger.warn("Failed to send data to set indexer", exc_info=f)
