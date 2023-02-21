"""
The purpose of this script is to read on-chain data for sets
and store them in our backend, making sure that things fit.

It is not considered a huge deal if it fails to pick up some sets,
as those can be corrected manually.

Its main goal is to keep workload light.
This is achieved by regularly running an async task in the server, for simplicity.
"""

from dataclasses import dataclass
import logging
from typing import Any, Dict, Union
import requests
from briq_api.chain.networks import get_network_metadata
from briq_api.set_indexer.create_set_metadata import create_set_metadata
from briq_api.storage.file.file_client import FileClient

from briq_api.config import ENV

from briq_api.set_identifier import SetRID

logger = logging.getLogger(__name__)


@dataclass
class StorableSetData:
    name: str
    description: str
    briqs: Any


class SetIndexer:
    network: str
    pending: Dict[str, Union[StorableSetData, None]] = {}
    storage: FileClient

    def __init__(
        self,
        network: str,
        storage: FileClient,
    ):
        self.network = network
        self.storage = storage

    def add_set_to_pending(self, token_id: str, data: Union[StorableSetData, None] = None):
        self.pending[token_id] = data

    def process_pending_set(self):
        if len(self.pending) == 0:
            return
        token_id = list(self.pending.keys())[0]
        self.store_set(token_id)

    def store_set(self, token_id: str):
        if token_id not in self.pending:
            logger.warn(
                'store_set called with set token %(token)s but this set is not in the pending list',
                {"token": token_id}
            )
            return
        data = self.pending[token_id]
        # Drop the key from the pending items
        self.pending.pop(token_id, None)

        if data is None:
            logger.warn('store_set called with set token %(token)s but no pending data', {"token": token_id})
            return

        if self.storage.has_set_metadata(SetRID(chain_id=self.network, token_id=token_id)):
            return self._verify_correct_storage(data, token_id)
        return self._store_set(data, token_id)

    def _get_storage_data(self, data: StorableSetData, token_id: str) -> dict[str, Any]:
        return create_set_metadata(
            token_id=token_id,
            name=data.name or token_id,
            description=data.description or "",
            network=self.network,
            briqs=data.briqs
        )

    def _compare_storage(self, expected_data: dict[str, Any], stored_data: dict[str, Any]):
        passes = True
        mistake = ""
        for key in expected_data:
            mistake = key
            if key == "briqs":
                if len(stored_data[key]) != len(expected_data[key]):
                    passes = False
                    return passes, mistake
                # Ignore the order of stored briqs for now be cause it is inconsistent
                # So just store according to what expected_data does (which is what transactions do)
                sorted_briqs = sorted(stored_data[key], key=lambda x: x['pos'])
                for i in range(len(sorted_briqs)):
                    if (sorted_briqs[i]['pos'][0] != expected_data[key][i]['pos'][0]
                            or sorted_briqs[i]['pos'][1] != expected_data[key][i]['pos'][1]
                            or sorted_briqs[i]['pos'][2] != expected_data[key][i]['pos'][2]
                            or sorted_briqs[i]['data']["color"].lower() != expected_data[key][i]['data']["color"].lower()
                            or sorted_briqs[i]['data']["material"] != expected_data[key][i]['data']["material"]):
                        passes = False
                        return passes, mistake
            elif stored_data[key] != expected_data[key]:
                passes = False
                return passes, mistake
        return passes, mistake

    def _verify_correct_storage(self, data: StorableSetData, token_id: str):
        stored_data = self.storage.load_set_metadata(SetRID(chain_id=self.network, token_id=token_id))
        expected_data = self._get_storage_data(data, token_id)
        passes, mistake = self._compare_storage(expected_data, stored_data)

        if not passes:
            # In prod, store the expected data alongside the stored data.
            # Otherwise, just erase (convenient in test env when changing storage formats).
            if ENV == 'prod':    
                self.storage.get_backend(self.network).store_json(
                    self.storage.set_metadata_path(SetRID(chain_id=self.network, token_id=token_id)).replace('_metadata', '_expected_metadata'),
                    expected_data
                )
                logger.warn(
                    'store_set called with set token %(token)s but the data does not match the stored data at %(cat)s. '
                    'Storing expected data alongside the stored data.',
                    {"token": token_id, "cat": mistake}
                )
            else:
                self.storage.get_backend(self.network).store_json(
                    self.storage.set_metadata_path(SetRID(chain_id=self.network, token_id=token_id)),
                    expected_data
                )
                logger.warn(
                    'store_set called with set token %(token)s but the data does not match the stored data at %(cat)s. '
                    'Replacing stored data.',
                    {"token": token_id, "cat": mistake}
                )
        else:
            logger.info("Verified set %(token)s", {"token": token_id})

        # Request an update on the mintsquare metadata, in case they indexed us too fast.
        if ENV == 'prod':
            try:
                requests.post(f"https://api.mintsquare.io/nft/metadata/{self.network}/{get_network_metadata(self.network).set_address}/{token_id}/")
                logger.debug("Pinged mintsquare API to update token %(token_id)s", {"token_id": token_id})
            except Exception as e:
                logger.debug("Could not ping mintsquare API for token %(token_id)s",{'token_id': token_id}, exc_info=e)


    def _store_set(self, data: StorableSetData, token_id: str):
        self.storage.store_set_metadata(SetRID(chain_id=self.network, token_id=token_id), self._get_storage_data(data, token_id))
        logger.info('Stored new set %(token)s', {"token": token_id})
