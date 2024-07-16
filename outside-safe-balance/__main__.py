import json
import os
import time
from enum import Enum

import click
from dotenv import load_dotenv

from .graphql_providers import SafesProvider
from .hoprd_api import HoprdAPI
from .taskmanager import TaskManager
from .utils import Utils, asynchronous


class AddressType(Enum):
    INVALID = "Provided address is not a valid safe or node address"
    SAFE = "Provided address is a safe address"
    NODE = "Provided address is a node address. Using related safe address"


@click.command()
@click.option(
    "--address",
    "address",
    default=None,
    required=False,
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

    # Get all peers channels balances
    with TaskManager("Getting outgoing channels for all detected nodes"):
        balances = Utils.aggregatePeerBalanceInChannels(
            (await api.all_channels(False)).all
        )

    with TaskManager("Getting all nodes from subgraph"):
        all_nodes = await Utils.nodesFromSubgraph(provider)

    safe_addresses = list(set((map(lambda x: x.safe_address.lower(), all_nodes))))
    node_addresses = list(set(map(lambda x: x.node_address.lower(), all_nodes)))
    nodes_balances = {"timestamp": time.time(), "safes": {}}

    if address := address:
        address = address.lower()
        safe_address = None

        with TaskManager("Checking provided address"):
            if address in safe_addresses:
                safe_address = address
                addressType = AddressType.SAFE

            elif address in node_addresses:
                safe_address = all_nodes[node_addresses.index(address)].safe_address
                addressType = AddressType.NODE

            else:
                raise ValueError(AddressType.INVALID.value)

        print(addressType.value)

        with TaskManager("Getting safe funds"):
            nodes_balances.update(Utils.safeFunds(safe_address, all_nodes, balances))

        print(
            f"\tFound {len(nodes_balances[safe_address]['nodes_channels_balances'])} nodes linked to safe '{safe_address}'"
        )
        print(
            f"\tTotal funds in outgoing channels: {nodes_balances[safe_address]['total_balance']} wxHOPR"
        )
    else:
        with TaskManager(f"Getting funds for {len(safe_addresses)} safes"):
            for safe_address in safe_addresses:
                nodes_balances["safes"].update(
                    Utils.safeFunds(safe_address, all_nodes, balances)
                )

    if output := output:
        with TaskManager(f"Dumping nodes total outgoing funds to {output}"):
            with open(output, "w") as f:
                json.dump(nodes_balances, f)


if __name__ == "__main__":
    main()
