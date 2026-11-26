# ChatGPT (GPT Go) prompts: battle sprites in the new art style

One image per **class and sex** (12 images), plus one Archer back-equipment sheet. For each: start a message, attach
1. `templates/<class>_template.png` (the canvas to draw on), and
2. `refs/<class>_<sex>_ref.png` (outfit from the new portrait + the poses to follow),

then paste the **common prompt** followed by the **class block** (replace `<SEX>` with `male` or `female`).

Rules carried over from the design doc: facing right, ~6-7 heads tall, no weapons ever drawn by AI (weapons, shields,
bows and arrows are drawn in code at the guide rods), **1h weapon always in the right hand**, magenta rod = right hand,
cyan rod = left hand, one frame per state (stand / attack / hit; bow: stand / nock / attack = release / hit), bald
heads (hair is a separate layer matched to the portrait). Archer (rules confirmed 2026-11-19): the quiver / bolt case
is a separate layer shown by the **equipped ammunition** (full / partial / empty), so the Archer sheet marks its place
with a flat pure-blue stick on the back in every pose, and the six containers are drawn on their own sheet. The Archer
sheet has a crossbow row (stand | aim | release | hit, user's choice 2026-11-19). New for the new art: bare skin in **shades of pure yellow**
(the cyan key used for portrait bodies is taken by the left-hand rod here).

---

## Common prompt (paste first)

> Use the first attached image as the canvas. It is a grid of cells on a flat pure green (#00FF00) background; each
> cell has a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid and the green exactly as
> they are. Draw **one full-body character per cell**, standing on that cell's ground line, top of the head at the
> dashed line when standing upright, all cells at the same scale.
>
> The second attached image shows the character: on the left, the outfit from their portrait (match its design,
> colours and materials exactly); on the right, the pose for every cell, in the same grid order. Those right-hand
> figures are old art: copy only the poses, not their outfit, colours or weapons.
>
> Style: Fire Emblem-style anime pixel art matching the portrait: clean dark outlines, cel shading, light from the
> upper left, natural anime proportions about 6-7 heads tall, 3/4 view **facing right** in every cell. Same character,
> same outfit in every cell.
>
> Hard rules:
> - **No weapons, shields, bows, arrows or quivers.** Each fist grips a flat, straight **guide rod** instead, 2-3 % of
>   the figure height thick, sticking out of both sides of the fist where the handle would be, fingers wrapped over it:
>   **pure magenta (#FF00FF) in the character's RIGHT hand, pure cyan (#00FFFF) in the LEFT hand.** The rods are flat
>   single colours with no shading or outline. No other magenta or cyan anywhere.
> - **Bald head**: no hair, no helmet, no hood up, no headband. Ears visible. Small anime face: dark eye lines, a tiny
>   bit of white, short mouth line.
> - **All bare skin (face, ears, neck, hands, any bare arms or chest) in shades of pure yellow** (red = green, blue near
>   zero): dark yellow for shadows, bright yellow for highlights, shaded like normal skin. Nothing else may be yellow or gold:
>   trims, buckles, embroidery and clasps must be **silver or dark bronze/brown**, never gold or yellow.
> - No text, labels, numbers, shadows on the ground, effects, motion lines or background objects.
> - Output one PNG at the canvas's exact size.

## Class blocks (paste after the common prompt)

### Soldier main sheet (v6, 2026-11-21 - self-contained, do NOT paste the common prompt)
Main sheet = shield, two-handed and spear rows, 4 cells each (STAND | READY | ATTACK | GET HIT); the dual weapons have
their own sheet (next section). Long-hair piece in a red key under the helmet for both sexes (shown only for long
portrait hairstyles, `hair_length.json`).
Attach, in this order: (1) `templates/soldier_template.png`, (2) `source/concepts/soldier_outfit_ref.png` (the final design cropped to the outfit only: its animation frames had the dual
weapons in the wrong hands, so they are left out),
(3) `refs/soldier_shield_ref.png`. Replace `<SEX>`, add the male or female line, one run per sex.

```
Use the first attached image as the canvas: a grid of 3 rows x 4 cells on flat pure green (#00FF00), each cell with a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the helmet at the dashed line when standing upright, all 12 figures at the same scale and the same character.

Character: <SEX> Soldier, exactly as in the second attached image (outfit reference only - it shows no poses): Standard plain BARBUTE helm (open face, no crest, no gold, no emblem), simple silver plate armour (rounded pauldrons, plain cuirass, segmented tassets), blue scarf, blue tabard with a light trim, brown leather belt and gloves, steel greaves. Ignore its text labels. Style: Fire Emblem-style anime pixel art matching that sheet: clean dark outlines, cel shading, light from the upper left, natural anime proportions about 6 heads tall including the helmet, 3/4 view FACING RIGHT in every cell, body turned to the right.

Rows, top to bottom; cells left to right = STAND | READY | ATTACK | GET HIT, where READY is the wind-up a moment before the attack.
1. Sword + SQUARE shield (the third attached image shows STAND, ATTACK and GET HIT - copy those poses only): the LEFT arm carries the Soldier's own large SQUARE shield in every cell of this row: an upright rectangle with slightly rounded corners, from the shoulder to mid-thigh, as wide as the torso, dark navy-blue face with a silver/white cross in relief, a silver steel rim with rivets - no gold or yellow on it. The left fist is hidden behind the shield (no cyan rod in this row). STAND = guard: shield held upright in front of the torso, covering it; right fist raised beside the shoulder with the magenta rod pointing up (sword raised). READY = wind-up: shield pulled in tight in front of the chest, body coiled, weight on the back foot, the right arm drawn back behind the shoulder with the magenta rod angled back. ATTACK = controlled horizontal slash: deep lunge forward, the right arm sweeps across IN FRONT of the body at waist height, magenta rod pointing forward and slightly down; the shield opens slightly to the side (still on the left arm, turned a little outward) so the sword arm passes in front of it. GET HIT = grounded recoil: feet planted, knees bent, braced behind the shield, the shield tilted up and forward to absorb the blow, head knocked back and wincing, right fist low by the hip holding the magenta rod pointing down.
2. Two-handed (no shield): both fists together on ONE magenta rod (one fist above the other). STAND = rod held upright in front of the body, fists at the waist. READY = wind-up: rod raised high over the right shoulder, both fists together above the head, body leaning back, weight on the back foot. ATTACK = heavy downward strike finishing low in front, rod angled down and forward, deep lunge. GET HIT = recoiling back, rod pulled up across the body.
3. Spear (no shield): ONE long magenta pole, as long as the body is tall, held at hip height through both fists, front fist forward, back fist at the rear hip. STAND = spear guard, pole level and pointing forward. READY = coiled: pole drawn back along the hip, back fist far behind the body, front fist close to the chest, crouched, weight on the back foot. ATTACK = full forward thrust, deep lunge, pole level. GET HIT = recoiling back, pole still held, tip lifted.

Hair under the helmet: in EVERY cell, a ponytail of long hair comes out from under the back of the helmet and hangs down behind the neck, following each pose (swinging back in the lunges, flicking up in the get-hit poses). It always stays BEHIND the body: it never covers the armour, scarf, arms or face, so the figure looks complete without it. Paint the hair entirely in shades of pure red (#FF0000 family: very dark red for the outline and shadows, mid red, bright red for highlights), shaded like hair - no black outline on it. No other hair visible.

Hard rules:
- No weapons and no capes. The square shield appears ONLY in row 1. Each fist that holds a weapon grips a flat, straight guide rod instead, 2-3% of the figure height thick, sticking out of both sides of the fist where the handle would be, fingers wrapped over it: pure magenta (#FF00FF) in the character's RIGHT hand, pure cyan (#00FFFF) in the LEFT hand. Flat single colours, no shading or outline. No other magenta or cyan anywhere.
- Rods: magenta is ALWAYS in the hand of the BACK arm (its shoulder on the left side of the picture - the sword arm of row 1); in rows 2 and 3 both fists share the one magenta rod.
- The barbute helm is worn in every cell, same design.
- The face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero): dark yellow for shadows, bright yellow for highlights, shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold.
- Pure red is used ONLY for the hair. Leather and trims stay brown or blue.
- No text, labels, slash effects, motion lines, dust, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
Male line: "Male: broad, sturdy frame." Female line: "Female: clearly feminine - smaller frame, narrower shoulders,
curved waist and hips, visible chest under the armour, slimmer limbs, smaller pauldrons, a soft feminine face with
larger eyes and a small chin, same armour and helmet."

Earlier Soldier sheets: v1 in `source/soldier_v1/`, v2 (bald) in `source/soldier_v2/`; v3 in `source/soldier_v3/`, v4 (3 cells per row) in
`source/soldier_v4/`. The male v5 sheet (4 x 4, with the old dual row) is still `source/soldier_m_sheet.png` and is read
with its old layout (`SHEET_ROWS` in `make_refs.py`); the female should use this v6 main sheet + the dual sheet.

### Soldier dual weapons (own sheet, 2026-11-21, from the user's concept `source/concepts/dual_slash_concept.png`)
Attach, in this order: (1) `templates/soldier_dual_template.png` (2 rows x 3 cells), (2) `source/concepts/soldier_outfit_ref.png`,
(3) `source/concepts/dual_slash_concept.png` (poses only). Replace `<SEX>`, add the male/female line. The arms are named by
their ROD COLOUR, never "left/right", because ChatGPT mixes up the character's left and right in a right-facing view.

```
Use the first attached image as the canvas: a grid of 2 rows x 3 cells on flat pure green (#00FF00), each cell with a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the helmet at the dashed line when standing upright, all 6 figures at the same scale and the same character.

Character: <SEX> Soldier, exactly as in the second attached image (outfit reference only): Standard plain BARBUTE helm (open face, no crest, no gold, no emblem), simple silver plate armour, blue scarf, blue tabard with a light trim, brown leather belt and gloves, steel greaves. No shield. Style: Fire Emblem-style anime pixel art matching that sheet: clean dark outlines, cel shading, light from the upper left, about 6 heads tall including the helmet, 3/4 view FACING RIGHT in every cell.

Poses: copy the dual-sword attack of the third attached image (poses only - ignore its character, outfit, swords, slash arcs and text). Each hand grips a flat straight guide rod instead of a sword:
- the FRONT arm - its shoulder on the RIGHT side of the picture, closer to where the character faces - always holds the CYAN rod (#00FFFF);
- the BACK arm - its shoulder on the LEFT side of the picture - always holds the MAGENTA rod (#FF00FF).
The rods NEVER change arms. Below, the arms are named by their rod colour.

Cells, top row left to right, then bottom row left to right:
1. STAND: low wide stance, both rods held low at the sides pointing down and outward - the cyan rod down and forward, the magenta rod down and back (concept: first figure).
2. READY: the CYAN arm raised high above the head, its rod angled back over the head, ready to chop; the magenta arm low and back, its rod pointing down behind; weight shifting forward (concept: "Wind-up").
3. SLASH 1: the CYAN arm has chopped down in front of the body, its rod pointing down and forward near the front foot; the magenta arm still low and back (concept: "Slash Down").
4. SLASH 2: deep lunge; the MAGENTA arm sweeps horizontally across the front of the body at waist height (mid-swing), its rod level; the cyan arm pulled back low (concept: "Slash").
5. FINISH: follow-through; the MAGENTA arm fully extended forward at shoulder height, its rod level and pointing forward; the cyan arm pulled back and down behind the body, its rod pointing down and back; scarf and tabard swinging (concept: "Follow-through").
6. GET HIT: recoiling back, knees bent, head knocked back, wincing; cyan rod still in the front hand, magenta rod in the back hand, both held low.

Hair under the helmet: in EVERY cell, a ponytail of long hair comes out from under the back of the helmet and hangs down behind the neck, following each pose. It always stays BEHIND the body: it never covers the armour, scarf, arms or face. Paint the hair entirely in shades of pure red (#FF0000 family: very dark red for the outline and shadows, mid red, bright red for highlights) - no black outline on it.

Hard rules:
- No swords or other weapons, no shield, no cape. Rods: flat single colours, no shading or outline, 2-3% of the figure height thick, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta or cyan anywhere.
- The face is the only bare skin: shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold.
- Pure red is used ONLY for the hair.
- No text, labels, slash arcs, motion lines, dust, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
Male line: "Male: broad, sturdy frame." Female line: "Female: clearly feminine - smaller frame, narrower shoulders, curved
waist and hips, visible chest under the armour, slimmer limbs, smaller pauldrons, a soft feminine face with larger eyes and
a small chin, same armour and helmet."
In game: stand -> ready -> slash 1 (cyan / off-hand weapon) -> slash 2 (magenta / main-hand weapon) -> finish -> stand.
One weapon only (no shield): stand -> slash 2 -> finish, from the magenta (main) hand.
**Superseded by v2 below**: with this prompt ChatGPT kept putting the cyan rod on the near arm in SLASH 1 (10+ tries) and read
the concept's slash 2 / follow-through backwards. The male sheet was then fixed by hand in code.

### Soldier dual weapons v2 (2026-11-21) - copy the fixed male sheet
Use this for every new dual sheet (female, redraws). The pose reference is the hand-fixed male sheet, so ChatGPT copies
finished poses instead of reading the concept. Attach, in this order: (1) `templates/soldier_dual_template.png`,
(2) `source/soldier_dual_m_sheet.png` (fixed male sheet: poses and rods), (3) `source/concepts/soldier_outfit_ref.png`.
The arms are named by their shoulder plate and rod colour. "Left/right" and "front/back" both confused ChatGPT.
Slash waves are added in code; ChatGPT must not draw them.

```
Use the first attached image as the canvas: a grid of 2 rows x 3 cells on flat pure green (#00FF00), each cell with a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, all 6 figures at the same scale and the same character.

POSES: the second attached image is the pose sheet. Copy each of its 6 cells into the same cell of the canvas: the same stance, the same leg positions, the same body angle, the same arm positions, and the same coloured rod in the same hand pointing the same way. Change only the character's build as described below. Do not invent new poses, do not mirror any figure, do not swap the rods.

The two arms (check this in every cell before you finish):
- The NEAR arm is the arm closest to the viewer. Its big round shoulder plate sits IN FRONT of the chest, on the LEFT side of the picture, and overlaps the torso. The near arm ALWAYS holds the MAGENTA rod (#FF00FF).
- The FAR arm is the arm farther from the viewer. Its shoulder is half hidden BEHIND the scarf and chest, on the RIGHT side of the picture. The far arm ALWAYS holds the CYAN rod (#00FFFF).
- The chest always faces the viewer at 3/4, turned toward the right. Never show the character's back, and never move the big near shoulder plate to the right side of the chest.

Cells (top row left to right, then bottom row left to right) - all exactly as in the pose sheet:
1. STAND: wide low stance; magenta rod low on the left pointing down and back, cyan rod low on the right pointing down and forward.
2. READY: the FAR (cyan) arm raised high above the helmet, its rod angled back over the head; the near (magenta) arm low, rod pointing down and back.
3. SLASH 1: the FAR (cyan) arm has come down in front: its hand at the front hip, the cyan rod pointing down and forward toward the front foot, the arm passing BEHIND the torso. The near (magenta) arm stays low with its rod pointing down and back. This is the cell that usually goes wrong: the cyan rod belongs to the far arm, never to the near arm.
4. SLASH 2: the NEAR (magenta) arm swung out BEHIND the body to the left at chest height, almost straight; the magenta rod passes through the fist and points FORWARD (to the right) across the waist, below the arm. The far (cyan) arm low in front, rod pointing down and forward.
5. FINISH: the NEAR (magenta) arm extended back and slightly up to the left at shoulder height; the magenta rod points back and up-left past the fist. The far (cyan) arm low in front, rod pointing down and forward.
6. GET HIT: recoiling back, head knocked back, wincing; rods held low, magenta in the near hand, cyan in the far hand.

Character: <SEX> Soldier, outfit exactly as in the third attached image: plain BARBUTE helm (open face, no crest, no gold, no emblem), simple silver plate armour, blue scarf, blue tabard with a light trim, brown leather belt and gloves, steel greaves. No shield. Style: Fire Emblem-style anime pixel art matching the pose sheet: clean dark outlines, cel shading, light from the upper left, about 6 heads tall including the helmet, FACING RIGHT in every cell.

Hair under the helmet: in EVERY cell a ponytail comes out from under the back of the helmet and hangs behind the neck, following each pose as in the pose sheet. It always stays BEHIND the body and never covers the armour, scarf, arms or face. Paint the hair entirely in shades of pure red (#FF0000 family: very dark red for outline and shadows, mid red, bright red highlights), with no black outline.

Hard rules:
- No swords or other weapons, no shield, no cape. Rods: flat single colours, no shading or outline, as thick as in the pose sheet, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta or cyan anywhere.
- The face is the only bare skin: shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold.
- Pure red is used ONLY for the hair.
- No text, labels, slash arcs, slash waves, motion lines, dust, ground shadows or background objects.
- Output one PNG at the canvas's exact size.
```
Female line (add at the end): "Female: clearly feminine - smaller frame, narrower shoulders, curved waist and hips, visible
chest under the armour, slimmer limbs, smaller pauldrons, a soft feminine face with larger eyes and a small chin, same armour
and helmet, same poses as the pose sheet." Male line: "Male: broad, sturdy frame, same build as the pose sheet."
If one cell still comes out wrong, ask ChatGPT to redraw only that cell: "Redraw only cell <N> so it matches cell <N> of the
pose sheet exactly - the near arm (big shoulder plate in front of the chest, left side of the picture) holds magenta, the far
arm holds cyan. Keep the other 5 cells pixel-identical." If it still fails, send the sheet anyway and it is fixed in code.

### Soldier dual weapons - Gemini edit (2026-11-21, user: "let's try using Gemini on this")
Gemini is used as an EDITOR: attach only `source/soldier_dual_m_sheet.png` (the hand-fixed male sheet) and ask for the same
sheet with a female body. Poses, rods, colour keys and grid are already right, so nothing about the arms is left to redraw.

```
Edit the attached sprite sheet. It shows a male armoured soldier in six poses, in a grid of 2 rows x 3 cells on a flat green screen. Turn him into a FEMALE soldier and change nothing else.

Keep exactly as they are:
- the canvas size, the 2 x 3 grid, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position, height and feet of every figure, standing on the same ground lines;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle, the same flat colours with no shading;
- the red ponytail behind the neck (same shades of pure red), the face painted in shades of pure yellow;
- the plain barbute helmet, silver plate armour, blue scarf, blue tabard, belt, gloves and greaves, with the same colours;
- the pixel-art style, outlines and shading.

Change only the body and face: clearly feminine - a smaller, slimmer frame, narrower shoulders, curved waist and hips, a visible chest under the breastplate, slimmer arms and legs, smaller shoulder plates, and a soft feminine face with larger eyes and a small chin.

Do not add swords, weapons, slash effects, motion lines, shadows, text or anything else. Output the whole sheet at the same size.
```
If Gemini changes a pose or moves a stick to the other hand, attach its result together with the male sheet and say:
"Fix cell <N> of the first image so its pose and sticks match cell <N> of the second image exactly. Keep everything else."
The Gemini app may put a small sparkle logo in a corner: fine, it is cut out with the green.


### Archer
> Character: **<SEX> Archer** (light armour and hooded cloak with the hood DOWN, from the portrait). Rows, top to bottom:
> 1. **One-handed (dagger)**, cells = stand | attack | hit: stand = right fist raised by the shoulder (magenta rod up),
>    left fist forward (cyan rod upright). Attack = lunge, right arm thrust forward with the magenta rod level, left fist
>    guarding the chest. Hit = recoiling back, wincing, both rods still held.
> 2. **Bow**, cells = stand | nock | release | hit: the bow is a vertical **cyan** rod in the LEFT fist, about two thirds
>    of the body height. Stand = relaxed, bow rod lowered at the side, right hand empty and relaxed. Nock = full draw:
>    left arm straight forward at shoulder height holding the cyan rod upright, right hand pulled back to the cheek, and
>    a thin straight **magenta line** (the arrow) from the right hand to the cyan rod. Release = same stance, right hand
>    open and flung back, no magenta line. Hit = recoiling back, wincing, still holding the cyan rod.
> 3. **Crossbow** (new poses, nothing to copy in the reference - follow this text), cells = stand | aim | release | hit:
>    the crossbow stock is ONE straight **magenta** rod, about as long as the forearm plus hand, held in BOTH fists:
>    right fist at the rear end (trigger grip), left fist further forward under it. Stand = crossbow held low and
>    level across the hips, pointing forward. Aim = crossbow raised to the shoulder, rear end against the right shoulder,
>    rod level and pointing forward, head tilted to sight along it. Release = same as aim, rod kicked up a little from the
>    recoil, shoulders pushed back. Hit = recoiling back, wincing, still holding the rod in both fists, pointing up.
>
> **Back equipment marker (this sheet only):** the quiver or bolt case is a separate layer, so don't draw a quiver. In
> **every cell**, draw one flat **pure blue (#0000FF)** stick on the back where the quiver sits: a straight rounded bar,
> as long as the torso and about as thick as the forearm, top end behind the right shoulder, slanting down toward the
> left hip, partly hidden behind the body like a real quiver would be. Flat colour, no shading, no outline, no arrows.
> A leather strap across the chest is fine. No other pure blue anywhere.
> Female: clearly feminine, slightly fuller chest.

### Archer back equipment (quiver and bolt case)
Attach `templates/archer_ammo_template.png` (and `refs/archer_m_ref.png` for the style), then paste this alone
(not the common prompt):
> Use the attached green image as the canvas: 6 cells, each with a vertical dashed guide between two ticks. Keep the
> canvas, grid and green exactly as they are. In each cell draw ONE item, standing upright, its length exactly from the
> top tick to the bottom tick, centred on the cell, in Fire Emblem-style anime pixel art (clean dark outlines, cel
> shading, light from the upper left) matching the archer in the second image. Order, left to right:
> - Top row, a **back quiver** of brown leather with a strap ring at the top: **full** (a thick bunch of arrow shafts and
>   fletchings sticking out of the top), **partial** (only 3-4 arrows), **empty** (no arrows, open mouth visible).
> - Bottom row, a **bolt case** (a shorter, boxier leather-and-wood case with a flap; draw it at the same length guide):
>   **full** (many short crossbow bolts with stubby fletchings), **partial** (3-4 bolts), **empty** (no bolts).
> Same item design across its three states; only the amount of ammunition changes. No character, no strap across the
> cell, no text, no shadows, no yellow, no pure blue, no magenta, no cyan. Output one PNG at the canvas's exact size.

### Acolyte
> Character: **<SEX> Acolyte** (cleric robes with a single centred cross, never two crosses, from the portrait; hood
> down). Rows, top to bottom, cells = stand | attack | hit:
> 1. **One-handed (mace + shield):** same as a soldier's: stand = right fist raised (magenta rod up), left fist forward
>    (cyan rod upright). Attack = deep lunge, right arm extended forward with the magenta rod level (not downward); the LEFT
>    forearm is RAISED and braced across the front of the chest, left fist at chest height with the cyan rod upright,
>    like holding a shield up - NOT down at the belt or hip. Hit = recoil, wince, rods still held.
> 2. **Two-handed (quarterstaff):** ONE magenta rod about as long as the body is tall, both fists on it a little apart.
>    Stand = guard, staff angled across the body. Attack = forward strike with the staff end. Hit = recoil.
> 3. **Reach (spear):** ONE long magenta pole held at hip height through both fists, front fist forward, back fist at
>    the rear hip. Stand = guard. Attack = full thrust, deep lunge. Hit = recoil.

### Mage
> Character: **<SEX> Mage** (violet robe, silver trim, high collar, crescent clasp, from the portrait). One row, cells =
> stand | attack | hit:
> **One-handed (staff):** the staff is ONE magenta rod about as long as the body is tall, held upright in the RIGHT
> fist; the left hand is open (no rod, no cyan). Stand = staff planted upright beside the body, left hand relaxed. Attack
> = casting: step forward, staff thrust forward and up, left palm pushed forward. Hit = recoiling back, wincing, staff
> still held.
> Light build, no armour.

### Warrior
> Character: **<SEX> Warrior** (armoured barbarian from the portrait: fur mantle, scale shirt, leather harness with iron
> rings, **bare upper arms** - those are skin, so yellow). Rows, top to bottom, cells = stand | attack | hit:
> 1. **Unarmed (fists):** short magenta rod in the right fist, short cyan rod in the left (they mark where the hand
>    wraps go). Stand = boxer's guard, both fists up. Attack = big right straight punch, arm fully extended, lunging in,
>    left fist guarding the chin. Hit = recoil, wince, guard dropped.
> 2. **Two-handed (great axe):** both fists together on ONE magenta rod. Stand = guard, rod angled up and forward.
>    Attack = heavy forward chop. Hit = recoil.
> 3. **Reach (spear):** ONE long magenta pole at hip height through both fists. Stand = guard. Attack = full thrust.
>    Hit = recoil.
> Muscular frame. Female: clearly feminine but strong.

### Rogue
> Character: **<SEX> Rogue** (charcoal leather armour, plum short cape with the hood down, scarf, chest strap, from the
> portrait). One row, cells = stand | attack | hit:
> **Dual daggers:** short magenta rod in the right fist, short cyan rod in the left. Stand = low, crouched ready stance,
> right fist raised, left fist forward. Attack = fast lunge, right arm stabbing forward with the magenta rod level, left
> fist low and ready. Hit = recoiling back, wincing, both rods still held.
> Lean, agile build.

---

## Notes from the first sheets (Soldier m/f, 2026-11-19)
- Skin came out yellow-orange (about #F8B840), which is fine; the belt buckle and tabard trim came out the same gold,
  so the common prompt now asks for silver / dark bronze trims.
- The 1h attack's left (shield) fist ended low at the belt instead of braced in front of the chest.

## Shield rule (user, 2026-11-20)
Each class with a shield has its OWN shield, drawn by ChatGPT **into the body** (on the left arm) **in its final colours**,
so the overlaps are right. Headgear (user, 2026-11-20) is likewise drawn into the battle sprite per class (Soldier =
plain barbute helm) and never appears on portraits. The look never changes with equipment: shield items are broad categories (light shield, heavy
shield, tower shield) that change the rules only, and the sprite always shows the class shield. Soldier = **square**
shield (navy face, silver cross and rim, from the concept), Acolyte and Warrior = **round** shield, kite shield = reserved
for a future Knight class. A one-handed weapon **without** a shield uses the **dual-weapon stance** (left hand empty).

### Fix: redraw only the Soldier's shield row (keep the other rows)
Poses from the user's square-shield concept (`source/concepts/soldier_shield_concept.png`, 2026-11-20): key frames cropped into
`refs/soldier_shield_ref.png` (stand = stand frame 1, attack = attack frame 4, get hit = get-hit frame 4).
Attach (1) the current Soldier sheet `source/soldier_<sex>_sheet.png`, (2) `source/concepts/soldier_concept.png` (outfit),
(3) `refs/soldier_shield_ref.png` (poses), then:
```
Edit the first attached sheet. Redraw ONLY the top row (3 cells); rows 2-4, the canvas, the grid and the green must stay pixel-identical. Same character, outfit (second image), scale and ground lines. Copy the three poses of the third image, in order (pose only - ignore its colours, sword, slash arc and background). In all three top-row cells the LEFT arm carries a large SQUARE shield (an upright rectangle with slightly rounded corners, from the shoulder to mid-thigh, as wide as the torso, a thick rim with rivets and a raised cross in relief on the face). Colour it like the shield in the third image: dark navy-blue face, a silver/white cross in relief, a silver steel rim with rivets - no gold or yellow on it. The left fist is hidden behind the shield (no cyan rod). STAND = guard: shield held upright in front of the torso, covering it; right fist raised beside the shoulder with the magenta rod pointing up (sword raised). ATTACK = controlled horizontal slash: deep lunge forward, the right arm sweeps across IN FRONT of the body at waist height, magenta rod pointing forward and slightly down; the shield opens slightly to the side (still on the left arm, turned a little outward) so the sword arm passes in front of it. GET HIT = grounded recoil: feet planted, knees bent, braced behind the shield, the shield tilted up and forward to absorb the blow, head knocked back and wincing, right fist low by the hip holding the magenta rod pointing down. Rods stay flat pure #FF00FF. Bare skin stays yellow. Bald head. No sword, no effects.
```

### Fix: Soldier dual ATTACK 1 must be the RIGHT arm (2026-11-20)
In right-facing sprites the character's LEFT arm is the lead arm (right side of the picture, the shield arm) and the
RIGHT arm is the rear arm. An earlier rule here wrongly asked for magenta in the lead hand; ChatGPT then drew both dual
attacks with the same (left) arm. Attach the sheet and send:
```
Edit the attached sheet. Redraw ONLY the second cell of the SECOND row (dual weapons ATTACK 1); every other cell, the canvas, the grid and the green must stay pixel-identical. Same character, helmet, armour, hair, scale and ground line. The RIGHT arm - the rear arm, whose shoulder is on the LEFT side of the picture (the sword arm of row 1) - swings forward ACROSS the front of the body and thrusts out at shoulder height holding the magenta rod level and pointing forward. The LEFT arm - the lead arm on the right side of the picture - pulls back and down holding the cyan rod. This must be a different arm from the one thrusting in ATTACK 2. Rods stay flat pure #FF00FF and #00FFFF, sticking out of both sides of the fists. The face stays yellow, the hair stays pure red. No weapons, no effects.
```

### Dual weapons: two attack poses (main hand + off-hand), 2026-11-20
Dual wield attacks twice (main hand, then off-hand), so the dual row gets two attacks. The Soldier v4 male sheet came back
with the OFF-HAND attack (left arm forward with cyan) - keep that sheet as is; it gives ATTACK 2. Then make an edited copy
for ATTACK 1 (main hand). Attach that sheet alone and send:
```
Edit the attached sheet. Redraw ONLY the middle cell of the SECOND row (dual weapons ATTACK); every other cell, the canvas, the grid and the green must stay pixel-identical. Same character, helmet, armour, hair, scale and ground line. Make it the MAIN-HAND attack: a lunging slash with the RIGHT arm swept fully forward at shoulder height holding the magenta rod level and pointing forward, and the LEFT arm pulled back low holding the cyan rod. The RIGHT arm is the one in front of the body. Rods stay flat pure #FF00FF (right) and #00FFFF (left), sticking out of both sides of the fists. The face stays yellow, the hair stays pure red. No weapons, no effects.
```
If a sheet comes back with the main-hand attack instead, ask for the OFF-HAND attack the same way: "the LEFT arm swept forward at shoulder height holding the cyan rod level, the RIGHT arm pulled back low holding the magenta rod; the body twisted so the left arm is in front."

## If ChatGPT struggles
- Too many figures (Soldier, Acolyte, Warrior have 9): ask for **one row at a time** on the same template ("draw only
  row 1, leave the other cells empty green").
- Rods missing or shaded: reply "the guide rods must be flat pure #FF00FF (right hand) and #00FFFF (left hand), straight,
  sticking out of both ends of the fist".
- Hair or weapons appear: reply "remove all hair and weapons, keep everything else identical".

### Soldier dual slash frames - Gemini adds the weapon smear (2026-11-21, v2)
The code-drawn blurred sword was rejected ("bad design"). v1 of this prompt said "sword" and "blade", so Gemini drew a
recognisable sword; the dual stance takes any one-handed weapon (sword, mace, axe...), so the smear must read as "a weapon
swung fast" without showing which weapon (user). v2 never names a weapon: it asks for an animation SMEAR - a steel-grey
streak with no edge, head or handle shape. One image per chat message: attach `source/concepts/soldier_dual_m_slash1_gemini.png`
(or `_slash2_gemini.png`) and paste the matching prompt. The result replaces the image and is run through `tools/gemini_fx_*`.

Slash 1:
```
Edit the attached image. Add a SMEAR of something heavy swung extremely fast, the way classic 2D fighting games and anime draw a smear frame, and change nothing else.

The smear comes out of the fist at the bottom of the yellow slash arc (the hand at the front hip, on the right of the picture, inside the glow). It sweeps down along the arc: narrow where it leaves the fist, wider and brighter along the arc, ending near the front foot, then fading back UP the arc in 2 or 3 thin see-through streaks.

What the smear looks like: a solid streak of cold steel grey and white, like polished metal stretched by speed - a pale silver core, a slightly darker steel-grey edge, soft streaky lines along the direction of motion. It must NOT show any object: no outline of an edge, point, head, spikes, guard, handle or pommel - nobody can tell what was swung, only that a metal weapon passed through. It sits on top of the yellow arc and blends into its glow.

Keep exactly as they are: the character, pose, armour, face, hair, the magenta stick in the other hand, the yellow slash arc, the image size and the pure black background. No magenta, cyan, red or yellow in the smear. No text, no other effects.
```

Slash 2:
```
Edit the attached image. Add a SMEAR of something heavy swung extremely fast, the way classic 2D fighting games and anime draw a smear frame, and change nothing else.

The smear comes out of the fist at the far LEFT of the picture (the arm stretched out behind the body, the fist inside the yellow glow). It runs forward (to the right) along the yellow sweep across the front of the waist, below the outstretched arm: narrow where it leaves the fist, wider and brighter in front of the body, then fading out to the RIGHT along the sweep in 2 or 3 thin see-through streaks.

What the smear looks like: a solid streak of cold steel grey and white, like polished metal stretched by speed - a pale silver core, a slightly darker steel-grey edge, soft streaky lines along the direction of motion. It must NOT show any object: no outline of an edge, point, head, spikes, guard, handle or pommel - nobody can tell what was swung, only that a metal weapon passed through. It sits on top of the yellow sweep and blends into its glow.

Keep exactly as they are: the character, pose, armour, face, hair, the cyan stick in the other hand, the yellow sweep, the image size and the pure black background. No magenta, cyan, red or yellow in the smear. No text, no other effects.
```
If Gemini still draws a recognisable weapon, follow up in the same chat: "Remove every shape of the weapon - no edge, tip,
head or handle. Keep only a soft steel-grey motion streak along the arc, like a blur of light on metal."

### Soldier dual sheet - Gemini puts the smear frames into the sheet (2026-11-21)
Attach, in this order: (1) `source/concepts/soldier_dual_m_sheet_handfixed.png` (the hand-fixed sheet, clean cells),
(2) `source/concepts/soldier_dual_m_slash1_gemini_smear.png`, (3) `source/concepts/soldier_dual_m_slash2_gemini_smear.png`.
The result becomes `source/soldier_dual_m_sheet.png`; the glow and smear are then split off the green into the effect layer.

```
Edit the first attached image, a sprite sheet of 2 rows x 3 cells on a flat pure green (#00FF00) background. Replace ONLY two cells and keep everything else pixel-identical.

- Top row, RIGHT cell (cell 3): replace the figure with the character from the second attached image, together with its yellow slash arc and its grey motion smear.
- Bottom row, LEFT cell (cell 4): replace the figure with the character from the third attached image, together with its yellow sweep and its grey motion smear.

For both new cells:
- Remove their black background completely: the figure, arc and smear sit on the same flat pure green as the rest of the sheet, with no black or dark halo anywhere. The glow of the arc fades straight into the green.
- Scale the character to exactly the same size as the characters in the other cells (same helmet size, same height when standing), feet standing on that cell's dark ground line, horizontally in the same place as the figures in the other cells.
- Keep the arc and smear whole: shrink them together with the character, never crop them; they may come close to the cell edge but must not cross into the next cell.
- Keep the character, pose, colours, the magenta stick (cell 3) and the cyan stick (cell 4) exactly as in the attached images.

Do not change the other four cells, the grid lines, the ground lines, the dashed lines or the canvas size. No text, no new effects.
```
If Gemini changes the other cells or leaves black around the effects, the cells can also be put in by code
(`tools/gemini_fx_split.py` + `gemini_fx_compose.py` take the black-background images directly).

### Female Soldier - Gemini edits of the male sheets (2026-11-21)
Same approach that worked for the dual sheet: Gemini only turns the finished male sheets female, so poses, rods, colour
keys and grid are copied, not redrawn. One sheet per chat message.
- Main sheet: attach `source/soldier_m_sheet.png` (4 x 4; its row 2 is the old dual row and is skipped in processing) ->
  save the result as `source/soldier_f_sheet.png` (`SHEET_ROWS` for `('soldier', 'f')` = the male v5 layout).
- Dual sheet: attach `source/concepts/soldier_dual_m_sheet_gemini_smear.png` (the user's sheet with the slash arcs and
  smears) -> save as `source/soldier_dual_f_sheet.png`.
Earlier mistakes this guards against: female figures with a big head and a manly face; poses mirrored or rods moved to
the other hand; shields or effects redrawn differently.

Main sheet:
```
Edit the attached sprite sheet. It shows a male armoured soldier in 16 poses, in a grid of 4 rows x 4 cells on a flat green screen. Turn him into a FEMALE soldier and change nothing else.

Keep exactly as they are:
- the canvas size, the 4 x 4 grid, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position and feet of every figure, standing on the same ground lines;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle and length, the same flat colours with no shading;
- the square navy shield with the silver cross and rim in the top row, on the same arm and at the same angle;
- the red ponytail behind the neck (same shades of pure red), the face painted in shades of pure yellow;
- the plain barbute helmet, silver plate armour, blue scarf, blue tabard, belt, gloves and greaves, with the same colours;
- the pixel-art style, outlines and shading.

Change only the body and face: clearly feminine - a smaller, slimmer frame, narrower shoulders, a curved waist and hips, a visible chest under the breastplate, slimmer arms and legs, smaller shoulder plates, and a soft feminine face with larger eyes, softer cheeks and a small chin. Keep the head and helmet in proportion: the helmet is NOT bigger than his, the figure is about 6 helmet-heights tall. She is about as tall as him, so her helmet top stays near the dashed line.

Do not add weapons, effects, shadows, text or anything else. Output the whole sheet at the same size.
```

Dual sheet:
```
Edit the attached sprite sheet. It shows a male armoured soldier in six poses, in a grid of 2 rows x 3 cells on a flat green screen, two of them with a yellow slash arc and a grey motion smear. Turn him into a FEMALE soldier and change nothing else.

Keep exactly as they are:
- the canvas size, the 2 x 3 grid, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position and feet of every figure, standing on the same ground lines;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle and length, the same flat colours with no shading;
- the yellow slash arcs and grey smears in the top-right and bottom-left cells: same shape, size, position and colours;
- the red ponytail behind the neck (same shades of pure red), the face painted in shades of pure yellow;
- the plain barbute helmet, silver plate armour, blue scarf, blue tabard, belt, gloves and greaves, with the same colours;
- the pixel-art style, outlines and shading.

Change only the body and face: clearly feminine - a smaller, slimmer frame, narrower shoulders, a curved waist and hips, a visible chest under the breastplate, slimmer arms and legs, smaller shoulder plates, and a soft feminine face with larger eyes, softer cheeks and a small chin. Keep the head and helmet in proportion: the helmet is NOT bigger than his, the figure is about 6 helmet-heights tall. She is about as tall as him, so her helmet top stays near the dashed line.

Do not add weapons, new effects, shadows, text or anything else. Output the whole sheet at the same size.
```
If one cell changes pose or a stick swaps hands, attach Gemini's result together with the male sheet and say:
"Fix cell <N> of the first image so its pose and sticks match cell <N> of the second image exactly. Keep everything else."

### Soldier DOWNED sprite, both sexes (2026-11-24, user: "downed sprite for each gender, used for all soldier")
One downed pose per sex, shared by every Soldier loadout, so no weapon, rod or shield. Attach only
`templates/soldier_downed_template.png` (`tools/make_downed_template.py`): top row empty, bottom row = the finished male
and female STAND figures as outfit, scale and colour-key reference. The result is saved as
`source/soldier_downed_sheet.png`. If one sex comes out wrong, redo only that cell with Gemini ("Fix cell <N> ... keep
everything else"), or turn the good male figure female with the Gemini edit prompt above.

```
Use the attached image as the canvas: a grid of 2 rows x 3 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are, and keep the whole bottom row exactly as it is.

The bottom row shows the same armoured soldier, MALE in the bottom-left cell and FEMALE in the bottom-middle cell, standing. Draw each of them DOWNED in the empty cell directly above them:
- top-left cell: the male soldier from the bottom-left cell;
- top-middle cell: the female soldier from the bottom-middle cell;
- top-right cell: leave empty green.

DOWNED pose (knocked out of the fight but still alive), the same for both: collapsed on both knees on the ground line, sitting back on the heels, torso slumped forward, head hanging down so the face is half hidden, both arms hanging limp with the open, empty hands resting on the ground beside the knees. Still in 3/4 view, the body turned toward the right, like the figures below. The ponytail hangs down behind the neck.

Same character, same scale: the helmet, armour plates and limbs are exactly as big as in the standing figure below (the figure is shorter only because it kneels). Copy the outfit and colours exactly from the figure below: plain barbute helmet, silver plate armour, blue scarf, blue tabard with light trim, brown belt and gloves, steel greaves, same pixel-art style, outlines and shading. Each figure keeps its own build: the male broad and sturdy, the female slimmer and clearly feminine, as below.

Colour keys, exactly as in the figures below:
- the face is the only bare skin and is painted in shades of pure yellow;
- the ponytail is painted in shades of pure red, behind the neck and never covering the armour;
- nothing else is yellow, gold or pure red.

No weapons, no sticks or rods, no shield, nothing in the hands. No text, labels, shadows on the ground, effects or background objects. Output one PNG at the canvas's exact size.
```

### Archer step 1 - battle design sheet (2026-11-24, user: "create archer on GPT")
Same order as the Soldier: design first, poses after (the Soldier's mistakes came from drawing poses before the look
was fixed). Attach `source/concepts/soldier_final_design.png` (style and proportions) and
`source/concepts/archer_portrait_ref.png` (the Archer's outfit from the portraits). The user picks the headgear and the
look; then step 2 = the pose sheets, written with the Soldier lessons (arms named by rod colour and shoulder plate,
male sheet first, female by a Gemini edit of the finished male sheet, ready poses, red hair key, blue quiver marker,
one-handed dagger in the dual stance on its own sheet).

```
Create a character design sheet for a fantasy game's ARCHER class, in exactly the same art style, proportions and level of detail as the first attached image (a Soldier design sheet): Fire Emblem-style anime pixel art, clean dark outlines, cel shading, light from the upper left, about 6 heads tall including the headgear.

The outfit must match the second attached image (the Archer's portrait busts, male and female): a forest-green hooded cloak with a thin gold trim (hood DOWN, lying on the shoulders), a brown leather vest laced at the front over a white shirt, brass buckles; add what an archer wears in battle and the busts do not show: a leather bracer on the bow arm, a shooting glove, brown leather trousers or leggings, soft knee-high boots, a belt with a small pouch.

Show on one sheet, on a plain light background:
1. Top row: the MALE archer and the FEMALE archer, full body, standing, 3/4 view facing right, empty hands. The male lean and athletic; the female clearly feminine (narrower shoulders, curved waist and hips, slightly fuller chest, soft face with larger eyes and a small chin), with a head NOT bigger than the male's.
2. Bottom row: three HEADGEAR options on the male's head (head and shoulders only), side by side: (a) a leather archer's cap with a single feather; (b) a light open-face leather-and-steel skullcap; (c) a green cloth hood pulled UP over the head, face open. Each option must leave the back of the neck uncovered so a ponytail could hang out under it.
3. A back quiver of brown leather with arrows, worn across the back from the right shoulder to the left hip, shown on both full-body figures.

No bow, crossbow or other weapon in the hands (weapons are added in the game). No text other than the small letters a, b, c under the headgear options. Output one image.
```

### Archer step 2 - main pose sheet from the pose draft (2026-11-24)
User chose: headgear **c, hood UP** (so no hair key: the hood hides the hair) and a **pose draft** drawn in code
(`tools/archer_pose_draft.py` -> `refs/archer_pose_draft.png`): grey mannequins on the archer template, NEAR arm darker
in front of the body, FAR arm lighter behind it, sticks in the right hands. Main sheet = bow row + crossbow row
(the dagger uses the dual stance on its own sheet - later, as a Gemini edit of the finished Soldier dual sheet).
Male first; the female is a Gemini edit of the finished male sheet. Attach, in order: (1) `templates/archer_template.png`,
(2) `refs/archer_pose_draft.png`, (3) `source/concepts/archer_design.png`.

```
Use the first attached image as the canvas: a grid of 2 rows x 4 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the hood at the dashed line when standing upright, all 8 figures at the same scale and the same character.

POSES: the second attached image is the pose draft: grey mannequins on the same grid. Copy each mannequin's pose into the same cell: the same stance, legs, body angle, arm positions and the same coloured stick in the same hand at the same angle. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm (darker grey in the draft) is the arm closest to the viewer: its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body.
- The FAR arm (lighter grey in the draft) is the arm farther from the viewer: its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body.
- Top row (bow): the FAR hand holds the bow = a straight vertical CYAN stick (#00FFFF). In the 2nd cell the NEAR hand draws a thin straight MAGENTA line (#FF00FF, the arrow) back to the cheek. In the 3rd cell the NEAR hand is open and flung back, and there is no magenta.
- Bottom row (crossbow): ONE straight MAGENTA stick (the crossbow stock) held in BOTH fists, the NEAR fist at its rear end, the FAR fist further forward under it.

Cells, top row left to right: BOW STAND (bow lowered at the side) | NOCK (full draw) | RELEASE | GET HIT (recoiling back, wincing, still holding the bow). Bottom row left to right: CROSSBOW STAND (held low across the hips) | AIM (raised to the shoulder, sighting along it) | RELEASE (kicked up by the recoil) | GET HIT (recoiling back, crossbow pointing up, still in both fists).

Character: MALE ARCHER exactly as on the left of the third attached image (design sheet): forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open, brown leather vest laced at the front over a white shirt, brass buckles, leather bracer, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch. Lean and athletic. Style: Fire Emblem-style anime pixel art matching the design sheet, clean dark outlines, cel shading, light from the upper left, about 6 heads tall, 3/4 view FACING RIGHT in every cell.

Quiver marker: do NOT draw the quiver. In every cell, draw one flat pure BLUE (#0000FF) bar on the back exactly where the blue bar is in the draft: top end sticking up behind the near shoulder, slanting down behind the back. Flat colour, no shading, no outline, partly hidden behind the body and cloak.

Hard rules:
- No bow, crossbow, arrows or other weapons: only the flat sticks described above, 2-3% of the figure height thick (the arrow line thinner), flat single colours with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta, cyan or pure blue anywhere.
- The face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold except the thin cloak trim and the buckles.
- No hair visible: the hood covers it. No pure red anywhere.
- No text, labels, effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```

### Archer dagger / dual daggers - Gemini edit of the finished Soldier dual sheet (2026-11-25)
One sheet covers both loadouts: one dagger (no shield) plays stand -> slash 2 -> finish with the main hand only; two
daggers play the whole sheet. The poses, sticks, slash arcs and smears are already right on the Soldier dual sheets, so
Gemini only changes the outfit. One message per sex. Attach (1) `source/concepts/soldier_dual_<m|f>_sheet_gemini_smear.png`
and (2) `source/concepts/archer_design.png`; save the result as `source/concepts/archer_dual_<m|f>_sheet_gemini_smear.png`
(its arc and smear are lifted off the green with `tools/green_fx_split.py`, like the Soldier's).

```
Edit the first attached image, a sprite sheet of 2 rows x 3 cells on a flat green screen: an armoured soldier in six poses, two of them with a yellow slash arc and a grey motion smear. Turn the soldier into the <SEX> ARCHER from the second attached image (design sheet) and change nothing else.

Change only the outfit and build:
- forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open; brown leather vest laced at the front over a white shirt, brass buckles, leather bracers, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch - exactly as on the design sheet;
- no helmet, no plate armour, no scarf or tabard;
- a lighter, leaner build than the soldier: <BUILD>;
- no hair visible (the hood covers it) and no red anywhere;
- one flat pure BLUE (#0000FF) bar on the back in every cell where the quiver would be: top end sticking up behind the shoulder on the left of the picture, slanting down behind the back, partly hidden by the body and cloak; flat colour, no shading, no outline. Do not draw the quiver itself.

Keep exactly as they are:
- the canvas size, the 2 x 3 grid, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position, height and feet of every figure;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle and length, the same flat colours with no shading;
- the yellow slash arcs and grey smears in the top-right and bottom-left cells: same shape, size, position and colours;
- the face painted in shades of pure yellow; the pixel-art style, outlines and shading.

No weapons, no bow, no quiver, no new effects, no shadows, no text. Output the whole sheet at the same size.
```
`<SEX>` / `<BUILD>`: male = "MALE" / "lean and athletic"; female = "FEMALE" / "clearly feminine - narrower shoulders, curved
waist and hips, slightly fuller chest, a soft face with larger eyes and a small chin".
If a cell changes pose or a stick swaps hands: attach Gemini's result together with the Soldier sheet and say "Fix cell
<N> of the first image so its pose and sticks match cell <N> of the second image exactly. Keep everything else."

### Archer dual daggers + one dagger - two ChatGPT sheets from pose drafts (2026-11-25)
User chose **two separate sheets** for the Archer: the dual sheet (stand, ready, slash 1, slash 2, finish, hit) and its
own one-handed sheet (one dagger, off-hand empty: stand, ready, attack, hit). (Supersedes the Gemini-edit idea above.)
Drafts by `tools/archer_pose_draft.py`: `refs/archer_dual_pose_draft.png`, `refs/archer_1h_pose_draft.png`.
Male first (ChatGPT); the female is a Gemini edit of each finished male sheet. Attach, in order: (1) the template
(`templates/archer_dual_template.png` or `templates/archer_1h_template.png`), (2) the matching pose draft,
(3) `source/concepts/archer_design.png`. The slash arc/smear is added afterwards (code wave, or a Gemini smear like the Soldier's).

Dual sheet:
```
Use the first attached image as the canvas: a grid of 2 rows x 3 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the hood at the dashed line when standing upright, all 6 figures at the same scale and the same character.

POSES: the second attached image is the pose draft: grey mannequins on the same grid. Copy each mannequin's pose into the same cell: the same stance, legs, body angle, arm positions and the same coloured stick in the same hand at the same angle. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm (darker grey in the draft): its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body. The near hand ALWAYS holds the MAGENTA stick (#FF00FF).
- The FAR arm (lighter grey in the draft): its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body. The far hand ALWAYS holds the CYAN stick (#00FFFF).
- The sticks never change hands.

Cells, top row left to right: STAND (low guard, both sticks low) | READY (the FAR arm raised high above the hood, its cyan stick angled back) | SLASH 1 (the FAR arm has chopped down in front, cyan stick pointing down toward the front foot). Bottom row left to right: SLASH 2 (deep lunge, the NEAR arm swung out behind the body at chest height, its magenta stick pointing FORWARD across the waist) | FINISH (the NEAR arm stretched back and up at shoulder height, magenta stick pointing back) | GET HIT (recoiling back, wincing, both sticks held low).

Character: MALE ARCHER exactly as on the left of the third attached image (design sheet): forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open, brown leather vest laced at the front over a white shirt, brass buckles, leather bracers, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch. Lean and athletic. Style: Fire Emblem-style anime pixel art matching the design sheet, clean dark outlines, cel shading, light from the upper left, about 6 heads tall, 3/4 view FACING RIGHT in every cell.

Quiver marker: do NOT draw the quiver. In every cell, draw one flat pure BLUE (#0000FF) bar on the back exactly where the blue bar is in the draft. Flat colour, no shading, no outline, partly hidden behind the body and cloak.

Hard rules:
- No daggers, knives or other weapons: only the flat sticks, 2-3% of the figure height thick, flat single colours with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta, cyan or pure blue anywhere.
- The face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold except the thin cloak trim and the buckles.
- No hair visible: the hood covers it. No pure red anywhere.
- No text, labels, slash effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```

One-handed sheet:
```
Use the first attached image as the canvas: a grid of 2 rows x 2 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the hood at the dashed line when standing upright, all 4 figures at the same scale and the same character.

POSES: the second attached image is the pose draft: grey mannequins on the same grid. Copy each mannequin's pose into the same cell: the same stance, legs, body angle, arm positions and the magenta stick in the same hand at the same angle. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm (darker grey in the draft): its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body. The near hand holds the only stick, MAGENTA (#FF00FF) - the dagger.
- The FAR arm (lighter grey in the draft): its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body. The far hand is OPEN and EMPTY in every cell.

Cells, top row left to right: STAND (guard: the near fist at the hip with the magenta stick pointing forward, the far hand open in front of the chest) | READY (crouched, weight back, the near arm drawn back, stick pointing forward). Bottom row left to right: ATTACK (deep lunge, the near arm thrust straight forward at shoulder height, stick level and pointing forward; the far arm pulled back) | GET HIT (recoiling back, wincing, the near fist low with the stick, the far hand open).

Character: MALE ARCHER exactly as on the left of the third attached image (design sheet): forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open, brown leather vest laced at the front over a white shirt, brass buckles, leather bracers, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch. Lean and athletic. Style: Fire Emblem-style anime pixel art matching the design sheet, clean dark outlines, cel shading, light from the upper left, about 6 heads tall, 3/4 view FACING RIGHT in every cell.

Quiver marker: do NOT draw the quiver. In every cell, draw one flat pure BLUE (#0000FF) bar on the back exactly where the blue bar is in the draft. Flat colour, no shading, no outline, partly hidden behind the body and cloak.

Hard rules:
- No dagger, knife or other weapon: only the flat magenta stick, 2-3% of the figure height thick, flat single colour with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over it. No cyan anywhere; no other magenta or pure blue.
- The face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold except the thin cloak trim and the buckles.
- No hair visible: the hood covers it. No pure red anywhere.
- No text, labels, effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```

### Archer - ALL poses on ONE sheet (2026-11-25, user: "combine them in 1 file, so I can give GPT 1 task")
Supersedes the three Archer pose prompts above (main, dual, one-handed). One 6 x 3 sheet: row 1 = bow (stand | nock |
release | hit) + one dagger (stand | ready); row 2 = crossbow (stand | aim | release | hit) + one dagger (attack | hit);
row 3 = dual daggers (stand | ready | slash 1 | slash 2 | finish | hit). Figures ~266 px tall on a 1536 x 1024 sheet.
Attach, in order: (1) `templates/archer_template.png`, (2) `refs/archer_pose_draft.png`, (3) `source/concepts/archer_design.png`.
Male first; the female is a Gemini edit of the finished male sheet. Save as `source/archer_<m|f>_sheet.png`.

```
Use the first attached image as the canvas: a grid of 3 rows x 6 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell (18 figures), feet on that cell's ground line, top of the hood at the dashed line when standing upright, all at the same scale and the same character.

POSES: the second attached image is the pose draft: grey mannequins on the same grid. Copy each mannequin's pose into the same cell: the same stance, legs, body angle, arm positions and the same coloured stick in the same hand at the same angle. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm (darker grey in the draft): its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body.
- The FAR arm (lighter grey in the draft): its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body.
- A stick never moves to the other hand.

Cells and sticks:
- Row 1, cells 1-4 (BOW): STAND (bow lowered at the side) | NOCK (full draw) | RELEASE | GET HIT. The FAR hand holds the bow = a straight vertical CYAN stick (#00FFFF). In NOCK the NEAR hand draws a thin straight MAGENTA line (#FF00FF, the arrow) back to the cheek; in RELEASE the near hand is open and flung back, no magenta.
- Row 2, cells 1-4 (CROSSBOW): STAND (held low across the hips) | AIM (at the shoulder, sighting along it) | RELEASE (kicked up by the recoil) | GET HIT (pointing up). ONE straight MAGENTA stick held in BOTH fists: the NEAR fist at its rear end, the FAR fist further forward under it.
- Row 1, cells 5-6 and row 2, cells 5-6 (ONE DAGGER): STAND (guard, near fist at the hip) | READY (crouched, near arm drawn back) | ATTACK (deep lunge, near arm thrust straight forward) | GET HIT. Only the NEAR hand holds a stick, MAGENTA, pointing forward; the FAR hand is OPEN and EMPTY.
- Row 3 (TWO DAGGERS): STAND | READY (the far arm raised above the hood) | SLASH 1 (the far arm chopped down in front) | SLASH 2 (deep lunge, the near arm swung out behind the body, its stick pointing forward across the waist) | FINISH (the near arm stretched back and up) | GET HIT. The NEAR hand ALWAYS holds MAGENTA, the FAR hand ALWAYS holds CYAN.

Character: MALE ARCHER exactly as on the left of the third attached image (design sheet): forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open, brown leather vest laced at the front over a white shirt, brass buckles, leather bracers, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch. Lean and athletic. Style: Fire Emblem-style anime pixel art matching the design sheet, clean dark outlines, cel shading, light from the upper left, about 6 heads tall, 3/4 view FACING RIGHT in every cell.

Quiver marker: do NOT draw the quiver. In every cell, draw one flat pure BLUE (#0000FF) bar on the back exactly where the blue bar is in the draft. Flat colour, no shading, no outline, partly hidden behind the body and cloak.

Hard rules:
- No bow, crossbow, arrows, daggers or other weapons: only the flat sticks described above, 2-3% of the figure height thick (the arrow line thinner), flat single colours with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta, cyan or pure blue anywhere.
- The face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero), shaded like normal skin. Small anime face: dark eye lines, a tiny bit of white, short mouth line. Nothing else may be yellow or gold except the thin cloak trim and the buckles.
- No hair visible: the hood covers it. No pure red anywhere.
- No text, labels, slash effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
If a few cells come out wrong, keep the sheet and fix only those cells in Gemini: attach the sheet and the pose draft and
say "Fix cell <row>,<column> of the first image so its pose and sticks match the same cell of the second image. Keep
everything else."

### Archer - dagger sheet: one dagger + dual daggers on ONE sheet (2026-11-25)
The bow + crossbow sheet is done (`source/archer_m_sheet.png`, the user's ChatGPT result from the 2 x 4 draft), so the
18-cell combined sheet above is not needed. The dagger poses are one 5 x 2 sheet (one ChatGPT task): row 1 = one dagger
(stand | ready | attack | hit) + dual stand; row 2 = dual ready | slash 1 | slash 2 | finish | hit.
Attach, in order: (1) `templates/archer_dagger_template.png`, (2) `refs/archer_dagger_pose_draft.png`,
(3) `source/archer_m_sheet.png` (the finished Archer: copy the character from it). Save as `source/archer_dagger_m_sheet.png`.

```
Use the first attached image as the canvas: a grid of 2 rows x 5 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell (10 figures), feet on that cell's ground line, top of the hood at the dashed line when standing upright, all at the same scale and the same character.

POSES: the second attached image is the pose draft: grey mannequins on the same grid. Copy each mannequin's pose into the same cell: the same stance, legs, body angle, arm positions and the same coloured stick in the same hand at the same angle. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm (darker grey in the draft): its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body. The near hand ALWAYS holds the MAGENTA stick (#FF00FF).
- The FAR arm (lighter grey in the draft): its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body.
- A stick never moves to the other hand.

Cells:
- Row 1, cells 1-4 = ONE DAGGER: STAND (guard, near fist at the hip, stick pointing forward) | READY (crouched, near arm drawn back) | ATTACK (deep lunge, near arm thrust straight forward, stick level) | GET HIT (recoiling back, wincing). Only the near hand holds a stick; the FAR hand is OPEN and EMPTY.
- Row 1, cell 5 and row 2 = TWO DAGGERS: the FAR hand holds a CYAN stick (#00FFFF) as well. STAND (both sticks low) | READY (the far arm raised above the hood, cyan stick angled back) | SLASH 1 (the far arm chopped down in front, cyan stick pointing down toward the front foot) | SLASH 2 (deep lunge, the near arm swung out behind the body at chest height, its magenta stick pointing FORWARD across the waist) | FINISH (the near arm stretched back and up, magenta stick pointing back) | GET HIT (recoiling back, both sticks low).

Character: exactly the archer of the third attached image (same face, same forest-green cloak with the hood up, same brown leather vest, white shirt, bracers, fingerless gloves, trousers, laced boots, belt and pouch, same colours, same size, same pixel-art style). FACING RIGHT in every cell.

Quiver marker: in every cell, the same flat pure BLUE (#0000FF) bar on the back as in the third image, exactly where the blue bar is in the draft. Flat colour, no shading, no outline, partly hidden behind the body and cloak. Do not draw the quiver.

Hard rules:
- No daggers, knives or other weapons: only the flat sticks, 2-3% of the figure height thick, flat single colours with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta, cyan or pure blue anywhere.
- The face is the only bare skin, in shades of pure yellow as in the third image. No hair visible; no pure red anywhere.
- No text, labels, slash effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
If a few cells come out wrong, fix only those in Gemini: attach the sheet and the pose draft and say "Fix cell
<row>,<column> of the first image so its pose and sticks match the same cell of the second image. Keep everything else."

### Archer daggers - FINAL plan (user, 2026-11-25: "the dual weapon use the same pose as soldier, but add quiver or bolt")
Supersedes the 5 x 2 dagger sheet above.
**Dual daggers** = the Soldier's finished dual sheet re-dressed as the Archer by Gemini, same poses, sticks, slash arcs and
smears, plus the blue back marker (it stands for the quiver OR the bolt case - both use the same back slot; the game
shows whichever ammunition is equipped). One Gemini message per sex: attach (1) `source/concepts/soldier_dual_<m|f>_sheet_gemini_smear.png`,
(2) `source/archer_m_sheet.png` (the finished Archer). Save as `source/concepts/archer_dual_<m|f>_sheet_gemini_smear.png`.

```
Edit the first attached image, a sprite sheet of 2 rows x 3 cells on a flat green screen: an armoured soldier in six poses, two of them with a yellow slash arc and a grey motion smear. Turn the soldier into the <SEX> ARCHER of the second attached image and change nothing else.

Change only the character:
- the archer's outfit exactly as in the second image: forest-green hooded cloak with a thin gold trim, HOOD UP over the head with the face open, brown leather vest laced at the front over a white shirt, brass buckles, leather bracers, fingerless brown gloves, brown trousers, laced knee-high boots, a belt with a pouch;
- no helmet, no plate armour, no scarf or tabard, no red ponytail - no hair visible and no red anywhere;
- the archer's lighter, leaner build: <BUILD>;
- add one flat pure BLUE (#0000FF) bar on the back in every cell, like the blue bar in the second image (it marks where the quiver is worn): top end sticking up behind the shoulder on the LEFT side of the picture, slanting down behind the back, partly hidden by the body and cloak; flat colour, no shading, no outline. Do not draw the quiver itself.

Keep exactly as they are:
- the canvas size, the 2 x 3 grid, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position, height and feet of every figure;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle and length, the same flat colours with no shading;
- the yellow slash arcs and grey smears in the top-right and bottom-left cells: same shape, size, position and colours;
- the face painted in shades of pure yellow; the pixel-art style, outlines and shading.

No weapons, no bow, no quiver, no new effects, no shadows, no text. Output the whole sheet at the same size.
```
`<SEX>` / `<BUILD>`: male = "MALE" / "lean and athletic, like the second image"; female = "FEMALE" / "clearly feminine -
narrower shoulders, curved waist and hips, slightly fuller chest, a soft face with larger eyes and a small chin".

**One dagger** = its own 2 x 2 ChatGPT sheet (stand | ready / attack | hit, off-hand open and empty). Attach
(1) `templates/archer_dagger_template.png`, (2) `refs/archer_dagger_pose_draft.png`, (3) `source/archer_m_sheet.png`;
use the "One-handed sheet" prompt above, with "exactly the archer of the third attached image (same face, outfit,
colours, size and style)" as the character line and the quiver marker "the same blue bar as in the third image".

### Archer daggers - ONE sheet, one dagger + the Soldier's dual poses (2026-11-25, user: "combine 1 handed you design and old dual weapon pose")
Supersedes the dagger plans above. 4 x 3 sheet (`EXTRA_SHEETS['archer']['dagger']`): row 1 = one dagger (stand | ready |
attack | hit, mannequins); row 2 = dual stand | ready | slash 1 | slash 2; row 3 = dual finish | hit - rows 2-3 show the
Soldier's finished dual figures, so the Archer copies the exact same poses (and the Soldier's drawn slash arc/smear layer
can be reused). Attach, in order: (1) `templates/archer_dagger_template.png`, (2) `refs/archer_dagger_pose_draft.png`,
(3) `source/archer_m_sheet.png`. Save as `source/archer_dagger_m_sheet.png`; the female = Gemini edit of it.

```
Use the first attached image as the canvas: a grid of 3 rows on flat pure green (#00FF00) - 4 cells in the top and middle rows, 2 wide cells in the bottom row - each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are. Draw ONE full-body character per cell (10 figures), feet on that cell's ground line, top of the hood at the dashed line when standing upright, all at the same scale and the same character.

POSES: the second attached image is the pose sheet. Copy each figure's pose into the same cell: the same stance, legs, body angle, arm positions and the same coloured stick in the same hand at the same angle. The top row shows grey mannequins; the middle and bottom rows show an armoured soldier - copy ONLY its pose, never its armour, helmet, scarf, tabard or red hair. The grey patch on the soldier's waist in the middle row's last cell only marks the hidden torso. Do not invent new poses and do not mirror any figure.

The two arms (check every cell before you finish):
- The NEAR arm: its shoulder is on the LEFT side of the picture and it is drawn IN FRONT of the body (the darker grey arm on the mannequins; on the soldier, the arm whose big shoulder plate covers the chest). The near hand always holds the MAGENTA stick (#FF00FF).
- The FAR arm: its shoulder is on the RIGHT side of the picture, partly hidden BEHIND the body. In the middle and bottom rows it holds the CYAN stick (#00FFFF); in the top row it is OPEN and EMPTY.
- A stick never moves to the other hand. Where the pose sheet shows a hand WITHOUT a stick (the far hand in the middle row's 3rd cell, the near hand in its 4th cell - the weapon is lost in the swing), draw that hand empty too.

Cells: top row = ONE DAGGER: STAND | READY | ATTACK | GET HIT. Middle row = TWO DAGGERS: STAND | READY | SLASH 1 | SLASH 2. Bottom row = TWO DAGGERS: FINISH | GET HIT.

Character: exactly the archer of the third attached image (same face, same forest-green cloak with the hood up, same brown leather vest, white shirt, bracers, fingerless gloves, trousers, laced boots, belt and pouch, same colours, same size, same pixel-art style), FACING RIGHT in every cell.

Quiver marker: in every cell, the same flat pure BLUE (#0000FF) bar on the back as in the third image: top end sticking up behind the near shoulder, slanting down behind the back, partly hidden by the body and cloak. Flat colour, no shading, no outline. Do not draw the quiver.

Hard rules:
- No daggers, knives or other weapons: only the flat sticks, 2-3% of the figure height thick, flat single colours with no shading or outline, sticking out of both sides of the fist where the handle would be, fingers wrapped over them. No other magenta, cyan or pure blue anywhere.
- The face is the only bare skin, in shades of pure yellow as in the third image. No hair visible; no red anywhere.
- No text, labels, slash arcs, effects, motion lines, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
If a few cells come out wrong, fix only those in Gemini: attach the sheet and the pose sheet and say "Fix the cell in
row <r>, position <c> of the first image so its pose and sticks match the same cell of the second image. Keep everything else."

### Archer DOWNED sprite, both sexes (2026-11-25, user: "now work on downed sprite")
Same as the Soldier's: one downed pose per sex for every Archer loadout, no weapon. Attach (1) `templates/archer_downed_template.png`
(`tools/make_archer_downed_template.py`: bottom row = male bow stand from the finished sheet with its stick painted out,
female from the design sheet), (2) `source/soldier_downed_sheet.png` (the Soldier's downed pose, so both classes match).
Save as `source/archer_downed_sheet.png` (`process_downed()` reads `<cls>_downed_sheet.png`).

```
Use the first attached image as the canvas: a grid of 2 rows x 3 cells on flat pure green (#00FF00), each cell with a dark ground line and a dashed head-top line. Keep the canvas size, the grid, the lines and the green exactly as they are, and keep the whole bottom row exactly as it is.

The bottom row shows the same hooded archer, MALE in the bottom-left cell and FEMALE in the bottom-middle cell, standing. Draw each of them DOWNED in the empty cell directly above them:
- top-left cell: the male archer from the bottom-left cell;
- top-middle cell: the female archer from the bottom-middle cell;
- top-right cell: leave empty green.

DOWNED pose: exactly the pose of the kneeling soldiers in the second attached image (copy only the pose, not their armour): collapsed on both knees on the ground line, sitting back on the heels, torso slumped forward, head hanging down so the face is half hidden, both arms hanging limp with the open, empty hands resting on the ground beside the knees. 3/4 view, the body turned toward the right. The hood stays UP.

Same character, same scale: the hood, body and limbs are exactly as big as in the standing figure below (the figure is shorter only because it kneels). Copy the outfit and colours from the figure below: forest-green hooded cloak with a thin gold trim, brown leather vest laced over a white shirt, brass buckles, bracers, fingerless gloves, brown trousers, laced boots, belt and pouch, same pixel-art style. The male lean and athletic, the female clearly feminine, as below.

Colour keys - the SAME for both, like the male figure below (the female reference shows a real face and a quiver: do not copy those two things):
- the face is the only bare skin and is painted in shades of pure yellow;
- do NOT draw the quiver; instead one flat pure BLUE (#0000FF) bar on the back where the quiver is worn, like the male figure below (top end sticking up behind the shoulder, slanting down behind the back, partly hidden by the body and cloak), flat colour, no shading, no outline;
- no hair visible, no red anywhere.

No weapons, no sticks or rods, nothing in the hands. No text, labels, shadows on the ground, effects or background objects. Output one PNG at the canvas's exact size.
```

### Female Archer - Gemini edit of the combined male sheet (2026-11-25, user: "use this as a template to create female version")
Attach (1) `source/archer_m_all_sheet.png` (all 19 male poses), (2) `source/concepts/archer_f_ref.png` (the female Archer
ChatGPT drew as the downed sheet's standing reference: right outfit, yellow face key, blue bar). Save the result as
`source/archer_f_all_sheet.png` (same cell layout, `source/archer_m_all_layout.json`).

```
Edit the first attached image, a sprite sheet of 19 cells on a flat green screen showing the same hooded male archer in 19 poses (the last row has 3 wider cells). Turn him into the FEMALE archer of the second attached image, in every cell, and change nothing else.

Change only the body and face: clearly feminine, like the second image - a smaller, slimmer frame, narrower shoulders, a curved waist and hips, a slightly fuller chest under the vest, slimmer arms and legs, and a soft feminine face with larger eyes and a small chin. Her head and hood are NOT bigger than his; she is about as tall as him, so the top of her hood stays near each cell's dashed line.

Keep exactly as they are:
- the canvas size, the grid of cells, the flat pure green background, the dark ground line and the dashed line in each cell;
- the position and feet of every figure, standing (or kneeling) on the same ground lines;
- every pose: the same stance, legs, body angle and arm positions in each cell, nothing mirrored;
- the flat magenta and cyan sticks in the hands: the same stick in the same hand, at the same angle and length, the same flat colours with no shading; open empty hands stay open and empty;
- the flat pure blue bar on the back in every cell;
- the outfit and colours: forest-green hood (UP) and cloak with the thin gold trim, brown leather vest laced over a white shirt, brass buckles, bracers, fingerless gloves, brown trousers, laced boots, belt and pouch;
- the face painted in shades of pure yellow, as in both images; no hair outside the hood, no red anywhere;
- the pixel-art style, outlines and shading.

Do not add weapons, a quiver, effects, shadows, text or anything else. Output the whole sheet at the same size.
```
If a cell changes pose or a stick swaps hands: attach Gemini's result together with the male sheet and say "Fix the cell in
row <r>, position <c> of the first image so its pose and sticks match the same cell of the second image. Keep everything else."
If Gemini returns the sheet smaller, that is fine (the build rescales); if it crops or squashes it, do the sheet in two
halves (rows 1-3, rows 4-5) by cropping the male sheet first. (2026-11-25: no slash arcs on the sheet - they are their own layer; slash 2's near
arm is raised to the finish angle, hand empty.)

### Acolyte - own priest poses from mannequin drafts, one sheet per stance (2026-11-26)
Supersedes the Soldier-pose Acolyte sheets (removed; the user: "the pose is different from soldier, check weapon access
first"). From the weapon sheet + class table, the user picked: one-handed + round shield, one-handed without shield
(off-hand open), two-handed staff (quarterstaff / spear), reach (longspear), crossbow; each with weapon frames
(ready + attack) and spell/cantrip frames (channel + cast) where the held weapon is raised as the holy focus. No dual
wield (dual wield is for Soldier, Archer, Warrior, Rogue for now), no sling/thrown poses. Calmer priest stances.
Drafts: `tools/acolyte_pose_draft.py` -> `refs/acolyte_<shield|1h|staff|reach|crossbow>_pose_draft.png` (2 x 3 cells:
stand | ready | attack / hit | channel | cast; crossbow: stand | aim | release / hit | channel | cast).
Concept: `source/concepts/acolyte_design.png`. Male first, one Gemini message per draft (5), attachments: (1) the draft,
(2) the concept. Save as `source/acolyte_<stance>_m_sheet.png`. Female = a Gemini edit of each finished male sheet
(the "Female Soldier" prompt pattern). Downed comes after, like the Archer's.

```
Edit the first attached image: a pose sheet of 2 rows x 3 cells on a flat pure green (#00FF00) screen, each cell with a grey mannequin, a dark ground line and a dashed head-top line. Replace every mannequin with the MALE ACOLYTE of the second attached image (design sheet), in exactly the mannequin's pose, and change nothing else.

POSES: copy each mannequin exactly: the same stance, legs, body angle and arm positions, and the same magenta stick in the same hand at the same angle and length. Do not invent new poses and do not mirror any figure.
- The NEAR arm (darker grey) has its shoulder on the LEFT side of the picture and is drawn IN FRONT of the body; it holds the MAGENTA stick (#FF00FF). Where a mannequin holds the stick in both fists, both hands grip the same stick.
- The FAR arm (lighter grey) has its shoulder on the RIGHT side of the picture, partly hidden BEHIND the body. An open grey hand stays OPEN and EMPTY.
<SHIELD>
The ACOLYTE, exactly as in the second image: white hooded robe with gold trim, HOOD UP with the small gold ornament on top and the face open, short white capelet with a gold cross on the chest, teal undercoat and sleeves with teal cuffs, a teal stole hanging down the front with gold fleurs-de-lis, layered white robe skirt to below the knees, brown belt with a gold buckle and a pouch, brown fingerless gloves, brown boots. A broad, sturdy man, about 6 heads tall, feet on each cell's ground line, top of the hood at the dashed line when standing upright, the same size in every cell. Style: Fire Emblem-style anime pixel art matching the second image, clean dark outlines, cel shading, light from the upper left, 3/4 view FACING RIGHT in every cell.

Colour keys:
- the face is the only bare skin: paint it in shades of pure yellow (red = green, blue near zero), shaded like normal skin; small anime face;
- the hair that shows inside the hood (fringe, locks beside the face) is painted ONLY in shades of pure red (#FF0000 family: very dark red outline and shadows, mid red, bright red highlights), no black outline; no hair outside the hood;
- the gold trim, cross and fleurs-de-lis stay a warm orange-gold, clearly different from the pure yellow of the face; no other pure red, magenta or cyan anywhere.

No weapons (only the flat magenta sticks, flat colour, no shading, fingers wrapped over them), no effects, glow, shadows on the ground or text. Keep the canvas size, the grid, the green and the lines exactly. Output the whole sheet at the same size.
```
`<SHIELD>` on the shield sheet: "- The far forearm carries the acolyte's ROUND shield where the grey disc is, in front of the
body, the same size and angle: white face with a gold cross, a thick gold rim and a thin teal ring inside the rim, no other
symbols." On the other sheets delete the line.
If a cell changes pose or a stick swaps hands: attach the result together with the draft and say "Fix the cell in row <r>,
position <c> of the first image so its pose and stick match the same cell of the second image. Keep everything else."
