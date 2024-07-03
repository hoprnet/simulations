import asyncio
import functools
from os import environ
from typing import Any

from .graphql_providers import ProviderError, SafesProvider
from .safe import Safe


def asynchronous(func):
    """
    Decorator to run async functions synchronously. Helpful espacially for the main function,
    when used alongside the click library.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


class Utils:
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
        all_nodes = list[Safe]()
        try:
            for safe in await provider.get():
                entries = [
                    Safe.fromSubgraphResult(node)
                    for node in safe["registeredNodesInNetworkRegistry"]
                ]
                all_nodes.extend(entries)

        except ProviderError as err:
            print(f"get_registered_nodes: {err}")

        return all_nodes

    @classmethod
    def safeFunds(
        cls, safe_address: str, all_nodes: list[Safe], balances: dict[str, dict]
    ):
        matching_nodes = list(
            filter(lambda x: x.safe_address == safe_address, all_nodes)
        )
        matching_node_addresses = list(map(lambda x: x.node_address, matching_nodes))

        # Filtering
        nodes_balances = {}
        for value in balances.values():
            if value["source_node_address"] not in matching_node_addresses:
                continue

            nodes_balances[value["source_node_address"]] = value["channels_balance"]

        # Safe balance
        safe_balance = matching_nodes[0].wxHoprBalance if len(matching_nodes) > 0 else 0
        channels_balance = sum(nodes_balances.values())

        return {
            safe_address: {
                "total_balance": channels_balance + safe_balance,
                "safe_balance": safe_balance,
                "nodes_channels_balances": nodes_balances,
            }
        }
