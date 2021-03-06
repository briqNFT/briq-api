import os
import json
import logging

# Imports the Google Cloud client library
from google.cloud import storage
# Imported by other files
from google.cloud.exceptions import NotFound as NotFoundException

from ..backend_interface import StorageBackend

logger = logging.getLogger(__name__)


class CloudStorage(StorageBackend):
    def __init__(self, bucket) -> None:
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket)

    def store_json(self, path, data):
        logger.debug("storing JSON at %s", path)
        self.bucket.blob(path).upload_from_string(json.dumps(data), content_type='application/json', timeout=10)
        return True

    def load_json(self, path):
        logger.debug("loading JSON from %s", path)
        try:
            return json.loads(self.bucket.blob(path).download_as_text())
        except NotFoundException:
            raise FileNotFoundError

    def has_json(self, path):
        return self.bucket.blob(path).exists()

    def store_bytes(self, path: str, data: bytes):
        logger.debug("Storing data to %s", path)
        self.bucket.blob(path).upload_from_string(data, content_type="application/octet-stream", timeout=10)
        return True

    def load_bytes(self, path: str):
        logger.debug("Loading data from %s", path)
        return self.bucket.blob(path).download_as_bytes()
