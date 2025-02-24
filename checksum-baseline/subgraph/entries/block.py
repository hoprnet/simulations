from lib.helper import keccak_256
from lib.subgraph import Entry

from .event import Event


class Block(Entry):
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
