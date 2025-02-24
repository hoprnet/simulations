import json
from pathlib import Path

import yaml

export_method = {
    ".json": json.dump,
    ".yaml": yaml.dump,
    ".yml": yaml.dump,
}


def export(file: Path, content: dict):
    if file.suffix in export_method:
        with open(file, "w") as f:
            export_method[file.suffix](content, f)
    else:
        raise ValueError(f"Output file must be a dict file ({', '.join(export_method.keys())})")
