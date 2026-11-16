# Portrait pipeline

How `res://portraits/parts/` was made. You only need this to add or redo portrait parts.

1. `raw/` holds the generated source images (Canva, pixel-art style A). Every part was generated as an
   edit of one bald base head per gender (`raw/m/base.png`, `raw/f/base.png`), so they line up.
   Hair was drawn in bright pink so it can be cut out cleanly; `raw/hair/unused/` are early shared
   styles replaced by per-gender sets.
2. `build_library.py` registers each image to its base, cuts out the changed part and writes the
   layers: fixed colour parts, plus grayscale value maps for skin, iris and hair. Output goes to
   `library/` (the game copy is `res://portraits/parts/`).
3. `palettes.json` holds the skin, hair and eye colour ramps (also copied to `res://portraits/`).
4. `compose.py` is the reference compositor and random roller; it writes `contact_sheet.png`.

Run from this folder with Python 3, Pillow, OpenCV, NumPy and SciPy:

```
python3 build_library.py
python3 compose.py
```

`previews/` has the review sheets, including the three style samples the pixel-art style was chosen from.
