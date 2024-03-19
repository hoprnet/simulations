from os import environ
from typing import Any

from .graphql_providers import ProviderError, SafesProvider
from .subgraph_entry import SubgraphEntry


class Utils:
    @classmethod
    def envvarWithPrefix(cls, prefix: str, type=str) -> dict[str, Any]:
        var_dict = {
            key: type(v) for key, v in environ.items() if key.startswith(prefix)
        }

        return dict(sorted(var_dict.items()))

    @classmethod
    def nodesAddresses(
        cls, address_prefix: str, keyenv: str
    ) -> tuple[list[str], list[str]]:
        addresses = Utils.envvarWithPrefix(address_prefix).values()
        keys = Utils.envvarWithPrefix(keyenv).values()

        return list(addresses), list(keys)

    @classmethod
    def aggregatePeerBalanceInChannels(cls, channels: list) -> dict[str, dict]:
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
    async def nodesFromSubgraph(cls, provider: SafesProvider):
        all_nodes = list[SubgraphEntry]()
        try:
            for safe in await provider.get():
                entries = [
                    SubgraphEntry.fromSubgraphResult(node)
                    for node in safe["registeredNodesInNetworkRegistry"]
                ]
                all_nodes.extend(entries)

        except ProviderError as err:
            print(f"get_registered_nodes: {err}")

        return all_nodes