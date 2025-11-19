import os
import time
from enum import Enum
from pathlib import Path

import click
from api_lib.headers.authorization import Bearer
from dotenv import load_dotenv

from lib import exporter
from lib.helper import asynchronous
from lib.hoprd_api import HoprdAPI
from lib.hoprd_api.balance import Balance
from lib.taskmanager import TaskManager

from .helper import aggregate_peer_balance_in_channels, nodes_from_subgraph, safe_funds
from .subgraph.providers import SafesProvider


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
    default="output.json",
    type=Path,
    help="Output file (.json) to save the results",
)
@asynchronous
async def main(address: str, output: Path):
    if not load_dotenv():
        print("No .env file found")
        return

    provider = SafesProvider("SUBGRAPH_SAFES_URL")
    api = HoprdAPI(os.environ["NODE_ADDRESS"], Bearer(os.environ["NODE_KEY"]), "/api/v4")

    # Get all peers channels balances
    channels = await api.channels()
    with TaskManager("Getting outgoing channels for all detected nodes"):
        if not hasattr(channels, "all"):
            raise ValueError("No channels found for the provided node address")

        balances: dict[str, Balance] = aggregate_peer_balance_in_channels(
            channels.all
        )

    with TaskManager("Getting all nodes from subgraph"):
        all_nodes = await nodes_from_subgraph(provider)
    
    node_safe_dict: dict[str, str] = { node.node_address:node.safe_address for node in all_nodes}

    safe_addresses: set[str] = set(node_safe_dict.values())
    node_addresses: set[str] = set(node_safe_dict.keys())

    nodes_balances: dict = {"timestamp": time.time()}

    if address := address:
        address = address.lower()
        safe_address = None

        with TaskManager("Checking provided address"):
            if address in safe_addresses:
                safe_address: str = address
                addressType = AddressType.SAFE

            elif address in node_addresses:
                safe_address = node_safe_dict[address]
                addressType = AddressType.NODE

            else:
                raise ValueError(AddressType.INVALID.value)

        print(addressType.value)

        with TaskManager("Getting safe funds"):
            nodes_balances.update(safe_funds(
                safe_address, all_nodes, balances))

        print(
            f"\tFound {len(nodes_balances[safe_address]['nodes_channels_balances'])} nodes linked to safe '{safe_address}'"
        )

        print(
            f"\tTotal funds in outgoing channels: {round(nodes_balances[safe_address]['channels_balance'], 2).as_str}"
        )

    else:
        with TaskManager(f"Getting funds for {len(safe_addresses)} safes"):
            for safe_address in safe_addresses:
                nodes_balances["safes"].update(
                    safe_funds(safe_address, all_nodes, balances)
                ) 

    with TaskManager(f"Dumping nodes total outgoing funds to {output}"):
        exporter.export(output, nodes_balances)


if __name__ == "__main__":
    main()
