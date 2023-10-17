import logging
from typing import Any
from apibara.starknet import felt

from .common import (
    Block, Info, EventIndexer, decode_event, encode_int_as_bytes, get_event_serializer, get_event_filter
)

logger = logging.getLogger(__name__)


class Erc1155Indexer(EventIndexer):
    contract_prefix: str

    def __init__(self, contract_prefix: str, address: str) -> None:
        super().__init__(contract_prefix, [address])
        self.contract_prefix = contract_prefix
        self.filters = [get_event_filter(address, "TransferSingle")]
        self.event_serializer = get_event_serializer({
            "name": "TransferSingle",
            "type": "event",
            "keys": [],
            "data": [
                {"name": "operator_", "type": "felt"},
                {"name": "from_", "type": "felt"},
                {"name": "to_", "type": "felt"},
                {"name": "id_", "type": "Uint256"},
                {"name": "value_", "type": "Uint256"},
            ],
        }, "TransferSingle")

    def _prepare_transfer_for_storage(self, event_data: dict[str, str], tx_hash: str, data: Block):
        return {
            "from": encode_int_as_bytes(event_data.from_),
            "to": encode_int_as_bytes(event_data.to_),
            "token_id": encode_int_as_bytes(event_data.id_),
            "value": encode_int_as_bytes(event_data.value_),
            "_tx_hash": encode_int_as_bytes(int(tx_hash, 16)),
            "_timestamp": data.header.timestamp.ToDatetime(),
            "_block": data.header.block_number,
        }

    async def process_transfers(self, data: Block, info: Info[Any, Any]):
        block_time = data.header.timestamp.ToDatetime()
        block_number = data.header.block_number

        # Store each in Mongo
        documents = []
        for event_with_tx in data.events:
            if felt.to_int(event_with_tx.event.from_address) not in self.addresses_int:
                continue
            tx_hash = felt.to_hex(event_with_tx.transaction.meta.hash)
            parsed_event = decode_event(self.event_serializer, event_with_tx.event)
            document = self._prepare_transfer_for_storage(parsed_event, tx_hash, data)
            documents.append(document)

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
