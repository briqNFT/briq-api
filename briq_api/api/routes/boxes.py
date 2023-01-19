import io
import logging
import time

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter

from .. import boxes, auctions
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
        "Cache-Control": f"public, max-age={3600}"
    })


@router.head("/booklet/pdf/{chain_id}/{theme_id}/{box_id}.pdf")
@router.get("/booklet/pdf/{chain_id}/{theme_id}/{box_id}.pdf")
async def booklet_pdf(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    pdf = boxes.get_booklet_pdf(rid)
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/booklet/texture/{chain_id}/{theme_id}/{box_id}")
@router.head("/booklet/texture/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/booklet/texture/{chain_id}/{theme_id}/{box_id}")
@router.get("/booklet/texture/{chain_id}/{theme_id}/{box_id}.png")
async def booklet_texture(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_texture(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })

@router.head("/box/texture/{chain_id}/{theme_id}/{box_id}")
@router.head("/box/texture/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/texture/{chain_id}/{theme_id}/{box_id}")
@router.get("/box/texture/{chain_id}/{theme_id}/{box_id}.png")
async def box_texture(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_texture(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_item/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_item(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_item(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_item/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_item_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_item_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_box/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_box/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_box(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_box(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_box/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_box/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_box_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_box_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.png")
@router.get("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.png")
async def box_cover_booklet(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_booklet(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.jpg")
@router.get("/box/cover_booklet/{chain_id}/{theme_id}/{box_id}.jpg")
async def box_cover_booklet_jpg(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_cover_booklet_jpg(rid)
    return StreamingResponse(io.BytesIO(image), media_type="image/jpeg", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}.png")
@router.get("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_image/{chain_id}/{theme_id}/{box_id}/{step}.png")
async def box_step_image(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_box_step_image(rid, step)
    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}.glb")
@router.get("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_glb/{chain_id}/{theme_id}/{box_id}/{step}.glb")
async def box_step_glb(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_step_glb(rid, step)[0]
    return StreamingResponse(io.BytesIO(image), media_type="model/gltf-binary", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}")
@router.head("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}.glb")
@router.get("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}")
@router.get("/box/step_glb_level/{chain_id}/{theme_id}/{box_id}/{step}.glb")
async def box_step_glb_level(chain_id: str, theme_id: str, box_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, box_id)
    image = boxes.get_booklet_step_glb(rid, step)[1]
    return StreamingResponse(io.BytesIO(image), media_type="model/gltf-binary", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/{chain_id}/{theme_id}/{quality}/cover.jpg")
@router.get("/{chain_id}/{theme_id}/{quality}/cover.jpg")
async def get_theme_cover(chain_id: str, theme_id: str, quality: str):
    data = boxes.get_theme_data(chain_id, theme_id)
    if data['sale_start'] is None or data['sale_start'] > time.time():
        output = boxes.box_storage.theme_cover_prelaunch(chain_id, theme_id, quality)
    else:
        output = boxes.box_storage.theme_cover_postlaunch(chain_id, theme_id, quality)
    return StreamingResponse(io.BytesIO(output), media_type="image/jpeg", headers={
        "Cache-Control": f"public, max-age={60 * 5}"
    })


@router.head("/{chain_id}/{theme_id}/{quality}/logo.png")
@router.get("/{chain_id}/{theme_id}/{quality}/logo.png")
async def get_theme_logo(chain_id: str, theme_id: str, quality: str):
    # Only in high quality, too cheap
    output = boxes.box_storage.theme_logo(chain_id, theme_id, 'high')
    return StreamingResponse(io.BytesIO(output), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={60 * 60 * 24 * 7}"
    })


@router.head("/{chain_id}/{theme_id}/{quality}/splash.jpg")
@router.get("/{chain_id}/{theme_id}/{quality}/splash.jpg")
async def get_theme_splash(chain_id: str, theme_id: str, quality: str):
    output = boxes.box_storage.theme_splash(chain_id, theme_id, quality)
    return StreamingResponse(io.BytesIO(output), media_type="image/jpeg", headers={
        "Cache-Control": f"public, max-age={60 * 60 * 24 * 7}"
    })


@router.head("/box_themes/list/{chain_id}")
@router.get("/box_themes/list/{chain_id}")
async def list_themes(chain_id: str):
    output = boxes.list_themes(chain_id)
    return JSONResponse(output, headers={
        "Cache-Control": f"public, max-age={60}"
    })


@router.head("/{chain_id}/{theme_id}/data")
@router.get("/{chain_id}/{theme_id}/data")
async def get_theme_data(chain_id: str, theme_id: str):
    output = boxes.get_theme_data(chain_id, theme_id)
    # Low cache for fast turnaround time but some minor CDN benefit
    return JSONResponse(output, headers={
        "Cache-Control": f"public, max-age={60}"
    })


@router.head("/{chain_id}/{theme_id}/boxes")
@router.get("/{chain_id}/{theme_id}/boxes")
async def list_boxes_of_theme(chain_id: str, theme_id: str):
    if theme_id == 'ducks_everywhere':
        return [f'ducks_everywhere/{i}' for i in range(1, 10)]
    data = boxes.get_theme_data(chain_id, theme_id)
    if data['sale_start'] is None or data['sale_start'] > time.time():
        output = []
    else:
        output = boxes.list_boxes_of_theme(chain_id, theme_id)
    # Turn off the caching client-side - this must update when the waves become active
    return output



@router.head("/{chain_id}/{theme_id}/saledata")
@router.get("/{chain_id}/{theme_id}/saledata")
async def get_box_saledata(chain_id: str, theme_id: str):
    theme_data = boxes.get_theme_data(chain_id, theme_id)
    box_list = boxes.list_boxes_of_theme(chain_id, theme_id)
    if theme_data['sale_start'] is None or theme_data['sale_start'] > time.time():
        return {}
    ret = {}
    for box in box_list:
        ret[box] = boxes.get_box_saledata(rid=BoxRID(chain_id, theme_id, box.split('/')[1]))
    # Turn off the caching client-side - this updates in real time
    return ret


@router.head("/box/data/{chain_id}/{theme_id}/{box_id}")
@router.head("/box/data/{chain_id}/{theme_id}/{box_id}.json")
@router.get("/box/data/{chain_id}/{theme_id}/{box_id}")
@router.get("/box/data/{chain_id}/{theme_id}/{box_id}.json")
async def box_data(chain_id: str, theme_id: str, box_id: str):
    rid = BoxRID(chain_id, theme_id, box_id)
    output = boxes.get_box_metadata(rid)
    return JSONResponse(output, headers={
        "Cache-Control": f"public, max-age={24 * 3600}"
    })


@router.head("/box/data_all/{chain_id}/{theme_id}")
@router.get("/box/data_all/{chain_id}/{theme_id}")
async def get_all_boxes_data(chain_id: str, theme_id: str):
    theme_data = boxes.get_theme_data(chain_id, theme_id)
    box_list = boxes.list_boxes_of_theme(chain_id, theme_id)
    if theme_data['sale_start'] is None or theme_data['sale_start'] > time.time():
        return {}
    ret = {}
    for box in box_list:
        ret[box] = boxes.get_box_metadata(rid=BoxRID(chain_id, theme_id, box.split('/')[1]))
    # Turn off the caching client-side - this must update when the waves become active
    return ret


@router.head("/box/get_transfer/{chain_id}/{theme_id}/{box_id}/{tx_hash}")
@router.get("/box/get_transfer/{chain_id}/{theme_id}/{box_id}/{tx_hash}")
async def get_box_transfer(chain_id: str, theme_id: str, box_id: str, tx_hash: str):
    return boxes.get_box_transfer(rid=BoxRID(chain_id, theme_id, box_id), tx_hash=tx_hash)
