import os
import json

from .storage import IStorage
# Imports the Google Cloud client library
from google.cloud import storage

import logging
logger = logging.getLogger(__name__)

BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET') or 'test-bucket'

class CloudStorage(IStorage):
    def __init__(self) -> None:
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(BUCKET)
        self.path = "sets/"

    def store_json(self, path, data):
        logger.debug("storing JSON at %s", path)
        self.bucket.blob(self.path + path + ".json").upload_from_string(json.dumps(data), content_type='application/json', timeout=10)
        return True

    def load_json(self, path):
        logger.debug("loading JSON from %s", path)
        return json.loads(self.bucket.blob(self.path + path + ".json").download_as_text())

    def has_json(self, path):
        return self.bucket.blob(self.path + path + ".json").exists()

    def list_json(self):
        return [x.name.replace(self.path, "") for x in self.storage_client.list_blobs(self.bucket, prefix=self.path, timeout=5) if ".json" in x.name]

    def store_image(self, path: str, data: bytes):
        logger.debug("Storing image to %s", path)
        self.bucket.blob(self.path + path + ".png").upload_from_string(data, content_type='image/png', timeout=10)
        return True

    def load_image(self, path: str) -> bytes:
        logger.debug("loading image from %s", path)
        return self.bucket.blob(self.path + path + ".png").download_as_bytes()
