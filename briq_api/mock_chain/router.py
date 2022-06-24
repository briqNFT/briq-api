import logging
from typing import List
from unittest import mock

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starkware.starknet.public.abi import get_selector_from_name

from briq_api.storage.client import storage_client

logger = logging.getLogger(__name__)

router = APIRouter()

mock_user = {
    "available_boxes": [
        int("0xb0a001", 16), int("0xb0a001", 16), int("0xb0a002", 16),
        int("0xb0a001", 16), int("0xb0a001", 16), int("0xb0a002", 16),
        int("0xb0a001", 16), int("0xb0a001", 16), int("0xb0a002", 16),
    ],
    "opened_boxes": [],
}

BOX_CONTRACT = 0xD

class getUnopenedBoxesCall(BaseModel):
    owner: str

@router.post("/getUnopenedBoxes")
async def getUnopenedBoxes(body: getUnopenedBoxesCall):
    return [hex(x) for x in mock_user['available_boxes']]


class ContractCall(BaseModel):
    calldata: List[str]
    contract_address: str
    entry_point_selector: str
    signature: List[str]


@router.post("/feeder_gateway/call_contract")
async def call_contract(body: ContractCall):
    if body.contract_address == '0xA':
        # briq contract
        if int(body.entry_point_selector, 16) == get_selector_from_name('fullBalanceOf_'):
            return {'result': ['0x4', '0x1', '0x141', '0x3', '0x143', '0x4', '0x144', '0x5', '0x145']}

    elif body.contract_address == '0xB':
        if int(body.entry_point_selector, 16) == get_selector_from_name('balanceDetailsOf_'):
            # Load local sets.
            sets = storage_client.get_backend('mock').list_json("sets/mock/")
            return {'result': [hex(len(sets)), *[x.replace('_metadata.json', '') for x in sets]]}
            #return {'result': ['0x0']}
        elif int(body.entry_point_selector, 16) == get_selector_from_name('ownerOf_'):
            return {'result': ['0x0']}

    elif body.contract_address == '0xcafebabe':
        if int(body.entry_point_selector, 16) == get_selector_from_name('get_nonce'):
            return {'result': ['0x1']}
        return {'result': ['0x0']}

    raise HTTPException(status_code=500)


@router.post("/gateway/add_transaction")
async def add_transaction(body: ContractCall):
    nb_calls = body.calldata[0]
    contract = int(body.calldata[1])
    selector = int(body.calldata[2])
    args_len = int(body.calldata[5])
    args = [int(x) for x in body.calldata[6:6 + args_len]]
    nonce = body.calldata[-1]
    # print(hex(contract), hex(selector), args, nonce)

    if contract == BOX_CONTRACT and selector == get_selector_from_name('unbox_'):
        mock_user['available_boxes'].remove(args[1])
        mock_user['opened_boxes'].append(args[1])

    return {'transaction_hash': '0xfadedead'}


@router.get("/feeder_gateway/get_transaction_status")
def get_transaction_status():
    return {'tx_status': 'RECEIVED'}


@router.get("/feeder_gateway/get_transaction")
def get_transaction():
    return {'tx_status': 'RECEIVED'}



@router.post("/feeder_gateway/estimate_fee")
async def estimate_fee():
    return {'result': ['0x1']}


@router.get("/feeder_gateway/get_contract_addresses")
def get_contract_addresses():
    return {}


@router.get("/feeder_gateway/get_code")
def get_code():
    return {
        'abi': [],
        'bytecode': ["0x40780017fff7fff"],
    }
