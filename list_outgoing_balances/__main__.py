import asyncio
import json

import click
from dotenv import load_dotenv

from .graphql_providers import SafesProvider
from .hoprd_api import HoprdAPI
from .utils import Utils


class TaskManager:
    def __init__(self, text: str):
        self.text = text

    def __enter__(self):
        print(f"- {self.text}...", end=" ")

    def __exit__(self, type, value, traceback):
        if type:
            print("❌")
            print(f"Error: {value}")
        else:
            print("✅")


@click.command()
@click.option(
    "--address",
    "safe_address",
    required=True,
    help="Safe address to get outgoing balances",
)
@click.option(
    "--output",
    "output_file",
    default=None,
    required=False,
    help="Output file (.json) to save the results",
)
def main(safe_address: str, output_file: str):
    if not load_dotenv():
        print("No .env file found")

    provider = SafesProvider(
        "https://api.studio.thegraph.com/query/40439/hopr-nodes-dufour/version/latest"
    )
    addresses, keys = Utils.nodesAddresses("NODE_ADDRESS", "NODE_KEY")
    api = HoprdAPI(addresses[0], keys[0])

    with TaskManager("Getting all nodes from subgraph"):
        all_nodes = asyncio.run(Utils.nodesFromSubgraph(provider))

    safe_entries = filter(lambda x: x.safe_address == safe_address, all_nodes)
    node_addresses = list(map(lambda x: x.node_address, safe_entries))

    print(f"\tFound {len(node_addresses)} nodes linked to safe `{safe_address}`")

    # Get all peers channels balances
    with TaskManager("Getting outgoing channels for all detected nodes"):
        channels = asyncio.run(api.all_channels(False))
        balances = Utils.aggregatePeerBalanceInChannels(channels.all)

    # Filtering
    node_balances_dict = {}
    for value in balances.values():
        if value["source_node_address"] not in node_addresses:
            continue

        node_balances_dict[value["source_node_address"]] = value["channels_balance"]

    if output_file is not None:
        with TaskManager(f"Dumping nodes total outgoing funds to {output_file}"):
            with open(output_file, "w") as f:
                json.dump(node_balances_dict, f)

    print(
        f"\tTotal funds in outgoing channels: {sum(node_balances_dict.values())} wxHOPR"
    )


if __name__ == "__main__":
    main()
