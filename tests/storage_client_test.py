import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch
from briq_api.set_identifier import SetRID
from briq_api.storage.backends.file_storage import FileStorage

from briq_api.storage.multi_backend_client import StorageClient

def test_storage_client(tmp_path):
    client = StorageClient()
    client.connect(FileStorage(str(tmp_path) + '/'))
    client.store_set_metadata(SetRID(chain_id="A", token_id="test"), {"data": "test-A"})
    assert client.load_set_metadata(SetRID(chain_id="A", token_id="test")) == {"data": "test-A"}

    with open(tmp_path / client.set_metadata_path(SetRID(chain_id="A", token_id="test")), "r") as f:
        assert f.read() == '{"data": "test-A"}'

    client.store_set_metadata(SetRID(chain_id="A", token_id="test2"), {"data": "test2-A"})
    assert client.load_set_metadata(SetRID(chain_id="A", token_id="test2")) == {"data": "test2-A"}
    assert client.load_set_metadata(SetRID(chain_id="A", token_id="test")) == {"data": "test-A"}

    client.connect_for_chain(chain_id="B", backend=FileStorage(str(tmp_path) + '/'))

    client.store_set_metadata(SetRID(chain_id="B", token_id="test"), {"data": "test-B"})
    assert client.load_set_metadata(SetRID(chain_id="B", token_id="test")) == {"data": "test-B"}
    assert client.load_set_metadata(SetRID(chain_id="A", token_id="test2")) == {"data": "test2-A"}
    assert client.load_set_metadata(SetRID(chain_id="A", token_id="test")) == {"data": "test-A"}

    client.connect(backend=FileStorage(str(tmp_path) + '/moved/'))
    assert client.load_set_metadata(SetRID(chain_id="B", token_id="test")) == {"data": "test-B"}
    with pytest.raises(FileNotFoundError):
        assert client.load_set_metadata(SetRID(chain_id="A", token_id="test2")) == {"data": "test2-A"}
    with pytest.raises(FileNotFoundError):
        assert client.load_set_metadata(SetRID(chain_id="A", token_id="test")) == {"data": "test-A"}

def test_explicit_chain_none(tmp_path):
    client = StorageClient()
    client.connect(FileStorage(str(tmp_path) + '/'))
    client.connect_for_chain(chain_id="A", backend=None)
    with pytest.raises(Exception, match="No available backend for A"):
        client.store_set_metadata(SetRID(chain_id="A", token_id="test"), {"data": "test-A"})
    with pytest.raises(Exception, match="No available backend for A"):
        client.load_set_metadata(SetRID(chain_id="A", token_id="test"))
