import json

import click
import yaml
from dotenv import load_dotenv

from lib.helper import asynchronous
from lib.taskmanager import TaskManager

from .subgraph import helper
from .subgraph.entries import Ticket

export_method = {
    "json": json.dump,
    "yaml": yaml.dump,
    "yml": yaml.dump,
}


@click.command()
@click.option(
    "--safe",
    "safe",
    default=None,
    required=True,
    help="Safe address to get transactions from",
)
@click.option(
    "--output",
    "output",
    default=None,
    required=False,
    help="Output file (.json/.yaml/.yml) where save the results to",
)
@asynchronous
async def main(safe: str, output: str):
    if not load_dotenv():
        print("No .env file found")
        return

    with TaskManager("Getting all nodes linked to safe"):
        relayers = await helper.safe_to_nodes(safe)
    print(f"\tFound {len(relayers)} nodes linked to the safe `{safe}` ")

    with TaskManager("Getting all tickets issued"):
        tickets = await helper.nodes_to_tickets(relayers)
    print(f"\tFound {len(tickets)} tickets issued by the relayers")

    with TaskManager("Aggregating ticket amounts"):
        stats = Ticket.aggregate(tickets)

    print(f"\tTotal amount redeemed: {stats['total']:7.2f} wxHOPR")
    for address, amount in stats["nodes"].items():
        print(f"\tAmount redeemed by {address}: {amount:7.2f} wxHOPR")

    if not output:
        return
    
    with TaskManager(f"Dumping total tickets amounts to {output}"):
        ext = output.split(".")[-1]

        if ext in export_method:
            with open(output, "w") as f:
                export_method[ext](stats, f)
        else:
            raise ValueError("Output file must be a .json or .yaml file")

if __name__ == "__main__":
    main()
