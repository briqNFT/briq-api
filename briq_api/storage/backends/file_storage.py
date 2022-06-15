import os
import json
import logging
import time
from pathlib import Path
from ..backend_interface import StorageBackend

logger = logging.getLogger(__name__)


class FileStorage(StorageBackend):
    """
    This storage backend is intended for local testing.
    It just stores data on the local computer filesystem.
    """
    def __init__(self, path="temp/", slowdown=0.0) -> None:
        self.path = path
        # Fake slowdown for testing
        self.slowdown = slowdown
        try:
            os.makedirs(self.path, exist_ok=True)
        except:
            logger.exception("Could not create folder at %(path)s", {"path": path})
            raise

    def ensure_path(self, path):
        # Create paths if necessary, we'll assume that's OK for debug usage.
        Path(self.path + path).parent.mkdir(parents=True, exist_ok=True)

    def store_json(self, path, data):
        logger.info("storing JSON")
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        with open(self.path + path, "w+") as f:
            json.dump(data, f)
        return True

    def load_json(self, path):
        logger.info("loading JSON")
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        with open(self.path + path, "r") as f:
            return json.load(f)

    def has_json(self, path):
        try:
            self.ensure_path(path)
            if self.slowdown:
                time.sleep(self.slowdown)
            with open(self.path + path, "r"):
                return True
        except:
            return False

    def list_json(self, path=""):
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        return [x for x in os.listdir(self.path + path) if x.endswith(".json")]

    def list_paths(self, path: str):
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        return [x for x in os.listdir(self.path + path) if x != ".DS_Store"]

    def iterate_files(self):
        self.ensure_path("")
        if self.slowdown:
            time.sleep(self.slowdown)
        for file in os.listdir(self.path):
            yield file

    # Bytes data

    def store_bytes(self, path: str, data: bytes):
        logger.info("Storing data to %s", path)
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        with open(self.path + path, "wb") as f:
            f.write(data)
        return True

    def load_bytes(self, path: str):
        logger.info("Loading data from %s", path)
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        with open(self.path + path, "rb") as f:
            return f.read()
