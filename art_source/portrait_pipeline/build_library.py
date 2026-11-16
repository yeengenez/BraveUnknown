"""Cut the generated style-A portraits into an aligned, recolorable parts library.

Every part exists per body type (m_ / f_ prefix), including hair.
Every part is a 200x200 RGBA PNG on the same canvas. Tintable parts are grayscale "value maps"
(0 = darkest shade of the ramp, 255 = lightest) that the game colors with a palette ramp.
  <m|f>_body_<class>_fixed.png   clothes, armor, outlines            (draw as-is)
  body_<class>_skin.png    head/neck skin value map            (tint with a skin ramp)
  face_<name>_fixed.png    brows, eye whites, mouth, lines     (draw as-is)
  face_<name>_skin.png     skin inside the face patch          (skin ramp)
  face_<name>_iris.png     iris value map                      (eye ramp)
  detail_<name>.png        scars etc.                          (draw as-is)
  <m|f>_hair_<name>.png          hair value map                      (hair ramp)
"""
import numpy as np, cv2, os, json
from scipy import ndimage as ndi

RAW, OUT = 'raw', 'library'
import shutil; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
S = 200
TPL_BOX = (66, 104, 84, 134)                      # y0,y1,x0,x1: eyes-to-mouth, used to register

def load(path, tpl=None):
    im = cv2.imread(f'{RAW}/{path}.png')
    if tpl is not None:
        res = cv2.matchTemplate(im, tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(res)
        dx, dy = TPL_BOX[2] - loc[0], TPL_BOX[0] - loc[1]
        if abs(dx) > 6 or abs(dy) > 6 or score < 0.5: dx = dy = 0
        if dx or dy:
            im = cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, dy]]), (S, S), borderMode=cv2.BORDER_REPLICATE)
        print(f'{path}: shift {dx},{dy} score {score:.2f}')
    return im

def lum(im): return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
def hsv(im): return cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.int32)
def diff(a, b): return np.abs(a.astype(np.int32) - b.astype(np.int32)).max(2)
def big(mask, min_size):
    lab, n = ndi.label(mask)
    if n == 0: return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= min_size])
def save_rgba(name, bgr, alpha):
    cv2.imwrite(f'{OUT}/{name}.png', np.dstack([bgr, alpha.astype(np.uint8) * 255]))
def save_value(name, val, alpha):
    v = np.clip(val, 0, 255).astype(np.uint8)
    cv2.imwrite(f'{OUT}/{name}.png', np.dstack([v, v, v, alpha.astype(np.uint8) * 255]))

def foreground(im):
    """Everything that is not the beige background (flood fill from the borders)."""
    bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[:, :4].reshape(-1, 3), im[:60, -4:].reshape(-1, 3)]), 0)
    near = np.abs(im.astype(np.int32) - bg).max(2) < 26
    lab, _ = ndi.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[:150, 0], lab[:150, -1]]))) - {0}
    return ndi.binary_fill_holes(~np.isin(lab, list(edge)))

def huefam(h):
    """Any pixel in the skin colour family, from highlights down to the soft brown lines."""
    return (h[..., 0] >= 2) & (h[..., 0] <= 25) & (h[..., 1] >= 45) & (h[..., 2] >= 50)

def skin_mask(im, fg, seed=(92, 118)):
    h = hsv(im)
    tone = (h[..., 0] >= 4) & (h[..., 0] <= 23) & (h[..., 1] >= 50) & (h[..., 1] <= 180) & fg
    lab, _ = ndi.label(tone & (h[..., 2] >= 150))
    core = lab == lab[seed] if lab[seed] else tone
    zone = np.zeros_like(core); zone[:140, 55:150] = True            # head and neck only
    lab2, _ = ndi.label(tone & (h[..., 2] >= 105) & zone)
    for _ in range(2):                                               # add ear, neck and shadowed skin next to the head
        near = ndi.binary_dilation(core, iterations=4)
        ids = set(np.unique(lab2[near])) - {0}
        core = core | np.isin(lab2, list(ids))
    # grow into the soft shading and line pixels around the skin, so no original-coloured fringe is left behind
    return ndi.binary_dilation(core, iterations=6, mask=huefam(h) & fg & zone) | core

