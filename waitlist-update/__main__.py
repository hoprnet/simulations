from os import environ

import click
from dotenv import load_dotenv

from .candidate import Candidate
from .graphql_providers import NFTProvider, SafesProvider
from .registration import Registration
from .safe import Safe
from .utils import (
    asynchronous,
    print_loaded_data,
    remove_duplicates,
    separator_text,
    sort_waitlist,
)


@click.command()
@click.option("--registry", default="registry.xlsx", help="Registry file (.xlsx)")
@click.option("--output", default="output.xlsx", help="Output file (.xlsx)")
@asynchronous
async def main(registry: str, output: str):
    if not load_dotenv():
        print("No .env file found")
        return

    # Loading nft holders from subgraph
    nft_holders = list[str]()

    for entry in await NFTProvider.safe_get(environ.get("SUBGRAPH_NFT_URL")):
        if owner := entry.get("owner", {}).get("id", None):
            nft_holders.append(owner)

    # Loading deployed safes from subgraph
    deployed_safes = list[Safe]()
    for entry in await SafesProvider.safe_get(environ.get("SUBGRAPH_SAFES_URL")):
        safe_address = entry.get("id", {})
        wxHOPR_balance = float(entry.get("balance", {}).get("wxHoprBalance", "0"))
        nodes = entry.get("registeredNodesInNetworkRegistry", {})

        entry = Safe(safe_address, wxHOPR_balance, [n["node"]["id"] for n in nodes])
        deployed_safes.append(entry)

    deployed_safes_addresses = [s.address for s in deployed_safes]
    running_nodes = sum([s.nodes for s in deployed_safes], [])

    # Loading registration data (from Andrius)
    registered_nodes = remove_duplicates(
        Registration.fromXLSX(registry), ["safe_address", "node_address"], True
    )
    print_loaded_data("Registered nodes", len(registered_nodes))

    waitlist_candidates = [
        n for n in registered_nodes if n.node_address not in running_nodes
    ]
    print_loaded_data("Waitlist candidates", len(waitlist_candidates))

    # Filtering candidates by stake and NFT ownership
    waitlist = []
    safe_not_deployed_candidates = []
    low_balance_candidates = []
    low_balance_nft_candidates = []
    invalid_node_address_candidates = []

    for c in waitlist_candidates:
        if c.safe_address not in deployed_safes_addresses:
            safe_not_deployed_candidates.append(c)
            continue

        index = deployed_safes_addresses.index(c.safe_address)
        deployed_safe = deployed_safes[index]
        candidate = Candidate(
            deployed_safe.address,
            c.node_address,
            deployed_safe.wxHoprBalance,
            c.safe_address in nft_holders,
        )

        if candidate.wxHOPR_balance < 10_000:
            low_balance_candidates.append(candidate)
            continue

        if candidate.wxHOPR_balance < 30_000 and not candidate.nr_nft:
            low_balance_nft_candidates.append(candidate)
            continue

        if not candidate.node_address.startswith("0x"):
            invalid_node_address_candidates.append(candidate)
            continue

        waitlist.append(candidate)

    nft_holders = [e for e in waitlist if e.nr_nft]
    non_nft_holders = [e for e in waitlist if not e.nr_nft]
    ordered_waitlist = sort_waitlist(nft_holders, non_nft_holders, (20, 10))

    # Printing candidates that were filtered out
    print(separator_text("Candidates filtered out", "-"))

    if data := safe_not_deployed_candidates:
        print("Safe not deployed:")
        for c in data:
            print(f"\t{c.safe_address}")

    if data := low_balance_candidates:
        print("Low balance safes -- format <safe> (<balance>):")
        for c in low_balance_candidates:
            print(f"\t{c.safe_address} ({c.wxHOPR_balance} wxHOPR)")

    if data := low_balance_nft_candidates:
        print("Low balance with NFT -- format <safe> (<balance>):")
        for c in data:
            print(f"\t{c.safe_address} ({c.wxHOPR_balance} wxHOPR)")

    if data := invalid_node_address_candidates:
        print("Invalid node address -- format <safe> (<node address>):")
        for c in data:
            print(f"\t{c.safe_address} ({c.node_address})")

    # Sorting users according to COMM team rules
    print(separator_text("Final results", "-"))
    print(f"{'NFT holders in waitlist':30s}\t{len(nft_holders)}")
    print(f"{'non-NFT holders in waitlist':30s}\t{len(non_nft_holders)}")
    print(f"{'Eligible candidates':30s}\t{len(ordered_waitlist)}")

    # Exporting waitlist
    Candidate.toDataFrame(ordered_waitlist).to_excel(output, index=False)
    print(f"\nWaitlist exported to '{output}'")

    # Sanity check
    assert len(ordered_waitlist) == len(nft_holders) + len(non_nft_holders)
    assert len(ordered_waitlist) == (
        len(remove_duplicates(ordered_waitlist, ["safe_address", "node_address"]))
    ), "Some entries are duplicated in the generated waitlist"


if __name__ == "__main__":
    main()
