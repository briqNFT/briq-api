import io
import logging

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter

from .. import boxes
from ..boxes import BoxRID

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


@router.head("/booklet/data/{chain_id}/{theme_id}/{booklet_id}")
@router.head("/booklet/data/{chain_id}/{theme_id}/{booklet_id}.json")
@router.get("/booklet/data/{chain_id}/{theme_id}/{booklet_id}")
@router.get("/booklet/data/{chain_id}/{theme_id}/{booklet_id}.json")
async def booklet_data(chain_id: str, theme_id: str, booklet_id: str):
    rid = BoxRID(chain_id, theme_id, booklet_id)
    output = boxes.get_booklet_metadata(rid)
    return JSONResponse(output, headers={
        "Cache-Control": f"public,max-age={3600}"
    })


@router.head("/booklet/pdf/{chain_id}/{theme_id}/{box_id}.pdf")
@router.get("/booklet/pdf/{chain_id}/{theme_id}/{box_id}.pdf")
async def booklet_pdf(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    pdf = boxes.get_booklet_pdf(rid)
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/booklet/texture/{chain_id}/{theme_id}/{box_id}")
@router.head("/booklet/texture/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/booklet/texture/{chain_id}/{theme_id}/{box_id}")
@router.get("/booklet/texture/{chain_id}/{theme_id}/{box_id}.png")
async def booklet_texture(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_texture(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })

@router.head("/box/texture/{chain_id}/{theme_id}/{box_id}")
@router.head("/box/texture/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/texture/{chain_id}/{theme_id}/{box_id}")
@router.get("/box/texture/{chain_id}/{theme_id}/{box_id}.png")
async def box_texture(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_texture(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_item/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_item(chain_id: str, theme_id: str, box_id: str):
    """Used as the preview of the NFT inside the box / when minting from the booklet"""
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_item(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_item/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_item_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_item_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_box/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_box/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_box(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_box(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_box/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_box/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_box_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_box_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_booklet(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_booklet(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_booklet_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_booklet_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}.png")
@router.get("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}.png")
async def box_step_image(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_step_image(rid, step)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}.glb")
@router.get("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}.glb")
async def box_step_glb(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_step_glb(rid, step)[0]
    return StreamingResponse(io.BytesIO(image), media_type="model/gltf-binary", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}.glb")
@router.get("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}.glb")
async def box_step_glb_level(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_step_glb(rid, step)[1]
    return StreamingResponse(io.BytesIO(image), media_type="model/gltf-binary", headers={
        "Cache-Control": f"public,max-age={3600 * 24}"
    })


@router.head("/box/data/{chain_id}/{theme_id}/{box_id}")
@router.head("/box/data/{chain_id}/{theme_id}/{box_id}.json")
@router.get("/box/data/{chain_id}/{theme_id}/{box_id}")
@router.get("/box/data/{chain_id}/{theme_id}/{box_id}.json")
async def box_data(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    output = boxes.get_box_metadata(rid)
    return JSONResponse(output, headers={
        "Cache-Control": f"public,max-age={24 * 3600}"
    })


@router.head("/box/get_transfer/{chain_id}/{theme_id}/{box_id}/{tx_hash}")
@router.get("/box/get_transfer/{chain_id}/{theme_id}/{box_id}/{tx_hash}")
async def get_box_transfer(chain_id: str, theme_id: str, box_id: str, tx_hash: str):
    return boxes.get_box_transfer(rid=BoxRID(chain_id, theme_id, box_id), tx_hash=tx_hash)
