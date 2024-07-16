class Candidate:
    def __init__(
        self,
        safe_address: str,
        node_address: str,
        balance: float,
        nr_nft: bool,
    ):
        self.safe_address = safe_address
        self.node_address = node_address
        self.balance = balance
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
    def toContractData(cls, entries: list["Candidate"]):
        node_count = len(entries)
        safe_addresses_str = "[" + ", ".join([e.safe_address for e in entries]) + "]"
        node_addresses_str = "[" + ", ".join([e.node_address for e in entries]) + "]"
        eligible_str = "[" + ", ".join(["true"] * node_count) + "]"

        return {
            "managerRegister": {
                "stakingAccounts": safe_addresses_str,
                "nodeAddresses": node_addresses_str,
            },
            "managerForceSync": {
                "stakingAccounts": safe_addresses_str,
                "eligibilities": eligible_str,
            },
        }
