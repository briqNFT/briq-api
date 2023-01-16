import io
import logging

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException

from briq_api.api import auctions

from .. import user_api

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


@router.head("/user/data/{chain_id}/{user_id}")
@router.get("/user/data/{chain_id}/{user_id}")
async def get_user_items(chain_id: str, user_id: str):
    return user_api.get_user_items(chain_id, user_id)


@router.head("/user/briqs/{chain_id}/{user_id}")
@router.get("/user/briqs/{chain_id}/{user_id}")
async def get_user_briqs(chain_id: str, user_id: str):
    return user_api.get_user_briqs(chain_id, user_id)


@router.head("/user/bids/{chain_id}/{auction_theme}/{user_id}")
@router.get("/user/bids/{chain_id}/{auction_theme}/{user_id}")
async def get_user_bids_auction(chain_id: str, auction_theme: str, user_id: str):
    return auctions.get_user_bids(chain_id, auction_theme, user_id)
