from typing import Any
import aiohttp
import os
from briq_api.config import ENV

rpc_key = {
    'starknet-testnet': os.getenv("ALCHEMY_API_KEY_TESTNET") or "",
    'starknet-testnet-dojo': os.getenv("NETHERMIND_RPC_KEY_TESTNET") or "",
    'starknet-mainnet': os.getenv("ALCHEMY_API_KEY_MAINNET") or "",
    'starknet-mainnet-dojo': os.getenv("ALCHEMY_API_KEY_MAINNET") or "",
}

alchemy_endpoint = {
    'starknet-testnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-testnet-dojo': "https://rpc.nethermind.io/goerli-juno/v0_6",
    'starknet-mainnet': "https://starknet-mainnet.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or ""),
    'starknet-mainnet-dojo': "https://starknet-mainnet.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or ""),
}

if ENV == 'dev':
    rpc_key['starknet-mainnet-dojo'] = os.getenv("NETHERMIND_RPC_KEY_TESTNET") or ""
    alchemy_endpoint['starknet-mainnet-dojo'] = "https://rpc.nethermind.io/mainnet-juno/v0_6"

rpc_session: aiohttp.ClientSession = None

def setup_rpc_session():
    global rpc_session
    if rpc_session is None:
        rpc_session = aiohttp.ClientSession()


async def end_rpc_session():
    global rpc_session
    if rpc_session is not None:
        await rpc_session.close()
        rpc_session = None


def get_rpc_session(chain_id: str):
    global rpc_session
    rpc_session.headers['x-apikey'] = rpc_key[chain_id]
    return rpc_session


async def rpc_post(chain_id: str, data: Any):
    rpc_session.headers['x-apikey'] = rpc_key[chain_id]
    async with rpc_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()
