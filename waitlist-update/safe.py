class Safe:

    def __init__(
        self,
        address: str,
        wxHoprBalance: int,
        nodes: list[str],
    ):
        self.nodes = nodes
        self.wxHoprBalance = wxHoprBalance
        self.address = address

    def has_address(self, address: str):
        return self.node_address == address

    def __eq__(self, other):
        return (
            self.nodes == other.nodes
            and self.wxHoprBalance == other.wxHoprBalance
            and self.address == other.address
        )

    def __str__(self):
        return (
            f"Safe(nodes={self.nodes}, "
            + f"wxHoprBalance={self.wxHoprBalance}, "
            + f"address={self.address}), "
        )

    def __repr__(self):
        return str(self)
