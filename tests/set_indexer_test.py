import json
from unittest import mock
import pytest
from briq_api.set_identifier import SetRID

from briq_api.set_indexer.set_indexer import SetIndexer, StorableSetData
from briq_api.set_indexer.server import NewSetStorageRequest, decode_string, store_new_set
from briq_api.set_indexer import server
from briq_api.storage.file.file_client import FileClient

@pytest.fixture
def small_set():
    return lambda token_id: '''
{
    "id": "''' + token_id + '''",
    "name": "Speeder",
    "description": "For when you gotta go fast.",
    "regionSize": 100000,
    "version": 1,
    "briqs": [
        {
            "pos": [
                -8,
                1,
                -4
            ],
            "data": {
                "material": "0x1",
                "color": "#4fecab"
            }
        },
        {
            "pos": [
                -8,
                1,
                -3
            ],
            "data": {
                "material": "0x1",
                "color": "#00cd15"
            }
        },
        {
            "pos": [
                -8,
                2,
                -3
            ],
            "data": {
                "material": "0x1",
                "color": "#00cd15"
            }
        }
    ],
    "image": "https://api.briq.construction/v1/preview/starknet-testnet/''' + token_id + '''.png",
    "animation_url": "https://api.briq.construction/v1/model/starknet-testnet/''' + token_id + '''.glb",
    "external_url": "https://briq.construction/set/starknet-testnet/''' + token_id + '''"
}'''


@pytest.fixture
def assemble_transaction():
    return [int(x, 16) for x in [
        '0x59df66af2e0e350842b11ea6b5a903b94640c4ff0418b04ccedcc320f531a08',
        '0x8ca581fb82ec435ca2a38eb4026afd00',
        '0x1', '0x53706565646572',
        '0x2', '0x466f72207768656e20796f7520676f', '0x74746120676f20666173742e',
        '0x1', '0x1', '0xfc',
        '0x0',
        '0x3',
            '0x233466656361620000000000000000000000000000000001', '0x7ffffffffffffff880000000000000017ffffffffffffffc',
            '0x233030636431350000000000000000000000000000000001', '0x7ffffffffffffff880000000000000017ffffffffffffffd',
            '0x233030636431350000000000000000000000000000000001', '0x7ffffffffffffff880000000000000027ffffffffffffffd',
        '0x2', '0x11000000000000000000000000000000000000000000000001', '0x2'
    ]]


@pytest.fixture
def dojo_assemble_transaction():
    return [int(x, 16) for x in [
        '0x59df66af2e0e350842b11ea6b5a903b94640c4ff0418b04ccedcc320f531a08',
        '0x8ca581fb82ec435ca2a38eb4026afd00',
        '0x1', '0x53706565646572',
        '0x2', '0x466f72207768656e20796f7520676f', '0x74746120676f20666173742e',
        '0x1', '0x1', '0xfc',
        '0x3',
            '0x233466656361620000000000000001', '0x7ffffff8800000017ffffffc',
            '0x233030636431350000000000000001', '0x7ffffff8800000017ffffffd',
            '0x233030636431350000000000000001', '0x7ffffff8800000027ffffffd',
        '0x2', '0x11000000000000000000000000000000000000000000000001', '0x2'
    ]]


@pytest.fixture
def fake_file_client() -> FileClient:
    class FakeFileClient(FileClient):
        data = {}

        def _key(self, rid: SetRID) -> str:
            return f'{rid.chain_id}/{rid.token_id}'

        def load_set_metadata(self, rid: SetRID) -> dict:
            return json.loads(self.data[self._key(rid)])

        def has_set_metadata(self, rid: SetRID) -> bool:
            return self._key(rid) in self.data

        def store_set_metadata(self, rid: SetRID, data: dict):
            self.data[self._key(rid)] = json.dumps(data)

    return FakeFileClient()


def test_string_decoder():
    # The final values cut through a unicode emoji codepoint, so we first must concatenate the bytes then convert to UTF8
    decode_string([6, 339738293713170351190154628795753573, 599131161924668781275065661968641377, 572086457812204471992076897945742951, 168189778188893672240391183161912697, 168372001333950074068234651068047248, 12037921844039927143589566451863], 0)

def test_store_set_inner(small_set, fake_file_client):
    set_data = StorableSetData(
        name="Speeder",
        description="For when you gotta go fast.",
        briqs=[
            {
                "pos": [-8, 1, -4],
                "data": {
                    "material": "0x1",
                    "color": "#4fecab"
                }
            },
            {
                "pos": [-8, 1, -3],
                "data": {
                    "material": "0x1",
                    "color": "#00cd15"
                }
            },
            {
                "pos": [-8, 2, -3],
                "data": {
                    "material": "0x1",
                    "color": "#00cd15"
                }
            }
        ]
    )
    SetIndexer('starknet-testnet', fake_file_client)._store_set(
        set_data,
        '0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000'
    )
    assert fake_file_client.has_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000')
    )
    assert fake_file_client.load_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000')
    ) == json.loads(small_set('0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000'))


@pytest.fixture
def mock_set_indexer(fake_file_client):
    with mock.patch('briq_api.set_indexer.server.set_indexer', { "starknet-testnet": SetIndexer('starknet-testnet', fake_file_client) }) as f:
        yield f


@pytest.mark.asyncio
async def test_server(fake_file_client, mock_set_indexer, small_set, assemble_transaction, dojo_assemble_transaction):
    await store_new_set(NewSetStorageRequest(
        chain_id="starknet-testnet",
        token_id="0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000",
        transaction_data=assemble_transaction,
    ))

    await store_new_set(NewSetStorageRequest(
        chain_id="starknet-testnet",
        token_id="0x5996470c4ff85fc84e92232db145156ed33710bee8b1d27fea22d9900000000",
        transaction_data=dojo_assemble_transaction,
    ))

    mock_set_indexer["starknet-testnet"].store_set("0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000")

    mock_set_indexer["starknet-testnet"].store_set("0x5996470c4ff85fc84e92232db145156ed33710bee8b1d27fea22d9900000000")

    assert fake_file_client.has_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000')
    )

    assert fake_file_client.has_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x5996470c4ff85fc84e92232db145156ed33710bee8b1d27fea22d9900000000')
    )

    assert fake_file_client.load_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000')
    ) == json.loads(small_set('0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000'))

    assert fake_file_client.load_set_metadata(SetRID(
        chain_id='starknet-testnet',
        token_id='0x5996470c4ff85fc84e92232db145156ed33710bee8b1d27fea22d9900000000')
    ) == json.loads(small_set('0x5996470c4ff85fc84e92232db145156ed33710bee8b1d27fea22d9900000000'))

    # Try again

    await store_new_set(NewSetStorageRequest(
        chain_id="starknet-testnet",
        token_id="0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000",
        transaction_data=assemble_transaction,
    ))

    with mock.patch.object(mock_set_indexer["starknet-testnet"], '_verify_correct_storage', wraps=mock_set_indexer["starknet-testnet"]._verify_correct_storage) as f:
        mock_set_indexer["starknet-testnet"].store_set("0x2aa4ce6935801fc7a15aa9dd29728dbfafe9aa7d2fa26719800000000000000")
        assert f.call_count == 1
