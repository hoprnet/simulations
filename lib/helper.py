import asyncio
import functools
import os
from typing import Any

import sha3


def asynchronous(func):
    """
    Decorator to run async functions synchronously. Helpful espacially for the main function,
    when used alongside the click library.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def progress_bar(current_value: int, max_value: int, percentage: float):
    """
    Print a progress bar to the console.
    """
    length = 75
    print(
        f"\r[{'#' * int(length * percentage)}{' ' * (length - int(length * percentage))}] {percentage:.2%}% ({current_value:_}/{max_value:_})",
        end="",
        flush=True,
    )
    

def keccak_256(input: bytearray):
    k = sha3.keccak_256()
    k.update(input)
    return bytearray.fromhex(k.hexdigest())


def envvar(key: str, default: Any = None, type = str) -> Any:
    """
    Get an environment variable, or return a default value if not set.
    """
    return type(os.getenv(key, default))
