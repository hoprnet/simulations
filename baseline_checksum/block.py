import json
from pathlib import Path

from .event import Event, EventsIO
from .library import keccak_256

class Block:
    def __init__(self, block_number: int):
        self.number = block_number
        self.checksum = None
        self.events: list[Event] = []

    @property
    def block_hash(self):
        return self.keccak_256().hex()
    
    def json_format(self):
        return { 
            f"{self.number}": {
                "checksum": self.checksum.hex(),
                "events": [event.json_format() for event in self.events]
            }
        }

    def add_event(self, event: Event):
        self.events.append(event)

    def keccak_256(self):
        return keccak_256(b''.join([event.tx_hash_bytes for event in self.events]))
    
    def __lt__(self, other):
        return self.number < other.number


    def __repr__(self):
        output = f"checksum @ block {self.number}: 0x{self.checksum.hex()} (hash: 0x{self.block_hash[:6]}...)"

        for event in self.events:
            output += f"\n  {event}"

        return output
    

class BlocksIO:
    def __init__(self, file: Path):
        self.file = file

    def fromSubgraphData(self, folder: Path, minblock: int, url: str):
        # import data, either from local files or from the subgraph API
        events_io = EventsIO(folder)
        if folder.exists():
            data = events_io.fromLocalFiles()
        else:
            folder.mkdir()
            data = events_io.fromSubgraph(url, minblock)

        # remove duplicates and sort by block_number, tx_index, log_index
        events = list(set([Event.fromDict(d) for d in data]))
        events.sort()

        # create blocks out of events
        blocks: list[Block] = []
        for event in events:
            if len(blocks) == 0 or blocks[-1].number != event.block_number:
                blocks.append(Block(event.block_number))

            blocks[-1].add_event(event)

        # calculate checksums
        checksums: list[bytearray] = [bytearray(32)]
        for block in blocks:
            cat_str = b''.join([checksums[-1], block.keccak_256()])
            block.checksum = keccak_256(cat_str)
            checksums.append(keccak_256(cat_str))

        self.toJSON(blocks)

        return blocks

    def fromJSON(self):
        print(f"Loading blocks from {self.file}")

        blocks = []
        block_jsons = {}
        with open(self.file, "r") as f:
            block_jsons = json.load(f)

        for block_number, block_json in block_jsons.items():
            block = Block(int(block_number))
            for event_json in block_json["events"]:
                block.add_event(Event.fromDict(event_json))
            block.checksum = bytearray.fromhex(block_json["checksum"])
            blocks.append(block)

        return blocks

    def toJSON(self, blocks: list[Block]):
        if not self.file:
            return
        
        print(f"Saving blocks to {self.file}")
        block_jsons = {}
        for block in blocks:
            block_jsons.update(block.json_format())
        with open(self.file, "w+") as f:
            json.dump(block_jsons, f)