import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from briq_api.server import app
from briq_api.set_identifier import SetRID
from briq_api.storage import client as storage_client

from tests.conftest import BRIQ_DATA

client = TestClient(app)


RID = SetRID(chain_id="test", token_id="0xcafe")
UNKNOWN_RID = SetRID(chain_id="bad_chain", token_id="0xcafe")

SET_DATA = {
    "sets/test/0xcafe_metadata.json": BRIQ_DATA
}


@pytest.fixture()
def temp_storage_client(tmp_path: Path):
    (tmp_path / "sets" / "test").mkdir(parents=True, exist_ok=True)
    storage_client.setup_local_storage(str(tmp_path) + "/")
    with patch('briq_api.api.api.storage_client', new=storage_client.get_storage_client()) as mock:
        yield mock


@pytest.fixture()
def mocked_network():
    with patch('briq_api.api.api.get_set_owner', new=AsyncMock(return_value=5)) as mock:
        yield mock


@pytest.mark.asyncio
def test_store_set(temp_storage_client):
    response = client.post("v1/store_set", json={
        'chain_id': RID.chain_id,
        'token_id': RID.token_id,
        'data': json.loads(SET_DATA["sets/test/0xcafe_metadata.json"]),
        'image_base64': "",
        'owner': "",
        'message_hash': "",
        'signature': [0, 0],
    })
    assert response.status_code == 200

    response = client.get(f"v1/metadata/{RID.chain_id}/{RID.token_id}")
    assert response.json()['name'] == "toto"

    # No preview
    response = client.get(f"v1/preview/{RID.chain_id}/{RID.token_id}.png")
    assert response.status_code == 500

    response = client.get(f"v1/model/{RID.chain_id}/{RID.token_id}.gltf")
    assert len(response.content) == 2248


@pytest.mark.asyncio
def test_store_set_repetition(temp_storage_client, mocked_network):
    call_data = {
        'chain_id': RID.chain_id,
        'token_id': RID.token_id,
        'data': json.loads(SET_DATA["sets/test/0xcafe_metadata.json"]),
        'image_base64': "",
        'owner': "",
        'message_hash': "",
        'signature': [0, 0],
    }

    mocked_network.return_value = 5

    # First time goes through, file doesn't exist.
    response = client.post("v1/store_set", json=call_data)
    assert response.status_code == 200

    # Second time fails.
    response = client.post("v1/store_set", json=call_data)
    assert response.status_code == 500

    # We no longer have an owner -> we overwrite.
    mocked_network.return_value = 0
    response = client.post("v1/store_set", json=call_data)
    assert response.status_code == 200
