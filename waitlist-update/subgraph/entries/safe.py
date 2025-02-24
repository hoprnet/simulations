from lib.subgraph import Entry


class Safe(Entry):
    def __init__(self, address: str, balance: int, nodes: list[str]):
        self.nodes = nodes
        self.balance = balance
        self.address = address

    @classmethod
    def fromSubgraphResult(cls, safe: dict):
        return cls(
            safe.get("id", {}),
            float(safe.get("balance", {}).get("wxHoprBalance", "0")),
            [n["node"]["id"]
                 for n in safe.get("registeredNodesInNetworkRegistry", {})]
        )        

    def has_address(self, address: str):
        return self.node_address == address