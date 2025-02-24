import json
from enum import Enum
from pathlib import Path

import click
from dotenv import load_dotenv

from lib import exporter
from lib.helper import asynchronous
from lib.taskmanager import TaskManager

from .candidate import Candidate
from .helper import Display, remove_duplicates, sort_waitlist
from .registration import Registration
from .subgraph.entries import NFTHolder, Safe
from .subgraph.providers import NFTProvider, SafesProvider


class EligibilityCase(Enum):
    APPROVED = "Approved"
    SAFE_NOT_DEPLOYED = "Safe not deployed"
    EMPTY_NODE_ADDRESS = "Empty node address"
    INVALID_NODE_ADDRESS = "Invalid node address"
    LOW_BALANCE_WO_NFT = "Low balance without NFT"
    LOW_BALANCE_WITH_NFT = "Low balance with NFT"


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
    with TaskManager("Getting NFT holders from subgraph"):
        for entry in await NFTProvider("SUBGRAPH_NFT_URL").get():
            nft_holders.append(NFTHolder.fromSubgraphResult(entry))
    print(f"\tLoaded {len(nft_holders)} entries")

    # Loading deployed safes from subgraph
    deployed_safes = list[Safe]()
    with TaskManager("Getting deployed safes from subgraph"):
        for entry in await SafesProvider("SUBGRAPH_SAFES_URL").get():    
            deployed_safes.append(Safe.fromSubgraphResult(entry))
    print(f"\tLoaded {len(deployed_safes)} entries")

    deployed_safes_addresses = [s.address for s in deployed_safes]
    running_nodes = sum([s.nodes for s in deployed_safes], [])

    # Loading registered nodes from registry
    registry = registry.with_suffix(".json")

    with TaskManager("Loading registered nodes from registry"):
        with open(registry, "r") as f:
            registered_nodes = remove_duplicates(
                Registration.fromJSON(json.load(f)), ["safe_address", "node_address"], True
            )
    print(f"\tLoaded {len(registered_nodes)} entries")

    # Filtering waitlist candidates (not already running)
    waitlist_candidates = [
        n for n in registered_nodes if n.node_address not in running_nodes
    ]
    print(f"There's {len(waitlist_candidates)} candidate willing to joining network")

    # Filtering candidates by stake and NFT ownership
    candidates: dict[EligibilityCase, list] = {case: [] for case in EligibilityCase}

    for wc in waitlist_candidates:
        if wc.safe_address not in deployed_safes_addresses:
            candidates[EligibilityCase.SAFE_NOT_DEPLOYED].append(wc)
            continue

        deployed_safe = deployed_safes[deployed_safes_addresses.index(wc.safe_address)]

        candidate = Candidate(
            deployed_safe.address,
            wc.node_address,
            deployed_safe.balance,
            wc.safe_address in [h.address for h in nft_holders],
        )

        if not candidate.node_address:
            candidates[EligibilityCase.EMPTY_NODE_ADDRESS].append(candidate)
            continue

        if not candidate.node_address.startswith("0x"):
            candidates[EligibilityCase.INVALID_NODE_ADDRESS].append(candidate)
            continue

        if candidate.balance < 10_000:
            candidates[EligibilityCase.LOW_BALANCE_WITH_NFT].append(candidate)
            continue

        if candidate.balance < 30_000 and not candidate.nr_nft:
            candidates[EligibilityCase.LOW_BALANCE_WO_NFT].append(candidate)
            continue

        candidates[EligibilityCase.APPROVED].append(candidate)

    nft_holders = [e for e in candidates[EligibilityCase.APPROVED] if e.nr_nft]
    non_nft_holders = [e for e in candidates[EligibilityCase.APPROVED] if not e.nr_nft]
    ordered_waitlist = sort_waitlist(nft_holders, non_nft_holders, (20, 10))

    # Printing candidates that were filtered out
    Display.separator("Candidates filtered out")

    # get all candidates that are not approved
    candidates.pop(EligibilityCase.APPROVED)
    Display.excludedCandidates(candidates)

    # Sorting users according to COMM team rules
    Display.separator("Final results")
    if not ordered_waitlist:
        print("No candidates to be approved")
        return

    Display.candidates("Approved candidates", ordered_waitlist)

    # Exporting waitlist
    with TaskManager(f"Exporting waitlist to {output}"):
        exporter.export(output, Candidate.toContractData(ordered_waitlist))


if __name__ == "__main__":
    main()
