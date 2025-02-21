from lib.subgraph import Entry


class Event(Entry):
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

    def __lt__(self, other):
        if self.block_number != other.block_number:
            return self.block_number < other.block_number

        if self.tx_index != other.tx_index:
            return self.tx_index < other.tx_index

        return self.log_index < other.log_index

    def __repr__(self):
        return f"<Event object> with hash {self.tx_hash}"

    def __hash__(self):
        return hash(
            f"{self.id}, {self.block_number}, {self.log_index}, {self.tx_index}, {self.tx_hash}, {self.evt_name}"
        )
