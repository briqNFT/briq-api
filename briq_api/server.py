from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import asyncio
import time

from briq_api.storage.file_storage import FileStorage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://sltech.company",
        "https://www.sltech.company",
        "https://briq.construction",
        "https://www.briq.construction",
        "https://test.sltech.company",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from typing import Dict, Any, Tuple
from .storage.storage import get_storage
storage_client = get_storage()

@app.get("/health")
def health():
    return "ok"

@app.post("/store_get/{token_id}")
@app.get("/store_get/{token_id}")
async def store_get(token_id: str):
    try:
        data = storage_client.load_json(path=token_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="File not found")

    return {
        "code": 200,
        "token_id": token_id,
        "data": data
    }

import io
from starlette.responses import StreamingResponse

@app.get("/preview/{token_id}")
async def get_preview(token_id: str):
    try:
        data = storage_client.load_image(path=token_id)
        return StreamingResponse(io.BytesIO(data), media_type="image/png", headers={
            "Cache-Control": f"public, max-age={3600 * 24}"
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="File not found")

@app.post("/store_list")
@app.get("/store_list")
def store_list():
    return {
        "code": 200,
        "sets": storage_client.list_json()
    }

import os
CUSTOM_SET_ADDRESS = os.environ.get("SET_ADDRESS")
print(CUSTOM_SET_ADDRESS)
from starknet_py.contract import Contract
from starknet_py.net.client import Client
client = Client("testnet" if CUSTOM_SET_ADDRESS != "" else "testnet")
SET_CONTRACT_ADDRESS = CUSTOM_SET_ADDRESS or "0x0266b1276d23ffb53d99da3f01be7e29fa024dd33cd7f7b1eb7a46c67891c9d0"
set_contract_promise = Contract.from_address(CUSTOM_SET_ADDRESS, client)
set_contract = None

async def get_set_contract():
    global set_contract
    if set_contract is None:
        try:
            set_contract = await set_contract_promise
            print("Set contract address to " + SET_CONTRACT_ADDRESS)
        except RuntimeError:
            # if we're here, someone is already awaiting it, so we'll just wait.
            while set_contract is None:
                await asyncio.sleep(1)
    return set_contract

gallery_items = []
future_gallery_items = []
updating_task = None

async def update_gallery_items_unused():
    global future_gallery_items
    global gallery_items
    global updating_task
    future_gallery_items = []

    print("UPDATING GALLERY ITEMS")
    files = storage_client.list_json()

    async def get_set_if_owner(filename: str) -> str:
        set_id = filename.replace(".json", "")
        try:
            (owner,) = await (await get_set_contract()).functions["owner_of"].call(int(set_id, base=16))
            if owner == 0:
                return ""
            return set_id
        except Exception as err:
            print("Error querying gallery item ", set_id)
            print(err)
            return ""

    # Send some requests in parallel but throttle to avoid problems.
    GROUP = 1
    for i in range(len(files) // GROUP):
        future_gallery_items.append(files[i].replace(".json", ""))
        continue
        futures = []
        for j in range(GROUP):
            if len(files) > i * GROUP + j:
                futures.append(get_set_if_owner(files[i * GROUP + j]))
        ids = await asyncio.gather(*futures)
        for id in ids:
            if len(id) > 0:
                future_gallery_items.append(id)
    print("DONE UPDATING, FOUND ", len(future_gallery_items), " items")
    gallery_items = future_gallery_items
    updating_task = None

async def update_gallery_items():
    global future_gallery_items
    global gallery_items
    global updating_task
    future_gallery_items = []

    print("UPDATING GALLERY ITEMS")
    if isinstance(storage_client, FileStorage):
        future_gallery_items = [x.replace(".json", "") for x in storage_client.list_json()]
    else:
        future_gallery_items = [x for x in storage_client.bucket.blob("gallery_sets.txt").download_as_text().split('\n') if len(x) > 0]
    print("DONE UPDATING, FOUND ", len(future_gallery_items), " items")
    gallery_items = future_gallery_items
    updating_task = None

@app.on_event("startup")
async def startup_event():
    global updating_task
    updating_task = asyncio.create_task(update_gallery_items())
    # asyncio.create_task(set_contract_promise)

@app.get("/gallery_items")
async def get_gallery_items():
    global updating_task
    if updating_task is None:
        updating_task = asyncio.create_task(update_gallery_items())
    return {
        "code": 200,
        "sets": gallery_items if len(gallery_items) > 0 else future_gallery_items
    }

import base64

from PIL import Image

class StoreSetRequest(BaseModel):
    owner: str
    token_id: str
    data: Dict[str, Any]
    message_hash: str
    signature: Tuple[int, int]
    image_base64: bytes

@app.post("/store_set")
async def store_set(set: StoreSetRequest):
    print("Into store Set")
    if CUSTOM_SET_ADDRESS == "":
        (owner,) = await (await get_set_contract()).functions["owner_of"].call(int(set.token_id, base=16))

        # NB: this is a data-race, as there may be pending transactions, but we'll ignore that for now.
        if owner != 0:
            # Check that we are the owner.
            # TODO: add ABI here.
            contract = await Contract.from_address(set.owner, client)
            (is_valid,) = await contract.functions["is_valid_signature"].call(hash=int(set.message_hash, base=16), sig=set.signature)
            if not is_valid:
                raise HTTPException(status_code=403, detail="Wrong signature for the public key.")
            if owner != set.owner:
                raise HTTPException(status_code=403, detail="You are not the owner of the NFT.")

    if len(set.image_base64) > 0:
        HEADER = b'data:image/png;base64,'
        if set.image_base64[0:len(HEADER)] != HEADER:
            raise HTTPException(status_code=403, detail="Only base-64 encoded PNGs are accepted.")
        if len(set.image_base64) > 1000 * 1000:
            raise HTTPException(status_code=403, detail="Image is too heavy, max size is 1MB")

        png_data = base64.decodebytes(set.image_base64[len(HEADER):])
        image = Image.open(io.BytesIO(png_data))

        if image.width > 1000 or image.height > 1000 or image.width < 10 or image.height < 10:
            raise HTTPException(status_code=403, detail="Image is too large, acceptable size range from 10x10 to 1000x1000")

        storage_client.store_image(path=set.token_id, data=png_data)

    # ERC 721 metadata compliance
    set.data["image"] = f"https://briq.construction/preview/{set.token_id}"
    set.data["description"] = "A set made of briqs"

    # Will overwrite, which is OK since we checked the owner.
    storage_client.store_json(path=set.token_id, data=set.data)

    return {
        "code": 200,
        "value": set.token_id
    }
