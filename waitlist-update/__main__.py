import json
from os import environ
from pathlib import Path

import click
from dotenv import load_dotenv

from .candidate import Candidate
from .graphql_providers import NFTProvider, SafesProvider
from .registration import Registration
from .safe import Safe
from .utils import Decorator, Display, remove_duplicates, sort_waitlist


@click.command()
@click.option("--registry", type=Path, help="Registry file (.json)")
@click.option("--output", type=Path, default="output.json", help="Output file (.json)")
@Decorator.asynchronous
async def main(registry: Path, output: Path):
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

    # Loading registered nodes from registry
    registry = registry.with_suffix(".json")
    with open(registry, "r") as f:
        registered_nodes = remove_duplicates(
            Registration.fromJSON(json.load(f)), ["safe_address", "node_address"], True
        )
    Display.loadedData("Registered nodes", len(registered_nodes))

    # Filtering waitlist candidates (not already running)
    waitlist_candidates = [
        n for n in registered_nodes if n.node_address not in running_nodes
    ]
    Display.loadedData("Waitlist candidates", len(waitlist_candidates))

    # Filtering candidates by stake and NFT ownership
    cases = [
        "Approved",
        "Safe not deployed",
        "Empty node address",
        "Invalid node address",
        "Low balance (w/o NFT)",
        "Low balance (with NFT)",
    ]
    candidates: list[dict] = [{"list": [], "case": case} for case in cases]

    for wc in waitlist_candidates:
        if wc.safe_address not in deployed_safes_addresses:
            candidates[1]["list"].append(wc)
            continue

        deployed_safe = deployed_safes[deployed_safes_addresses.index(wc.safe_address)]

        candidate = Candidate(
            deployed_safe.address,
            wc.node_address,
            deployed_safe.balance,
            wc.safe_address in nft_holders,
        )

        if not candidate.node_address:
            candidates[2]["list"].append(candidate)
            continue

        if not candidate.node_address.startswith("0x"):
            candidates[3]["list"].append(candidate)
            continue

        if candidate.balance < 10_000:
            candidates[4]["list"].append(candidate)
            continue

        if candidate.balance < 30_000 and not candidate.nr_nft:
            candidates[5]["list"].append(candidate)
            continue

        candidates[0]["list"].append(candidate)

    nft_holders = [e for e in candidates[0]["list"] if e.nr_nft]
    non_nft_holders = [e for e in candidates[0]["list"] if not e.nr_nft]
    ordered_waitlist = sort_waitlist(nft_holders, non_nft_holders, (20, 10))

    # Printing candidates that were filtered out
    Display.separator("Candidates filtered out")
    Display.excludedCandidates(candidates[1:])

    # Sorting users according to COMM team rules
    Display.separator("Final results")
    if not ordered_waitlist:
        print("No candidates to be approved")
        return

    Display.candidates("Approved candidates", ordered_waitlist)

    # Exporting waitlist
    output = output.with_suffix(".json")
    with open(output, "w") as f:
        json.dump(Candidate.toContractData(ordered_waitlist), f, indent=4)
    print(f"\nWaitlist exported to '{output}'")


if __name__ == "__main__":
    main()
