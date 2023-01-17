import logging
from fastapi import APIRouter
from .. import auctions

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


@router.head("/{chain_id}/{auction_theme}/auction_data")
@router.get("/{chain_id}/{auction_theme}/auction_data")
async def get_theme_auction_data(chain_id: str, auction_theme: str):
    return auctions.get_theme_auction_data(chain_id, auction_theme)


@router.head("/{chain_id}/{auction_theme}/{auction_id}/bids")
@router.get("/{chain_id}/{auction_theme}/{auction_id}/bids")
async def get_auction_bids(chain_id: str, auction_theme: str, auction_id: str):
    return auctions.get_auction_bids(chain_id, auction_theme, auction_id)
