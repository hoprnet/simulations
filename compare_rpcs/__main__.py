import asyncio
import json

import click

from lib.colors import Color
from lib.helper import asynchronous, progress_bar
from lib.rpc.entries.log import Log
from lib.rpc.entries.types.block import Block
from lib.rpc.query_provider import ETHGetLogsRPCProvider

from .rpc_url import RPCUrl

MAX_SINGLE_QUERY_BLOCK_RANGE: int = 100


def get_ranges(from_block: Block, to_block: Block, max_range: int):
    current_start = from_block

    while current_start <= to_block:
        current_end = min(current_start + (max_range - 1), to_block)
        yield current_start, current_end
        current_start = current_end + 1


@click.command()
@click.option("--url", "-u", "urls", type=RPCUrl, multiple=True, help="RPC URLs to connect to")
@click.option("--fromBlock", "from_block", type=Block, help="Starting block number")
@click.option("--toBlock", "to_block", type=Block, help="Ending block number")
@asynchronous
async def main(urls: list[RPCUrl], from_block: Block, to_block: Block):
    logs: dict[str, list[dict]] = {}

    for item in urls: 
        print(*Color.BOLD_STRING, sep=item.url)
        logs[item.url] = []

        for start, end in get_ranges(from_block, to_block, MAX_SINGLE_QUERY_BLOCK_RANGE):
            if to_block != from_block:
                progress_bar(start.idx, to_block.idx, percentage=(start.idx - from_block.idx) / (to_block.idx - from_block.idx))

            sub_logs: list[Log] = await ETHGetLogsRPCProvider(item.url).get(
                    fromBlock=start.idx,
                    toBlock=end.idx,
                    address=None,
                    topics=[]
            )
            logs[item.url].extend([log.as_dict for log in sub_logs])
        print(f" -> Found {len(logs[item.url])} logs")

    for values in zip(*logs.values()):
        if not all(value == values[0] for value in values):
            print(
                f"Discrepancy found: {[f"{val["block_number"]}/{val["transaction_hash"]}/{val["log_index"]}" for val in values]}")
            break
    else :
        print("No discrepancies found.")

    with open("logs.json", "w") as f:
        f.write(json.dumps(logs, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
