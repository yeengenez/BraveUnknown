"""Grip bodies -> clean bodies + grip data, for every class. No per-body hand points needed:
rod pieces are grouped by being on one straight line.
  1h:    two rods (front hand, raised back hand); front = the one further right.
  2h / reach: one rod through both fists (shared_rod).
  bow:   front hand holds a near-vertical rod (bow grip); the back hand pinches a near-horizontal line
         (arrow) whose rear end is the draw hand."""
import sys, json, glob, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
from PIL import Image
from scipy import ndimage as ndi
from keyrod import load, magenta_mask
from process import shared_rod
BODIES = os.path.join(HERE, '..')

def fit(pts):
    c = pts.mean(0); _, _, vt = np.linalg.svd(pts - c); d = vt[0]
    if d[1] > 0 or (abs(d[1]) < 1e-6 and d[0] < 0): d = -d
    return c, d

def pieces(m, min_px=5):
    lab, n = ndi.label(m, structure=np.ones((3, 3))); out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) >= min_px: out.append(np.stack([xs, ys], 1).astype(float))
    return out

def group_collinear(ps):
    """Merge pieces that lie on one line (angle within 20 deg, offset under 4 px)."""
    groups = [[p] for p in ps]; merged = True
    while merged and len(groups) > 1:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                a, b = np.vstack(groups[i]), np.vstack(groups[j])
                ca, da = fit(a) if len(a) > 2 else (a.mean(0), np.array([0., -1.]))
                cb, db = fit(b) if len(b) > 2 else (b.mean(0), np.array([0., -1.]))
                ang = np.degrees(np.arccos(min(1, abs(da @ db))))
                off = abs((cb - ca) @ np.array([-da[1], da[0]]))
                if ang < 20 and off < 4 and np.linalg.norm(cb - ca) < 45:
                    groups[i] += groups[j]; del groups[j]; merged = True; break
            if merged: break
    return groups

def hand_from(group):
    pts = np.vstack(group); c, d = fit(pts)
    if len(group) >= 2:
        spans = sorted([(((p - c) @ d).min(), ((p - c) @ d).max()) for p in group])
        k = int(np.argmax([spans[i + 1][0] - spans[i][1] for i in range(len(spans) - 1)]))
        gap = (spans[k][1] + spans[k + 1][0]) / 2; fg = spans[k + 1][0] - spans[k][1]
    else:                                     # one piece only: the fist is at its lower end
        t = (pts - c) @ d; gap = t.min() - 5; fg = 10.0
    g = c + d * gap
    return dict(point=[round(float(g[0]), 1), round(float(g[1]), 1)], angle=round(float(np.degrees(np.arctan2(d[1], d[0]))), 1), fist_gap=round(float(fg), 1))

def clean(a, m, orig):
    out = a.copy(); mm = ndi.binary_dilation(m, iterations=1); zone = ndi.binary_dilation(m, iterations=3)
    mm |= zone & (a[..., 0] - a[..., 1] > 6) & (a[..., 2] - a[..., 1] > 6) | zone & (a.min(2) > 190)
    bgc = np.median(a[:6, :6].reshape(-1, 3), 0); body_orig = orig.min(2) < 236
    out[mm & body_orig] = orig[mm & body_orig]; out[mm & ~body_orig] = bgc
    return out

def process(cls, name):
    a = load(f'raw/{cls}_{name}.png'); m = magenta_mask(a)
    orig = load(f'{BODIES}/{cls}/bodies/{name}.png')
    stance = name.split('_', 1)[1]
    if stance in ('2h', 'reach'):
        g = shared_rod(m)
    elif stance == 'bow':
        ys, xs = np.where(m)
        col = np.bincount(xs, minlength=a.shape[1]); rx = int(np.argmax(col))           # bow rod column
        on = np.abs(xs - rx) <= 1; vy = np.unique(ys[on])
        runs = np.split(vy, np.where(np.diff(vy) > 2)[0] + 1)
        if len(runs) >= 2:                                                            # fist = biggest gap in the rod
            k = int(np.argmax([runs[i + 1][0] - runs[i][-1] for i in range(len(runs) - 1)]))
            gy = (runs[k][-1] + runs[k + 1][0]) / 2; fg = runs[k + 1][0] - runs[k][-1]
        else:
            gy = vy.mean(); fg = 10
        g = {'front': dict(point=[float(rx), round(float(gy), 1)], angle=-90.0, fist_gap=float(fg))}
        g['bow_rod'] = dict(top=float(vy.min()), bottom=float(vy.max()))
        arr = xs < rx - 3
        g['arrow'] = dict(y=round(float(ys[arr].mean()), 1), x0=float(xs[arr].min()), x1=float(rx))
        g['back'] = dict(point=[float(xs[arr].min()), round(float(ys[arr][np.argmin(xs[arr])]), 1)], angle=0.0, fist_gap=8.0)
    else:
        groups = group_collinear(pieces(m)); groups.sort(key=lambda gr: -sum(len(p) for p in gr)); groups = groups[:2]
        hs = [hand_from(gr) for gr in groups]; hs.sort(key=lambda h: h['point'][0])
        g = {'back': hs[0], 'front': hs[-1]} if len(hs) == 2 else {'front': hs[0]}
    Image.fromarray(clean(a, m, orig).astype(np.uint8)).save(f'bodies/{cls}_{name}.png')
    json.dump({'grips': g}, open(f'grips/grips_{cls}_{name}.json', 'w'))
    return g

if __name__ == '__main__':
    todo = sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob('raw/*.png') if 'nogloves' not in f)
    for t in todo:
        cls, name = t.split('_', 1); g = process(cls, name)
        print(t, json.dumps({k: (v.get('point'), v.get('angle')) if 'point' in v else v for k, v in g.items()}))
