import logging

from fastapi import APIRouter, HTTPException

from .. import api
from . import boxes, user, uri_route, forest, auctions as auctions_route, set as set_routes, theme, admin

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger=logger))

router.include_router(boxes.router, tags=["box"])
router.include_router(user.router, tags=["user"])
router.include_router(uri_route.router, tags=["uri"])
router.include_router(forest.router, tags=["briqmas_forest"])
router.include_router(auctions_route.router, tags=["auctions"])
router.include_router(set_routes.router, tags=["set"])
router.include_router(theme.router, tags=["theme"])
router.include_router(admin.router, tags=["admin"])


@router.head("/bids/user/{chain_id}/{user_id}")
@router.get("/bids/user/{chain_id}/{user_id}")
async def get_user_bids(chain_id: str, user_id: str):
    output = api.get_user_bids(chain_id, user_id)

    return output


@router.head("/bids/box/{chain_id}/{theme_name}/{box_name}")
@router.get("/bids/box/{chain_id}/{theme_name}/{box_name}")
async def get_bids_for_box(chain_id: str, theme_name: str, box_name: str):
    box_id = f"{theme_name}/{box_name}"
    output = api.get_bids_for_box(chain_id, box_id)

    return output


@router.head("/activity/set/{chain_id}/{set_id}")
@router.get("/activity/set/{chain_id}/{set_id}")
async def get_set_activity(chain_id: str, set_id: str):
    return await get_item_activity("set", chain_id, set_id)


@router.head("/activity/{item_kind}/{chain_id}/{theme}/{item}")
@router.get("/activity/{item_kind}/{chain_id}/{theme}/{item}")
async def get_other_activity(item_kind: str, chain_id: str, theme: str, item: str):
    return await get_item_activity(item_kind, chain_id, f"{theme}/{item}")


async def get_item_activity(item_type: str, chain_id: str, item: str):
    if item_type != 'box' and item_type != 'booklet' and item_type != 'set':
        raise HTTPException(status_code=400, detail="Item type is invalid")

    try:
        output = api.get_item_activity(item_type, chain_id, item)
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Could not get item activity")

    return output
