import random
from packaging.version import Version


class Address:
    def __init__(self, id: str, address: str):
        self.id = id
        self.address = address

    def __eq__(self, other):
        return self.id == other.id and self.address == other.address

    def __hash__(self):
        return hash((self.id, self.address))


class Peer:
    def __init__(self, id: str, address: str, version: str):
        self.address = Address(id, address)
        self.version = version
        self.channel_balance = 0

        self.safe_address = ""
        self.safe_balance = 0
        self.safe_allowance = 0

        self.safe_address_count = 1

        self.economic_model = None
        self.reward_probability = 0

        self.max_apr = float("inf")

    def version_is_old(self, min_version: str | Version) -> bool:
        if isinstance(min_version, str):
            min_version = Version(min_version)

        return self.version < min_version

    @property
    def version(self) -> Version:
        return self._version

    @version.setter
    def version(self, value: str | Version):
        if isinstance(value, str):
            value = Version(value)

        self._version = value

    @property
    def node_address(self) -> str:
        return self.address.address

    @property
    def has_low_stake(self) -> bool:
        if self.economic_model is None:
            raise ValueError("Economic model not set")

        return self.split_stake < self.economic_model.parameters.l

    @property
    def transformed_stake(self) -> float:
        if self.economic_model is None:
            raise ValueError("Economic model not set")

        return self.economic_model.transformed_stake(self.split_stake)

    @property
    def total_balance(self) -> float:
        if self.safe_balance is None:
            raise ValueError("Safe balance not set")
        if self.channel_balance is None:
            raise ValueError("Channel balance not set")

        return float(self.channel_balance) + float(self.safe_balance)

    @property
    def split_stake(self) -> float:
        if self.safe_balance is None:
            raise ValueError("Safe balance not set")
        if self.channel_balance is None:
            raise ValueError("Channel balance not set")
        if self.safe_address_count is None:
            raise ValueError("Safe address count not set")

        return float(self.safe_balance) / float(self.safe_address_count) + float(
            self.channel_balance
        )

    @property
    def rewards(self):
        if self.economic_model is None:
            raise ValueError("Economic model not set")
        if self.reward_probability is None:
            raise ValueError("Reward probability not set")

        return self.reward_probability * self.economic_model.budget.budget

    @property
    def apr(self):
        if self.economic_model is None:
            raise ValueError("Economic model not set")

        seconds_in_year = 60 * 60 * 24 * 365
        period = self.economic_model.budget.period

        apr = (self.rewards / self.split_stake) * (seconds_in_year / period)

        return min(self.max_apr, apr)

    def __repr__(self):
        return f"Peer(address: {self.address})"

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)
    
    @classmethod
    def extra(cls, random_range: list[int]):
        extra = Peer("extra_peer", "extra_address", "100.0.0")
        extra.safe_address = "extra_safe"
        extra.safe_balance = random.randint(*random_range)

        return extra