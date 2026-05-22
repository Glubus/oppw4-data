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
    assets = data.get("assets")
    require(isinstance(assets, dict), f"{rel}: assets must be an object")
    costumes = assets.get("costumes")
    require(isinstance(costumes, list), f"{rel}: assets.costumes must be an array")
    for costume in costumes:
        require(isinstance(costume, dict), f"{rel}: costume refs must be objects")
        require(costume.get("id"), f"{rel}: costume id is required")
        ref = costume.get("ref")
        require(isinstance(ref, str), f"{rel}: costume ref is required")
        costume_path = path.parent / ref
        require(costume_path.is_file(), f"{rel}: costume ref missing: {ref}")
        validate_costume(costume_path, data["id"], costume["id"])
    movesets = data.get("movesets")
    if movesets is not None:
        require(isinstance(movesets, dict), f"{rel}: movesets must be an object")
        require(movesets.get("ref") == "movesets.json", f"{rel}: movesets.ref must be movesets.json")
        require((path.parent / "movesets.json").is_file(), f"{rel}: movesets ref missing")
    return data["id"]


def validate_costume(path, character_id, costume_id):
    data = load(path)
    rel = path.relative_to(ROOT)
    require(data.get("character_id") == character_id, f"{rel}: character_id mismatch")
    require(data.get("id") == costume_id, f"{rel}: id mismatch")
    require(data.get("label"), f"{rel}: label is required")
    require(isinstance(data.get("assets"), list), f"{rel}: assets must be an array")
    seen = set()
    for asset in data["assets"]:
        key = asset_key(asset)
        require(key not in seen, f"{rel}: duplicate asset {key}")
        seen.add(key)
    body_parts = data.get("body_parts", [])
    require(isinstance(body_parts, list), f"{rel}: body_parts must be an array")
    seen_parts = set()
    for part in body_parts:
        require(isinstance(part, dict), f"{rel}: body_parts entries must be objects")
        part_id = part.get("id")
        require(isinstance(part_id, str) and part_id, f"{rel}: body_part id is required")
        require(part_id not in seen_parts, f"{rel}: duplicate body_part {part_id}")
        seen_parts.add(part_id)
        require(part.get("label"), f"{rel}: body_part {part_id} label is required")
        require(
            isinstance(part.get("assets"), list),
            f"{rel}: body_part {part_id} assets must be an array",
        )
        seen_assets = set()
        for asset in part["assets"]:
            key = asset_key(asset)
            require(
                key not in seen_assets,
                f"{rel}: body_part {part_id} duplicate asset {key}",
            )
            seen_assets.add(key)


def asset_key(asset):
    return (
        asset.get("kind"),
        asset.get("archive"),
        asset.get("path"),
        asset.get("hash"),
        asset.get("file_type"),
        asset.get("variant"),
    )


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


def validate_mission(path):
    data = load(path)
    rel = path.relative_to(ROOT)
    require(data.get("id") == path.parent.name, f"{rel}: id must match folder name")
    require(isinstance(data.get("aliases"), list), f"{rel}: aliases must be an array")
    ids = data.get("ids")
    require(isinstance(ids, dict), f"{rel}: ids must be an object")
    require(isinstance(ids.get("mission"), int), f"{rel}: ids.mission must be an integer")
    require(isinstance(data.get("modes"), list), f"{rel}: modes must be an array")
    for key, expected_ref in (
        ("difficulties", "difficulties.json"),
        ("rank_conditions", "rank_conditions.json"),
        ("rewards", "rewards.json"),
    ):
        ref_block = data.get(key)
        require(isinstance(ref_block, dict), f"{rel}: {key} must be an object")
        require(ref_block.get("ref") == expected_ref, f"{rel}: {key}.ref must be {expected_ref}")
        ref_path = path.parent / expected_ref
        require(ref_path.is_file(), f"{rel}: {key} ref missing")
        validate_mission_detail(ref_path, data["id"], key)
    return data["id"]


def validate_mission_detail(path, mission_id, key):
    data = load(path)
    rel = path.relative_to(ROOT)
    require(data.get("mission_id") == mission_id, f"{rel}: mission_id mismatch")
    require(isinstance(data.get("observations"), list), f"{rel}: observations must be an array")
    for index, observation in enumerate(data["observations"]):
        require(isinstance(observation, dict), f"{rel}: observation {index} must be an object")
        require(observation.get("source"), f"{rel}: observation {index} source is required")
        require(isinstance(observation.get("notes"), list), f"{rel}: observation {index} notes must be an array")
        if key == "rank_conditions":
            require(isinstance(observation.get("rank_row"), int), f"{rel}: observation {index} rank_row must be an integer")
            require(isinstance(observation.get("condition_row"), int), f"{rel}: observation {index} condition_row must be an integer")
        if key == "rewards":
            require(isinstance(observation.get("items"), list), f"{rel}: observation {index} items must be an array")


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

    for data_path in sorted((ROOT / "missions").glob("*/data.json")):
        try:
            validate_mission(data_path)
        except ValueError as error:
            errors.append(str(error))

    try:
        load(ROOT / "generated" / "index.json")
        load(ROOT / "schemas" / "character.schema.json")
        load(ROOT / "schemas" / "costume.schema.json")
        load(ROOT / "schemas" / "movesets.schema.json")
        load(ROOT / "schemas" / "mission.schema.json")
        load(ROOT / "schemas" / "mission_difficulties.schema.json")
        load(ROOT / "schemas" / "mission_rank_conditions.schema.json")
        load(ROOT / "schemas" / "mission_rewards.schema.json")
    except ValueError as error:
        errors.append(str(error))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
