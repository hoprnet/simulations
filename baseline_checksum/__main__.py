import asyncio
import json
import os
from pathlib import Path
import click

from .event import Event, events_from_local_files, events_from_subgraph
from .block import Block
from .library import keccak_256

from dotenv import load_dotenv

load_dotenv()

BOLD = "\033[1m"
RESET = "\033[0m"

DUNE_API_KEY = os.environ.get("DUNE_API_KEY")
DUNE_QUERY_ID = os.environ.get("DUNE_QUERY_ID")
url = f"https://gateway-arbitrum.network.thegraph.com/api/{DUNE_API_KEY}/subgraphs/id/{DUNE_QUERY_ID}"

@click.command()
@click.option("--minblock", default=29706814, type=int, help="The block number to start from")
@click.option("--path", default="./foo_results", help="The folder to store the data in")
@click.option("--blocknumber", default=None, type=int, help="A specific block to calculate the checksum for")
@click.option("--blocksfile", default=None, help="A .json file to store the blocks, events and checksums in")
def main(minblock: int, path, blocknumber, blocksfile):
    blocks: list[Block] = []

    if blocksfile and Path(blocksfile).exists():
        print(f"Loading blocks from {blocksfile}")

        block_jsons = {}
        with open(blocksfile, "r") as f:
            block_jsons = json.load(f)

        for block_number, block_json in block_jsons.items():
            block = Block(int(block_number))
            for event_json in block_json["events"]:
                block.add_event(Event.fromDict(event_json))
            block.checksum = bytearray.fromhex(block_json["checksum"])
            blocks.append(block)
    else:
        # import data, either from local files or from the subgraph API
        folder = Path(path)
        if folder.exists():
            data = events_from_local_files(folder)
        else:
            folder.mkdir()
            data = asyncio.run(events_from_subgraph(folder, url, minblock))

        # remove duplicates and sort by block_number, tx_index, log_index
        events = list(set([Event.fromDict(d) for d in data]))
        events.sort()

        # create blocks out of events
        for event in events:
            if not blocks or blocks[-1].number != event.block_number:
                blocks.append(Block(event.block_number))

            blocks[-1].add_event(event)

        # calculate checksums
        checksums: list[bytearray] = [bytearray(32)]
        for block in blocks:
            cat_str = b''.join([checksums[-1], block.keccak_256()])
            block.checksum = keccak_256(cat_str)
            checksums.append(keccak_256(cat_str))

        # save blocks, events and checksums to file
        if blocksfile:
            print(f"Saving blocks to {blocksfile}")
            block_jsons = {}
            for block in blocks:
                block_jsons.update(block.json_format())
            with open(blocksfile, "w+") as f:
                json.dump(block_jsons, f)


    # show block and events structure
    print(f"Retrieved range of blocks from #{blocks[0].number} to #{blocks[-1].number}")
    print("\n" + "-"*os.get_terminal_size().columns)
    for block in blocks[:5]:
        print(f"{BOLD}Block {block.number}{RESET} with {len(block.events)} event(s). Keccak256: {block.keccak_256().hex()}")
        for event in block.events:
            print(f"  {event}")
    if len(blocks) > 5:
        print("...")
    print("-"*os.get_terminal_size().columns + "\n")
    
    # show checksum for specific block
    block_numbers = [block.number for block in blocks]
    if blocknumber and blocknumber not in block_numbers:
        print(f"Block {blocknumber} not in retrieved blocks")
        return
    
    index = block_numbers.index(blocknumber) if blocknumber else -1
    block = blocks[index]
    print(f"checksum @ block {BOLD}{block.number}{RESET}: {block.checksum.hex()}")
    print(f"{len(block.events)} log(s)):")
    for event in block.events:
        print(f"  {event}")

if __name__ == "__main__":
    main()



#  OK: 29839885
# NOK: 29839895


# NOT IN LIST: 29839905
