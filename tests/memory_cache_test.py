from briq_api.memory_cache import CacheData

i = 0
def get_data(chain_id: str) -> str:
    global i
    i += 1
    return chain_id + str(i)


def test_memory_cache():
    _memcache = {}

    cached_get_data = CacheData.memory_cache(lambda chain_id: f'{chain_id}', timeout=5 * 60, memcache=_memcache)(get_data)

    assert cached_get_data('a') == 'a1'
    assert cached_get_data('a') == 'a1'
    _memcache.clear()
    assert cached_get_data('a') == 'a2'
    assert cached_get_data('a') == 'a2'
