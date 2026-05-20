#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY_BANK = ROOT.parent / "oppw4-sdk" / "crates" / "character-bank" / "data" / "characters.json"

# The legacy SDK bank still carries a few ambiguous prototype assignments.
# Keep known corrections here until the legacy embedded bank is replaced by this
# data repository.
MOVESET_ENTRY_OVERRIDES = {
    "garp": None,
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def default_costume(model_id):
    return {
        "id": "default",
        "ref": "costumes/default.json",
    }


def default_model_asset(character):
    stem = character.get("model_stem")
    return {
        "kind": "model",
        "label": "Default character model",
        "variant": "default",
        "archive": "CharacterEditor",
        "path": f"{stem}.g1m" if stem else None,
        "hash": None,
        "file_type": "g1m",
        "source": None,
        "notes": [],
    }


def asset_key(asset):
    return (
        asset.get("kind"),
        asset.get("archive"),
        asset.get("path"),
        asset.get("hash"),
        asset.get("file_type"),
        asset.get("variant"),
    )


def ensure_default_model_asset(costume, character):
    model = default_model_asset(character)
    key = asset_key(model)
    if not any(asset_key(asset) == key for asset in costume["assets"]):
        costume["assets"].insert(0, model)


def sync_movesets(character_dir, data, character):
    character_id = character["canonical"]
    entry = MOVESET_ENTRY_OVERRIDES.get(character_id, character.get("moveset_linkdata_entry"))
    movesets_path = character_dir / "movesets.json"
    if entry is None:
        data.pop("movesets", None)
        if movesets_path.exists():
            movesets_path.unlink()
        return

    data["movesets"] = {"ref": "movesets.json"}
    movesets = {
        "$schema": "../../schemas/movesets.schema.json",
        "character_id": character_id,
        "base": {
            "linkdata_file": "LINKDATA_A",
            "entry": entry,
        },
        "variants": [],
        "notes": [],
    }
    write_json(movesets_path, movesets)


def main():
    for character in read_json(LEGACY_BANK):
        character_id = character["canonical"]
        character_dir = ROOT / "characters" / character_id
        data_path = character_dir / "data.json"
        if data_path.is_file():
            data = read_json(data_path)
        else:
            data = {
                "$schema": "../../schemas/character.schema.json",
                "id": character_id,
                "display_name": character["display_name"],
                "aliases": character.get("aliases", []),
                "ids": {},
                "notes": [],
                "assets": {"costumes": []},
            }

        data["display_name"] = character["display_name"]
        data["aliases"] = character.get("aliases", [])
        data["ids"] = {
            "playable": character.get("playable_id"),
            "runtime": character.get("runtime_id"),
            "boss_runtime": character.get("boss_runtime_id"),
            "model": character.get("model_id"),
        }
        data.setdefault("notes", [])
        data.setdefault("assets", {}).setdefault("costumes", [])
        if not any(costume.get("id") == "default" for costume in data["assets"]["costumes"]):
            data["assets"]["costumes"].append(default_costume(character.get("model_id")))

        costume_path = character_dir / "costumes" / "default.json"
        if costume_path.is_file():
            costume = read_json(costume_path)
        else:
            costume = {
                "$schema": "../../../schemas/costume.schema.json",
                "character_id": character_id,
                "id": "default",
                "label": "Default",
                "slot": None,
                "model_id": character.get("model_id"),
                "assets": [],
                "notes": [],
            }
        costume["character_id"] = character_id
        costume["id"] = "default"
        costume.setdefault("label", "Default")
        costume["model_id"] = character.get("model_id")
        costume.setdefault("slot", None)
        costume.setdefault("assets", [])
        costume.setdefault("notes", [])
        ensure_default_model_asset(costume, character)
        sync_movesets(character_dir, data, character)

        write_json(data_path, data)
        write_json(costume_path, costume)


if __name__ == "__main__":
    main()
