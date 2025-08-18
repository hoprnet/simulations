import asyncio
import datetime
import json
from pathlib import Path

import click

from lib.helper import asynchronous, progress_bar
from lib.rpc.entries.types.block import Block, get_ranges
from lib.rpc.query_provider import ETHGetLogsRPCProvider, ProviderError

from .config_parser import load_config_file
from .rpc_url import RPC_URL_TYPE, RPCUrl


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    callback=load_config_file,
    is_eager=True,  # Load before other options are processed
    expose_value=False,  # We don't need to pass it to the function
    help="Path to config file (json, yml/yaml, or ini)",
)
@click.option("--rpc1", type=RPC_URL_TYPE, help="RPC URL to connect to")
@click.option("--rpc2", type=RPC_URL_TYPE, help="RPC URL to connect to")
@click.option("--fromBlock", "from_block", type=Block, help="Starting block number")
@click.option("--toBlock", "to_block", type=Block, help="Ending block number")
@click.option("--out", "output_file", type=click.Path(), help="Output file path")
@click.option("--address", "address", type=str, default=None, help="Ethereum address to filter logs")
@click.option("--topics", "topics", type=str, multiple=True, help="Topics to filter logs")
@click.option("--block-range", "block_range", type=int, help="Maximum block range for a single query")
@asynchronous
async def main(
    rpc1: RPCUrl,
    rpc2: RPCUrl,
    from_block: Block,
    to_block: Block,
    output_file: Path,
    address: str,
    topics: list[str],
    block_range: int,
):
    RPCs: dict[str, str] = {rpc.name: rpc.url for rpc in [rpc1, rpc2]}

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    for start, end in get_ranges(from_block, to_block, block_range):
        if to_block != from_block:
            progress_bar(
                start.idx, to_block.idx, percentage=(start.idx - from_block.idx) / (to_block.idx - from_block.idx)
            )

        logs = {key: [] for key in RPCs.keys()}

        for name, url in RPCs.items():
            try:
                logs[name].extend(
                    await ETHGetLogsRPCProvider(url).get(
                        fromBlock=start.idx, toBlock=end.idx, address=address, topics=[topics]
                    )
                )
            except ProviderError as e:
                print(f"Error fetching logs from {name} ({url}): {e}")

        # check if the length of all values are the same
        logs_lengths: dict[str, int] = {key: len(value) for key, value in logs.items()}

        if logs_lengths["Erigon"] > logs_lengths["Nethermind"]:
            print(" Discrepancy found: More logs with Erigon than Nethermind.")

            with open(Path(f"{output_file}_{start.idx}_{end.idx}.json"), "w") as f:
                data = {}
                data["logs"] = {key: [log.as_dict for log in value] for key, value in logs.items()}
                data["meta"] = {
                    "timestamp": datetime.datetime.now().timestamp(),
                    "url": RPCs,
                    "query": ETHGetLogsRPCProvider.get_query(
                        fromBlock=start.idx, toBlock=end.idx, address=address, topics=[topics])
                }
                f.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