# value-map normalisation ranges (fixed so every part shades consistently)
SKIN_LO, SKIN_HI = 30.0, 235.0
def skin_value(im): return (lum(im) - SKIN_LO) / (SKIN_HI - SKIN_LO) * 255

meta = {'canvas': [S, S], 'body_types': ['m', 'f'], 'bodies': ['soldier', 'archer', 'cleric'],
        'faces': ['neutral', 'smile', 'stern', 'grin', 'sleepy'], 'details': ['scar']}
FACE_BOX = np.zeros((S, S), bool); FACE_BOX[56:112, 76:140] = True

def head_metrics(im):
    sk = skin_mask(im, foreground(im))
    if sk.sum() < 500:                                   # seed missed: take the biggest skin blob near the top
        h = hsv(im); t = (h[..., 0] >= 4) & (h[..., 0] <= 23) & (h[..., 1] >= 50) & (h[..., 1] <= 180) & (h[..., 2] >= 150)
        t[130:] = False; lab, n = ndi.label(t); sk = lab == (1 + np.argmax(ndi.sum(t, lab, range(1, n + 1))))
    top = np.where(sk.any(1))[0][0]
    rows = sk[top + 10: top + 45]; xs = np.where(rows.any(0))[0]
    return top, xs[-1] - xs[0] + 1, (xs[0] + xs[-1]) / 2

