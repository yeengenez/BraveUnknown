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
