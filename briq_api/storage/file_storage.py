import os
import json

from pydantic.errors import PathError

from .storage import IStorage

import logging
logger = logging.getLogger(__name__)

class FileStorage(IStorage):
    def __init__(self) -> None:
        self.path = 'temp/'
        try:
            os.mkdir(self.path)
        except:
            pass

    def store_json(self, path, data):
        logger.info("storing JSON")
        with open(self.path + path + ".json", "w+") as f:
            json.dump(data, f)
        return True

    def load_json(self, path):
        logger.info("loading JSON")
        with open(self.path + path + ".json", "r") as f:
            return json.load(f)

    def has_json(self, path):
        try:
            with open(self.path + path + ".json", "r"):
                return True
        except:
            return False

    def list_json(self):
        return [x for x in os.listdir(self.path) if x.endswith(".json")]


    def store_image(self, path: str, data: bytes):
        logger.info("storing image to %s", path)
        with open(self.path + path + ".png", "wb+") as f:
            f.write(data)
        return True


    def load_image(self, path: str):
        logger.info("loading image at %s", path)
        with open(self.path + path + ".png", "rb") as f:
            return f.read()