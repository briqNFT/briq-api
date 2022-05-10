from abc import abstractmethod
from typing import Dict, Iterable


class IStorage:
    def __init__(self) -> None:
        pass

    def store_json(self, path, data):
        pass

    @abstractmethod
    def load_json(self, path) -> Dict:
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
    def load_bytes(self, path_including_ext: str) -> bytes:
        pass

    @abstractmethod
    def store_image(self, path: str, data: bytes):
        pass

    @abstractmethod
    def load_image(self, path: str) -> bytes:
        pass
