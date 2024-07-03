import asyncio
import pickle
from pathlib import Path

from .graphql_provider import EventsProvider, LastBlockProvider
from .library import progress_bar


class Event:
    def __init__(
        self,
        id: str,
        block_number: int,
        log_index: int,
        tx_index: int,
        evt_name: str,
        tx_hash: str,
    ):
        self.id = id
        self.block_number: int = int(block_number)
        self.log_index: str = int(log_index)
        self.tx_index: str = int(tx_index)
        self.tx_hash: str = tx_hash
        self.evt_name: str = evt_name

    @property
    def tx_hash_bytes(self):
        try:
            return bytearray.fromhex(self.tx_hash[2:].strip())
        except ValueError as e:
            print(f"Error with {self.tx_hash}")
            raise e

    def json_format(self):
        return {
            "id": self.id,
            "block_number": self.block_number,
            "log_index": self.log_index,
            "tx_index": self.tx_index,
            "tx_hash": self.tx_hash,
            "evt_name": self.evt_name,
        }

    @classmethod
    def fromDict(cls, data: dict):
        return cls(
            data["id"],
            int(data["block_number"]),
            int(data["log_index"]),
            int(data["tx_index"]),
            data["evt_name"],
            data["tx_hash"],
        )

    def __eq__(self, other):
        return (
            self.block_number == other.block_number
            and self.tx_index == other.tx_index
            and self.log_index == other.log_index
        )

    def __lt__(self, other):
        if self.block_number != other.block_number:
            return self.block_number < other.block_number

        if self.tx_index != other.tx_index:
            return self.tx_index < other.tx_index

        return self.log_index < other.log_index

    def __repr__(self):
        return f"<Event object> with hash {self.tx_hash}"

    def __str__(self):
        return f"Event(block:{self.block_number}, tx_index:{self.tx_index:2d}, log_index:{self.log_index:2d}, tx_hash:{self.tx_hash[:8]}..., evt_name:{self.evt_name})"

    def __hash__(self):
        return hash(
            f"{self.id}, {self.block_number}, {self.log_index}, {self.tx_index}, {self.tx_hash}, {self.evt_name}"
        )


class EventsIO:
    def __init__(self, folder: Path):
        self.folder = folder

    def fromLocalFiles(self):
        data = []
        files = list(self.folder.glob("*.pkl"))
        print(f"Loading data from {len(files)} files in folder `{self.folder}`")
        for file in files:
            print(f"\rLoading {file.name}", end="")
            with open(file, "rb") as f:
                data.extend(pickle.load(f))
        print("\r" + " " * 100, end="")
        print("\rLoading done!")
        return data

    def fromSubgraph(self, url: str, minblock: int):
        print("Loading missing data from subgraph")
        last_block = asyncio.run(LastBlockProvider(url).get())[0]
        provider = EventsProvider(url)
        data = []

        idx = 0
        while idx == 0 or len(temp_data) == 6000:
            block_number = int(data[-1]["block_number"]) if len(data) > 0 else minblock
            temp_data = asyncio.run(provider.get(block_number=str(block_number)))

            with open(self.folder.joinpath(f"part_{idx}.pkl"), "wb") as f:
                pickle.dump(temp_data, f)

            data.extend(temp_data)

            progress_bar(
                block_number,
                last_block,
                (block_number - minblock) / (last_block - minblock),
            )

            idx += 1

        progress_bar(last_block, last_block, 1)
        print("")

        return data
