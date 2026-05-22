#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = ROOT / "characters"
MISSIONS = ROOT / "missions"
INDEX = ROOT / "generated" / "index.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    character_entries = []
    for data_path in sorted(CHARACTERS.glob("*/data.json")):
        character_dir = data_path.parent
        data = read_json(data_path)
        entry = {
            "id": data["id"],
            "display_name": data["display_name"],
            "path": data_path.relative_to(ROOT).as_posix(),
        }
        movesets_ref = data.get("movesets", {}).get("ref")
        if movesets_ref:
            entry["movesets"] = (character_dir / movesets_ref).relative_to(ROOT).as_posix()
        character_entries.append(entry)

    mission_entries = []
    for data_path in sorted(MISSIONS.glob("*/data.json")):
        mission_dir = data_path.parent
        data = read_json(data_path)
        entry = {
            "id": data["id"],
            "display_name": data["display_name"],
            "path": data_path.relative_to(ROOT).as_posix(),
            "mission_id": data["ids"]["mission"],
        }
        for key in ("difficulties", "rank_conditions", "rewards"):
            ref = data.get(key, {}).get("ref")
            if ref:
                entry[key] = (mission_dir / ref).relative_to(ROOT).as_posix()
        mission_entries.append(entry)

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(
        json.dumps(
            {"characters": character_entries, "missions": mission_entries},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
