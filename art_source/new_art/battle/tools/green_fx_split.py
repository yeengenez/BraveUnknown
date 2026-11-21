"""Split drawn effects (yellow slash arc + grey weapon smear, drawn by the user with Gemini) off a dual sheet on green.

Writes the sheet without the effects (source/soldier_dual_<sex>_sheet.png) and the effects as a soft-alpha RGBA layer
of the same size (source/soldier_dual_<sex>_fx.png), which process_battle.py draws over the slash frames. The effect's
own colours are recovered from the green it was blended with (effect colours are grey/white/yellow, so their green
equals their red). The body hidden under the waist sweep (cell 4) is filled from the surrounding armour; the effect
layer is drawn over it anyway.
Usage: python3 tools/green_fx_split.py <gemini sheet> <sex>
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# cells with effects: (row, col) -> body area hidden under the effect (cell px, 512-cell scale) or None
FX_CELLS = {(0, 2): (None, 512), (1, 0): ([(225, 248), (320, 243), (345, 268), (352, 300), (340, 312), (190, 312), (192, 285)], 316)}
# (hidden body polygon, lowest row the effect reaches - keeps the tabard's gold trim out of the effect)
FACE = (235, 145, 305, 215)            # helmet opening (yellow face key) - never an effect


def split_cell(c, hide_poly, ymax, k):
    r, g, b = [c[..., i].astype(float) for i in range(3)]
    H, W = r.shape
    face = np.zeros((H, W), bool); x0, y0, x1, y1 = [round(v * k) for v in FACE]; face[y0:y1, x0:x1] = True
    yellow = (r > 200) & (g > 0.75 * r) & (b < 0.3 * r)
    orange = (r - g > 12) & (b < 0.3 * g) & (r > 150)                 # orange glow of the arc (armour pink has blue)
    grey = (np.abs(r - b) < 20) & (g >= r - 2) & (r > 130)
    seed = (yellow | grey) & ~face
    lab, n = ndi.label(seed, np.ones((3, 3))); sz = ndi.sum(seed, lab, range(1, n + 1))
    seed = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 150 * k * k])
    pure_green = (g > 235) & (r < 25) & (b < 25)
    body_col = ((r - g > 12) & ~orange) | (b - r > 25) | (((r + g + b) / 3 < 70) & (g < r + 30))
    low = np.zeros((H, W), bool); low[round(ymax * k):] = True
    cand = ~body_col & ~face & ~pure_green & ~low
    seed &= ~low
    E = seed.copy()
    for _ in range(round(30 * k)):
        nE = E | (ndi.binary_dilation(E) & cand)
        if (nE == E).all(): break
        E = nE
    # loose bits left on the green (thin wisps of the effect) also belong to the effect
    green = (g - r > 60) & (g - b > 60)
    rest = ~green & ~E; rest[-round(40 * k):] = False                  # (not the ground line)
    lab, n = ndi.label(rest, np.ones((3, 3))); sz = ndi.sum(rest, lab, range(1, n + 1))
    hairk = (r > 45) & (g < 0.3 * r) & (b < 0.3 * r)                  # red hair key
    rodk = ((r > 170) & (b > 170) & (g < 120)) | ((g > 170) & (b > 170) & (r < 120))
    for i in range(n):                   # the sweep can cut the figure apart: keep hair, rods and big body pieces
        cm = lab == i + 1
        if sz[i] > 8000 * k * k or hairk[cm].mean() > 0.3 or rodk[cm].any(): continue
        E |= cm & ~face & ~low & ((r + g + b) / 3 > 60)      # (never the dark ground line)
    a = np.clip(np.where(g > r, 1 - (g - r) / 255, 1.0), 0, 1) * E
    col = np.dstack([r, np.where(g > r, r, g), b]) / np.maximum(a, 1e-3)[..., None]
    fx = np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8); fx[a < 0.02] = 0
    out = c.copy(); out[E] = (0, 255, 0)
    if hide_poly:
        pm = Image.new('L', (W, H), 0); ImageDraw.Draw(pm).polygon([(x * k, y * k) for x, y in hide_poly], fill=1)
        hid = (np.asarray(pm) > 0) & E
        body = ~((g - r > 60) & (g - b > 60)) & ~E
        iy, ix = ndi.distance_transform_edt(~body, return_distances=False, return_indices=True)
        fill = c[iy, ix].astype(np.float32)
        from PIL import ImageFilter
        sm = np.asarray(Image.fromarray(fill.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * k)))
        out[hid] = sm[hid]
    return out, fx


def main(src, sex):
    a = np.asarray(Image.open(src).convert('RGB')).copy()
    H, W = a.shape[:2]; fxs = np.zeros((H, W, 4), np.uint8)
    k = (W / 3) / 512
    for (row, col), (poly, ymax) in FX_CELLS.items():
        y0, y1, x0, x1 = round(row * H / 2), round((row + 1) * H / 2), round(col * W / 3), round((col + 1) * W / 3)
        out, fx = split_cell(a[y0:y1, x0:x1], poly, ymax, k)
        a[y0:y1, x0:x1] = out; fxs[y0:y1, x0:x1] = fx
    Image.fromarray(a).save(os.path.join(HERE, 'source', f'soldier_dual_{sex}_sheet.png'))
    Image.fromarray(fxs).save(os.path.join(HERE, 'source', f'soldier_dual_{sex}_fx.png'))
    return a, fxs


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
