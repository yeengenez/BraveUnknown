# Attack and get-hit animations (2026-11-18)

Built from layers, not drawn frame by frame: tinted grip body (`../grip_bodies/`), weapons drawn at each frame's
angle from the measured grip points, the fists redrawn over the handles, and simple effects. Weapons are drawn in
code (`class_weapons.py`: dagger, mace, quarterstaff, mage staff, bow, arrow; `../../weapons/`: longsword and
kite shield cut from the first test image, painted great axe, pixel longspear). Never generated with Canva.

**Version 2 (current, `anim2.py`, 2026-11-18).** The user found v1 (only the weapon swinging about a frozen
fist) laughable and asked for the approach of the first reference animations: the **arm moves with the weapon**.
The attacking forearm and fist are cut out of the body as one part (the gap is refilled from neighbouring pixels
inside the body outline) and swung about the elbow with the weapon locked in the fist. Spear thrusts and punches
push the arms forward (the punch smears the arm to show it stretching). The far (back) arm swings behind the head
and body. The body leans back on the wind-up, tilts into the strike and lunges; ground shadow; per-frame timing
with a short hold on impact; slash trails and speed lines drawn behind the character.

Run `python3 anim2.py [class ...]` (it reuses helpers from `anim.py`, the v1 script). Output, **attack and hit
are separate animations**:
- `sheets/<class>_<sex>_<loadout>_<attack|hit>.png`: frames left to right, transparent, 399×270 each (three
  formation squares, body in the middle). `.txt` next to each sheet: frame durations in ms.
- `gif/<class>_attack.gif`, `gif/<class>_hit.gif`: every loadout of the class, for review.

| Class | Loadouts (attack) |
|---|---|
| Soldier | longsword (slash), sword + shield (overhead slash), great axe (chop), longspear (thrust) |
| Archer | bow (draw, loose, arrow flies), dagger (slash) |
| Acolyte | mace + shield (overhead slash), quarterstaff (chop), longspear (thrust) |
| Mage | staff (glow, then a magic orb flies) |
| Brawler | unarmed (lunging punch with impact burst), great axe (chop), longspear (thrust) |
| Rogue | dual daggers (front then back slash) |

Get hit (all): white flash with an impact burst, red flash and knockback with a lean back, recover. Preview skin tones vary per class to
show the skin layer (the game uses each hero's own tone).
