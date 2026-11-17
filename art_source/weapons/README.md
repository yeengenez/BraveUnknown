# Weapon layers (test: sword, shield, great axe, longspear)

Weapons are separate layers merged onto the weapon-less battle sprite bodies (`../battle_sprites/`).

- `pixel_weapons.py` draws each weapon pixel by pixel on one shared 15-colour palette, lying flat with the
  point to the right. The dark outline is added automatically. Each weapon has a grip point (`grip`, and
  `grip2` for the second hand on two-handed weapons). Output: `px_<weapon>.png`.
- `rig.json` holds each body's fist centres (`front` = toward the enemy, `back`) and the blade angle for a
  one-handed weapon.
- `merge.py` rotates a weapon with a pixel-art-safe method (scale2x ×3, rotate, sample) and places it by
  its grip on the fists. Layer order, back to front: weapon_back, body, weapon_front, fists (the body's fist
  pixels redrawn over the handle).
  - Sword alone: front hand, over the body.
  - Sword + shield: shield on the front arm (hides the front fist), sword in the raised back hand, behind the body.
  - Two-handed and reach: the back hand anchors the weapon, aimed through the front hand.
- `previews/weapon_merge_test.png`: every test on a three-square strip. The body stands in the middle
  square; the longspear reaches well into the next square (about 105 px past the cell edge).

## Aseprite

`aseprite/build_weapons.lua` builds `weapons.aseprite` (one layer per weapon, slices `<weapon>_grip` /
`<weapon>_grip2` whose pivot is the hand point) and `merge_examples.aseprite` (one tagged frame per test;
layers squares, weapon_back, body, weapon_front, fists), and exports PNGs to `export/`. It reads the layer
PNGs written next to it (`layers/`). On the user's PC it lives in `Documents\BraveUnknownArt\weapons`, run
from Aseprite via File > Scripts > "Brave Unknown - build weapons" (`launcher.lua` in the Aseprite scripts folder).

Run from this folder: `python3 pixel_weapons.py && python3 merge.py`
