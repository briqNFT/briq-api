from dataclasses import dataclass
import logging

from pymongo import MongoClient
from ..chain.networks import get_network_metadata

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
            self.mongo = MongoClient(url, serverSelectionTimeoutMS=3000)
            self.db = self.mongo[db_name]
            logger.debug("MongoDB server information: \n%(mongo)s", {"mongo": self.mongo.server_info()})
        except:
            logger.info("Could not connect to a mongo DB instance for indexing data")


class MongoStorage(StorageClient[MongoBackend]):
    def get_available_boxes(self, chain_id: str, box_token_id: int) -> int:
        try:
            data = self.get_backend(chain_id).db["box_tokens"].find_one({
                "token_id": box_token_id.to_bytes(32, "big"),
                "owner": int(get_network_metadata(chain_id).auction_address, 16).to_bytes(32, "big"),
                "_chain.valid_to": None,
            })
            if data:
                return int.from_bytes(data['quantity'], "big")
            return 0
        except Exception as ex:
            logger.error(ex, exc_info=ex)
            raise

    def get_user_nfts(self, chain_id: str, user_id: str, collection: str) -> UserNFTs:
        try:
            data = self.get_backend(chain_id).db[collection + "_tokens"].find({
                "owner": int(user_id, 16).to_bytes(32, "big"),
                "_chain.valid_to": None,
            })
            block_nb = 0
            nft_list = []
            for nft in data:
                nft_list += [hex(int.from_bytes(nft['token_id'], "big"))] * int.from_bytes(nft['quantity'], "big")
                block_nb = max(block_nb, nft['updated_block'])
            return UserNFTs(block_nb, nft_list)
        except Exception as ex:
            logger.error(ex, exc_info=ex)
            raise

    def get_user_briqs(self, chain_id: str, user_id: str) -> list:
        try:
            data = self.get_backend(chain_id).db["briq_tokens"].find({
                "owner": int(user_id, 16).to_bytes(32, "big"),
                "_chain.valid_to": None,
            })
            return list(data)
        except Exception as ex:
            logger.error(ex, exc_info=ex)
            raise

    def get_transfer(self, chain_id: str, collection: str, tx_hash: str, box_token_id: int):
        try:
            transfer = self.get_backend(chain_id).db[f'{collection}_transfers'].find_one({
                "token_id": box_token_id.to_bytes(32, "big"),
                "_tx_hash": int(tx_hash, 16).to_bytes(32, "big"),
            })
            if transfer is None:
                return None
            return {
                "from": hex(int.from_bytes(transfer["from"], 'big')),
                "to": hex(int.from_bytes(transfer["to"], 'big')),
                "quantity": str(int.from_bytes(transfer["value"], 'big')),
                "timestamp": str(transfer['_timestamp'])
            }
        except Exception as ex:
            logger.error(ex, exc_info=ex)
        return None


mongo_storage = MongoStorage()
mongo_storage.connect(MongoBackend())
