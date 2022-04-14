import pytest
from briq_api.set_interaction import get_set_contract

@pytest.mark.asyncio
async def test_nothing():
    set_contract = await get_set_contract()
    assert (await set_contract.functions["ownerOf_"].call("0xcafedead")).owner == 0
