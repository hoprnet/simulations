import json
import os

import click
from dotenv import load_dotenv

from .graphql_providers import SafesProvider
from .hoprd_api import HoprdAPI
from .taskmanager import TaskManager
from .utils import Utils, asynchronous


@click.command()
@click.option(
    "--address",
    "address",
    required=True,
    help="Safe address to get outgoing balances",
)
@click.option(
    "--output",
    "output",
    default=None,
    required=False,
    help="Output file (.json) to save the results",
)
@asynchronous
async def main(address: str, output: str):
    if not load_dotenv():
        print("No .env file found")
        return

    provider = SafesProvider(os.environ["SUBGRAPH_SAFES_URL"])
    api = HoprdAPI(os.environ["NODE_ADDRESS"], os.environ["NODE_KEY"])

    with TaskManager("Getting all nodes from subgraph"):
        all_nodes = await Utils.nodesFromSubgraph(provider)

    safe_addresses = list(map(lambda x: x.safe_address, all_nodes))
    node_addresses = list(map(lambda x: x.node_address, all_nodes))
    safe_address = None

    if address in safe_addresses:
        safe_address = address
        print("\tProvided address is a safe address")

    if address in node_addresses:
        safe_address = all_nodes[node_addresses.index(address)].safe_address
        print(f"\tProvided address is a node address. Using related safe address")

    if safe_address is None:
        print("\tProvided address is not a valid safe or node address")
        return

    matching_nodes = list(filter(lambda x: x.safe_address == safe_address, all_nodes))
    matching_node_addresses = list(map(lambda x: x.node_address, matching_nodes))

    print(f"\tFound {len(matching_nodes)} nodes linked to safe '{safe_address}'")

    # Get all peers channels balances
    with TaskManager("Getting outgoing channels for all detected nodes"):
        channels = await api.all_channels(False)
        balances = Utils.aggregatePeerBalanceInChannels(channels.all)

    # Filtering
    node_balances = {}
    for value in balances.values():
        if value["source_node_address"] not in matching_node_addresses:
            continue

        node_balances[value["source_node_address"]] = value["channels_balance"]

    if output := output:
        with TaskManager(f"Dumping nodes total outgoing funds to {output}"):
            with open(output, "w") as f:
                json.dump(node_balances, f)

    print(f"\tTotal funds in outgoing channels: {sum(node_balances.values())} wxHOPR")


if __name__ == "__main__":
    main()
