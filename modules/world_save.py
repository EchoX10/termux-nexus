"""Persistência local das partidas de World of Choices."""

from __future__ import annotations

import json
from pathlib import Path

SAVE_DIR = Path.home() / ".config" / "termux-nexus" / "world"
SAVE_FILE = SAVE_DIR / "save.json"


def new_game() -> dict:
    return {
        "version": 1,
        "location": "crossroads",
        "inventory": [],
        "discovered": [],
        "flags": {},
        "relationships": {"mira": 0, "oren": 0},
        "visited": ["crossroads"],
        "journal": ["Você chegou à Encruzilhada de Brumafria."],
    }


def load_game() -> dict | None:
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        if data.get("version") != 1 or data.get("location") not in {
            "crossroads", "old_bridge", "pine_camp"
        }:
            return None
        return data
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def save_game(data: dict) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = SAVE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(SAVE_FILE)


def delete_save() -> None:
    SAVE_FILE.unlink(missing_ok=True)
