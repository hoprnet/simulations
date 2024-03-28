import pickle

# get current date and time as a string
from datetime import datetime, timedelta
from os import environ
from pathlib import Path

import requests

from helpers.graphql_provider import SafesProvider
from helpers.hoprd_api import HoprdAPI
from models.economic_model import (
    BudgetParameters,
    EconomicModel,
    Equation,
    Equations,
    Parameters,
)
from models.peer import Address, Peer
from models.subgraph_entry import SubgraphEntry
from models.tolopogy_entry import TopologyEntry


class Utils:
    @classmethod
    def daysInThePast(cls, days: int):
        return datetime.now() - timedelta(days=days)
    
    @classmethod
    def utf8len(cls, s: str):
        return len(s.encode())
    
    @classmethod
    def envvar(cls, key, type: type, default=None):
        var = environ.get(key, default)
        if var is None:
            return default
        return type(var)

    @classmethod
    def apiHostAndKey(cls, envhost: str, envkey: str):
        host = Utils.envvar(envhost, str)
        key = Utils.envvar(envkey, str)
        return host, key

    @classmethod
    async def aggregatePeerBalanceInChannels(cls, channels: list) -> dict[str, dict]:
        """
        Returns a dict containing all unique source_peerId-source_address links.
        """

        results: dict[str, dict] = {}
        for c in channels:
            if not (
                hasattr(c, "source_peer_id")
                and hasattr(c, "source_address")
                and hasattr(c, "status")
            ):
                continue

            if c.status != "Open":
                continue

            if c.source_peer_id not in results:
                results[c.source_peer_id] = {
                    "source_node_address": c.source_address,
                    "channels_balance": 0,
                }

            results[c.source_peer_id]["channels_balance"] += int(c.balance) / 1e18

        return results

    @classmethod
    def buildSubgraphURL(cls, envvar_name: str):
        deployer_key = Utils.envvar("SUBGRAPH_DEPLOYER_KEY", str)
        query_id = Utils.envvar(envvar_name, str)
        return (
            f"https://gateway.thegraph.com/api/{deployer_key}/subgraphs/id/{query_id}"
        )

    @classmethod
    def mergeTopoPeersSafes(
        cls,
        topology: list[TopologyEntry],
        peers: list[Peer],
        safes: list[SubgraphEntry],
    ):
        merged_result: list[Peer] = []
        addresses = [item.node_address for item in topology]

        for address in addresses:
            peer = next(filter(lambda p: p.address.address == address, peers), None)
            topo = next(filter(lambda t: t.node_address == address, topology), None)
            safe = next(filter(lambda s: s.node_address == address, safes), None)

            if peer is None or topo is None or safe is None:
                continue

            peer.safe_address = safe.safe_address
            peer.safe_balance = safe.wxHoprBalance
            peer.safe_allowance = float(safe.safe_allowance)
            peer.channel_balance = topo.channels_balance

            merged_result.append(peer)

        return merged_result

    @classmethod
    def exclude(cls, source: list[Peer], blacklist: list[Address]) -> list[Peer]:
        addresses = [peer.address for peer in source]
        indexes = [addresses.index(item) for item in blacklist if item in addresses]
        [source.pop(index) for index in sorted(indexes, reverse=True)]

    @classmethod
    def allowManyNodePerSafe(cls, peers: list[Peer]):
        safe_counts = {peer.safe_address: 0 for peer in peers}

        # Calculate the number of safe_addresses related to a node address
        for peer in peers:
            safe_counts[peer.safe_address] += 1

        # Update the input_dict with the calculated splitted_stake
        for peer in peers:
            peer.safe_address_count = safe_counts[peer.safe_address]

    @classmethod
    def rewardProbability(cls, peers: list[Peer]) -> list[int]:
        """
        Evaluate the function for each stake value in the eligible_peers dictionary.
        :param eligible_peers: A dict containing the data.
        :returns: nothing.
        """

        indexes_to_remove = [
            idx for idx, peer in enumerate(peers) if peer.has_low_stake
        ]

        # remove entries from the list
        for index in sorted(indexes_to_remove, reverse=True):
            peer: Peer = peers.pop(index)

        # compute ct probability
        total_tf_stake = sum(peer.transformed_stake for peer in peers)
        for peer in peers:
            peer.reward_probability = peer.transformed_stake / total_tf_stake

    @classmethod
    def binsFromRange(cls, min: int, max: int, count: int):
        min, max, count = int(min), int(max), int(count)
        bins = list(range(min, max, int((max - min) / count)))
        bin_size = (max - min) / count
        bins.append(bins[-1] + bin_size)
        return bins

    @classmethod
    def getEligiblesPeers(
        cls,
        topology: list[TopologyEntry],
        peers: list[Peer],
        safes: list[SubgraphEntry],
        min_version: str,
    ):
        eligibles = Utils.mergeTopoPeersSafes(topology, peers, safes)

        addresses_to_exclude = [
            peer.address for peer in eligibles if peer.version_is_old(min_version)
        ]
        Utils.exclude(eligibles, addresses_to_exclude)

        addresses_to_exclude = [
            peer.address for peer in eligibles if peer.safe_allowance < 0
        ]
        Utils.exclude(eligibles, addresses_to_exclude)

        Utils.allowManyNodePerSafe(eligibles)

        return eligibles

    @classmethod
    async def getSafesData(cls):
        key = "registeredNodesInNetworkRegistry"
        query_id = "SUBGRAPH_SAFES_BALANCES_QUERY_ID"
        safes_provider = SafesProvider(Utils.buildSubgraphURL(query_id))

        results = list[SubgraphEntry]()
        for safe in await safes_provider.get():
            results.extend([SubgraphEntry.fromDict(node) for node in safe[key]])

        return results

    @classmethod
    async def getTopologyData(cls):
        api = HoprdAPI(*Utils.apiHostAndKey("API_HOST", "API_KEY"))

        channels = await api.all_channels(False)

        results = await Utils.aggregatePeerBalanceInChannels(channels.all)
        return [TopologyEntry.fromDict(*arg) for arg in results.items()]

    @classmethod
    async def getPeers(cls):
        fields = ["peer_id", "peer_address", "reported_version"]
        api = HoprdAPI(*Utils.apiHostAndKey("API_HOST", "API_KEY"))

        node_result = await api.peers(params=fields, quality=0.5)

        return {Peer(*[item[f] for f in fields]) for item in node_result}

    @classmethod
    def getRewardProbability(
        cls,
        eligibles: list[Peer],
        token_price: float,
        budget_dollars: int,
        limits: list[int],
        slope: float,
        flattening_factor: float,
    ):
        equations = Equations(
            Equation("a * x", "l <= x <= c"),
            Equation("a * c + (x - c) ** (1 / b)", "x > c"),
        )

        parameters = Parameters(slope, flattening_factor, limits[1], limits[0])
        budget_params = BudgetParameters(
            budget_dollars / token_price, 2628000, 1, 365, 0.03, 1.0
        )
        economic_model = EconomicModel(equations, parameters, budget_params)

        for peer in eligibles:
            peer.economic_model = economic_model
        Utils.rewardProbability(eligibles)

        return eligibles

    @classmethod
    def dumpSnapshot(
        cls,
        **kwargs
    ):
        date_time = datetime.now().strftime("%Y_%m_%d")

        folder_path = Path(f"snapshots/{date_time}")
        folder_path.mkdir(parents=True, exist_ok=True)

        for key, value in kwargs.items():
            with open(f"{folder_path}/{key}.pkl", "wb") as f:
                pickle.dump(value, f)

    @classmethod
    def loadSnapshot(cls, folder: str, *args):
        data = []
        for key in args:
            if not Path(f"snapshots/{folder}/{key}.pkl").exists():
                return None
            
            with open(f"snapshots/{folder}/{key}.pkl", "rb") as f:
                data.append(pickle.load(f))
            
        return data