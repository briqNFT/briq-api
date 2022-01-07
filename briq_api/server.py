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

@app.post("/store_list")
@app.get("/store_list")
def store_list():
    return {
        "code": 200,
        "sets": storage_client.list_json()
    }

from starknet.contract import Contract
from starknet.net.client import Client

from starkware.crypto.signature.signature import verify
class StoreSetRequest(BaseModel):
    owner: str
    token_id: str
    data: Dict[str, Any]
    transaction_hash: str
    message_hash: str
    signature: Tuple[int, int]

@app.post("/store_set")
async def store_set(set: StoreSetRequest):
    # Fetch the public key from the account - this confirms that owner is indeed sending the message.
    client = Client("testnet")

    transaction_query = client.get_transaction(set.transaction_hash, None)

    # TODO: add ABI here.
    contract = await Contract.from_address(set.owner, client)
    (public_key,) = await contract.functions["get_signer"].call()
    signature_ok = verify(int(set.message_hash, base=16), set.signature[0], set.signature[1], int(public_key))
    if not signature_ok:
        raise HTTPException(status_code=403, detail="Wrong signature for the public key.")

    # Now we need to check that owner indeed has the right to define data for this token.
    transaction = await transaction_query

    # Wait for the transaction to be in a certain state.
    start = time.time()
    while transaction["status"] == 'RECEIVED' or transaction["status"] == 'NOT_RECEIVED':
        if time.time() - start > 60:
            raise HTTPException(status_code=503, detail="Timeout while trying to get transaction status")
        await asyncio.sleep(1)
        transaction = await client.get_transaction(set.transaction_hash, None)

    # Prelim check - that we didn't lie about the owner.
    if transaction["transaction"]["contract_address"] != set.owner:
        raise HTTPException(status_code=403, detail="Owner does not match transaction owner.")

    # Validate transaction arguments
    if int(transaction["transaction"]["calldata"][0]) != int("0x01618ffcb9f43bfd894eb4a176ce265323372bb4d833a77e20363180efca3a65", base=16):
        raise HTTPException(status_code=422, detail="Transaction not called on the set contract")

    if int(transaction["transaction"]["calldata"][4]) != int(set.token_id, base=16):
        raise HTTPException(status_code=422, detail="Transaction not called with the given token_id")

    if transaction["status"] != 'PENDING' and transaction["status"] != 'ACCEPTED_ON_L1' and transaction["status"] != 'ACCEPTED_ON_L2':
        raise HTTPException(status_code=500, detail="Transaction failed")

    # Will overwrite, which is OK
    storage_client.store_json(path=set.token_id, data=set.data)
    
    return {
        "code": 200,
        "value": set.token_id
    }
