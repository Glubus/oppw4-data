#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = ROOT / "characters"
INDEX = ROOT / "generated" / "index.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    entries = []
    for data_path in sorted(CHARACTERS.glob("*/data.json")):
        character_dir = data_path.parent
        data = read_json(data_path)
        movesets_path = character_dir / "movesets.json"
        entries.append(
            {
                "id": data["id"],
                "display_name": data["display_name"],
                "path": data_path.relative_to(ROOT).as_posix(),
                "movesets": movesets_path.relative_to(ROOT).as_posix()
                if movesets_path.is_file()
                else None,
            }
        )

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(
        json.dumps({"characters": entries}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
