# Grip bodies (2026-11-18)

> **LEGACY — reference only (2026-11-18).** The bodies are Canva edits. Use the images for reference only; the grip-measurement scripts are still usable. See [`../../LEGACY.md`](../../LEGACY.md).

Battle sprite bodies for **every class** whose fists actually close around a handle, plus the skin layer.
These replace `../<class>/bodies/` as the bodies to use.

**How they are made.** Each confirmed weapon-less body was edited in Canva (team Benchamarachuthit
Chanthaburi) so the fists grip a flat **magenta guide rod** (`raw/`):
- 1h: front hand rod up-forward, raised back hand rod straight up.
- 2h: one rod through both stacked fists. reach: one long pole at hip height through both fists.
- bow (Archer): front hand grips a vertical rod (the bow); the drawing hand pinches a horizontal line (arrow).

`process2.py` (current; `process.py` was the Soldier-only first version) fits a line through the rod on both
sides of each fist and writes each hand's **grip point, angle and fist size** to `grips/grips_<class>_<sex>_<stance>.json`
(bow: bow grip, bow length, arrow height, draw hand). The magenta is removed and the pixels behind it are
refilled from the original body (`bodies/`).

**Skin layer** (`skin_layers.py`, like the portraits): `layers/<body>_fixed.png` (everything but skin) and
`layers/<body>_skin.png` (brightness map + mask). At runtime the skin is coloured with the hero's portrait skin
ramp (`portraits/palettes.json`), so head and body match each other and the portrait. Skin = the head, bare
hands at the grip points (Acolyte, Mage, Rogue, Brawler), Brawler arms and chest above the belt, and the female
Rogue's neckline. Head and body brightness are evened out. Review: `previews/skin_review.png` (porcelain, tan, deep).

Bodies (26): Soldier, Acolyte, Brawler: 1h, 2h, reach. Archer: 1h, bow. Mage, Rogue: 1h. Male and female each.
Canva ids: `grip_canva_ids.json`.

Known flaws: the male Acolyte reach body inherited a warm head tint (the skin layer fixes the colour), and the
female Acolyte reach body has no gold cross. `raw/soldier_m_2h_nogloves.png` is the rejected version.
