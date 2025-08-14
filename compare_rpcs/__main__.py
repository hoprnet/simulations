import asyncio
import json

import click

from lib.colors import Color
from lib.helper import asynchronous
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
        print(*Color.BOLD_STRING, sep=item.short_url)
        logs[item.url] = []

        for start, end in get_ranges(from_block, to_block, MAX_SINGLE_QUERY_BLOCK_RANGE):
            print(*Color.BOLD_STRING, sep=f"Range: {start} - {end}")

            sub_logs: list[Log] = await ETHGetLogsRPCProvider(item.url).get(
                    fromBlock=start.idx,
                    toBlock=end.idx,
                    address="0x77C9414043d27fdC98A6A2d73fc77b9b383092a7",
                topics=["0xdd90f938230335e59dc925c57ecb0e27a28c2d87356e31f00cd5554abd6c1b2d"]
            )
            logs[item.url].extend([log.as_dict for log in sub_logs])            

    with open("logs.json", "w") as f:
        f.write(json.dumps(logs, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
