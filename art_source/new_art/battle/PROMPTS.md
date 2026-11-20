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

### Soldier (v5, 2026-11-20 - self-contained, do NOT paste the common prompt)
v5 = 4 cells per row (user, 2026-11-20): STAND | READY | ATTACK | GET HIT, and the dual row STAND | ATTACK 1 (main
hand) | ATTACK 2 (off-hand) | GET HIT. Otherwise as v4 = dual row with fixed hands (see the hand rule below) and a long-hair piece in a
red key under the helmet for both sexes (shown only for long portrait hairstyles, `hair_length.json`).
Attach, in this order: (1) `templates/soldier_template.png`, (2) `source/concepts/soldier_outfit_ref.png` (the final design cropped to the outfit only: its animation frames had the dual
weapons in the wrong hands, so they are left out),
(3) `refs/soldier_shield_ref.png`. Replace `<SEX>`, add the male or female line, one run per sex.

```
Use the first attached image as the canvas: a grid of 4 rows x 4 cells on flat pure green (#00FF00), each cell with a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the helmet at the dashed line when standing upright, all 16 figures at the same scale and the same character.

Character: <SEX> Soldier, exactly as in the second attached image (outfit reference only - it shows no poses): Standard plain BARBUTE helm (open face, no crest, no gold, no emblem), simple silver plate armour (rounded pauldrons, plain cuirass, segmented tassets), blue scarf, blue tabard with a light trim, brown leather belt and gloves, steel greaves. Ignore its text labels. Style: Fire Emblem-style anime pixel art matching that sheet: clean dark outlines, cel shading, light from the upper left, natural anime proportions about 6 heads tall including the helmet, 3/4 view FACING RIGHT in every cell, body turned to the right.

Rows, top to bottom. Rows 1, 3 and 4: cells left to right = STAND | READY | ATTACK | GET HIT, where READY is the wind-up a moment before the attack. Row 2: STAND | ATTACK 1 | ATTACK 2 | GET HIT.
1. Sword + SQUARE shield (the third attached image shows STAND, ATTACK and GET HIT - copy those poses only): the LEFT arm carries the Soldier's own large SQUARE shield in every cell of this row: an upright rectangle with slightly rounded corners, from the shoulder to mid-thigh, as wide as the torso, dark navy-blue face with a silver/white cross in relief, a silver steel rim with rivets - no gold or yellow on it. The left fist is hidden behind the shield (no cyan rod in this row). STAND = guard: shield held upright in front of the torso, covering it; right fist raised beside the shoulder with the magenta rod pointing up (sword raised). READY = wind-up: shield pulled in tight in front of the chest, body coiled, weight on the back foot, the right arm drawn back behind the shoulder with the magenta rod angled back. ATTACK = controlled horizontal slash: deep lunge forward, the right arm sweeps across IN FRONT of the body at waist height, magenta rod pointing forward and slightly down; the shield opens slightly to the side (still on the left arm, turned a little outward) so the sword arm passes in front of it. GET HIT = grounded recoil: feet planted, knees bent, braced behind the shield, the shield tilted up and forward to absorb the blow, head knocked back and wincing, right fist low by the hip holding the magenta rod pointing down.
2. Dual weapons (no shield): the same side-on stance as the shield row - the LEFT arm is the lead arm in front (on the right-hand side of the picture, where the shield arm is in row 1) and the RIGHT arm is the rear arm (its shoulder on the left side of the picture). STAND = left (lead) hand forward at waist height holding the cyan rod pointing forward and slightly down; right (rear) hand back and low holding the magenta rod. ATTACK 1 (main hand) = the RIGHT (rear) arm swings forward ACROSS the front of the body and thrusts out at shoulder height holding the magenta rod level and pointing forward; the left arm pulls back and down with the cyan rod. ATTACK 2 (off-hand) = the LEFT (lead) arm thrusts fully forward at shoulder height holding the cyan rod level; the right arm pulls back low with the magenta rod. GET HIT = recoiling back, wincing, left hand in front with the cyan rod, right hand back with the magenta rod.
3. Two-handed (no shield): both fists together on ONE magenta rod (one fist above the other). STAND = rod held upright in front of the body, fists at the waist. READY = wind-up: rod raised high over the right shoulder, both fists together above the head, body leaning back, weight on the back foot. ATTACK = heavy downward strike finishing low in front, rod angled down and forward, deep lunge. GET HIT = recoiling back, rod pulled up across the body.
4. Spear (no shield): ONE long magenta pole, as long as the body is tall, held at hip height through both fists, front fist forward, back fist at the rear hip. STAND = spear guard, pole level and pointing forward. READY = coiled: pole drawn back along the hip, back fist far behind the body, front fist close to the chest, crouched, weight on the back foot. ATTACK = full forward thrust, deep lunge, pole level. GET HIT = recoiling back, pole still held, tip lifted.

Hair under the helmet: in EVERY cell, a ponytail of long hair comes out from under the back of the helmet and hangs down behind the neck, following each pose (swinging back in the lunges, flicking up in the get-hit poses). It always stays BEHIND the body: it never covers the armour, scarf, arms or face, so the figure looks complete without it. Paint the hair entirely in shades of pure red (#FF0000 family: very dark red for the outline and shadows, mid red, bright red for highlights), shaded like hair - no black outline on it. No other hair visible.

Hard rules:
- No weapons and no capes. The square shield appears ONLY in row 1. Each fist that holds a weapon grips a flat, straight guide rod instead, 2-3% of the figure height thick, sticking out of both sides of the fist where the handle would be, fingers wrapped over it: pure magenta (#FF00FF) in the character's RIGHT hand, pure cyan (#00FFFF) in the LEFT hand. Flat single colours, no shading or outline. No other magenta or cyan anywhere.
- Hands (same in every cell): the character's LEFT arm is the lead arm, on the right-hand side of the picture (the shield arm in row 1); the RIGHT arm is the rear arm, its shoulder on the left side of the picture. Magenta is ALWAYS in the right (rear-arm) hand, cyan ALWAYS in the left (lead-arm) hand - a rod never changes hands between cells. When the right arm attacks, it swings forward across the front of the body.
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
`source/soldier_v4/`; v5 sheets go to `source/soldier_<sex>_sheet.png`. The current sprites stay until then.

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
