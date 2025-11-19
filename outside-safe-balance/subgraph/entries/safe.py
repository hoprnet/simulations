from lib.hoprd_api.balance import Balance
from lib.subgraph import Entry


class Safe(Entry):
    def __init__(
        self,
        node_address: str,
        wxHoprBalance: str,
        safe_address: str,
        safe_allowance: str,
    ):
        self.node_address = node_address
        self.wxHoprBalance = Balance(f"{wxHoprBalance} wxHOPR")
        self.safe_address = safe_address
        self.safe_allowance = Balance(f"{safe_allowance} wxHOPR")

    @classmethod
    def fromSubgraphResult(cls, node: dict):
        return cls(
            node["node"]["id"],
            float(node["safe"]["balance"]["wxHoprBalance"]),
            node["safe"]["id"],
            float(node["safe"]["allowance"]["wxHoprAllowance"]),
        )

    def has_address(self, address: str):
        return self.node_address == address