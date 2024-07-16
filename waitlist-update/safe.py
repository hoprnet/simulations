class Safe:
    def __init__(self, address: str, balance: int, nodes: list[str]):
        self.nodes = nodes
        self.balance = balance
        self.address = address

    def has_address(self, address: str):
        return self.node_address == address

    def __eq__(self, other):
        return (
            self.nodes == other.nodes
            and self.balance == other.balance
            and self.address == other.address
        )
