import asyncio
import logging
from dataclasses import dataclass
from time import time
from typing import Callable, TypeVar, Generic, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheData(Generic[T]):
    data: T
    timeout: int

    @staticmethod
    def memory_cache(cache_path: Callable[..., str], timeout: int, memcache=None) -> Callable[[Callable[..., T]], Callable[..., T]]:
        if memcache is None:
            _memcache: dict[str, CacheData[T]] = {}
        else:
            _memcache = memcache

        def wrapper2(f: Callable[..., T]) -> Callable[..., T]:
            async def wrapper(*args, **kwargs) -> T:
                c_p = cache_path(*args, **kwargs)
                try:
                    cache_data = _memcache[c_p]
                    if cache_data.timeout > time():
                        return cache_data.data
                    else:
                        raise Exception('Cache expired')
                except Exception:
                    data = await f(*args, **kwargs)
                    _memcache[c_p] = CacheData(data=data, timeout=int(time()) + timeout)
                    return data

            def sync_wrapper(*args, **kwargs) -> T:
                c_p = cache_path(*args, **kwargs)
                try:
                    cache_data = _memcache[c_p]
                    if cache_data.timeout > time():
                        return cache_data.data
                    else:
                        raise Exception('Cache expired')
                except Exception:
                    data = f(*args, **kwargs)
                    _memcache[c_p] = CacheData(data=data, timeout=int(time()) + timeout)
                    return data

            return wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper
        return wrapper2
