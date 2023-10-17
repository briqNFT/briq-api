from typing import Any
import aiohttp
import os

rpc_key = {
    'starknet-testnet': os.getenv("ALCHEMY_API_KEY_TESTNET") or "",
    'starknet-testnet-dojo': os.getenv("NETHERMIND_RPC_KEY_TESTNET") or "",
    'starknet-mainnet': os.getenv("ALCHEMY_API_KEY_MAINNET") or ""
}

alchemy_endpoint = {
    'starknet-testnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-testnet-dojo': "https://rpc.nethermind.io/goerli-juno/v0_4",
    'starknet-mainnet': "https://starknet-mainnet.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or "")
}

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


async def rpc_post(chain_id: str, data: Any):
    print("rpc_post", chain_id, rpc_key[chain_id])
    rpc_session.headers['x-apikey'] = rpc_key[chain_id]
    async with rpc_session.post(alchemy_endpoint[chain_id], data=data) as response:
        return await response.json()
