import os
import json
import logging
import shutil
import time
from pathlib import Path
from uuid import uuid1
from ..file_client import FileStorageBackend

logger = logging.getLogger(__name__)


class FileStorage(FileStorageBackend):
    """
    This storage backend is intended for local testing.
    It just stores data on the local computer filesystem.
    """
    def __init__(self, path="temp/", ensure_paths=False, slowdown=0.0) -> None:
        self.path = path
        self.ensure_paths = ensure_paths
        # Fake slowdown for testing
        self.slowdown = slowdown
        try:
            os.makedirs(self.path, exist_ok=True)
        except:
            logger.exception("Could not create folder at %(path)s", {"path": path})
            raise

    def ensure_path(self, path):
        if self.ensure_paths:
            Path(self.path + path).parent.mkdir(parents=True, exist_ok=True)

    def store_json(self, path, data):
        logger.info("storing JSON")
        self.ensure_path(path)
        if self.slowdown:
            time.sleep(self.slowdown)
        with open(self.path + path, "w+") as f:
            json.dump(data, f)

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

    def has_path(self, path: str):
        if self.slowdown:
            time.sleep(self.slowdown)
        return os.path.exists(self.path + path)

    def backup_file(self, path: str):
        # Backup a file by making a timestamped copy on disk
        if self.slowdown:
            time.sleep(self.slowdown)
        if os.path.exists(self.path + path):
            # This errors if the destination file already exists so it's safe enough
            shutil.copy2(src=self.path + path, dst=self.path + path + f".{uuid1().hex}")

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
