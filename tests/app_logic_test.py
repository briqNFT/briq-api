from asyncio import Future
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from briq_api import app_logic

@pytest.fixture
def bad_store_set_rq():
    return app_logic.StoreSetRequest(owner="", token_id="", data={"name": "test_a", "briqs": []}, message_hash="", signature=(0, 0), image_base64=b'')

@pytest.fixture
def realms_store_set_rq():
    return app_logic.StoreSetRequest(owner="0xcafe", token_id="0xfade", data={
        "name": "test_b",
        "briqs": [{"data": {"material": "0x2"}}],
        "background_color": "",
        "image": "",
        "external_url": "",
        "animation_url": "",
    }, message_hash="", signature=(0, 0), image_base64=b'')

async def fake_get_owner(token_id: str):
    return {
        "": 0,
        "0xfade": int("0xcafe", 16)
    }[token_id]

@pytest.mark.asyncio
@patch('briq_api.app_logic.get_owner', new=fake_get_owner)
@patch('briq_api.app_logic.requests.post')
async def test_hook(bad_store_set_rq, realms_store_set_rq):
    await app_logic.trigger_hook_once_complete(bad_store_set_rq)
    await app_logic.trigger_hook_once_complete(realms_store_set_rq)
