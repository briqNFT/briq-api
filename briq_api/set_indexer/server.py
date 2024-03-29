import asyncio
import logging
import math
import os
from typing import Union
from briq_api.chain.networks import MAINNET
from briq_api.config import ENV
from briq_api.set_indexer.config import NETWORK
from briq_api.set_indexer.set_indexer import SetIndexer, StorableSetData
from briq_api.stores import file_storage, setup_stores

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import HTTPException
from pydantic import BaseModel

from starkware.cairo.common.hash_state import compute_hash_on_elements


logger = logging.getLogger(__name__)

app = FastAPI()

# Allow any origin, not publicly exposed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_indexer: dict[str, SetIndexer] = {}


class NewSetStorageRequest(BaseModel):
    chain_id: str
    transaction_data: list[int]


def decode_string(data: list[int], offset: int):
    l = data[offset]
    return (b''.join(x.to_bytes(math.ceil(x.bit_length() / 8), 'big') for x in data[offset + 1:offset + 1 + l])).decode('utf-8', errors="ignore")


def from_storage_form(v):
    return v - 0x8000000000000000


# NB -> This can't actually tell what the NFT is, since that depends on other metadata
def uncompress_shape_item(col_nft_mat: int, x_y_z: int):
    color: int = col_nft_mat // 2 ** 136
    has_token_id: bool = bool(col_nft_mat & (2**128))
    mat: int = col_nft_mat & 0xffffffffffffffff
    x: int = from_storage_form(x_y_z // 2 ** 128)
    y: int = from_storage_form((x_y_z // 2 ** 64) & 0xffffffffffffffff)
    z: int = from_storage_form(x_y_z & 0xffffffffffffffff)
    return color.to_bytes(7, 'big').decode('ascii'), mat, x, y, z, has_token_id


def parse_transaction(data: list[int]):
    token_id = hex(get_token_id_from_calldata(data[0], data[1], []))
    cursor = 2
    name = decode_string(data, cursor)
    cursor += 1 + data[cursor]
    description = decode_string(data, cursor)
    cursor += 1 + data[cursor]
    cursor += 1 + data[cursor] * 2 # FTs have two items
    cursor += 1 + data[cursor]
    briqs = []
    for i in range(0, data[cursor] * 2, 2):
        bd = uncompress_shape_item(*data[cursor + i + 1:cursor + i + 3])
        briqs.append({
            "pos": bd[2:5],
            "data": {
                'color': bd[0].lower(),
                'material': hex(bd[1]),
            },
            #  'has_token_id': bd[5],
        })
    return (token_id, StorableSetData(name=name, description=description, briqs=briqs))


def get_token_id_from_calldata(owner: int, hint: int, uri: list[int]):
    raw_tid = compute_hash_on_elements([owner, hint]) & ((2**251 - 1) - (2**59 - 1))
    if len(uri) == 2 and uri[1] < 2**59:
        raw_tid += uri[1]
    return raw_tid


@app.get("/health")
async def health():
    return "ok"


@app.post("/store")
async def store_new_set(request: NewSetStorageRequest):
    if request.chain_id not in set_indexer:
        raise HTTPException(status_code=400, detail="Invalid chain ID")

    try:
        token_id, set_data = parse_transaction(request.transaction_data)
    except Exception as e:
        logger.warn("Failed to decode transaction", {
            "transaction_data": request.transaction_data,
        }, exc_info=e)
        raise HTTPException(status_code=400, detail="Invalid transaction data")

    set_indexer[request.chain_id].add_set_to_pending(token_id, set_data)
    return "ok"


pending_task: Union[asyncio.Task, None] = None


@app.on_event("startup")
def startup_event():
    global set_indexer
    global pending_task

    setup_stores(os.getenv("LOCAL") or False, False)

    set_indexer[NETWORK.id] = SetIndexer(NETWORK.id, file_storage)
    # In test, add mainnet processing.
    if ENV == 'test':
        set_indexer[MAINNET.id] = SetIndexer(MAINNET.id, file_storage)
    pending_task = asyncio.create_task(process_pending_sets())


async def process_pending_sets():
    global pending_task
    try:
        for indexer in set_indexer.values():
            indexer.process_pending_set()
    except Exception as e:
        logger.error("Error processing pending set", exc_info=e)
    await asyncio.sleep(1)
    pending_task = asyncio.create_task(process_pending_sets())


@app.on_event("shutdown")
def shutdown_event():
    if pending_task:
        pending_task.cancel()
