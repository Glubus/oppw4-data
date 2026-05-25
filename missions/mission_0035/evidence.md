# mission_0035 Evidence

Seeded from `sdk.runtime` log `2026-05-21-215933`.

- Runtime mission id: `35`.
- Observed mode: free log (`mode_id=1`).
- Observed difficulty: normal (`difficulty_id=1`).
- Rank slot data points at fixed-table row candidates around row `12`; the older
  "condition row `12`" name is now treated as raw table evidence, not a final
  visible-rank label.
- Condition/raw fixed-table values still need labels.
- Inflated `LINKDATA_A.BIN` entry `3` evidence:
  - fixed rank row `12` starts at raw offset `0x330`;
  - condition row base starts at raw offset `0xc684`;
  - condition row `12` starts at raw offset `0xc8f4`.
- `global + 0x1d9b0` stores the rank/result profile row id, not the final visible grade.
- Visible grade calculation is handled by threshold helpers:
  - `FUN_1412dd9e0`: lower-is-better float/time thresholds;
  - `FUN_1412dd950`: higher-is-better count/score thresholds.
- Runtime `rank_helper_probe` should be used to correlate those helper rows with
  visible rank labels before exposing public rank-condition editing APIs.
- Difficulty row fields `0x334..0x39c` still need labels.
- Soul reward commit fields are still unknown.
- Normal/free-log row values observed from runtime/Ghidra notes:
  - `0x334 = 270`;
  - `0x33c = 550`;
  - `0x340 = 550`;
  - `0x348 = 2500`.
- Easy rank cap behavior is now confirmed:
  - Easy result code downgrades S/S+-like candidates and sets the warning flag;
  - bypassing all identified Easy cap branches lets Easy award S/S+ and the matching berry/item reward context;
  - future public API name should be explicit, e.g. `set_easy_s_rankable(true)`.
- UI/data work still needed before visible custom difficulty/rank names:
  - difficulty labels are in language LinkData (`LANG/FRA/LINKDATA_LANG_FRA.BIN` entry `0`, `LANG/ENG/LINKDATA_LANG_ENG.BIN` entry `1`);
  - known difficulty text keys include `tb_difficult` and `tb_level_of_difficulty`;
  - known rank UI/layout keys include `mai_epi_rank`, `mai_epi_rank_A`, `CUIGalleryRewardSplus`, and `cmn_topmenu_txt_splus_reward_confirmation`.
