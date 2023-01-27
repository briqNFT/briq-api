from datetime import datetime
import logging

from starlette.responses import JSONResponse
from fastapi import APIRouter
from briq_api.indexer.storage import mongo_storage

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


forest_data = {
    "last_update": 0,
    "data": {}
}


@router.head("/forest/{chain_id}/full_data")
@router.get("/forest/{chain_id}/full_data")
async def get_forest_data(chain_id: str):
    print(datetime.now().timestamp(), forest_data["last_update"] + 5 * 60)
    if datetime.now().timestamp() < forest_data["last_update"] + 5 * 60:
        return JSONResponse(forest_data["data"], headers={
            "Cache-Control": f"public, max-age={5*60}"
        })

    trees = mongo_storage.get_backend(chain_id).db["booklet_tokens"].find({
        "token_id": ((2**192 * 10) + 1).to_bytes(32, "big"),
        "_chain.valid_to": None,
    })
    potential_sets = []
    for tree in trees:
        potential_sets.append(tree["owner"])

    out = {}
    for token_id in potential_sets:
        actual_set = mongo_storage.get_backend(chain_id).db["set_tokens"].find_one({
            "token_id": token_id,
            "_chain.valid_to": None,
        })
        if not actual_set:
            continue
        age = datetime.now().timestamp() - actual_set['updated_at'].timestamp()
        out[hex(int.from_bytes(token_id, "big"))] = {
            "age": round(age),
            "owner": hex(int.from_bytes(actual_set["owner"], "big")),
        }
    forest_data["data"] = out
    forest_data["last_update"] = datetime.now().timestamp()
    return JSONResponse(out, headers={
        "Cache-Control": f"public, max-age={5*60}"
    })
