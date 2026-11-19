# Legacy assets (Canva) — reference only

**Decision (user, 2026-11-18):** every asset generated in Canva, and every image cut, edited or composed
from a Canva image, is **Legacy**. Use it **for reference only**: style, proportions, colours, poses,
grip positions. Do not ship new game content built from it, and do not extend it with more Canva
generations. New production art replaces it.

Machine-readable list: [`legacy_assets.json`](legacy_assets.json).

## What is Legacy

| Asset | Path | Why |
|---|---|---|
| Hero portrait parts | `portraits/parts/*` (game module, also on `main`) | Cut from Canva source images |
| Portrait source images and previews | `art_source/portrait_pipeline/raw/`, `previews/` | Generated in Canva |
| Battle sprite bodies, all classes | `art_source/battle_sprites/<class>/bodies/`, `soldier/previews/` | Canva (first full-body bodies) |
| Style reference | `art_source/battle_sprites/style_reference/` | Canva (media `MAHbDbX73BU`) |
| First layer test | `art_source/battle_sprites/first_layer_test/` | Canva image; the longsword and kite shield were cut from it |
| Grip bodies | `art_source/battle_sprites/grip_bodies/raw/`, `bodies/`, `layers/`, `previews/` | Canva edits of the bodies |
| Stand / attack / hit poses | `art_source/battle_sprites/poses/raw/`, `raw_v1_1h/`, `bodies/`, `layers/`, `sprites/`, `review.png` | Canva redraws of the grip bodies |
| Animation sheets and GIFs | `art_source/battle_sprites/animation/sheets/`, `gif/` | Built from the Canva grip bodies |
| Archer body copies | `art_source/battle_sprites/archer/bodies/` | Older copy of the Canva bodies |
| Weapons cut from Canva art | `art_source/weapons/k_longsword.png`, `k_rapier.png`, `weapon_merge_test2.png`, `previews/` | Cut from the first layer test image |
| Enemy sprites | `art_source/enemies/*.png` | Canva originals (wolf, boar, goblin) |

## Portraits: replaced in the game

The Legacy hero portraits stayed in the game until the new art was ready. **They were replaced on
2026-11-19** by `art_source/new_art/portraits/` (the game's `portraits/parts/` on `main`). The Legacy
portrait parts on this branch remain for reference only.

The Canva battle sprites were **not** put into the game.

## Not Legacy

- **Scripts and data** (pipelines, grip measurement, compose, palettes, `library.json`, grip JSON format,
  `HeroAppearance`): reusable with new art.
- **Weapons drawn in code**: great axe, longspear, dagger, mace, quarterstaff, mage staff, bow, arrow
  (`weapons/render_weapons.py`, `pixel_weapons.py`, `battle_sprites/animation/class_weapons.py`).
- **The user's own reference art** in `old_battle_sprites/` (already reference only).
- **Archer handoff docs** in `battle_sprites/archer/` (README, manifest, equipment-state rules).
- `outdated_fe_style/` is outdated for a different reason (old rules), not because of Canva.

## Name note
The class **Brawler was renamed Warrior** (2026-11-18). Legacy battle-sprite files and scripts keep the old name `brawler`; that art is the old Brawler look. The game's portrait parts were renamed to `warrior` so the game keeps working, but still show the old outfit until new art replaces it.
