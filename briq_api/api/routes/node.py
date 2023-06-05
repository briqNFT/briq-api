import logging
import os
import aiohttp

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))

alchemy_session = None
alchemy_endpoint = {
    'starknet-testnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-mainnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or "")
}

@router.post("/node/{chain_id}/rpc")
async def post_rpc(chain_id: str, request: Request):
    async with alchemy_session.post(alchemy_endpoint[chain_id], data=await request.body()) as response:
        # Return with some minor caching, hoping the CDNs will lift some weight of our shoulders
        return JSONResponse(await response.json(), headers={
            "Cache-Control": f"public,max-age={60 * 2}"
        })


@router.on_event("startup")
async def on_startup():
    global alchemy_session
    alchemy_session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await alchemy_session.close()
