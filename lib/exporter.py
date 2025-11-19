import json
from pathlib import Path
from typing import Any

import yaml

export_method = {
    ".json": json.dump,
    ".yaml": yaml.dump,
    ".yml": yaml.dump,
}


def sanitize_json(value: Any):
    if isinstance(value, dict):
        return {k: sanitize_json(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_json(v) for v in value]
    elif hasattr(value, "as_str"):
        return value.as_str
    else:
        return value

def export(file: Path, content: dict):
    content = sanitize_json(content)

    if file.suffix in export_method:
        with open(file, "w") as f:
            export_method[file.suffix](content, f, indent=4)
    else:
        raise ValueError(f"Output file must be a dict file ({', '.join(export_method.keys())})")
