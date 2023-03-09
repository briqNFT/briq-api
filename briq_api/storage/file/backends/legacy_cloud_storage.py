import os
import json
import logging

# Imports the Google Cloud client library
from google.cloud import storage
# Imported by other files
from google.cloud.exceptions import NotFound as NotFoundException

from ....chain.networks import TESTNET_LEGACY

from ..file_client import FileStorageBackend

logger = logging.getLogger(__name__)

legacy_chain_id = TESTNET_LEGACY.id


class LegacyCloudStorage(FileStorageBackend):
    def __init__(self, bucket, path="") -> None:
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket)
        self.path = path

    def store_json(self, path, data):
        logger.debug("storing JSON at %s", path)
        path = path.replace(f'{legacy_chain_id}/', '').replace('_metadata', '')
        self.bucket.blob(self.path + path).upload_from_string(json.dumps(data), content_type='application/json', timeout=10)
        return True

    def load_json(self, path):
        logger.debug("loading JSON from %s", path)
        try:
            path = path.replace(f'{legacy_chain_id}/', '').replace('_metadata', '')
            return json.loads(self.bucket.blob(self.path + path).download_as_text())
        except NotFoundException:
            raise FileNotFoundError

    def has_json(self, path):
        path = path.replace(f'{legacy_chain_id}/', '').replace('_metadata', '')
        return self.bucket.blob(self.path + path).exists()

    def list_paths(self, path: str) -> list[str]:
        return []

    def store_bytes(self, path: str, data: bytes):
        logger.debug("Storing data to %s", path)
        path = path.replace(f'{legacy_chain_id}/', '')
        self.bucket.blob(self.path + path).upload_from_string(data, content_type="application/octet-stream", timeout=10)
        return True

    def load_bytes(self, path: str):
        logger.debug("Loading data from %s", path)
        path = path.replace(f'{legacy_chain_id}/', '')
        return self.bucket.blob(self.path + path).download_as_bytes()

    def has_path(self, path: str) -> bool:
        raise NotImplementedError()

    def backup_file(self, path: str):
        raise NotImplementedError()
