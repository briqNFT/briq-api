import os
import json
import logging

# Imports the Google Cloud client library
from google.cloud import storage
# Imported by other files
from google.cloud.exceptions import NotFound as NotFoundException

from ..file_client import FileStorageBackend

logger = logging.getLogger(__name__)


class CloudStorage(FileStorageBackend):
    def __init__(self, bucket) -> None:
        self.storage_client = storage.Client()
        logger.info("Connecting cloud storage to bucket %s", bucket)
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

    def list_paths(self, path: str):
        """ Potentially slow method, take care. """
        # There seems to be a weird bug, but this should work.
        # See https://github.com/googleapis/python-storage/issues/294 for the for loop thing.
        results = self.storage_client.list_blobs(self.bucket, prefix=path, delimiter="/", timeout=5)
        for x in results.prefixes:
            pass
        return [result for result in [x.name[len(path):] for x in results] + [x[len(path):-1] for x in results.prefixes] if len(result) > 0]

    def store_bytes(self, path: str, data: bytes):
        logger.debug("Storing data to %s", path)
        self.bucket.blob(path).upload_from_string(data, content_type="application/octet-stream", timeout=10)
        return True

    def load_bytes(self, path: str):
        logger.debug("Loading data from %s", path)
        return self.bucket.blob(path).download_as_bytes()
