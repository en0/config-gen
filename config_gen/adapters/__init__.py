from ini_adapter import IniAdapter
from redis_adapter import RedisAdapter
import inspect

__all__ = [
    "IniAdapter",
    "RedisAdapter"
]


def is_adapater(x):
    if inspect.isclass(x) and x.__name__.endswith('Adapter'):
        return hasattr(x, "name")
    return False


def get_adapters():
    m = inspect.getmodule(get_adapters)
    a = dict(
        (v.name, v)
        for _, v
        in inspect.getmembers(m, predicate=is_adapater)
    )
    return a
