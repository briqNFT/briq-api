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
    def memory_cache(cache_path: Callable[..., str], timeout: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
        memcache: dict[str, CacheData[T]] = {}

        def wrapper2(f: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs) -> T:
                c_p = cache_path(*args, **kwargs)
                try:
                    cache_data = memcache[c_p]
                    if cache_data.timeout > time():
                        return cache_data.data
                    else:
                        raise Exception('Cache expired')
                except Exception:
                    data = f(*args, **kwargs)
                    memcache[c_p] = CacheData(data=data, timeout=int(time()) + timeout)
                    return data
            return wrapper
        return wrapper2
