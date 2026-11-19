# Portrait module (new art, 2026-11-19)

Hero portraits, 200×200, assembled from layered parts and finished in code.

- `parts/`: the new portrait art from `art_source/new_art/portraits/` (branch `art-source`).
  Per sex (`m_`, `f_`): head skin map, 6 class outfits (`body_<class>_fixed`, plus `_skin` where
  skin shows), 12 eye styles (`eyes_<style>_fixed` + `_iris`), 6 noses (`nose_<style>`, skin map), 6 expressions (`brows_<expr>` +
  `mouth_<expr>`), 12 hairstyles (`hair_<style>`).
- `library.json`: the lists above. `palettes.json`: 5 skin, 10 hair, 6 eye colour ramps.
- `hero_appearance.gd` (`HeroAppearance`): one look = body, class outfit, skin, expression,
  eye style, nose, hairstyle, hair colour, eye colour. `roll()`, `to_dict()` / `from_dict()`.
- `portrait_finish.gd` (`PortraitFinish`): stacks the layers (head skin → nose → body skin → body →
  eyes → iris → brows → mouth → hair) and runs the finish passes. **GDScript port of
  `art_source/new_art/portraits/finish.py` `compose()`; keep the two in step.** Finished portraits
  are cached per look; `texture_async()` builds on a worker thread.
- `hero_portrait.gd` (`HeroPortrait`): a Control that shows a look.

Check against the art pipeline: `tests/portrait_finish_check.gd` writes portraits and their looks;
compare them with `finish.py compose()` (latest check: at most 56 of 40,000 pixels differ per
portrait, all single outline pixels where two neighbours are equally near).

The Legacy (Canva) portrait parts were removed from the game on 2026-11-19; they remain on the
`art-source` branch for reference.
