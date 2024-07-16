class Registration:
    def __init__(
        self,
        safe_address: str,
        node_address: str,
        nr_nft: str,
    ):
        self.safe_address = safe_address
        self.node_address = node_address
        self.nr_nft = nr_nft

    @property
    def safe_address(self) -> str:
        return self._safe_address

    @safe_address.setter
    def safe_address(self, value: str):
        self._safe_address = value.strip().lower()

    @property
    def node_address(self) -> str:
        return self._node_address

    @node_address.setter
    def node_address(self, value: str):
        self._node_address = value.strip().lower()

    @classmethod
    def fromJSON(cls, data: dict):
        instances = []
        for entry in data["responses"]:
            addresses = [item.strip().lower() for item in entry["q6"].split("\n")]
            safe_address = entry["q5"].strip().lower()
            nr_nft = entry.get("q2", False)

            instances.extend(
                [
                    cls(safe_address=safe_address, node_address=item, nr_nft=nr_nft)
                    for item in addresses
                ]
            )

        return instances
