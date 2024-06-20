class SubgraphEntry:
    def __init__(
        self,
        node_address: str,
        wxHoprBalance: str,
        safe_address: str,
        safe_allowance: str,
    ):
        self.node_address = node_address
        self.wxHoprBalance = wxHoprBalance
        self.safe_address = safe_address
        self.safe_allowance = safe_allowance

    @classmethod
    def fromDict(cls, node: dict):
        return cls(
            node["node"]["id"],
            node["safe"]["balance"]["wxHoprBalance"],
            node["safe"]["id"],
            node["safe"]["allowance"]["wxHoprAllowance"],
        )
