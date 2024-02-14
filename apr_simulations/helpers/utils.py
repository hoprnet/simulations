from os import environ

from models.peer import Address, Peer
from models.subgraph_entry import SubgraphEntry
from models.tolopogy_entry import TopologyEntry


class Utils:
    @classmethod
    def envvar(cls, key, type: type, default=None):
        return type(environ.get(key, default))

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
