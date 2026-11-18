"""Split each grip body into a fixed colour layer and a skin brightness map (like the portraits), so skin is
coloured at runtime by the hero's portrait skin ramp. Head and body skin get the same brightness level."""
import glob, os, json, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image
from scipy import ndimage as ndi
PAL = json.load(open(os.path.join(HERE, '..', '..', '..', 'portraits', 'palettes.json')))['skin']
LO, HI = 40.0, 240.0

def rgba_body(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    white = a.min(2) > 232
    lab, _ = ndi.label(white); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return a, ~np.isin(lab, list(edge))

BARE_HANDS = {'acolyte', 'mage', 'rogue', 'brawler'}

def skin_mask(a, fg, cls, name, grips):
    """Skin = the head, plus bare hands at the grip points, plus class-specific bare skin
    (Brawler arms and chest above the belt; female Rogue neckline)."""
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int); h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    core = (h >= 3) & (h <= 22) & (s >= 80) & (s <= 215) & (v >= 120) & fg
    core = ndi.binary_opening(core, iterations=1)
    lab, n = ndi.label(core, structure=np.ones((3, 3)))
    ys = np.where(fg.any(1))[0]; top, bot = ys.min(), ys.max(); H = bot - top
    keep = []
    for i in range(1, n + 1):
        cy, cx = np.argwhere(lab == i).mean(0); sz = (lab == i).sum()
        if sz < 6: continue
        rel = (cy - top) / H
        ok = rel < 0.2 and sz >= 20                                          # head
        if cls in BARE_HANDS:
            ok |= any(np.hypot(cx - p[0], cy - p[1]) < 11 for p in grips)   # hands on the weapon
        if cls == 'brawler': ok |= rel < 0.48 and sz >= 10                  # arms and chest above the belt
        if cls == 'rogue' and name.startswith('f'): ok |= 0.12 < rel < 0.32 and abs(cx - 66) < 25
        if ok: keep.append(i)
    core = np.isin(lab, keep)
    fam = (h <= 24) & (s >= 60) & (v >= 60) & fg                             # the skin's own shading
    return ndi.binary_dilation(core, iterations=2, mask=fam) | core, top

def split(path):
    n = os.path.basename(path)[:-4]; cls, name = n.split('_', 1)
    g = json.load(open(os.path.join(HERE, 'grips', f'grips_{n}.json')))['grips']
    grips = [v['point'] for v in g.values() if isinstance(v, dict) and 'point' in v]
    a, fg = rgba_body(path); m, top = skin_mask(a, fg, cls, name, grips)
    lum = a[..., 0] * 0.35 + a[..., 1] * 0.45 + a[..., 2] * 0.2
    head = m.copy(); head[top + 34:] = False; body = m & ~head
    v = lum.copy()
    if head.sum() > 30 and body.sum() > 30: v[body] += np.median(lum[head]) - np.median(lum[body])
    val = np.clip((v - LO) / (HI - LO), 0, 1)
    fixed = np.dstack([a, (fg & ~m) * 255]).astype(np.uint8)
    skin = np.dstack([np.full(a.shape[:2], 255), np.full(a.shape[:2], 255), np.full(a.shape[:2], 255), np.zeros(a.shape[:2])]).astype(np.uint8)
    skin = np.zeros(a.shape[:2] + (2,), np.uint8); skin[..., 0] = (val * 255).astype(np.uint8); skin[..., 1] = m * 255
    return fixed, skin

def hexrgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)

def tint(fixed, skin, ramp):
    stops = np.array([hexrgb(c) for c in PAL[ramp]]); t = skin[..., 0] / 255 * (len(stops) - 1)
    i = np.clip(np.floor(t).astype(int), 0, len(stops) - 2); f = (t - i)[..., None]
    col = stops[i] * (1 - f) + stops[i + 1] * f
    out = fixed.copy(); m = skin[..., 1] > 0
    out[m, :3] = col[m].clip(0, 255).astype(np.uint8); out[m, 3] = 255
    return out

if __name__ == '__main__':
    os.chdir(HERE); os.makedirs('layers', exist_ok=True)
    for p in sorted(glob.glob('bodies/*.png')):
        n = os.path.basename(p)[:-4]; fixed, skin = split(p)
        Image.fromarray(fixed).save(f'layers/{n}_fixed.png'); Image.fromarray(skin, 'LA').save(f'layers/{n}_skin.png')
    # review: each body in porcelain, tan and deep
    names = sorted(os.path.basename(p)[:-4] for p in glob.glob('bodies/*.png'))
    tiles = []
    for n in names:
        fx = np.asarray(Image.open(f'layers/{n}_fixed.png')); sk = np.asarray(Image.open(f'layers/{n}_skin.png'))
        row = [tint(fx, sk, r) for r in ('porcelain', 'tan', 'deep')]
        tiles.append(np.hstack([t[:120] for t in row]))
    cols = 4; rows = (len(tiles) + cols - 1) // cols; th, tw = tiles[0].shape[:2]
    sheet = np.full((rows * th, cols * tw, 4), 255, np.uint8)
    for i, t in enumerate(tiles): sheet[(i // cols) * th:(i // cols + 1) * th, (i % cols) * tw:(i % cols + 1) * tw][t[..., 3] > 0] = t[t[..., 3] > 0]
    Image.fromarray(sheet).save('previews/skin_review.png'); print(sheet.shape, names)
