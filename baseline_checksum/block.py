from .event import Event
from .library import keccak_256

class Block:
    def __init__(self, block_number: int):
        self.number = block_number
        self.checksum = None
        self.events: list[Event] = []

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
