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

- `aseprite/` - hand editing on your PC. `build_portrait_parts.lua` makes, per sex, `<sex>_hair.aseprite`,
  `<sex>_eyes.aseprite` and `<sex>_bodies.aseprite` (one tagged frame per style, the base head underneath as a locked
  reference). `export_portrait_parts.lua` writes every edited layer back to its PNG. See `aseprite/README.md`.
- `source/eyes_<m|f>_sheet.png` + `process_eyes.py m|f` - 12 eye pairs per sex (ChatGPT drew them on the eye
  templates). Each head is aligned to the base head by silhouette, every pixel is classified (white / blue iris /
  dark line), and each canvas pixel takes the class covering most of it, so the eyes come out as clean pixel art.
  Output per style: `<sex>_eyes_<style>_fixed.png` (white #FAF8F6 and line #1E161A, never tinted) and
  `<sex>_eyes_<style>_iris.png` (grayscale, tinted with the 6 eye ramps). Stray pixels removed, far eye clipped to the
  face outline. `preview_eyes_<sex>.png`, `eyes_fit_<sex>.json`. `clean_eye_creases.py` then removes eyelid-crease
  lines above the male eyes (they read as a second pair of eyebrows); female eyes keep their separate lash strokes.
  Male: neutral_almond, sharp_narrow, heavy_lidded, round_youthful, hooded_stern, tired_droopy, upturned_fierce,
  downturned_gentle, deep_set_brooding, wide_alert, half_closed_calm, narrowed_squint.
  Female: neutral_almond, large_round, cat_eye, doe, sleepy, sharp_narrow, long_lashed_soft, hooded, wide_bright,
  gentle_smiling, fierce, half_lidded_mysterious.

- `source/body_<m|f>_sheet.png` + `process_bodies.py m|f` - class outfits as portrait busts (ChatGPT drew them under the
  base head on the body templates; bare skin in cyan). Output `<sex>_body_<id>_fixed.png` (full colour) and, where skin
  shows, `<sex>_body_<id>_skin.png` (grayscale, tinted with the skin ramp). Ids: soldier, archer, cleric (= Acolyte),
  mage, warrior, rogue. The drawn head is removed by its grey colour, so collars and scarves over the neck stay whole.
  Layer order for the new art: head skin -> body skin -> body fixed -> eyes -> hair. `preview_portraits.png` shows
  full assembled portraits (head, body, eyes, hair, varied skin/hair/eye colours).

- `source/brows_<m|f>_sheet.png` + `process_brows.py m|f` - eyebrows for 6 expressions (neutral, smile, stern, grin,
  sleepy, worried), drawn in red on `templates/face_template_<sex>.png`. Output `<sex>_brows_<expr>.png`: grayscale,
  **tinted with the hair ramp**. Aligned to the base head, then shifted so the template eyes sit on the base eyes;
  far brow clipped to the face. Layer order: ... eyes -> brows -> hair. `preview_brows_<sex>.png`.

- `source/mouth_<m|f>_sheet.png` + `process_mouths.py m|f` - mouths for the same 6 expressions, placed like the brows.
  Output `<sex>_mouth_<expr>.png`: fixed colours (line #1E161A, teeth #FAF8F6, inside #6E282A), never tinted.
  `source/mouth_alt_sheet.png` is an unused alternative male sheet. `preview_mouths.png`.
- `preview_full.py` -> `preview_full.png`: complete portraits from every layer with random looks.
  Full layer order: head skin -> body skin -> body -> eyes -> iris -> brows -> mouth -> hair.

Not yet in the game: all portrait layers exist now, but the game's `library.json` and `HeroPortrait` still use the
legacy parts. Switching needs the new layer names and order (separate eyes, brows tinted by hair, mouths, 6
expressions, 12 hairstyles per sex, new head placement).
