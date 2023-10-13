import logging

from starlette.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from briq_api.stores import theme_storage
from briq_api.api.api import get_metadata, SetRID
from briq_api.api.boxes import get_box_metadata, BoxRID, get_booklet_metadata
from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


def box_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        box_id = theme_storage.get_box_id(chain_id, token_id).split('/')
    else:
        box_id = theme_storage.get_box_id(chain_id, hex(int(token_id))).split('/')
    return get_box_metadata(BoxRID(chain_id, *box_id))


def booklet_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        box_id = theme_storage.get_booklet_id_from_token_id(chain_id, token_id).split('/')
    else:
        box_id = theme_storage.get_booklet_id_from_token_id(chain_id, hex(int(token_id))).split('/')
    return get_booklet_metadata(BoxRID(chain_id, *box_id))


async def set_uri(chain_id: str, token_id: str):
    if '0x' in token_id or '0X' in token_id:
        set_id = token_id
    else:
        set_id = hex(int(token_id))
    return await get_metadata(SetRID(chain_id=chain_id, token_id=set_id))


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
        output = box_uri(chain_id, token_id)
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public,max-age={2 * 60}"
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
        output = booklet_uri(chain_id, token_id)
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public,max-age={2 * 60}"
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
        output = await set_uri(chain_id, token_id)
        output['image'] = output['image'].replace('//preview', '/v1/preview')
        output['animation_url'] = output['animation_url'].replace('//model', '/v1/model')
        output['external_url'] = f'https://briq.construction/set/starknet-mainnet/{output["id"]}'
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")

    return JSONResponse(output, headers={
        # TODO: bump cache for prod
        "Cache-Control": f"public,max-age={2 * 60}"
    })
