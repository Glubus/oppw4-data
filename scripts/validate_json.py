#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        raise ValueError(f"{path.relative_to(ROOT)}: invalid JSON: {error}") from error


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_character(path):
    data = load(path)
    rel = path.relative_to(ROOT)
    require(data.get("id") == path.parent.name, f"{rel}: id must match folder name")
    require(data.get("display_name"), f"{rel}: display_name is required")
    require(isinstance(data.get("aliases"), list), f"{rel}: aliases must be an array")
    require(isinstance(data.get("ids"), dict), f"{rel}: ids must be an object")
    require(isinstance(data.get("models"), list) and data["models"], f"{rel}: models are required")
    require(isinstance(data.get("assets"), list), f"{rel}: assets must be an array")
    return data["id"]


def validate_movesets(path, character_id):
    data = load(path)
    rel = path.relative_to(ROOT)
    require(
        data.get("character_id") == character_id,
        f"{rel}: character_id must match data.json",
    )
    base = data.get("base")
    require(isinstance(base, dict), f"{rel}: base must be an object")
    require(base.get("linkdata_file") == "LINKDATA_A", f"{rel}: unsupported linkdata_file")
    require(isinstance(base.get("entry"), int), f"{rel}: base.entry must be an integer")


def main():
    errors = []
    for data_path in sorted((ROOT / "characters").glob("*/data.json")):
        try:
            character_id = validate_character(data_path)
            movesets_path = data_path.parent / "movesets.json"
            if movesets_path.is_file():
                validate_movesets(movesets_path, character_id)
        except ValueError as error:
            errors.append(str(error))

    try:
        load(ROOT / "generated" / "index.json")
        load(ROOT / "schemas" / "character.schema.json")
        load(ROOT / "schemas" / "movesets.schema.json")
    except ValueError as error:
        errors.append(str(error))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
