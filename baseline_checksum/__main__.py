import asyncio
import os
from pathlib import Path
import pickle
import click
import sha3

from .graphql_provider import EventsProvider

from dotenv import load_dotenv

load_dotenv()

BOLD = "\033[1m"
RESET = "\033[0m"

DUNE_API_KEY = os.environ.get("DUNE_API_KEY")
DUNE_QUERY_ID = os.environ.get("DUNE_QUERY_ID")
url = f"https://gateway-arbitrum.network.thegraph.com/api/{DUNE_API_KEY}/subgraphs/id/{DUNE_QUERY_ID}"
# url = "https://api.studio.thegraph.com/query/58438/logs-for-hoprd/v0.2.0"

def keccak_256(input: bytearray):
    k = sha3.keccak_256()
    k.update(input)
    return bytearray.fromhex(k.hexdigest())

class Event:
    def __init__(self, id: str, block_number: int, log_index: int, tx_index: int, evt_name: str, tx_hash: str):
        self.id = id
        self.block_number: str = block_number
        self.log_index: str = log_index
        self.tx_index: str = tx_index
        self.tx_hash: str = tx_hash
        self.evt_name: str = evt_name

    @property
    def tx_hash_bytes(self):
        try:
            return bytearray.fromhex(self.tx_hash[2:].strip())
        except ValueError as e:
            print(f"Error with {self.tx_hash}")
            raise e

    @classmethod
    def fromDict(cls, data: dict):
        return cls(data["id"], int(data["block_number"]), int(data["log_index"]), int(data["tx_index"]), data["evt_name"], data["tx_hash"])
    
    def __eq__(self, other):
        return self.id == other.id
    
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
        return hash(f"{self.id}, {self.block_number}, {self.log_index}, {self.tx_index}, {self.tx_hash}, {self.evt_name}")
    
class Block:
    def __init__(self, block_number: int):
        self.number = block_number
        self.events: list[Event] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def keccak_256(self):
        return keccak_256(b''.join([event.tx_hash_bytes for event in self.events]))


async def events_from_subgraph(folder: Path, initial_block):
    provider = EventsProvider(url)
    data = []
    temp_data = await provider.get(block_number=str(initial_block))

    with open(folder.joinpath("part_0.pkl"), "wb") as f:
        pickle.dump(temp_data, f)

    data.extend(temp_data)
    print(f"Retrieved {len(temp_data)} events (total: {len(data)})")

    idx = 1
    while len(temp_data) == 6000:
        print(f"In loop {idx}x")
        block_number = data[-1]["block_number"]


        print(f"{block_number=}")
        temp_data = await provider.get(block_number=f"{block_number}")

        with open(folder.joinpath(f"part_{idx}.pkl"), "wb") as f:
            pickle.dump(temp_data, f)

        data.extend(temp_data)
        print(f"Retrieved {len(temp_data)} events (total: {len(data)})")

        idx += 1

    return data

def events_from_local_files(folder: Path):
    data = []
    files = list(folder.glob("*.pkl"))
    print(f"Loading data from {len(files)} files in folder `{folder}`")
    for file in files:
        print(f"\rLoading {file.name}", end="")
        with open(file, "rb") as f:
            data.extend(pickle.load(f))
    print("\r"+" "*100, end="")
    print("\rLoading done!")
    return data

@click.command()
@click.option("--block", default=29706814, help="The block number to start from")
@click.option("--path", default="./foo_results", help="The folder to store the data in")
def main(block, path):
    # import data, either from local files or from the subgraph API
    folder = Path(path)
    if folder.exists():
        data = events_from_local_files(folder)
    else:
        folder.mkdir()
        data = asyncio.run(events_from_subgraph(folder, block))

    # remove duplicates and sort by block_number, tx_index, log_index
    events = list(set([Event.fromDict(d) for d in data]))
    events.sort()

    # create blocks out of events
    blocks: list[Block] = []
    for event in events:
        if not blocks or blocks[-1].number != event.block_number:
            blocks.append(Block(event.block_number))

        blocks[-1].add_event(event)

    print(f"Retrieved {len(blocks)} blocks ({len(events)} events)")

    # show block and events structure
    print("\n" + "-"*os.get_terminal_size().columns)
    for block in blocks[:5]:
        print(f"{BOLD}Block {block.number}{RESET} with {len(block.events)} event(s). Keccak256: {block.keccak_256().hex()}")
        for event in block.events:
            print(f"  {event}")
    print("-"*os.get_terminal_size().columns + "\n")
    
    # calculate checksums
    checksums: list[bytearray] = [bytearray(32)]
    for block in blocks[:20]:
        cat_str = b''.join([checksums[-1], block.keccak_256()])
        checksum = keccak_256(cat_str)
        checksums.append(checksum)

        if block.number % 5 == 0:
            print(f"checksum @ block {BOLD}{block.number}{RESET}: {checksum.hex()} ({len(block.events)} log(s))")


if __name__ == "__main__":
    main()