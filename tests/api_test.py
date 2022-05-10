import json
import pytest
from pathlib import Path

from unittest.mock import patch

from briq_api.api import api
from briq_api.set_identifier import SetRID
from briq_api.storage import client

from tests.conftest import BRIQ_DATA


RID = SetRID(chain_id="test", token_id="0xcafe")
UNKNOWN_RID = SetRID(chain_id="bad_chain", token_id="0xcafe")

SET_DATA = {
    "sets/test/0xcafe_metadata": BRIQ_DATA
}


@pytest.fixture()
def temp_storage_client(tmp_path: Path):
    (tmp_path / "sets" / "test").mkdir(parents=True, exist_ok=True)
    client.setup_local_storage(str(tmp_path) + "/")
    with patch('briq_api.api.api.storage_client', new=client.get_storage_client()) as mock:
        yield mock

@pytest.fixture()
def mocked_storage_client():
    with patch('briq_api.api.api.storage_client.load_json', side_effect=lambda path: SET_DATA[path]) as mock:
        yield mock


def test_get_metadata(mocked_storage_client):
    assert api.get_metadata(RID) == SET_DATA["sets/test/0xcafe_metadata"]


def test_get_metadata_bad(mocked_storage_client):
    with pytest.raises(Exception):
        api.get_metadata(UNKNOWN_RID)

@pytest.mark.asyncio
async def test_store_set(temp_storage_client):
    print(temp_storage_client)
    print(api.storage_client)
    await api.store_set(RID, json.loads(BRIQ_DATA), b'')
    assert api.get_metadata(RID)['name'] == 'toto'
