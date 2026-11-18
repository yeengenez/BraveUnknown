# New art (replaces the Legacy Canva art)

## portraits/
- `source/heads_sheet.png` - base heads from ChatGPT (2026-11-18): bald, no face, grayscale, male left, female right.
- `process_heads.py` - cuts each head out of the glow background and writes the game layers.
- `m_head_skin.png`, `f_head_skin.png` - 200x200 **skin value maps** (grayscale, the game tints them with the
  5 skin ramps in `portraits/palettes.json`). Same convention as the legacy `*_skin.png` parts: outline kept as the
  darkest values, mid skin ~204, skull top y=20, chin y~111, centred x~99, so they sit on the existing bodies.
  Both heads use one scale (set by the male head), so the female head is slightly smaller.
- `preview_heads.png` - both heads in all 5 skin tones, and over the legacy Soldier bust.

Not yet in the game: the faces (eyes, brows, mouth per expression) and hair still have to be drawn for these heads.
