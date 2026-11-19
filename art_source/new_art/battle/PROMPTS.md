# ChatGPT (GPT Go) prompts: battle sprites in the new art style

One image per **class and sex** (12 images). For each: start a message, attach
1. `templates/<class>_template.png` (the canvas to draw on), and
2. `refs/<class>_<sex>_ref.png` (outfit from the new portrait + the poses to follow),

then paste the **common prompt** followed by the **class block** (replace `<SEX>` with `male` or `female`).

Rules carried over from the design doc: facing right, ~6-7 heads tall, no weapons ever drawn by AI (weapons, shields,
bows and arrows are drawn in code at the guide rods), **1h weapon always in the right hand**, magenta rod = right hand,
cyan rod = left hand, one frame per state (stand / attack / hit; bow: stand / nock / attack = release / hit), bald
heads (hair is a separate layer matched to the portrait). New for the new art: bare skin in **shades of pure yellow**
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

### Soldier
> Character: **<SEX> Soldier** (heavy armour, from the portrait). Rows, top to bottom, cells left to right =
> stand | attack | hit:
> 1. **One-handed:** stand = right fist raised by the shoulder (magenta rod pointing up like a sword), left fist forward
>    at chest height (cyan rod upright like a shield grip). Attack = deep lunge forward, right arm fully extended at
>    shoulder height with the magenta rod level and pointing forward, left forearm braced across the front of the chest
>    with the cyan rod upright. Hit = recoiling back, wincing, knees bent, both fists still on their rods.
> 2. **Two-handed:** both fists together on ONE magenta rod (one fist above the other, like a great axe handle). Stand
>    = guard, rod angled up and forward. Attack = heavy forward chop, rod swung down and forward. Hit = recoil, rod pulled up.
> 3. **Reach:** ONE long magenta pole (as long as the body is tall) held at hip height through both fists, front fist
>    forward, back fist at the rear hip. Stand = spear guard. Attack = full forward thrust, deep lunge. Hit = recoil,
>    pole still held.
> Male: broad, bulky frame. Female: clearly feminine (smaller frame, narrower shoulders, curved waist and hips, visible
> chest under the armour, slimmer limbs, smaller pauldrons), same armour style.

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
> No quiver (it is a separate layer later). Female: clearly feminine, slightly fuller chest.

### Acolyte
> Character: **<SEX> Acolyte** (cleric robes with a single centred cross, never two crosses, from the portrait; hood
> down). Rows, top to bottom, cells = stand | attack | hit:
> 1. **One-handed (mace + shield):** same as a soldier's: stand = right fist raised (magenta rod up), left fist forward
>    (cyan rod upright). Attack = deep lunge, right arm extended forward with the magenta rod level, left forearm braced
>    across the chest with the cyan rod upright. Hit = recoil, wince, rods still held.
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

## If ChatGPT struggles
- Too many figures (Soldier, Acolyte, Warrior have 9): ask for **one row at a time** on the same template ("draw only
  row 1, leave the other cells empty green").
- Rods missing or shaded: reply "the guide rods must be flat pure #FF00FF (right hand) and #00FFFF (left hand), straight,
  sticking out of both ends of the fist".
- Hair or weapons appear: reply "remove all hair and weapons, keep everything else identical".
