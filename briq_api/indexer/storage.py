from dataclasses import dataclass
import logging
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from briq_api.indexer.events.common import decode_bytes, encode_int_as_bytes
from ..chain.networks import TESTNET, get_network_metadata

from briq_api.config import ENV
from briq_api.storage.multi_backend_client import StorageClient

from .config import INDEXER_ID, MONGO_URL, MONGO_PASSWORD, MONGO_USERNAME

logger = logging.getLogger(__name__)


@dataclass
class UserNFTs:
    last_block: int
    nfts: list[str]


class MongoBackend:
    def __init__(self, url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}", db_name=INDEXER_ID.replace("-", "_")) -> None:
        # TODO: separate reader/writer urls.
        try:
            self.mongo = MongoClient(url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, timeoutMS=3000)
            self.db = self.mongo[db_name]
            self.db["briq_tokens"].create_index("owner")
            self.db["set_tokens"].create_index("owner")
            self.db["booklet_tokens"].create_index("owner")
            self.db["box_tokens"].create_index("owner")
            self.db["briq_transfers"].create_index("token_id")
            self.db["set_transfers"].create_index("token_id")

            self.async_mongo = AsyncIOMotorClient(url)
            self.async_db = self.async_mongo[db_name]

            logger.debug("MongoDB server information: \n%(mongo)s", {"mongo": self.mongo.server_info()})
        except:
            if ENV == "prod":
                raise Exception("Could not connect to a mongo DB instance for indexing data")
            else:
                logger.warning("Could not connect to a mongo DB instance for indexing data")


class MongoStorage(StorageClient[MongoBackend]):
    async def get_available_boxes(self, chain_id: str, box_token_id: int) -> int:
        data = await self.get_backend(chain_id).async_db["box_tokens"].find_one({
            "token_id": box_token_id.to_bytes(32, "big"),
            "owner": int(get_network_metadata(chain_id).auction_address, 16).to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        if data:
            return int.from_bytes(data['quantity'], "big")
        return 0

    async def get_bought_boxes(self, chain_id: str, box_token_id: int) -> int:
        data = await self.get_backend(chain_id).async_db["box_pending_tokens"].find_one({
            "token_id": box_token_id.to_bytes(32, "big"),
            "owner": int(get_network_metadata(chain_id).auction_address, 16).to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        if data:
            return int.from_bytes(data['quantity'], "big")
        return 0

    async def get_user_nfts(self, chain_id: str, user_id: str, collection: str) -> UserNFTs:
        data = self.get_backend(chain_id).async_db[collection + "_tokens"].find({
            "owner": int(user_id, 16).to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        block_nb = 0
        nft_list = []
        async for nft in data:
            nft_list += [hex(int.from_bytes(nft['token_id'], "big"))] * int.from_bytes(nft['quantity'], "big")
            block_nb = max(block_nb, nft['updated_block'])
        return UserNFTs(block_nb, nft_list)

    async def get_mint_burn_dates(self, chain_id: str, collection: str, token_id: int):
        mint = self.get_backend(chain_id).async_db[collection + "_transfers"].find_one({
            "from": (0).to_bytes(32, "big"),
            "token_id": token_id.to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        burn = self.get_backend(chain_id).async_db[collection + "_transfers"].find_one({
            "to": (0).to_bytes(32, "big"),
            "token_id": token_id.to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        try:
            return (await mint)['_timestamp'].timestamp(), (await burn)['_timestamp'].timestamp()
        except:
            return -1, -1

    async def get_user_briqs(self, chain_id: str, user_id: str) -> list[Any]:
        data = self.get_backend(chain_id).async_db["briq_tokens"].find({
            "owner": int(user_id, 16).to_bytes(32, "big"),
            "_chain.valid_to": None,
        })
        return await data.to_list(None)


mongo_storage = MongoStorage()
