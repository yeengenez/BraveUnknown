# Attack and get-hit animations (2026-11-18)

Built from layers, not drawn frame by frame: tinted grip body (`../grip_bodies/`), weapons drawn at each frame's
angle from the measured grip points, the fists redrawn over the handles, and simple effects. Weapons are drawn in
code (`class_weapons.py`: dagger, mace, quarterstaff, mage staff, bow, arrow; `../../weapons/`: longsword and
kite shield cut from the first test image, painted great axe, pixel longspear). Never generated with Canva.

Run `python3 anim.py [class ...]`. Output:
- `sheets/<class>_<sex>_<loadout>_<attack|hit>.png`: frames left to right, transparent, 399×270 each (three
  formation squares; the body stands in the middle one so long weapons and missiles can cross into the next).
  Attack: 8 frames. Hit: 6 frames.
- `gif/<class>.gif`: every loadout of the class, attack then hit, for review.

| Class | Loadouts (attack) |
|---|---|
| Soldier | longsword (slash), sword + shield (overhead slash), great axe (chop), longspear (thrust) |
| Archer | bow (draw, loose, arrow flies), dagger (slash) |
| Acolyte | mace + shield (overhead slash), quarterstaff (chop), longspear (thrust) |
| Mage | staff (glow, then a magic orb flies) |
| Brawler | unarmed (lunging punch with impact burst), great axe (chop), longspear (thrust) |
| Rogue | dual daggers (front then back slash) |

Get hit (all): red flash, knockback with a white flash and shake, recover. Preview skin tones vary per class to
show the skin layer (the game uses each hero's own tone).

Motion notes: one-handed weapons rotate about the hand. Two-handed weapons turn only a little (they pivot on both
hands) and most of the motion comes from the body lunge. Spears slide through the fists on the thrust.
