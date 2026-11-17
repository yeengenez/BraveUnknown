# Weapon layers (test: sword, shield, great axe, longspear)

Weapons are separate layers merged onto the weapon-less battle sprite bodies (`../battle_sprites/`).
**Rule from the user (2026-11-17): never generate weapons with Canva.** The sword and shield below were cut
from images made earlier (the first layer test), which the user picked.

Current set (`previews/weapon_merge_test2.png`):

| Weapon | Source | How |
|---|---|---|
| Longsword | Cut from first test image A (`cut_kept.py` → `k_longsword.png`) | Grip replaced by a clean leather grip; hand point right under the guard |
| Kite shield (fleur-de-lis) | Cut from image A (`../battle_sprites/first_layer_test/layers/shield_kite.png`) | Placed by the front-fist offset |
| Great axe | Painted in code (`render_weapons.py`): lit at 4x, palette sampled from the bodies, tinted outline | Drawn directly at the held angle (no pixel rotation) |
| Longspear | Pixel art in code (`pixel_weapons.py`) | Rotated with a pixel-art-safe method |

Holds (`merge2.py`):
- **Sword alone, front hand:** steep (−66°) like the rapier in image B, guard just above the fist. The body's
  front fist is a forward punch, so a handle can only pass through it near-vertically.
- **Sword + shield:** sword raised in the back hand behind the head (−78°), shield on the front arm.
- **Great axe and longspear:** both drawn **behind the body**, aimed from the back fist through the front fist, so
  the arms and fists wrap over the shaft (drawn in front, the shaft looked like it pierced the forearm).
- Long weapons cross into the next formation square; each test is a three-square strip with the body in the middle.

Other files: `rig.json` (fist centres per body), `merge.py` (shared helpers, first test), `k_rapier.png` (rapier
cut from image B; its guard ring is tangled with the glove, not used yet), `pt_*.png`, `px_*.png` (code-drawn
versions; the user rejected the code-drawn shield and first axe).

## Aseprite

`make_aseprite_pack.py` writes `aseprite/` + layer PNGs: `build_weapons.lua` builds `weapons.aseprite` (one layer
per weapon, slices `<weapon>_grip` with the hand point as pivot) and `merge_examples.aseprite` (one tagged frame
per test; layers squares, weapon_back, body, weapon_front, fists) and exports PNGs. On the user's PC:
`Documents\BraveUnknownArt\weapons`, run from Aseprite via File > Scripts > "Brave Unknown - build weapons"
(`launcher.lua` in the Aseprite scripts folder).
