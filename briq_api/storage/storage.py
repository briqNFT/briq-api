from abc import abstractmethod

import logging
from typing import Iterable
logger = logging.getLogger(__name__)

class IStorage:
    def __init__(self) -> None:
        pass
    
    def store_json(self, path, data):
        pass

    def load_json(self, path):
        pass

    def has_json(self, path):
        pass

    def list_json(self, path):
        pass

    @abstractmethod
    def iterate_files(self) -> Iterable:
        pass

    @abstractmethod
    def store_bytes(self, path_including_ext: str, data: bytes):
        pass

    @abstractmethod
    def load_bytes(self, path_including_ext: str):
        pass

    @abstractmethod
    def store_image(self, path: str, data: bytes):
        pass

    @abstractmethod
    def load_image(self, path: str) -> bytes:
        pass


def get_storage(path=None):
    try:
        from .cloud_storage import CloudStorage
        if path is not None:
            return CloudStorage(path)
        else:
            return CloudStorage()
    except:
        logger.warning("Falling back to local storage")
        from .file_storage import FileStorage
        if path is not None:
            return FileStorage(path)
        else:
            return FileStorage()
