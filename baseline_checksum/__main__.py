import click
import os

from dotenv import load_dotenv
from pathlib import Path

from .block import BlocksIO

# load_dotenv()

# SUBGRAPH_API_KEY = os.environ.get("SUBGRAPH_API_KEY")
# SUBGRAPH_QUERY_ID = os.environ.get("SUBGRAPH_QUERY_ID")
# url = f"https://gateway-arbitrum.network.thegraph.com/api/{SUBGRAPH_API_KEY}/subgraphs/id/{SUBGRAPH_QUERY_ID}"
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
        block_range = range(startblock-10, startblock+10)

    block_numbers = [block.number for block in blocks]
    intersection = set(block_numbers).intersection(block_range)

    if not intersection:
        print(f"No blocks in {block_range} found")

    for blocknumber in intersection:
        print(blocks[block_numbers.index(blocknumber)])

if __name__ == "__main__":
    main()



#  OK: 29839885
# NOK: 29839895
# NOT IN LIST: 29839905
