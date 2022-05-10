import pytest

BRIQ_DATA = """
{
    "id": "0x1234",
    "description": "",
    "name": "toto",
    "regionSize": 10,
    "version": 1,
    "briqs": [
        {"pos": [-3, 0, 0], "data": {"material": "0x1", "color": "#c5ac73"}},
        {"pos": [-2, 0, 0], "data": {"material": "0x1", "color": "#c5ac73"}},
        {"pos": [-1, 0, 0], "data": {"material": "0x2", "color": "#fafafa"}}
    ]
}
"""

@pytest.fixture
def briq_data():
    return BRIQ_DATA

@pytest.fixture
def too_large_for_vox_briq_data():
    briqs = []
    for i in range(0, 300):
        briqs.append((str(i), f'"#{hex(i//2)[2:].ljust(2, "0")}{hex((i+1)//2)[2:].ljust(2, "0")}00"'))
    return """
{
    "id": "0x1234",
    "description": "",
    "name": "toto",
    "regionSize": 10,
    "version": 1,
    "briqs": [
""" + ','.join(["""{"pos": [""" + x[0] + """, 0, 0], "data": {"material": "0x2", "color": """ + x[1] + "}}" for x in briqs]) + "]}"
