import logging
import re
from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from briq_api.api.theme import list_booklets_of_theme

from briq_api.set_indexer.create_set_metadata import create_booklet_metadata, create_set_metadata

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


class NewNFTRequest(BaseModel):
    token_id: str
    data: dict[str, Any]
    preview_base64: bytes
    booklet_base64: bytes
    background_color: Optional[str] = None


@router.post("/admin/{chain_id}/{auction_theme}/validate_new_nft")
async def validate_new_nft(set: NewNFTRequest, chain_id: str, auction_theme: str):
    if auction_theme != "ducks_everywhere":
        raise HTTPException(status_code=400, detail="Invalid auction theme")

    booklets = list_booklets_of_theme(chain_id, auction_theme)

    metadata = create_set_metadata(
        token_id=set.token_id,
        name=set.data["name"],
        description=set.data["description"],
        network=chain_id,
        briqs=set.data["briqs"],
    )
    if set.background_color:
        metadata["backgroundColor"] = set.background_color
        # Check format matches 6 hex values without preceding #
        if not re.match(r"^[0-9a-fA-F]{6}$", set.background_color):
            raise HTTPException(status_code=400, detail="Invalid background color")

    return {
        "set_meta": metadata,
        "booklet_meta": create_booklet_metadata(
            theme_id=auction_theme,
            theme_name="Ducks Everywhere",
            theme_artist="OutSmth",
            theme_date="TODO",
            name=set.data["name"],
            description=set.data["description"],
            network=chain_id,
            briqs=set.data["briqs"],
            nb_steps=1001001,
            step_progress_data=[],
        ),
        "serial_number": len(booklets) + 1,
    }
