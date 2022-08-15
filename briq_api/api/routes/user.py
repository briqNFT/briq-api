import io
import logging

from starlette.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException

from .. import user_api

logger = logging.getLogger(__name__)

router = APIRouter()


@router.head("/user/boxes/{chain_id}/{user_id}")
@router.get("/user/boxes/{chain_id}/{user_id}")
async def get_user_boxes(chain_id: str, user_id: str):
    try:
        return user_api.get_user_boxes(chain_id, user_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Error while loading data")


@router.head("/user/briqs/{chain_id}/{user_id}")
@router.get("/user/briqs/{chain_id}/{user_id}")
async def get_user_briqs(chain_id: str, user_id: str):
    try:
        return user_api.get_user_briqs(chain_id, user_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Error while loading data")
