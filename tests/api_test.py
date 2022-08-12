import json
import pytest
from pathlib import Path

from unittest.mock import patch

from briq_api.api import api
from briq_api.set_identifier import SetRID
from briq_api.storage import multi_backend_client
from briq_api.storage.backends.file_storage import FileStorage

from tests.conftest import BRIQ_DATA


RID = SetRID(chain_id="test", token_id="0xcafe")
UNKNOWN_RID = SetRID(chain_id="bad_chain", token_id="0xcafe")

SET_DATA = {
    "sets/test/0xcafe_metadata": BRIQ_DATA
}


@pytest.fixture()
def temp_storage_client(tmp_path: Path):
    (tmp_path / "sets" / "test").mkdir(parents=True, exist_ok=True)
    multi_backend_client.storage_client.connect(FileStorage(str(tmp_path) + "/"))
    with patch('briq_api.api.api.storage_client', new=multi_backend_client.storage_client) as mock:
        yield mock

@pytest.mark.asyncio
async def test_store_set(temp_storage_client):
    await api.store_set(RID, json.loads(BRIQ_DATA), b'')
    assert api.get_metadata(RID)['name'] == 'toto'

    with pytest.raises(Exception):
        api.get_metadata(UNKNOWN_RID)
