from abc import abstractmethod

import logging
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

    def store_image(self, path: str, data: bytes):
        pass

    @abstractmethod
    def load_image(self, path: str) -> bytes:
        pass

def get_storage():
    try:
        from .cloud_storage import CloudStorage
        return CloudStorage()
    except:
        from .file_storage import FileStorage
        logger.warning("Falling back to local storage")
        return FileStorage()
