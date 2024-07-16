from pandas import DataFrame, Series

from .entry import Entry


class Candidate(Entry):
    def __init__(
        self,
        safe_address: str,
        node_address: str,
        wxHOPR_balance: float,
        nr_nft: bool,
    ):
        self.safe_address = safe_address
        self.node_address = node_address
        self.wxHOPR_balance = wxHOPR_balance
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

    def _toPandaSerie(self):
        return Series(
            {
                value: getattr(self, key)
                for key, value in self._import_keys_and_values().items()
            }
        )

    def __repr__(self):
        return (
            "Candidate("
            + f"{self.safe_address}, "
            + f"{self.wxHOPR_balance}, "
            + f"{self.nr_nft})"
        )

    @classmethod
    def toDataFrame(cls, entries: list["Candidate"]):
        return DataFrame([entry._toPandaSerie() for entry in entries])

    @classmethod
    def _import_keys_and_values(self) -> dict[str, str]:
        return {
            "safe_address": "safe_address",
            "node_address": "node_address",
            "wxHOPR_balance": "wxHOPR_balance",
            "nr_nft": "nr_nft",
        }
