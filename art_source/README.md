# Art source files

Working files behind the game's art: source images, the scripts that cut them into layers, and
previews. Godot ignores this folder (`.gdignore`), so nothing here is imported into the game.
The finished portrait parts the game uses live in `res://portraits/`.

Design decisions for all of this are in the Claude project doc `claude/design-decisions.md`
(project "Expedition: Brave unknown"). Read it before continuing any of this work.

| Folder | What it is | Status |
|---|---|---|
| `battle_sprites/` | Full-body battle sprites that match the portraits | **Legacy (Canva): reference only**; scripts reusable |
| `portrait_pipeline/` | Source images and scripts that built `res://portraits/parts/` | **Legacy (Canva): reference only**; parts stay in the game until replaced |
| `old_battle_sprites/` | The earlier animated sprites cut from your reference art ("battle sprites v2") | Reference only |
| `enemies/` | Wolf, boar and goblin sprites (facing left) | **Legacy (Canva): reference only** |
| `outdated_fe_style/` | Stat sheet, battle simulator and status-screen mockup from the Fire Emblem-style rules | Outdated; replaced by the PF1e-style rules |

Most images were generated in Canva and are also in the Canva account (media ids are listed in the
READMEs where they matter). **All Canva-made images are Legacy, reference only (user, 2026-11-18): see
[`LEGACY.md`](LEGACY.md).**
