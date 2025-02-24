from lib.subgraph import Entry


class NFTHolder(Entry):
    def __init__(self, address: str):
        self.address = address

    @classmethod
    def fromSubgraphResult(cls, entry: dict):
        return cls(entry["owner"]["id"])