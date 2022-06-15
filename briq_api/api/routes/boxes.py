import io

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException

from .. import boxes
from ..boxes import BoxRID

router = APIRouter()


@router.head("/box/data/{chain_id}/{theme_id}/{token_id}")
@router.head("/box/data/{chain_id}/{theme_id}/{token_id}.json")
@router.get("/box/data/{chain_id}/{theme_id}/{token_id}")
@router.get("/box/data/{chain_id}/{theme_id}/{token_id}.json")
async def box_data(chain_id: str, theme_id: str, token_id: str):
    rid = BoxRID(chain_id, theme_id, token_id)

    try:
        output = boxes.get_box_metadata(rid)
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public, max-age={2 * 60}"
    })


@router.head("/box/cover_item/{chain_id}/{theme_id}/{token_id}")
@router.head("/box/cover_item/{chain_id}/{theme_id}/{token_id}.png")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{token_id}")
@router.get("/box/cover_item/{chain_id}/{theme_id}/{token_id}.png")
async def box_cover_item(chain_id: str, theme_id: str, token_id: str):
    rid = BoxRID(chain_id, theme_id, token_id)

    try:
        image = boxes.get_box_cover_item(rid)
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")

    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box/step_image/{chain_id}/{theme_id}/{token_id}/{step}")
@router.head("/box/step_image/{chain_id}/{theme_id}/{token_id}/{step}.png")
@router.get("/box/step_image/{chain_id}/{theme_id}/{token_id}/{step}")
@router.get("/box/step_image/{chain_id}/{theme_id}/{token_id}/{step}.png")
async def box_step_image(chain_id: str, theme_id: str, token_id: str, step: int):
    rid = BoxRID(chain_id, theme_id, token_id)

    try:
        image = boxes.get_box_step_image(rid, step)
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")

    return StreamingResponse(io.BytesIO(image), media_type="image/png", headers={
        "Cache-Control": f"public, max-age={3600 * 24}"
    })


@router.head("/box_themes/list/{chain_id}")
@router.get("/box_themes/list/{chain_id}")
async def box_themes_list(chain_id: str):
    try:
        output = boxes.list_themes(chain_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not list themes")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public, max-age={2 * 60}"
    })
