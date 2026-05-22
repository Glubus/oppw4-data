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
    costumes/
      default.json
    movesets.json
    evidence.md
missions/
  mission_0035/
    data.json
    difficulties.json
    rank_conditions.json
    rewards.json
    evidence.md
schemas/
  character.schema.json
  costume.schema.json
  movesets.schema.json
  mission.schema.json
  mission_difficulties.schema.json
  mission_rank_conditions.schema.json
  mission_rewards.schema.json
generated/
  index.json
```

`characters/<id>/data.json` owns stable identity metadata and points to costume
asset files through `assets.costumes`.
`characters/<id>/costumes/<costume>.json` owns known models, textures,
portraits, UI files, materials, effects, sounds, voices, body-part asset groups,
RDB references, and LinkData references for that costume.
Use optional `body_parts` entries for targetable texture/model pieces such as
`body`, `left_arm`, `right_arm`, `weapon_01`, `weapon_left`, `weapon_right`, or
other community-confirmed part names. Part ids are intentionally data-defined so
characters with multiple weapons or unusual equipment can expose as many
targetable pieces as needed.
`characters/<id>/movesets.json` owns moveset references when known.
`evidence.md` records where uncertain IDs or relationships came from.

`missions/<id>/data.json` owns stable mission identity and points to focused
mission data files. `difficulties.json` records observed effective difficulty
state and raw difficulty rows, `rank_conditions.json` records fixed rank rows
and condition rows, and `rewards.json` records Berry, item/medal, crew point,
and soul reward evidence. Unknown fields should stay as raw values with notes
instead of invented labels.

`generated/index.json` is derived from the source folders and should be
regenerated when character or mission source data changes.

## Commands

Regenerate the index:

```sh
python3 scripts/generate_index.py
```

Sync identity and default model assets from the legacy SDK bank:

```sh
python3 scripts/sync_from_legacy_bank.py
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
