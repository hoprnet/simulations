import json
from pathlib import Path

import click
from dotenv import load_dotenv

from lib.helper import asynchronous

from .candidate import Candidate
from .helper import Display, remove_duplicates, sort_waitlist
from .registration import Registration
from .subgraph.entries import NFTHolder, Safe
from .subgraph.providers import NFTProvider, SafesProvider


@click.command()
@click.option("--registry", type=Path, help="Registry file (.json)")
@click.option("--output", type=Path, default="output.json", help="Output file (.json)")
@asynchronous
async def main(registry: Path, output: Path):
    if not load_dotenv():
        print("No .env file found")
        return

    # Loading nft holders from subgraph
    nft_holders = list[str]()

    for entry in await NFTProvider("SUBGRAPH_NFT_URL").get():
        nft_holders.append(NFTHolder.fromSubgraphResult(entry))
    Display.loadedData("NFTHolder", len(nft_holders))

    # Loading deployed safes from subgraph
    deployed_safes = list[Safe]()
    for entry in await SafesProvider("SUBGRAPH_SAFES_URL").get():    
        deployed_safes.append(Safe.fromSubgraphResult(entry))
    Display.loadedData("SafesProvider", len(deployed_safes))


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
            wc.safe_address in [h.address for h in nft_holders],
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
