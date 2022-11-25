import io
import logging

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException

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
