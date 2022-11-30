import logging
import requests
from apibara import Info
from apibara.model import EventFilter, BlockHeader, StarkNetEvent
from starknet_py.contract import FunctionCallSerializer, identifier_manager_from_abi

from .common import uint256_abi, decode_event, encode_int_as_bytes
from ..config import NETWORK, SET_INDEXER_URL

logger = logging.getLogger(__name__)

contract_address = NETWORK.set_address
contract_prefix = "set"
transfer_filters = [
    EventFilter.from_event_name(name="Transfer", address=contract_address),
]

transfer_abi = {
    "name": "Transfer",
    "type": "event",
    "keys": [],
    "outputs": [
        {"name": "from_", "type": "felt"},
        {"name": "to_", "type": "felt"},
        {"name": "id_", "type": "Uint256"},
    ],
}

transfer_decoder = FunctionCallSerializer(
    abi=transfer_abi,
    identifier_manager=identifier_manager_from_abi([transfer_abi, uint256_abi]),
)


def prepare_transfer_for_storage(event: StarkNetEvent, block: BlockHeader):
    transfer_data = decode_event(transfer_decoder, event.data)
    return {
        "from": encode_int_as_bytes(transfer_data.from_),
        "to": encode_int_as_bytes(transfer_data.to_),
        "token_id": encode_int_as_bytes(transfer_data.id_),
        "value": encode_int_as_bytes(1),
        "_tx_hash": event.transaction_hash,
        "_timestamp": block.timestamp,
        "_block": block.number,
    }


async def process_transfers(info: Info, block: BlockHeader, transfers: list[StarkNetEvent]):
    block_time = block.timestamp

    # Store each in Mongo
    documents = []
    for tr in transfers:
        if tr.name == 'Transfer' and int.from_bytes(tr.address, 'big') == int(contract_address, 16):
            document = prepare_transfer_for_storage(tr, block)
            documents.append(document)

            if int.from_bytes(document['from'], "big") == 0 and SET_INDEXER_URL is not None:
                try:
                    # Need to decode the transaction to find the right offset. There might be several.
                    assembly_calls = []
                    calls = int.from_bytes(tr.transaction.calldata[0], "big")
                    for i in range(calls):
                        callarray = tr.transaction.calldata[1 + i * 4: 1 + (i + 1) * 4]
                        if int.from_bytes(callarray[0], "big") == int(contract_address, 16):
                            if int.from_bytes(callarray[1], "big") == 0x2f2e26c65fb52f0e637c698caccdefaa2a146b9ec39f18899efe271f0ed83d3:
                                assembly_calls.append([int.from_bytes(x, "big") for x in callarray[2:4]])  # offset, length
                    # Now send all transactions to the set indexer
                    # We don't care if there are repeats, the indexer handles that.
                    for call in assembly_calls:
                        calldata = tr.transaction.calldata[calls * 4 + 2 + call[0]:calls * 4 + 2 + call[0] + call[1]]
                        # Request storage in the set indexer. Short timeout, we don't care outrageously if this fails.
                        requests.post(f"http://{SET_INDEXER_URL}:5432/store", json={
                            "chain_id": NETWORK.id,
                            "token_id": hex(int.from_bytes(document['token_id'], "big")),
                            "transaction_data": [int.from_bytes(x, "big") for x in calldata],
                        }, timeout=1)
                except Exception as f:
                    logger.warn("Failed to send data to set indexer", exc_info=f)

    if (not len(documents)):
        return

    await info.storage.insert_many(f'{contract_prefix}_transfers', documents)

    logger.info("Stored %(docs)s new %(prefix)s transfers", {"docs": len(documents), "prefix": contract_prefix})

    # TODO -> this can be optimised a bit
    for transfer in documents:
        # Update from
        if int.from_bytes(transfer['from'], "big") != 0:
            og_ownership = await info.storage.find_one(f"{contract_prefix}_tokens", {
                "token_id": transfer['token_id'],
                "owner": transfer['from'],
            })
            og_amount = int.from_bytes(og_ownership['quantity'], "big") if og_ownership else 0
            await info.storage.find_one_and_replace(
                f"{contract_prefix}_tokens",
                {
                    "token_id": transfer['token_id'],
                    "owner": transfer['from'],
                },
                {
                    "token_id": transfer['token_id'],
                    "owner": transfer['from'],
                    "quantity": encode_int_as_bytes(og_amount - int.from_bytes(transfer['value'], 'big')),
                    "updated_at": block_time,
                    "updated_block": block.number,
                },
                upsert=True,
            )

        # Update to
        if int.from_bytes(transfer['to'], "big") != 0:
            to_ownership = await info.storage.find_one(f"{contract_prefix}_tokens", {
                "token_id": transfer['token_id'],
                "owner": transfer['to'],
            })
            to_amount = int.from_bytes(to_ownership['quantity'], "big") if to_ownership else 0
            await info.storage.find_one_and_replace(
                f"{contract_prefix}_tokens",
                {
                    "token_id": transfer['token_id'],
                    "owner": transfer['to'],
                },
                {
                    "token_id": transfer['token_id'],
                    "owner": transfer['to'],
                    "quantity": encode_int_as_bytes(to_amount + int.from_bytes(transfer['value'], 'big')),
                    "updated_at": block_time,
                    "updated_block": block.number,
                },
                upsert=True,
            )

    logger.info("Updated %(prefix)s token owners", {"prefix": contract_prefix})
