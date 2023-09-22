import logging
import secrets
import time
from typing import List

from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel

from briq_api.chain.rpcs import alchemy_endpoint

from fastapi import APIRouter
from briq_api.api.routes.common import ExceptionWrapperRoute

from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.utils.typed_data import TypedData

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))

auth_data = {}


def is_authenticated(session_id: str):
    return session_id in auth_data and auth_data[session_id]["authenticated"]


def is_admin(request: Request):
    session_id = request.state.session_id
    if not is_authenticated(session_id):
        raise HTTPException(status_code=401, detail="Not authorized.")
    data = auth_data[session_id]
    if data['verified_network'] == StarknetChainId.TESTNET.value:
        if data['verified_address'] in [
            0x03ef5b02bcc5d30f3f0d35d55f365e6388fe9501eca216cb1596940bf41083e2,
            0x044Fb5366f2a8f9f8F24c4511fE86c15F39C220dcfecC730C6Ea51A335BC99CB, 
        ]:
            return
    elif data['verified_network'] == StarknetChainId.MAINNET.value:
        if data['verified_address'] in [
            0x03ef5b02bcc5d30f3f0d35d55f365e6388fe9501eca216cb1596940bf41083e2,
            0x044Fb5366f2a8f9f8F24c4511fE86c15F39C220dcfecC730C6Ea51A335BC99CB, 
        ]:
            return
    raise HTTPException(status_code=401, detail="Not authorized.")


IsAdminDep = Depends(is_admin)


def issue_challenge(chainId: str, address: str):
    return {
        "types": {
            "StarkNetDomain": [
                {"name": "name", "type": "felt"},
                {"name": "version", "type": "felt"},
                {"name": "chainId", "type": "felt"},
            ],
            "SignatureChallenge": [
                {"name": "message", "type": "felt"},
                {"name": "address", "type": "felt"},
                {"name": "issuedAt", "type": "felt"},
                {"name": "expirationTime", "type": "felt"},
                {"name": "nonce", "type": "felt"},
                {"name": "version", "type": "felt"},
                {"name": "chainId", "type": "felt"},
            ],
        },
        "primaryType": "SignatureChallenge",
        "domain": {"name": "Sign in with starknet", "version": "1", "chainId": chainId},
        "message": {
            "message": "Sign in with starknet",
            "address": address,
            "issuedAt": int(time.time()),
            "expirationTime": int(time.time() + 60 * 60 * 24),
            "nonce": "0xdeadbeef",
            "version": "1",
            "chainId": chainId,
        },
    }


async def validate_challenge(typed_data, signature: List[str]):
    client = FullNodeClient(node_url=alchemy_endpoint["starknet-testnet"])
    contract = Contract(typed_data['message']['address'], [{
            "name": "is_valid_signature",
            "type": "function",
            "inputs": [
            {
                "name": "hash",
                "type": "felt"
            },
            {
                "name": "signature_len",
                "type": "felt"
            },
            {
                "name": "signature",
                "type": "felt*"
            }
            ],
            "outputs": [
            {
                "name": "is_valid",
                "type": "felt"
            }
            ],
            "stateMutability": "view"
        }
    ], client)
    signature_as_int = [int(x, 16) for x in signature]
    try:
        (value,) = await contract.functions["is_valid_signature"].call(
            TypedData.from_dict(typed_data).message_hash(int(typed_data['message']['address'], 16)), signature_as_int
        )
        return value == 1
    except:
        return False


def gen_session_id():
    return secrets.token_urlsafe(16)

@router.get("/start/{chain_id}/{address}")
def auth_start(chain_id: str, address: str, request: Request, response: Response):
    """Create a challenge, with some replay prevention, and return it to the user to be signed."""
    challenge = issue_challenge(hex(StarknetChainId.TESTNET.value), address)
    session_id = gen_session_id()

    if request.state.session_id and request.state.session_id in auth_data:
        del auth_data[request.state.session_id]
    request.state.session_id = session_id
    auth_data[session_id] = {
        "challenge": challenge,
        "authenticated": False,
    }
    return {
        "challenge": challenge,
    }


class AuthFinished(BaseModel):
    signature: List[str]


@router.post("/finish")
async def auth_finish(body: AuthFinished, request: Request):
    """Validate the challenge."""
    if request.state.session_id not in auth_data or "challenge" not in auth_data[request.state.session_id]:
        return HTTPException(status_code=401, detail="No challenge issued.")
    if is_authenticated(request.state.session_id):
        return "already authenticated"

    challenge = auth_data[request.state.session_id]["challenge"]
    signature = body.signature
    validation = await validate_challenge(challenge, signature)
    if not validation:
        return HTTPException(status_code=401, detail="Invalid signature.")
    auth_data[request.state.session_id]["authenticated"] = True
    auth_data[request.state.session_id]["verified_address"] = int(challenge["message"]["address"], 16)
    auth_data[request.state.session_id]["verified_network"] = int(challenge["message"]["chainId"], 16)
    del auth_data[request.state.session_id]["challenge"]
    return "authenticated"
