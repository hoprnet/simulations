import click
from pathlib import Path

from .block import BlocksIO

RESET = "\033[0m"
BOLD = "\033[1m"

url = "https://api.studio.thegraph.com/query/58438/logs-for-hoprd/version/latest"

@click.command()
@click.option("--minblock", default=29706814, type=int, help="The block number to start from")
@click.option("--startblock", type=int, help="A specific block to calculate the checksum for (or from)")
@click.option("--endblock", default=None, type=int, help="A specific block to calculate the checksum to (or until)")
@click.option("--blocksfile", default=Path("blocks.json"), 
              type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
              help="A .json file to store the blocks, events and checksums in")
@click.option("--folder", default=Path("./_temp_results"), 
              type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
              help="The folder to store the data in")
def main(minblock: int, folder: Path, startblock: int, endblock: int, blocksfile: Path):
    blocks_io = BlocksIO(blocksfile)

    if blocksfile and blocksfile.exists():
        blocks = blocks_io.fromJSON()
    else:
        blocks = blocks_io.fromSubgraphData(folder, minblock, url)
    
    if endblock:
        block_range = range(startblock, endblock+1)
    else:
        block_range = range(startblock-5, startblock+6)

    block_numbers = [block.number for block in blocks]
    intersection = list(set(block_numbers).intersection(block_range))
    intersection.sort()

    if not intersection:
        print(f"No blocks in {block_range} found")

    for blocknumber in intersection:         
        if blocknumber == startblock:
            print(BOLD, end="")

        print(blocks[block_numbers.index(blocknumber)], end=f"{RESET}\n")

if __name__ == "__main__":
    main()

# block #30548792 with checksum: 0x42ff4ad17e5f49e3e382291c59b38df02e73d0f54cfaadf6e31d4035864f0ed2
