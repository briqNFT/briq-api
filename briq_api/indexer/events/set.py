import logging
from apibara import Info
from apibara.model import EventFilter, BlockHeader, StarkNetEvent
from starknet_py.contract import DataTransformer, identifier_manager_from_abi

from ...chain.networks import TESTNET
from .common import uint256_abi, decode_event, encode_int_as_bytes

logger = logging.getLogger(__name__)

contract_address = TESTNET.briq_address
contract_prefix = "briq"
transfer_filters = [
    EventFilter.from_event_name(name="TransferSingle", address=contract_address),
]

transfer_single_abi = {
    "name": "TransferSingle",
    "type": "event",
    "keys": [],
    "outputs": [
        {"name": "operator_", "type": "felt"},
        {"name": "from_", "type": "felt"},
        {"name": "to_", "type": "felt"},
        {"name": "id_", "type": "Uint256"},
        {"name": "value_", "type": "Uint256"},
    ],
}

transfer_batch_abi = {
    "name": "TransferSingle",
    "type": "event",
    "keys": [],
    "outputs": [
        {"name": "_operator", "type": "felt"},
        {"name": "_from", "type": "felt"},
        {"name": "_to", "type": "felt"},
        {"name": "_ids_len", "type": "felt"},
        {"name": "_ids", "type": "Uint256"},
        {"name": "_values_len", "type": "felt"},
        {"name": "_values", "type": "Uint256*"},
    ],
}

transfer_single_decoder = DataTransformer(
    abi=transfer_single_abi,
    identifier_manager=identifier_manager_from_abi([transfer_single_abi, uint256_abi]),
)


def prepare_transfer_for_storage(event: StarkNetEvent, block: BlockHeader):
    transfer_data = decode_event(transfer_single_decoder, event.data)
    return {
        "from": encode_int_as_bytes(transfer_data.from_),
        "to": encode_int_as_bytes(transfer_data.to_),
        "token_id": encode_int_as_bytes(transfer_data.id_),
        "value": encode_int_as_bytes(transfer_data.value_),
        "_tx_hash": event.transaction_hash,
        "_timestamp": block.timestamp,
        "_block": block.number,
    }


async def process_transfers(info: Info, block: BlockHeader, transfers: list[StarkNetEvent]):
    block_time = block.timestamp

    # Store each in Mongo
    documents = [prepare_transfer_for_storage(tr, block) for tr in transfers if tr.name == 'TransferSingle' and int.from_bytes(tr.address, 'big') == int(contract_address, 16)]
    if (not len(documents)):
        return

    await info.storage.insert_many(f'{contract_prefix}_transfers', documents)

    logger.info("Stored %(docs)s new %(prefix)s transfers", {"docs": len(documents), "prefix": contract_prefix})

    # Store the new owner in the DB (only the last transfer matters here)
    new_token_owner = dict()
    for transfer in documents:
        new_token_owner[transfer['token_id']] = transfer['to']

    for token_id, new_owner in new_token_owner.items():
        await info.storage.find_one_and_replace(
            f"{contract_prefix}_tokens",
            {"token_id": token_id},
            {
                "token_id": token_id,
                "owner": new_owner,
                "updated_at": block_time,
                "updated_block": block.number,
            },
            upsert=True,
        )

    logger.info("Updated %(docs)s %(prefix)s token owners", {"docs": len(new_token_owner), "prefix": contract_prefix})
