import logging
from abc import ABC, abstractmethod
from typing import Any
from briq_api.set_identifier import SetRID
from ..multi_backend_client import StorageClient

logger = logging.getLogger(__name__)

SET_STORAGE_PREFIX = "sets/"


class FileStorageBackend(ABC):

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
    def has_path(self, path: str) -> bool:
        pass

    @abstractmethod
    def backup_file(self, path: str):
        """Backup a file using an appropriate method for the backend."""
        pass

    @abstractmethod
    def store_bytes(self, path: str, data: bytes):
        pass

    @abstractmethod
    def load_bytes(self, path: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, path: str):
        pass


class FileClient(StorageClient[FileStorageBackend]):
    """
    This is basically a bare-bones ORM.
    TODO: This initially seemed like a good idea, but I think it's overall much more sensible
    to abstract at a much higher level, so this should be removed.
    """

    # Set Metadata
    def set_metadata_path(self, rid: SetRID):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}_metadata.json"

    def store_set_metadata(self, rid: SetRID, data: dict[str, Any]):
        self.get_backend(rid.chain_id).store_json(self.set_metadata_path(rid), data)

    def load_set_metadata(self, rid: SetRID) -> dict[str, Any]:
        return self.get_backend(rid.chain_id).load_json(self.set_metadata_path(rid))

    def has_set_metadata(self, rid: SetRID) -> bool:
        return self.get_backend(rid.chain_id).has_json(self.set_metadata_path(rid))

    # Set Preview
    def set_preview_path(self, rid: SetRID):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}.png"

    def store_set_preview(self, rid: SetRID, data: bytes):
        self.get_backend(rid.chain_id).store_bytes(self.set_preview_path(rid), data)

    def load_set_preview(self, rid: SetRID) -> bytes:
        return self.get_backend(rid.chain_id).load_bytes(self.set_preview_path(rid))

    # Set Model
    def set_model_path(self, rid: SetRID, kind: str):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}.{kind}"

    def store_set_model(self, rid: SetRID, kind: str, data: bytes):
        self.get_backend(rid.chain_id).store_bytes(self.set_model_path(rid, kind), data)

    def load_set_model(self, rid: SetRID, kind: str) -> bytes:
        return self.get_backend(rid.chain_id).load_bytes(self.set_model_path(rid, kind))
