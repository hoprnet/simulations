from pathlib import Path

import yaml

from .rpc_url import RPCUrl


def load_config_file(ctx, param, value):
    if not value:
        return value

    config_path = Path(value)
    cfg = yaml.safe_load(config_path.read_text())

    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg

    ctx.default_map = ctx.default_map or {}

    # Map rpc1, rpc2 keys from config to RPCUrl objects
    for rpc_key in ["rpc1", "rpc2"]:
        if rpc_key in cfg:
            entry = cfg[rpc_key]
            ctx.default_map[rpc_key] = RPCUrl(entry["name"], entry["url"])

    # Any other flat keys can be mapped here if needed
    for k in ["from_block", "to_block", "output_file", "address", "topics", "block_range"]:
        if k in cfg:
            ctx.default_map[k] = cfg[k]

    return value
