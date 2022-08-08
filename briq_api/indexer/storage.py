import logging

from pymongo import MongoClient

from briq_api.storage.client import StorageClient

from .config import INDEXER_ID, MONGO_URL, MONGO_PASSWORD, MONGO_USERNAME

logger = logging.getLogger(__name__)


class MongoStorage:
    def __init__(self, url=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_URL}", db_name=INDEXER_ID.replace("-", "_")) -> None:
        # TODO: separate reader/writer urls.
        try:
            self.mongo = MongoClient(url, serverSelectionTimeoutMS=3000)
            self.db = self.mongo[db_name]
            logger.debug("MongoDB server information: \n%(mongo)s", {"mongo": self.mongo.server_info()})
        except:
            logger.info("Could not connect to a mongo DB instance for indexing data")


mongo_storage = StorageClient()
mongo_storage.connect(MongoStorage())
