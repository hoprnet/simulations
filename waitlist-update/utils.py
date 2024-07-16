import asyncio
import functools
import os


class Decorator:
    @classmethod
    def asynchronous(cls, func):
        """
        Decorator to run async functions synchronously. Helpful espacially for the main function,
        when used alongside the click library.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))

        return wrapper


class Display:
    @classmethod
    def separator(cls, text: str, fill: str = "-", width: int = None):
        text_len = len(text) + 2

        if not width:
            width = os.get_terminal_size().columns

        if text_len >= width:
            return text

        left = (width - text_len) // 2
        right = (width - text_len) - left

        print("\n" + fill * left + " " + text + " " + fill * right)

    @classmethod
    def candidates(cls, text: str, data: list):
        if not data:
            return

        print(f"{text}:")
        for c in data:
            string = f"\t{c.safe_address} / {c.node_address}"
            if hasattr(c, "balance"):
                string += f" ({round(c.balance, 5)} wxHOPR)"
            print(string)

    @classmethod
    def excludedCandidates(cls, exclusion_list: list[dict]):
        for v in exclusion_list:
            cls.candidates(v["case"], v["list"])

    @classmethod
    def loadedData(cls, type: str, count: int):
        print(f"\033[1m{type:20s}\t// Loaded {count} entries\033[0m")


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
