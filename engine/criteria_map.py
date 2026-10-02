from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_MAPPING_PATH = Path(__file__).parent / "criteria" / "fsi_2026_mapping.json"
_UNMAPPED = {"domain": "미분류", "itemCode": "-", "itemName": "미분류"}


@lru_cache(maxsize=1)
def load_mapping() -> dict[str, dict[str, str]]:
    raw = json.loads(_MAPPING_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def criteria_for(rule_id: str) -> dict[str, str]:
    return load_mapping().get(rule_id, _UNMAPPED)
