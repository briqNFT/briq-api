import logging
import secrets
import time
from typing import List

from fastapi import Depends, HTTPException, Request, Response
from pydantic import BaseModel

from briq_api.chain.rpcs import alchemy_endpoint, get_rpc_session

from fastapi import APIRouter
from briq_api.api.routes.common import ExceptionWrapperRoute
from briq_api.config import ENV
from briq_api.stores import session_storage

from briq_api.chain.networks import MAINNET_DOJO, get_network_metadata
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.utils.typed_data import TypedData

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


def is_authenticated(session_id: str):
    data = session_storage.get_backend().load_json(session_id)
    try:
        return data["authenticated"] and data["expires_at"] > time.time()
    except:
        return False


def is_admin(request: Request):
    session_id = request.state.session_id
    if not is_authenticated(session_id):
        raise HTTPException(status_code=401, detail="Not authorized.")
    data = session_storage.get_backend().load_json(session_id)
    if data['verified_network'] == StarknetChainId.GOERLI.value:
        if data['verified_address'] in [
            0x03ef5b02bcc5d30f3f0d35d55f365e6388fe9501eca216cb1596940bf41083e2,  # wraitii
            0x044Fb5366f2a8f9f8F24c4511fE86c15F39C220dcfecC730C6Ea51A335BC99CB,
            0x009fa2C8FB501C57140E79fc720ab7160E9BBF41186d89eC45722A1d1Eb4D567,  # Alternative wraitii testnet wallet
            0x02ef9325a17d3ef302369fd049474bc30bfeb60f59cca149daa0a0b7bcc278f8,  # OutSmth Braavos
            0x0246db469dFfb4A5309E2BEBbf8eEC6AeA477D30724924949F7619D9C52A5888,  # OutSmth Argent X
        ]:
            return
    elif data['verified_network'] == StarknetChainId.MAINNET.value:
        if data['verified_address'] in [
            0x03ef5b02bcc5d30f3f0d35d55f365e6388fe9501eca216cb1596940bf41083e2,
            0x044Fb5366f2a8f9f8F24c4511fE86c15F39C220dcfecC730C6Ea51A335BC99CB,
            0x02ef9325a17d3ef302369fd049474bc30bfeb60f59cca149daa0a0b7bcc278f8,  # OutSmth Braavos
            0x0246db469dFfb4A5309E2BEBbf8eEC6AeA477D30724924949F7619D9C52A5888,  # OutSmth Argent X
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
    chain_id = int(typed_data["domain"]["chainId"], 16)
    if chain_id == MAINNET_DOJO.chain_id:
        chain_id = "starknet-mainnet-dojo"
    else:
        chain_id = "starknet-testnet-dojo"
    client = FullNodeClient(node_url=alchemy_endpoint[chain_id], session=get_rpc_session(chain_id))
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
    signature_as_int = [int(x, 16) if x.startswith("0x") else int(x) for x in signature]
    try:
        (value,) = await contract.functions["is_valid_signature"].call(
            TypedData.from_dict(typed_data).message_hash(int(typed_data['message']['address'], 16)), signature_as_int
        )
        return value == 1 or value == 370462705988
    except Exception as e:
        if ENV != "prod":
            logger.exception(e)
        return False


def gen_session_id():
    return secrets.token_urlsafe(16)

@router.get("/start/{chain_id}/{address}")
def auth_start(chain_id: str, address: str, request: Request, response: Response):
    """Create a challenge, with some replay prevention, and return it to the user to be signed."""
    challenge = issue_challenge(hex(get_network_metadata(chain_id).chain_id), address)
    session_id = gen_session_id()

    if request.state.session_id and session_storage.get_backend().has_json(request.state.session_id):
        session_storage.get_backend().delete(request.state.session_id)
    request.state.session_id = session_id
    session_storage.get_backend().store_json(session_id, {
        "challenge": challenge,
        "authenticated": False,
    })
    return {
        "challenge": challenge,
    }


class AuthFinished(BaseModel):
    signature: List[str]


@router.post("/finish")
async def auth_finish(body: AuthFinished, request: Request):
    """Validate the challenge."""
    if not session_storage.get_backend().has_json(request.state.session_id):
        return HTTPException(status_code=401, detail="No challenge issued.")
    data = session_storage.get_backend().load_json(request.state.session_id)
    if "challenge" not in data:
        return HTTPException(status_code=401, detail="No challenge issued.")
    if is_authenticated(request.state.session_id):
        return "already authenticated"

    challenge = data["challenge"]
    signature = body.signature
    validation = await validate_challenge(challenge, signature)
    if not validation:
        return HTTPException(status_code=401, detail="Invalid signature.")
    data["authenticated"] = True
    data["verified_address"] = int(challenge["message"]["address"], 16)
    data["verified_network"] = int(challenge["message"]["chainId"], 16)
    data["expires_at"] = int(time.time() + 60 * 60 * 24)
    del data["challenge"]
    session_storage.get_backend().store_json(request.state.session_id, data)
    return "authenticated"

@router.get("/check", dependencies=[IsAdminDep])
def check_authorized():
    return "ok"
