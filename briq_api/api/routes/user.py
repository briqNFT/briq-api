import logging

from fastapi import APIRouter
from pydantic import BaseModel

from briq_api.api import auctions

from .. import user_api

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


@router.head("/user/data/{chain_id}/{user_id}")
@router.get("/user/data/{chain_id}/{user_id}")
async def get_user_items(chain_id: str, user_id: str):
    return await user_api.get_user_items(chain_id, user_id)


@router.head("/user/briqs/{chain_id}/{user_id}")
@router.get("/user/briqs/{chain_id}/{user_id}")
async def get_user_briqs(chain_id: str, user_id: str):
    return await user_api.get_user_briqs(chain_id, user_id)


@router.head("/user/bids/{chain_id}/{auction_theme}/{user_id}")
@router.get("/user/bids/{chain_id}/{auction_theme}/{user_id}")
async def get_user_bids_auction(chain_id: str, auction_theme: str, user_id: str):
    return await auctions.get_user_bids(chain_id, auction_theme, user_id)


class UserBillingInfo(BaseModel):
    wallet_address: str
    outside_eu: bool
    eu_country: str


@router.post("/user/billing_country")
async def log_user_billing_country(data: UserBillingInfo):
    logger.info("User billing data: %(wallet_address)s %(outside_eu)s %(eu_country)s", data.dict())
