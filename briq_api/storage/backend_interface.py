from abc import ABC, abstractmethod


class StorageBackend(ABC):

    @abstractmethod
    def store_json(self, path: str, data: dict):
        pass

    @abstractmethod
    def load_json(self, path: str) -> dict:
        pass

    @abstractmethod
    def has_json(self, path: str) -> bool:
        pass

    @abstractmethod
    def list_paths(self, path: str) -> list[str]:
        pass

    @abstractmethod
    def store_bytes(self, path: str, data: bytes):
        pass

    @abstractmethod
    def load_bytes(self, path: str) -> bytes:
        pass
