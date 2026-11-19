"""Remove leftover template-head outline strokes from the outfit layers (<sex>_body_<class>_fixed.png).

The body sheets were drawn on a template that had a head; process_bodies.py removed most of its outline, but short
dark strokes stayed on the chin / throat (they read as a goatee or a scratch on the neck). These PNGs also hold the
user's Aseprite touch-ups, so this edits them in place instead of re-cutting the sheets.

Rule, applied only inside the base head mask (face + neck): a dark pixel (outline colour) that touches bare skin and
has no real outfit area (a lighter patch of 20+ px) in its 3x3 neighbourhood is a stroke, not the edge of a collar - it goes, repeatedly, so a stroke is eaten back
to where it meets real outfit. Pure-green speckles (template background) inside the head go too. Idempotent.
Usage: python3 clean_body_necks.py
"""
import os, glob, numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))


def clean(path, B):
    a = np.asarray(Image.open(path).convert('RGBA')).copy()
    c = a[..., :3].astype(int); on = a[..., 3] > 0
    dark = on & (c.max(2) < 62) & (c.max(2) - c.min(2) < 28)      # near-black neutral = the template's outline
    green = on & (c[..., 1] - c[..., 0] > 60) & (c[..., 1] - c[..., 2] > 60)
    gone = green & B
    on = on & ~gone; dark &= ~gone
    K = np.ones((3, 3), bool)
    for _ in range(30):
        fill = on & ~dark
        lab, n = ndi.label(fill, K); sz = ndi.sum(fill, lab, range(1, n + 1))
        fill = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 20])       # real outfit areas, not a stroke's grey
        edge = ndi.binary_dilation(~on, K)                                   # strokes lie on bare skin
        lonely = dark & B & edge & ~ndi.binary_dilation(fill, K)
        if not lonely.any(): break
        gone |= lonely; on &= ~lonely; dark &= ~lonely
    # crumbs left inside the head: tiny pieces (<12 px) not connected to the main outfit
    lab, n = ndi.label(on, np.ones((3, 3), bool)); sz = ndi.sum(on, lab, range(1, n + 1))
    crumbs = np.isin(lab, [i + 1 for i in range(n) if sz[i] < 12]) & B
    gone |= crumbs
    a[gone] = 0
    Image.fromarray(a).save(path)
    return int(gone.sum())


if __name__ == '__main__':
    for sex in 'mf':
        B = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))[..., 3] > 0
        for p in sorted(glob.glob(os.path.join(HERE, f'{sex}_body_*_fixed.png'))):
            print(os.path.basename(p), clean(p, B), 'px removed')
