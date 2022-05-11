from typing import Union
import logging
from briq_api.set_identifier import SetRID
from briq_api.storage.backend_interface import StorageBackend

logger = logging.getLogger(__name__)

SET_STORAGE_PREFIX = "sets/"


class StorageClient:
    def __init__(self):
        # Fallback backend.
        self.backend: Union[None, StorageBackend] = None
        # Backend for a specific chain. Higher priority than the fallback backend
        self.backend_for = {}

    def connect(self, backend: Union[None, StorageBackend]):
        self.backend = backend

    def connect_for_chain(self, chain_id: str, backend: Union[None, StorageBackend]):
        self.backend_for[chain_id] = backend

    def get_backend(self, chain_id: str) -> StorageBackend:
        # note: this on purpose returns None if that was explicitly specified.
        if chain_id in self.backend_for:
            if not self.backend_for[chain_id]:
                raise Exception(f"No available backend for {chain_id}")
            return self.backend_for[chain_id]
        if not self.backend:
            raise Exception(f"No available backend for {chain_id}")
        return self.backend

    ## Set Metadata
    def set_metadata_path(self, rid: SetRID):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}_metadata.json"

    def store_set_metadata(self, rid: SetRID, data: dict):
        self.get_backend(rid.chain_id).store_json(self.set_metadata_path(rid), data)

    def load_set_metadata(self, rid: SetRID) -> dict:
        return self.get_backend(rid.chain_id).load_json(self.set_metadata_path(rid))

    def has_set_metadata(self, rid: SetRID) -> bool:
        return self.get_backend(rid.chain_id).has_json(self.set_metadata_path(rid))

    ## Set Preview
    def set_preview_path(self, rid: SetRID):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}.png"

    def store_set_preview(self, rid: SetRID, data: bytes):
        self.get_backend(rid.chain_id).store_bytes(self.set_preview_path(rid), data)

    def load_set_preview(self, rid: SetRID) -> bytes:
        return self.get_backend(rid.chain_id).load_bytes(self.set_preview_path(rid))

    ## Set Model
    def set_model_path(self, rid: SetRID, kind: str):
        return f"{SET_STORAGE_PREFIX}{rid.chain_id}/{rid.token_id}.{kind}"

    def store_set_model(self, rid: SetRID, kind: str, data: bytes):
        self.get_backend(rid.chain_id).store_bytes(self.set_model_path(rid, kind), data)

    def load_set_model(self, rid: SetRID, kind: str) -> bytes:
        return self.get_backend(rid.chain_id).load_bytes(self.set_model_path(rid, kind))


# Main export, just import this. Note that no backend is configured by default.
storage_client = StorageClient()
