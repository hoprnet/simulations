from pathlib import Path

import click
from dotenv import load_dotenv

from lib import exporter
from lib.helper import asynchronous
from lib.taskmanager import TaskManager

from .subgraph import helper
from .subgraph.entries import Ticket


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
    type=Path,
    help="Output file (.json/.yaml/.yml) where save the results to",
)
@asynchronous
async def main(safe: str, output: Path):
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

    print(
        f"\tTotal amount redeemed: {stats.resume.redeemed_value:7.2f} wxHOPR ({stats.resume.ticket_count} tickets)")

    for address, stat in stats.nodes.items():
        print(
            f"\tAmount redeemed by {address}: {stat.redeemed_value:7.2f} wxHOPR ({stat.ticket_count} tickets)")

    if not output:
        return

    with TaskManager(f"Dumping total tickets amounts to {output}"):
        exporter.export(output, stats.as_dict)

if __name__ == "__main__":
    main()
