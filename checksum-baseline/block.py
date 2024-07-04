import json
import signal
import sys
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
                "events": [event.json_format() for event in self.events],
            }
        }

    def add_event(self, event: Event):
        self.events.append(event)

    def keccak_256(self):
        return keccak_256(b"".join([event.tx_hash_bytes for event in self.events]))

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):

        output = f"checksum @ block {self.number}: 0x{self.checksum.hex()}"

        if len(self.events) > 0:
            output += f" (hash: 0x{self.block_hash[:6]}...)"
        else:
            output += " (no events)"

        for event in self.events:
            output += f"\n  {event}"

        return output


class BlocksIO:
    def __init__(self, file: Path, folder: Path):
        self.file = file
        self.temp_folder = folder
        self.blocks: list[Block] = []
        signal.signal(signal.SIGINT, self.interruption_handler)

    def _parseData(self, data: dict):
        # remove duplicates and sort by block_number, tx_index, log_index
        events = list(set([Event.fromDict(d) for d in data]))
        events.sort()

        # create blocks out of events
        for event in events:
            if len(self.blocks) == 0 or self.blocks[-1].number != event.block_number:
                self.blocks.append(Block(event.block_number))
            self.blocks[-1].add_event(event)

        # calculate checksums
        checksums: list[bytearray] = [bytearray(32)]
        for block in self.blocks:
            cat_str = b"".join([checksums[-1], block.keccak_256()])
            block.checksum = keccak_256(cat_str)
            checksums.append(block.checksum)

    async def fromSubgraphData(self, minblock: int, url: str):
        # import data, either from local files or from the subgraph API
        events_io = EventsIO(self.temp_folder)
        if self.temp_folder.exists():
            data = events_io.fromLocalFiles()
        else:
            self.temp_folder.mkdir()
            data = await events_io.fromSubgraph(url, minblock)

        self._parseData(data)

    def fillMissingBlocks(self):
        temp_block_list: list[Block] = []

        for block in self.blocks:
            last_block_number = temp_block_list[-1].number if temp_block_list else None
            if last_block_number and (block.number - last_block_number) > 1:
                missing_blocks = [
                    Block(item) for item in range(last_block_number + 1, block.number)
                ]
                for item in missing_blocks:
                    item.checksum = temp_block_list[-1].checksum

                temp_block_list.extend(missing_blocks)

            temp_block_list.append(block)

        self.blocks = temp_block_list

    def fromJSON(self):
        print(f"Loading blocks from {self.file}")

        block_jsons = {}
        with open(self.file, "r") as f:
            block_jsons = json.load(f)

        for block_number, block_json in block_jsons.items():
            block = Block(int(block_number))
            for event_json in block_json["events"]:
                block.add_event(Event.fromDict(event_json))
            block.checksum = bytearray.fromhex(block_json["checksum"])
            self.blocks.append(block)

    def toJSON(self):
        if not self.file:
            return

        print(f"Saving blocks to {self.file}")
        block_jsons = {}
        for block in self.blocks:
            block_jsons.update(block.json_format())

        with open(self.file, "w+") as f:
            json.dump(block_jsons, f)

        self.removeTempFiles()

    def removeTempFiles(self):
        for file in self.temp_folder.iterdir():
            file.unlink()
        self.temp_folder.rmdir()

    def interruption_handler(self, sig, frame):
        print("")
        self._parseData(EventsIO(self.temp_folder).fromLocalFiles())
        self.toJSON()
        sys.exit(0)

    @classmethod
    def blockNumbers(cls, blocks: list[Block]):
        return [block.number for block in blocks]
