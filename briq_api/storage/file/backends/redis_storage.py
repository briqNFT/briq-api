import json
import logging
import redis

from ..file_client import FileStorageBackend

logger = logging.getLogger(__name__)


class RedisStorage(FileStorageBackend):
    def __init__(self, url: str) -> None:
        self.client = redis.Redis(host=url, port=6379, decode_responses=True)
        logger.info("Connecting redis storage to %s", url)

    def store_json(self, path, data):
        logger.debug("storing JSON at %s", path)
        self.client.set(path, json.dumps(data))

    def load_json(self, path):
        logger.debug("loading JSON from %s", path)
        try:
            data = self.client.get(path)
            if data is None:
                raise FileNotFoundError
            return json.loads(data)
        except:
            raise FileNotFoundError

    def has_json(self, path):
        return self.client.get(path) is not None

    def list_paths(self, path: str):
        raise NotImplementedError

    def has_path(self, path: str):
        return self.client.get(path) is not None

    def backup_file(self, path: str):
        raise NotImplementedError

    # Bytes stuff

    def store_bytes(self, path: str, data: bytes):
        logger.debug("Storing data to %s", path)
        self.client.set(path, data)

    def load_bytes(self, path: str):
        logger.debug("Loading data from %s", path)
        return self.client.get(path)

    def delete(self, path: str):
        logger.debug("Deleting %s", path)
        self.client.delete(path)
