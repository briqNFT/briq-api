import logging
import os
import aiohttp

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from briq_api.memory_cache import CacheData

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))

alchemy_session = None
alchemy_endpoint = {
    'starknet-testnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-mainnet': "https://starknet-mainnet.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or "")
}


@CacheData.memory_cache(lambda chain_id, _, tx_hash: f'{chain_id}_{tx_hash}_rpc_tx_data', timeout=30)
async def get_rpc_tx_data(chain_id: str, data, tx_hash: str):
    async with alchemy_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()


@CacheData.memory_cache(lambda chain_id, _: f'{chain_id}_rpc_chain_id', timeout=3600)
async def get_rpc_chain_id(chain_id: str, data):
    async with alchemy_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()


@CacheData.memory_cache(lambda chain_id, _, entrypoint: f'{chain_id}_{entrypoint}_rpc_factory', timeout=60)
async def get_rpc_call_factory(chain_id: str, data, entrypoint: str):
    async with alchemy_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()


async def get_rpc_call(chain_id: str, data):
    async with alchemy_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()


@router.post("/node/{chain_id}/rpc")
async def post_rpc(chain_id: str, request: Request):
    body = await request.json()

    if body.get("method") == "starknet_getTransactionReceipt":
        tx_hash = body.get("params").get("transaction_hash")
        if len(tx_hash) < 3:
            raise HTTPException(status_code=400, detail="Invalid transaction hash")
        return await get_rpc_tx_data(chain_id, await request.body(), tx_hash)

    elif body.get("method") == "starknet_call":
        block = body.get("params").get("block_id")
        if block != "latest":
            raise HTTPException(status_code=400, detail="Only latest block is supported")
        contract_address = body.get("params").get("request").get("contract_address")
        if contract_address not in [
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # eth-usd contracts
            "0x0011ff172f1a9f3af71e77ef67036e81dcdb4c4d294d74bf5440d0d4c6ae61b7",  # testnet briq factory
            "0x05b021b6743c4f420e20786baa7fb9add1d711302c267afbc171252a74687376",  # mainnet briq factory
        ]:
            raise HTTPException(status_code=400, detail="Invalid contract address")
        if contract_address == '0x05b021b6743c4f420e20786baa7fb9add1d711302c267afbc171252a74687376':
            return await get_rpc_call_factory(chain_id, await request.body(), body.get("params").get("request").get("entry_point_selector"))
        return await get_rpc_call(chain_id, await request.body())

    elif body.get("method") == "starknet_chainId":
        return await get_rpc_chain_id(chain_id, await request.body())

    raise HTTPException(status_code=400, detail="Invalid method")


@router.on_event("startup")
async def on_startup():
    global alchemy_session
    alchemy_session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await alchemy_session.close()
