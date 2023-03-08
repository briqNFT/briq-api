import asyncio
import logging
import requests

from pydantic import BaseModel
from typing import Any, Tuple

from .set_interaction import get_set_contract


logger = logging.getLogger(__name__)


class StoreSetRequest(BaseModel):
    owner: str
    token_id: str
    data: dict[str, Any]
    message_hash: str
    signature: tuple[int, int]
    image_base64: bytes


# TODO: move more stuff here
def store_set(set: StoreSetRequest):
    asyncio.create_task(trigger_hook_once_complete(set))


async def get_owner(token_id: str):
    set_contract = await get_set_contract()
    return (await set_contract.functions["ownerOf_"].call(int(token_id, 16))).owner


async def trigger_hook_once_complete(set: StoreSetRequest):
    # Realms only
    tries = 0
    try:
        if len(set.data["briqs"]) > 0 and all([briq["data"]["material"] == "0x2" for briq in set.data["briqs"]]):
            while True:
                if tries > 5:
                    logging.info("Realms web hook: no result after 5 minutes, assuming failure to mint for set %(token_id)s and user %(owner)s", {
                        "token_id": set.token_id,
                        "owner": set.owner
                    })
                    return
                if (await get_owner(set.token_id)) != int(set.owner, 16):
                    logging.info("Realms web hook waiting for set %(token_id)s and user %(owner)s", {
                        "token_id": set.token_id,
                        "owner": set.owner
                    })
                    tries += 1
                    await asyncio.sleep(60)
                else:
                    break

            requests.post(url="https://squire-25q7c.ondigitalocean.app/briq", json={
                "token_id": set.token_id,
                "minter": set.owner,
                "name": set.data["name"],
                "background_color": set.data["background_color"],
                "image": set.data["image"],
                "external_url": set.data["external_url"],
                "animation_url": set.data["animation_url"],
            })
            logging.info("Sent Realms web hook about set %(token_id)s and user %(owner)s", {
                "token_id": set.token_id,
                "owner": set.owner
            })
    except Exception as err:
        logging.warning(err, exc_info=err)
