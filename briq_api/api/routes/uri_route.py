import logging

from starlette.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from .. import uri_api

logger = logging.getLogger(__name__)

router = APIRouter()

@router.head("/uri/box/{chain_id}/{token_id}")
@router.head("/uri/box/{chain_id}/{token_id}.json")
@router.get("/uri/box/{chain_id}/{token_id}")
@router.get("/uri/box/{chain_id}/{token_id}.json")
async def uri_box(chain_id: str, token_id: str):
    """
        Return the Token URI for a given box token.
        Note that token_id can be base 10 or base 16 (done for convenience on-chain).
    """
    try:
        output = uri_api.box_uri(chain_id, token_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public, max-age={2 * 60}"
    })


@router.head("/uri/booklet/{chain_id}/{token_id}")
@router.head("/uri/booklet/{chain_id}/{token_id}.json")
@router.get("/uri/booklet/{chain_id}/{token_id}")
@router.get("/uri/booklet/{chain_id}/{token_id}.json")
async def uri_booklet(chain_id: str, token_id: str):
    """
        Return the Token URI for a given booklet token.
        Note that token_id can be base 10 or base 16 (done for convenience on-chain).
    """
    try:
        output = uri_api.booklet_uri(chain_id, token_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public, max-age={2 * 60}"
    })

@router.head("/uri/set/{chain_id}/{token_id}")
@router.head("/uri/set/{chain_id}/{token_id}.json")
@router.get("/uri/set/{chain_id}/{token_id}")
@router.get("/uri/set/{chain_id}/{token_id}.json")
async def uri_set(chain_id: str, token_id: str):
    """
        Return the Token URI for a given set token.
        Note that token_id can be base 10 or base 16 (done for convenience on-chain).
    """
    try:
        output = uri_api.set_uri(chain_id, token_id)
    except Exception as e:
        logger.debug(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public, max-age={2 * 60}"
    })
