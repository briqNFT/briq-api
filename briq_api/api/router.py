import io
import json
import logging

from anyio import to_process
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from briq_api.mesh.briq import BriqData
from briq_api.set_identifier import SetRID
from briq_api.storage.file.backends.cloud_storage import NotFoundException
from . import api
from .routes import boxes, user

logger = logging.getLogger(__name__)

router = APIRouter()

router.include_router(boxes.router, tags=["box"])
router.include_router(user.router, tags=["user"])

@router.head("/metadata/{chain_id}/{token_id}")
@router.head("/metadata/{chain_id}/{token_id}.json")
@router.get("/metadata/{chain_id}/{token_id}")
@router.get("/metadata/{chain_id}/{token_id}.json")
async def metadata(chain_id: str, token_id: str):
    rid = SetRID(chain_id=chain_id, token_id=token_id)

    try:
        output = api.get_metadata(rid)
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")

    # Stream the data because files can get fairly hefty.
    out = io.StringIO()
    output = json.dump(output, out)
    out.seek(0)
    return StreamingResponse(out, media_type="application/json", headers={
        "Cache-Control": f"public, max-age={2 * 60}"
    })


@router.head("/preview/{chain_id}/{token_id}")
@router.head("/preview/{chain_id}/{token_id}.png")
@router.get("/preview/{chain_id}/{token_id}")
@router.get("/preview/{chain_id}/{token_id}.png")
async def preview(chain_id: str, token_id: str):
    rid = SetRID(chain_id=chain_id, token_id=token_id)

    try:
        preview = api.get_preview(rid)
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")

    return StreamingResponse(io.BytesIO(preview), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/model/{chain_id}/{token_id}.{kind}")
@router.get("/model/{chain_id}/{token_id}.{kind}")
async def model(chain_id: str, token_id: str, kind: str):
    mime_type = {
        "gltf": "model/gltf-binary",
        "glb": "model/gltf-binary",
        "vox": "application/octet-stream",
    }
    if kind not in mime_type:
        raise HTTPException(status_code=400, detail=f"Model kind {kind} is not supported")

    rid = SetRID(chain_id=chain_id, token_id=token_id)
    try:
        data = api.get_model(rid, kind)
    except (NotFoundException, OSError):
        try:
            metadata = api.get_metadata(rid)
            data = api.create_model(metadata, kind)
            api.store_model(rid, kind, data)
            logger.info("Created %(type)s model for %(rid)s on the fly.", {"type": kind, "rid": rid.json()})
        except Exception as e:
            logger.error(e, exc_info=e)
            raise HTTPException(status_code=500, detail="Error while creating model.")
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Error while fetching model.")

    return StreamingResponse(io.BytesIO(data), media_type=mime_type[kind], headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


class StoreSetRequest(BaseModel):
    chain_id: str
    token_id: str
    data: dict
    image_base64: bytes
    owner: str


@router.post("/store_set")
async def store_set(set: StoreSetRequest):
    # Attempt converting to GLTF but don't store it before it's first accessed.
    # Further, don't try .vox because that can fail somewhat spuriously.
    # (this is done to detect potential errors early)
    briq_data = BriqData().load(set.data)
    gltf_conv = to_process.run_sync(briq_data.to_gltf)

    # Ensure compliance of the metadata with ERC 721
    set.data["image"] = f"https://api.briq.construction/{router.prefix}/preview/{set.chain_id}/{set.token_id}.png"
    # Default to showing the GLB version of the mesh.
    set.data["animation_url"] = f"https://api.briq.construction/{router.prefix}/model/{set.chain_id}/{set.token_id}.glb"

    # Point to the builder.
    set.data["external_url"] = f"https://briq.construction/share?token_id={set.token_id}&chain_id={set.chain_id}&version=3"

    rid = SetRID(chain_id=set.chain_id, token_id=set.token_id)

    try:
        await gltf_conv
    except Exception as err:
        logger.warning("Error when converting the set data to 3D models. Set data: %(setdata)s", {"setdata": set.data}, exc_info=err)
        raise HTTPException(status_code=500, detail="Error when converting the set data to 3D models. Details: \n" + str(err))

    try:
        await api.store_set(rid, set.data, set.image_base64)
    except Exception as err:
        logger.error("Error saving JSON", exc_info=err)
        raise HTTPException(status_code=500, detail=str(err))

    logger.info("Stored new set %(rid)s for %(owner)s", {
        "rid": rid.json(),
        "owner": set.owner
    })


@router.head("/bids/user/{chain_id}/{user_id}")
@router.get("/bids/user/{chain_id}/{user_id}")
async def get_user_bids(chain_id: str, user_id: str):
    try:
        output = api.get_user_bids(chain_id, user_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Could not get user bids data")

    return output


@router.head("/bids/box/{chain_id}/{theme_name}/{box_name}")
@router.get("/bids/box/{chain_id}/{theme_name}/{box_name}")
async def get_bids_for_box(chain_id: str, theme_name: str, box_name: str):
    try:
        box_id = f"{theme_name}/{box_name}"
        output = api.get_bids_for_box(chain_id, box_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Could not get box bids data")

    return output

