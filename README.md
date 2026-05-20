# OPPW4 Data

Community-editable data for One Piece: Pirate Warriors 4 tooling.

This repository is intended to stay data-only. Rust crates, DLL code, runtime
hooks, and generated binaries belong in the SDK or loader repositories. Character
metadata lives here so IDs, aliases, models, assets, and moveset references can
be improved without recompiling the SDK.

## Layout

```text
characters/
  law/
    data.json
    movesets.json
    evidence.md
schemas/
  character.schema.json
  movesets.schema.json
generated/
  index.json
```

`characters/<id>/data.json` owns stable identity and model metadata.
It also has an `assets` list for known models, textures, portraits, UI files,
materials, effects, sounds, voices, RDB references, and LinkData references.
`characters/<id>/movesets.json` owns moveset references when known.
`evidence.md` records where uncertain IDs or relationships came from.

`generated/index.json` is derived from the character folders and should be
regenerated when source data changes.

## Commands

Regenerate the index:

```sh
python3 scripts/generate_index.py
```

Validate JSON shape:

```sh
python3 scripts/validate_json.py
```

## Rules

- Keep source data as JSON.
- Use one folder per canonical character ID.
- Prefer adding notes in `evidence.md` over leaving unexplained magic values.
- Do not put DLLs, mods, logs, or game assets in this repository.
- Generated files must be reproducible from source JSON.
