from .subgraph.entries import Safe
from .subgraph.providers import SafesProvider


def aggregate_peer_balance_in_channels(channels: list) -> dict[str, dict]:
    """
    Returns a dict containing all unique source_peerId-source_address links.
    """
    results: dict[str, dict] = {}
    for c in channels:
        if not c.status.is_open:
            continue

        if c.source_peer_id not in results:
            results[c.source_peer_id] = {
                "source_node_address": c.source_address,
                "channels_balance": 0,
            }
        if c.destination_peer_id not in results:
            results[c.destination_peer_id] = {
                "source_node_address": c.destination_address,
                "channels_balance": 0,
            }

        results[c.source_peer_id]["channels_balance"] += int(c.balance) / 1e18

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
    safe_address: str, all_nodes: list[Safe], balances: dict[str, dict]
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

        nodes_balances[value["source_node_address"]] = float(
            value["channels_balance"]
        )

    # Safe balance
    safe_balance = matching_nodes[0].wxHoprBalance if len(matching_nodes) > 0 else 0
    channels_balance = sum(nodes_balances.values())

    return {
        safe_address: {
            "total_balance": channels_balance + safe_balance,
            "safe_balance": safe_balance,
            "channels_balance": channels_balance,
            "nodes_channels_balances": nodes_balances,
        }
    }
