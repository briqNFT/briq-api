from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import asyncio
import time

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

import base64

from starknet_py.contract import Contract
from starknet_py.net.client import Client
from starkware.crypto.signature.signature import verify

from PIL import Image

class StoreSetRequest(BaseModel):
    owner: str
    token_id: str
    data: Dict[str, Any]
    message_hash: str
    signature: Tuple[int, int]
    image_base64: bytes

client = Client("testnet")
get_set_contract = Contract.from_address("0x01618ffcb9f43bfd894eb4a176ce265323372bb4d833a77e20363180efca3a65", client)
set_contract = None

@app.post("/store_set")
async def store_set(set: StoreSetRequest):
    global set_contract
    # Fetch the public key from the account - this confirms that owner is indeed sending the message.
    if set_contract is None:
        set_contract = await get_set_contract
    (owner,) = await set_contract.functions["owner_of"].call(int(set.token_id, base=16))

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
