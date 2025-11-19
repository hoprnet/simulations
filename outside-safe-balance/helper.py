from lib.hoprd_api.balance import Balance
from lib.hoprd_api.response_objects import Channel

from .subgraph.entries import Safe
from .subgraph.providers import SafesProvider


def aggregate_peer_balance_in_channels(channels: list[Channel]) -> dict[str, Balance]:
    """
    Returns a dict containing all unique source_peerId-source_address links.
    """
    results: dict[str, Balance] = {}
    for c in channels:
        if not c.status.is_open:
            continue

        if c.source not in results:
            results[c.source] = Balance.zero("wxHOPR")
        if c.destination not in results:
            results[c.destination] = Balance.zero("wxHOPR")

        results[c.source] += c.balance

    return results

async def nodes_from_subgraph(provider: SafesProvider):
    all_nodes = list[Safe]()
    try:
        for safe in await provider.get():
            entries = [
                Safe.fromSubgraphResult(node)
                for node in safe["registeredNodesInNetworkRegistry"]
            ]
            all_nodes.extend(entries)
    except Exception as err:
        raise err

    return all_nodes

def safe_funds(
    safe_address: str, all_nodes: list[Safe], balances: dict[str, Balance]
):
    matching_nodes: list[Safe] = list(
        filter(lambda x: x.safe_address == safe_address, all_nodes)
    )
    matching_node_addresses = list(map(lambda x: x.node_address, matching_nodes))

    # Filtering
    nodes_balances: dict[str, Balance] = {}

    for address, balance in balances.items():
        if address not in matching_node_addresses:
            continue

        nodes_balances[address] = balance

    # Safe balance
    safe_balance: Balance = matching_nodes[0].wxHoprBalance if len(matching_nodes) > 0 else Balance.zero("wxHOPR")
    channels_balance: Balance = sum(nodes_balances.values(), Balance.zero("wxHOPR"))

    return {
        safe_address: {
            "total_balance": channels_balance + safe_balance,
            "safe_balance": safe_balance,
            "channels_balance": channels_balance,
            "nodes_channels_balances": nodes_balances,
        }
    }
    