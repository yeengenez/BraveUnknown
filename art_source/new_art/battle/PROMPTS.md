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

### Soldier (v2, from the user's concept sheet - self-contained, do NOT paste the common prompt)
Attach `templates/soldier_template.png` (4 rows x 3 cells) and the concept sheet
`source/concepts/soldier_concept.png`, replace `<SEX>`, then paste:

```
Use the first attached image as the canvas: a grid of 4 rows x 3 cells on flat pure green (#00FF00), each cell with a dark-green ground line and a dashed head-top line. Keep the canvas size, the grid and the green exactly as they are. Draw ONE full-body character per cell, feet on that cell's ground line, top of the head at the dashed line when standing upright, all 12 figures at the same scale and the same character.

The second attached image is the concept sheet for this character. Use it for the OUTFIT (silver plate armour, blue scarf, blue tabard with a light trim, brown leather belts and pouches) and for the STANCES only. Ignore its helmet, shield, weapons, cape, slash effects, text and background.

Character: <SEX> Soldier. Style: Fire Emblem-style anime pixel art matching the concept: clean dark outlines, cel shading, light from the upper left, natural anime proportions about 6-7 heads tall, 3/4 view FACING RIGHT in every cell.

Rows, top to bottom; cells left to right = STAND | ATTACK | GET HIT:
1. One-handed + shield (Roman stance from the concept): STAND = low guard, left fist forward at chest height (where the shield grip would be) with the cyan rod upright in front of the chest; right fist raised by the shoulder with the magenta rod pointing up like a short sword. ATTACK = deep lunge forward, left fist stays forward at chest height with the cyan rod upright (shield braced in front of the chest), right arm thrusting forward past it at waist-to-chest height, magenta rod level and pointing forward. GET HIT = pushed back, knees bent, shoulders hunched behind the left fist, wincing, both rods still held.
2. Dual weapons: STAND = wide stance, both fists low and forward, magenta rod in the right fist and cyan rod in the left, both pointing forward and slightly down. ATTACK = lunging cross slash: right arm swept forward at shoulder height with the magenta rod level, left arm pulled back low with the cyan rod. GET HIT = recoiling back, wincing, arms pulled in, both rods still held.
3. Two-handed: both fists together on ONE magenta rod (one fist above the other). STAND = rod held upright in front of the body, fists at the waist. ATTACK = heavy downward strike finishing low in front, rod angled down and forward, deep lunge. GET HIT = recoiling back, rod pulled up across the body.
4. Spear: ONE long magenta pole, as long as the body is tall, held at hip height through both fists, front fist forward, back fist at the rear hip. STAND = spear guard, pole level and pointing forward. ATTACK = full forward thrust, deep lunge, pole level. GET HIT = recoiling back, pole still held, tip lifted.

Hard rules:
- No weapons, shields, helmets or capes. Each fist grips a flat, straight guide rod instead, 2-3% of the figure height thick, sticking out of both sides of the fist where the handle would be, fingers wrapped over it: pure magenta (#FF00FF) in the character's RIGHT hand, pure cyan (#00FFFF) in the LEFT hand. Flat single colours, no shading or outline. No other magenta or cyan anywhere.
- Bald head: no hair, no helmet, no hood. Ears visible. Small anime face: dark eye lines, a tiny bit of white, short mouth line.
- All bare skin (face, ears, neck, hands) in shades of pure yellow (red = green, blue near zero): dark yellow for shadows, bright yellow for highlights, shaded like normal skin. Nothing else may be yellow or gold: buckles, trims and studs must be silver or dark bronze/brown.
- No text, labels, slash effects, motion lines, dust, shadows on the ground or background objects.
- Output one PNG at the canvas's exact size.
```
Male: broad, bulky frame (as in the concept). Female: add to the prompt "Female: clearly feminine - smaller frame,
narrower shoulders, curved waist and hips, visible chest under the armour, slimmer limbs, smaller pauldrons, same
armour style."

The first Soldier sheets (3 rows, before the concept) are kept in `source/soldier_v1/`.

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

## Fix: shield arm in the one-handed attack (Soldier, Acolyte)
Only the classes that can use a shield need this (Soldier, Acolyte; Warrior, Archer, Mage and Rogue have no shield).
Attach the sheet ChatGPT made and send:
> Edit the attached sheet. Change ONLY the top-middle cell (one-handed attack); every other cell, the canvas, the
> grid and the green must stay pixel-identical. In that cell keep the same character, outfit, deep lunge and legs, and
> change the arms: the LEFT forearm is raised and braced across the front of the chest, left fist at chest height in
> front of the body, holding the cyan rod upright (as if holding a shield up in front of the chest). The RIGHT arm stays
> fully extended forward at shoulder height, the magenta rod level and pointing straight forward, not downward. Rods stay
> flat pure #FF00FF (right) and #00FFFF (left), sticking out of both sides of the fists. Bare skin stays yellow.

## Shield strike (Soldier 1h attack, user reference 2026-11-20)
Reference: `source/concepts/shield_strike_ref.png` (pose only). Attach the Soldier sheet + that reference, then:
```
Edit the first attached sheet. Change ONLY the top-middle cell (one-handed attack); every other cell, the canvas, the grid and the green must stay pixel-identical. Copy the striking pose of the second image (pose only - ignore its outfit, hair, shield, sword, slash effect, sparks, dummy and background): deep forward lunge, upper body hunched forward, head ducked down behind the left fist. The LEFT elbow is bent and the left fist is held close in front of the face/upper chest, the cyan rod upright and leaning a little forward (where the shield is held up in front of the face). The RIGHT arm has just swung a diagonal downward slash: right fist low in front of the hips, just below the left fist, magenta rod pointing forward and down at about 30-40 degrees, as in the reference. Same character, outfit, scale and ground line. Rods stay flat pure #FF00FF (right) and #00FFFF (left), sticking out of both sides of the fists. Bare skin stays yellow. Bald head. No shield, no weapon, no effects.
```

## If ChatGPT struggles
- Too many figures (Soldier, Acolyte, Warrior have 9): ask for **one row at a time** on the same template ("draw only
  row 1, leave the other cells empty green").
- Rods missing or shaded: reply "the guide rods must be flat pure #FF00FF (right hand) and #00FFFF (left hand), straight,
  sticking out of both ends of the fist".
- Hair or weapons appear: reply "remove all hair and weapons, keep everything else identical".
