# New art (replaces the Legacy Canva art)

## portraits/
- `source/heads_sheet.png` - base heads from ChatGPT (2026-11-18): bald, no face, grayscale, male left, female right.
- `process_heads.py` - cuts each head out of the glow background and writes the game layers.
- `m_head_skin.png`, `f_head_skin.png` - 200x200 **skin value maps** (grayscale, the game tints them with the
  5 skin ramps in `portraits/palettes.json`). Same convention as the legacy `*_skin.png` parts: outline kept as the
  darkest values, mid skin ~204, skull top y=34, chin y~125, centred x~99 (14 px lower than the legacy heads so tall hair fits inside the canvas; new bodies must use this placement).
  Both heads use one scale (set by the male head), so the female head is slightly smaller.
- `preview_heads.png` - both heads in all 5 skin tones, and over the legacy Soldier bust.

- `source/hair_m_sheet.png` + `process_hair.py m` - 12 male hairstyles (ChatGPT sheet: grayscale hair on a green
  mannequin). Each style is cut out, the mannequin and its outline removed, scaled and placed on `m_head_skin.png`
  by matching the mannequin's ear, face front and chin, then refined per style with a small affine fit (scale x/y,
  rotation, shift; `hair_fit_m.json`) so the mannequin lies on the base head and no bald skull shows past the hair.
  Then each style is re-cut around the base head's own ear (polygon `EAR` in the script, traced on the head): the ear
  sits in front of the hair unless the style covers it, small skull gaps are filled with the nearest hair, and a
  1-px dark line is drawn where hair meets skin. For the styles in `FILL_BALD` (user's list: sidepart, spiky,
  crewcut, slicked, shaggy, ponytail, long, topknot, knight_cut) all bald scalp above the hairline `FACE` and
  behind the ear is filled with the nearest hair. Output `m_hair_<style>.png`: 200x200 **hair value maps**
  (tinted with the 10 hair ramps). Styles: messy, sidepart, spiky, crewcut, slicked, shaggy, ponytail, long
  (the game's existing 8) + topknot, braided_mohawk, wild_mane, knight_cut (new).
  `preview_hair_m.png`: each style tinted on the base head, then the raw value maps.
- `source/hair_f_sheet.png` + `process_hair.py f` - 12 female hairstyles, same processing (all 12 get the bald-scalp
  fill): long, ponytail, bob, braids, wavy, pixie, bun (the game's existing 7) + crown_braid, side_braid, twin_buns,
  curly_mane, warrior_halfup (new). `preview_hair_f.png`, `hair_fit_f.json`.
- White shine streaks inside the hair stay hair; only the white background (large, or touching the mannequin) is cut.

- `aseprite/` - for hand touch-ups on your PC: `build_head_hair.lua` makes `m_head_hair.aseprite` (one frame per
  hairstyle, tagged; layers `head` + `hair`), `export_head_hair.lua` writes the edited layers back to the PNGs.

Not yet in the game: the faces (eyes, brows, mouth per expression) and hair still have to be drawn for these heads.
