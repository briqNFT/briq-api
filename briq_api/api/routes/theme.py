import io
import logging
import time

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter

from .. import boxes
from ..boxes import BoxRID

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


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