def fit_head(im, base_im, base_sk, tpl):
    """Scale and shift a body image so its head lands on the base head, then paste the base head over it."""
    tb, wb, cb = head_metrics(base_im); tn, wn, cn = head_metrics(im)
    s = wb / wn
    if abs(s - 1) < 0.03 and abs(tb - tn) <= 2 and abs(cb - cn) <= 2:
        s = 1.0
    else:
        M = np.float32([[s, 0, cb - s * cn], [0, s, tb - s * tn]])
        im = cv2.warpAffine(im, M, (S, S), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
    h = hsv(base_im)
    tone = (h[..., 0] >= 4) & (h[..., 0] <= 23) & (h[..., 1] >= 50) & (h[..., 1] <= 180) & (h[..., 2] >= 150)
    lab, _ = ndi.label(tone); face = ndi.binary_fill_holes(lab == lab[92, 118])     # face and skull only, no neck
    head = ndi.binary_dilation(face, iterations=2) & foreground(base_im)
    blue = (h[..., 0] >= 95) & (h[..., 0] <= 135) & (h[..., 1] >= 60)
    head &= ~blue & ~(base_im[..., 0].astype(int) > base_im[..., 2].astype(int) + 8)   # nothing bluer than it is red: scarf
    head[90:] &= face[90:]                                                         # below the ear: no outline, so no scarf pixels
    out = im.copy(); out[head] = base_im[head]
    print(f'   head fit: scale {s:.2f}')
    return out

def build_set(sex):
    base_im = load(f'{sex}/base')
    tpl = base_im[TPL_BOX[0]:TPL_BOX[1], TPL_BOX[2]:TPL_BOX[3]]
    base_sk = skin_mask(base_im, foreground(base_im))
    for cls in meta['bodies']:
        im = fit_head(load(f'{sex}/body_{cls}'), base_im, base_sk, tpl)
        fg = foreground(im); sk = skin_mask(im, fg)
        save_rgba(f'{sex}_body_{cls}_fixed', im, fg & ~sk)
        save_value(f'{sex}_body_{cls}_skin', skin_value(im), sk)
    variants = {n: load(f'{sex}/face_{n}', tpl) for n in meta['faces'][1:]}
    region = np.zeros((S, S), bool)
    for im in variants.values(): region |= (diff(im, base_im) > 26) & FACE_BOX
    region = ndi.binary_fill_holes(ndi.binary_dilation(big(region, 6), iterations=3)) & FACE_BOX
    pts = np.argwhere(base_sk)[:, ::-1].astype(np.int32)
    hull = np.zeros((S, S), np.uint8); cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
    head_inside = ndi.binary_erosion(hull.astype(bool), iterations=3)
    head_inside[94:, :88] = False        # below the ear there are no face features, only neck and collar
    def iris_of(im):
        h = hsv(im)
        return FACE_BOX & head_inside & (h[..., 0] >= 35) & (h[..., 0] <= 100) & (h[..., 1] >= 45)
    for im in [base_im, *variants.values()]: region |= ndi.binary_dilation(iris_of(im), iterations=4)
    region &= head_inside
    for n, im in {'neutral': base_im, **variants}.items():
        h = hsv(im)
        iris = region & iris_of(im)
        sk = region & huefam(h) & ~iris
        save_rgba(f'{sex}_face_{n}_fixed', im, region & ~sk & ~iris)
        save_value(f'{sex}_face_{n}_skin', skin_value(im), sk)
        save_value(f'{sex}_face_{n}_iris', (lum(im) - 60) / (190 - 60) * 255, iris)
    sc = load(f'{sex}/detail_scar', tpl)
    m = ndi.binary_dilation(big((diff(sc, base_im) > 22) & FACE_BOX, 3), iterations=1) & head_inside
    save_value(f'{sex}_detail_scar', skin_value(sc) + 20, m)
    return base_im, tpl

bases = {sex: build_set(sex)[0] for sex in 'mf'}

def load_hair(sex, n, box=(120, 180, 70, 140)):
    """Register a hair image to its own base head using the body below the head, which hair never covers
    (the face is partly hidden by fringes, so it gives unreliable matches)."""
    im = cv2.imread(f'{RAW}/hair/{sex}/{n}.png'); a = im.astype(np.int32); b = bases[sex].astype(np.int32); best = None
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            sh = np.roll(np.roll(a, dy, 0), dx, 1)
            d = np.abs(sh[box[0]:box[1], box[2]:box[3]] - b[box[0]:box[1], box[2]:box[3]]).sum(2)
            sc = np.median(d) + np.mean(np.minimum(d, 60))
            if best is None or sc < best[0]: best = (sc, dx, dy)
    _, dx, dy = best
    print(f'{sex}_hair_{n}: shift {dx},{dy}')
    return cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, dy]]), (S, S), borderMode=cv2.BORDER_REPLICATE)

# ---------- hair: each body type has its own styles, cut against its own base head ----------
HAIR = {'m': ['messy', 'sidepart', 'spiky', 'crewcut', 'slicked', 'shaggy', 'ponytail', 'long'],
        'f': ['long', 'ponytail', 'bob', 'braids', 'wavy', 'pixie', 'bun']}
meta['hair'] = HAIR
for sex, names in HAIR.items():
    for n in names:
        im = load_hair(sex, n)
        h = hsv(im)
        pink = big(((h[..., 0] >= 150) | (h[..., 0] <= 4)) & (h[..., 1] >= 70) & (h[..., 2] >= 90), 12)
        d = diff(im, bases[sex]) > 30
        edge = ndi.binary_dilation(pink, iterations=2) & (lum(im) < 95) & d
        m = big(ndi.binary_closing(pink | edge, iterations=1) & (d | pink), 40)
        l = lum(im); lo, hi = 35.0, np.percentile(l[pink], 97)
        save_value(f'{sex}_hair_{n}', (l - lo) / (hi - lo) * 255, m)

json.dump(meta, open(f'{OUT}/library.json', 'w'), indent=1)
print('parts written:', len(os.listdir(OUT)))
