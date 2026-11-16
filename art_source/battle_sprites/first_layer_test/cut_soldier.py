"""Cut the soldier test weapons into layers and find hand anchors on each stance."""
import numpy as np, cv2, json, os
from scipy import ndimage as ndi
RAW, OUT = 'raw/soldier', 'soldier_test'
os.makedirs(OUT, exist_ok=True)
def rd(n): return cv2.imread(f'{RAW}/{n}.png')
def big(m, n):
    lab, k = ndi.label(m)
    if k == 0: return m
    s = ndi.sum(m, lab, range(1, k + 1)); return np.isin(lab, [i + 1 for i, v in enumerate(s) if v >= n])
def fg(im):  # not the white background
    near = (im.min(2) > 232)
    lab, _ = ndi.label(near); edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    return ~np.isin(lab, list(edge))
def save(name, im, mask):
    cv2.imwrite(f'{OUT}/{name}.png', np.dstack([im, mask.astype(np.uint8) * 255]))

# male hand anchors, read off the grids (x, y)
ANCH = {'m_1h': {'back': (41, 47), 'front': (105, 78)}, 'm_2h': {'grip': (42, 65)}}
# female anchors: template-match the male fist patch near the same spot
def find(im_f, im_m, pt, r=6, s=7):
    x, y = pt; tpl = im_m[y - s:y + s, x - s:x + s]
    win = im_f[y - s - r:y + s + r, x - s - r:x + s + r]
    res = cv2.matchTemplate(win, tpl, cv2.TM_SQDIFF_NORMED); _, _, loc, _ = cv2.minMaxLoc(res)
    return (x - r + loc[0], y - r + loc[1])
for st in ['1h', '2h']:
    m, f = rd(f'm_{st}'), rd(f'f_{st}')
    ANCH[f'f_{st}'] = {k: find(f, m, p) for k, p in ANCH[f'm_{st}'].items()}
print(ANCH)

# bodies
for n in ['m_1h', 'm_2h', 'f_1h', 'f_2h']:
    im = rd(n); save(f'body_{n}', im, fg(im))

# weapons: what changed against the empty-handed base
def register(im, b, rows=(115, 195)):
    """Shift the edited image so its legs line up with the base (legs never hold anything)."""
    best = None
    for dy in range(-10, 11):
        for dx in range(-10, 11):
            sh = np.roll(np.roll(im, dy, 0), dx, 1)
            dd = np.abs(sh[rows[0]:rows[1], 15:118].astype(int) - b[rows[0]:rows[1], 15:118].astype(int)).sum(2)
            sc = np.mean(np.minimum(dd, 120))
            if best is None or sc < best[0]: best = (sc, dx, dy)
    _, dx, dy = best
    print('  registered shift', dx, dy)
    return cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, dy]]), (im.shape[1], im.shape[0]), borderValue=(255, 255, 255))
FIST_R = 6
def fist_mask(shape, pts, r=FIST_R):
    m = np.zeros(shape[:2], np.uint8)
    for p in pts: cv2.circle(m, tuple(int(v) for v in p), r, 1, -1)
    return m.astype(bool)
def glove(im):
    h = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    return (h[..., 0] >= 3) & (h[..., 0] <= 22) & (h[..., 1] >= 90) & (h[..., 2] < 170)   # brown leather glove / sleeve
def axis_dist(m):
    ys, xs = np.nonzero(m)
    pts = np.c_[xs, ys].astype(float); c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c); u = vt[0]
    yy, xx = np.mgrid[:m.shape[0], :m.shape[1]]
    return np.abs((xx - c[0]) * u[1] - (yy - c[1]) * u[0])
def cut(name, base, hands, long=False, width=4.5, region=None, strip_glove=False):
    b = rd(base); im = register(rd(name), b)
    diff = np.abs(im.astype(int) - b.astype(int)).max(2)
    body = ndi.binary_erosion(fg(b), iterations=1)
    keep = np.ones(diff.shape, bool) if region is None else region
    outside = big((diff > 38) & fg(im) & ~body & keep, 8)          # sticks out of the body: pure weapon
    if long:
        near = axis_dist(outside) <= width                           # blade / pole axis from the part outside the body
        hilt = fist_mask(im.shape, [ANCH[base][h] for h in hands], 9)   # crossguard and pommel sit next to the hand
        outside &= near | hilt
        inside = (diff > 16) & body & (near | hilt) & keep
    else:
        inside = (diff > 38) & body & keep
    d = ndi.binary_closing(outside | inside, iterations=1)
    d = ndi.binary_fill_holes(d) & fg(im) & keep
    d &= ~fist_mask(im.shape, [ANCH[base][h] for h in hands], FIST_R + 1)   # the body's own fist goes on top
    if strip_glove: d &= ~(glove(im) & body)
    grips = fist_mask(im.shape, [ANCH[base][h] for h in hands], FIST_R + 3)   # the hand joins the parts above and below it
    lab, k = ndi.label(ndi.binary_dilation(d, iterations=3) | grips)          # one weapon = the biggest piece plus anything touching it
    if k > 1:
        sizes = ndi.sum(d, lab, range(1, k + 1)); d &= lab == (1 + int(np.argmax(sizes)))
    return im, d
xs = np.arange(133)[None, :].repeat(200, 0)
im, d = cut('w_longsword_shield', 'm_1h', ['back'], region=xs >= 80); save('shield_kite', im, d)
im, d = cut('w_longsword_shield', 'm_1h', ['back'], long=True, width=5, region=xs < 80, strip_glove=True); save('w_longsword', im, d)
im, d = cut('w_rapier', 'm_1h', ['front'], long=True, width=3.5); save('w_rapier', im, d)
im, d = cut('w_greatsword', 'm_2h', ['grip'], long=True, width=5.5); save('w_greatsword', im, d)
im, d = cut('w_glaive', 'm_2h', ['grip'], long=True, width=8); save('w_glaive', im, d)

# fists cut from each body, drawn on top of the weapon so the hand wraps the handle
for n, hands in ANCH.items():
    im = rd(n)
    for h, p in hands.items():
        save(f'fist_{n}_{h}', im, fist_mask(im.shape, [p]) & fg(im))

# where each weapon was drawn (which stance/hand), so it can be moved to another hand
WEAP = {'longsword': ('m_1h', 'back'), 'rapier': ('m_1h', 'front'), 'shield_kite': ('m_1h', 'front'),
        'greatsword': ('m_2h', 'grip'), 'glaive': ('m_2h', 'grip')}
json.dump({'anchors': ANCH, 'weapons': WEAP}, open(f'{OUT}/rig.json', 'w'), indent=1)
