import json
import signal
import sys
from pathlib import Path

from lib.helper import keccak_256

from .events_io import EventsIO
from .subgraph.entries import Block, Event


class BlocksIO:
    def __init__(self, file: Path, folder: Path):
        self.file = file
        self.temp_folder = folder
        self.blocks: list[Block] = []
        signal.signal(signal.SIGINT, self.interruption_handler)

    def _parse_data(self, data: dict):
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

    async def from_subgraph_data(self, minblock: int, url: str):
        # import data, either from local files or from the subgraph API
        events_io = EventsIO(self.temp_folder)
        if self.temp_folder.exists():
            data = events_io.from_local_files()
        else:
            self.temp_folder.mkdir()
            data = await events_io.from_subgraph(url, minblock)

        self._parse_data(data)

    def fill_missing_blocks(self):
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

    def from_json(self):
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

    def to_json(self):
        if not self.file:
            return

        print(f"Saving blocks to {self.file}")
        block_jsons = {}
        for block in self.blocks:
            block_jsons.update(block.json_format())

        with open(self.file, "w+") as f:
            json.dump(block_jsons, f)

        self.remove_temp_files()

    def remove_temp_files(self):
        for file in self.temp_folder.iterdir():
            file.unlink()
        self.temp_folder.rmdir()

    def interruption_handler(self, sig, frame):
        print("")
        self._parse_data(EventsIO(self.temp_folder).from_local_files())
        self.to_json()
        sys.exit(0)

    @classmethod
    def block_numbers(cls, blocks: list[Block]):
        return [block.number for block in blocks]
