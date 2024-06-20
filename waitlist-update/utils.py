import asyncio
import functools
import os


def asynchronous(func):
    """
    Decorator to run async functions synchronously. Helpful espacially for the main function,
    when used alongside the click library.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def remove_duplicates(data: list, keys: list[str], keep_last: bool = False) -> list:
    """
    Remove duplicates from a list of objects according to the specified keys.
    """
    _data = data[-1::-1] if keep_last else data

    attributes = ["-".join(getattr(entry, param) for param in keys) for entry in _data]
    return [_data[attributes.index(attr)] for attr in set(attributes)]


def sort_waitlist(nft_holders: list, non_holders: list, chunk_sizes: tuple):
    nr_chunk_size, stake_chunk_size = chunk_sizes
    nr_index, stake_index = 0, 0

    ordered_waitlist = []

    while len(ordered_waitlist) != (len(nft_holders) + len(non_holders)):
        if nr_index < len(nft_holders):
            ordered_waitlist.extend(nft_holders[nr_index : nr_index + nr_chunk_size])
            nr_index += nr_chunk_size

        if stake_index < len(non_holders):
            ordered_waitlist.extend(
                non_holders[stake_index : stake_index + stake_chunk_size]
            )
            stake_index += stake_chunk_size

    return ordered_waitlist


def print_loaded_data(cls: str, count: int):
    print(f"\033[1m{cls:20s}\t// Loaded {count} entries\033[0m")


def separator_text(text: str, fill: str, width: int = None):
    if not width:
        width = os.get_terminal_size().columns

    text_len = len(text) + 2
    if text_len >= width:
        return text

    total_padding = width - text_len
    left = total_padding // 2
    right = total_padding - left

    return "\n" + fill * left + " " + text + " " + fill * right
