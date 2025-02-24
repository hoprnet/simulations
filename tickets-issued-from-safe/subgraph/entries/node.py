from lib.subgraph import Entry


class Node(Entry):
    def __init__(self, id: str):
        self.id = id

    @classmethod
    def fromSubgraphResult(cls, node: dict):
        return cls(node["node"]['id'])
