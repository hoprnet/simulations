from pathlib import Path

import click

from .block import BlocksIO
from .library import asynchronous

RESET = "\033[0m"
BOLD = "\033[1m"

url = "https://api.studio.thegraph.com/query/58438/logs-for-hoprd/version/latest"


@click.command()
@click.option(
    "--minblock", default=29706814, type=int, help="The block number to start from"
)
@click.option(
    "--block",
    "startblock",
    type=int,
    help="A specific block to calculate the checksum for (or from)",
)
@click.option(
    "--to",
    "endblock",
    default=None,
    type=int,
    help="A specific block to calculate the checksum to (or until)",
)
@click.option(
    "--blocksfile",
    default=Path("blocks.json"),
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
    help="A .json file to store the blocks, events and checksums in",
)
@click.option(
    "--folder",
    default=Path("./.temp_results"),
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="The folder to store the data in",
)
@click.option("--no-update", "-u", is_flag=True, help="Do not update the blocks file")
@click.option("--fill", "-f", is_flag=True, help="Fill the missing blocks with empty blocks")
@asynchronous
async def main(
    minblock: int,
    folder: Path,
    startblock: int,
    endblock: int,
    blocksfile: Path,
    no_update: bool,
    fill: bool
):
    blocks_io = BlocksIO(blocksfile, folder)

    if blocksfile and blocksfile.exists():
        blocks_io.fromJSON()
        minblock = blocks_io.blocks[-1].number

    if not no_update:
        await blocks_io.fromSubgraphData(minblock, url)
        blocks_io.toJSON()
    else:
        print("Skipping blocks update with onchain data")

    if fill:
        blocks_io.fillMissingBlocks()

    block_numbers = [block.number for block in blocks_io.blocks]

    if endblock:
        block_range = range(startblock, endblock + 1)
    else:
        block_range = range(startblock - 5, startblock + 6)

    block_numbers = [block.number for block in blocks_io.blocks]
    intersection = list(set(block_numbers).intersection(block_range))
    intersection.sort()

    print(f"Using events from block {block_numbers[0]} to {block_numbers[-1]}")
    if not intersection:
        print(f"No blocks in {block_range} found")

    for blocknumber in intersection:
        if blocknumber == startblock:
            print(BOLD, end="")

        print(blocks_io.blocks[block_numbers.index(blocknumber)], end=f"{RESET}\n")


if __name__ == "__main__":
    main()
