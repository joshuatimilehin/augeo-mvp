import json
import os
from typing import Dict, Any


def save_taste_label(record: Dict[str, Any], out_path: str = None) -> str:
    """Append a taste label record as JSONL to `out_path`.

    Returns the path written to.
    """
    out_path = out_path or os.path.join(os.getcwd(), "output", "taste_labels.jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return out_path
