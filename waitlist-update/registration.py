from pandas import Series

from .entry import Entry


class Registration(Entry):
    def __init__(
        self,
        time: str,
        participant: str,
        safe_address: str,
        node_address: str,
        nr_nft: str,
        telegram: str,
    ):
        self.time = time
        self.participant = participant
        self.safe_address = safe_address
        self.node_address = node_address
        self.nr_nft = nr_nft
        self.telegram = telegram

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
    def fromPandaSerie(cls, entry: Series):
        node_addresses = (
            entry[
                "What is your Node address? (If you want to add multiple, just include one node per row)"
            ]
            .replace("&#xA;", "\n")
            .split("\n")
        )

        instances = []
        for address in node_addresses:
            address = address.strip().lower()

            instance = cls(
                time=entry["Time"],
                participant=entry["Participant"],
                safe_address=entry["What is your HOPR safe address?"],
                node_address=address,
                nr_nft=entry["Do you already have the Network Registry NFT?"],
                telegram=entry["What is your Telegram handle?"],
            )

            instances.append(instance)
        return instances
