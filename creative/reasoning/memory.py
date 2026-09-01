import json
from pathlib import Path
from typing import Dict, Any

_OUT = Path("output")
_OUT.mkdir(exist_ok=True)


def _append_jsonl(filename: str, payload: Dict[str, Any]) -> None:
    path = _OUT / filename
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def record_learning(record: Dict[str, Any]) -> None:
    _append_jsonl("creative_learning.jsonl", record)


def record_rejection(record: Dict[str, Any]) -> None:
    _append_jsonl("creative_rejections.jsonl", record)
