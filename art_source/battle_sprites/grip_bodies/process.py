"""Turn a grip body (fists holding magenta guide rods) into a clean weapon-less body plus grip data.
For each hand: the rod pieces above and below the fist are fitted with one straight line; the grip point
is the middle of the gap the fist covers. Magenta is removed; pixels it covered are refilled from the
original body (registered), or made background where the original body had nothing."""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from keyrod import load, magenta_mask
import os
HERE = os.path.dirname(os.path.abspath(__file__))
RIG = json.load(open(os.path.join(HERE, '..', '..', 'weapons', 'rig.json')))
BODIES = os.path.join(HERE, '..')

def shared_rod(m):
    """Two-handed and reach: one rod through both fists. Fit one line to all magenta and find the two
    gaps along it where the fists cover the rod."""
    ys, xs = np.where(m); pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c); d = vt[0]
    if d[0] < 0: d = -d                                           # toward the front (right)
    nrm = np.array([-d[1], d[0]]); keep = np.abs((pts - c) @ nrm) < 3.5
    t = np.sort(np.round((pts[keep] - c) @ d).astype(int)); occ = np.unique(t)
    gaps = [(occ[i], occ[i + 1]) for i in range(len(occ) - 1) if occ[i + 1] - occ[i] > 3]
    gaps = sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:2]; gaps.sort()
    ang = round(float(np.degrees(np.arctan2(d[1], d[0]))), 1)
    out = {}
    for h, g in zip(('back', 'front'), gaps):
        p = c + d * ((g[0] + g[1]) / 2)
        out[h] = dict(point=[round(float(p[0]), 1), round(float(p[1]), 1)], angle=ang, fist_gap=float(g[1] - g[0]))
    out['rod'] = dict(ends=[(c + d * occ.min()).round(1).tolist(), (c + d * occ.max()).round(1).tolist()], angle=ang)
    return out

def process(cls, name, src, out_png):
    a = load(src); m = magenta_mask(a)
    orig = load(f'{BODIES}/{cls}/bodies/{name}.png')
    best = None                                                   # register the original body by the legs
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            sh = np.roll(np.roll(orig, dy, 0), dx, 1); e = np.abs(sh[140:195] - a[140:195]).sum()
            if best is None or e < best[0]: best = (e, dx, dy)
    orig = np.roll(np.roll(orig, best[2], 0), best[1], 1)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    segs = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) >= 6: segs.append(np.stack([xs, ys], 1).astype(float))
    rig = RIG[f'{cls}/{name}']; hands = {}
    for s in segs:                                                # each piece belongs to the nearest fist
        c = s.mean(0); k = min(('front', 'back'), key=lambda h: np.hypot(*(c - np.array(rig[h]))))
        hands.setdefault(k, []).append(s)
    grips = {}
    if name.endswith(('_2h', '_reach')): hands = {}; grips = shared_rod(m)
    for h, pieces in hands.items():
        pts = np.vstack(pieces); c = pts.mean(0); _, _, vt = np.linalg.svd(pts - c); d = vt[0]
        if d[1] > 0 or (abs(d[1]) < 1e-6 and d[0] < 0): d = -d   # direction toward the weapon's head (up / forward)
        ts = [np.sort((p - c) @ d) for p in pieces]
        if len(pieces) >= 2:                                      # gap between the pieces = the fist
            spans = sorted([(t.min(), t.max()) for t in ts]); gap = (spans[0][1] + spans[1][0]) / 2
        else:
            gap = (np.array(rig[h]) - c) @ d
        g = c + d * gap
        grips[h] = dict(point=[round(float(g[0]), 1), round(float(g[1]), 1)], angle=round(float(np.degrees(np.arctan2(d[1], d[0]))), 1),
                        fist_gap=round(float(spans[1][0] - spans[0][1]), 1) if len(pieces) >= 2 else None)
    # remove the magenta: refill from the original body where it had something, else background
    clean = a.copy(); mm = ndi.binary_dilation(m, iterations=1)
    zone = ndi.binary_dilation(m, iterations=3)                   # faint pink fringe around the rods
    tinted = zone & (a[..., 0] - a[..., 1] > 6) & (a[..., 2] - a[..., 1] > 6)
    light = zone & (a.min(2) > 190)
    mm |= tinted | light
    body_orig = orig.min(2) < 236
    bgc = np.median(a[:6, :6].reshape(-1, 3), 0)
    fill = mm & body_orig; clean[fill] = orig[fill]; clean[mm & ~body_orig] = bgc
    Image.fromarray(clean.astype(np.uint8)).save(out_png)
    return dict(grips=grips, register=[best[1], best[2]])

if __name__ == '__main__':
    cls, name, src, out = sys.argv[1:5]
    r = process(cls, name, src, out); print(json.dumps(r))
