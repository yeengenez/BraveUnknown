"""Cut hairstyles out of a ChatGPT hair sheet (4x3 grid, grayscale hair on a flat green mannequin head, white
background) and fit each one onto the new base head (<sex>_head_skin.png) as a 200x200 hair value map.

Usage: python3 process_hair.py m    (reads source/hair_m_sheet.png, writes <sex>_hair_<style>.png + preview)

How it works
- Hair = pixels that are neither white background nor green mannequin, minus the mannequin's own black outline
  (dark pixels touching both the green head and the white background).
- Alignment: the mannequin is the same in every cell. Its ear-to-face width and chin are matched to the base head
  (same landmarks measured on <sex>_head_skin.png), so every style lands on the head the game uses.
- Values are stretched to the legacy hair convention (full 0-255 range, ~median 150-170) with one stretch per sheet,
  so styles keep the same brightness relative to each other.
"""
import os, sys, json, numpy as np, cv2
from scipy.optimize import minimize
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
STYLES = {'m': ['messy', 'sidepart', 'spiky', 'crewcut', 'slicked', 'shaggy', 'ponytail', 'long',
                'topknot', 'braided_mohawk', 'wild_mane', 'knight_cut'],
          'f': ['long', 'ponytail', 'bob', 'braids', 'wavy', 'pixie', 'bun', 'crown_braid',
                'side_braid', 'twin_buns', 'curly_mane', 'warrior_halfup']}


def runs(m, gap=5):
    idx = np.where(m)[0]
    sp = np.split(idx, np.where(np.diff(idx) > gap)[0] + 1)
    return [(int(s[0]), int(s[-1])) for s in sp if len(s) > 20]


def landmarks(head):
    """ear-back x, face-front x and chin y of a head mask (green mannequin or base head skin)."""
    ys, xs = np.where(head)
    x0, x1 = xs.min(), xs.max()
    front = xs > x1 - 0.12 * (x1 - x0)                   # face front columns
    chin = ys[front].max()
    # ear back: leftmost head pixel above the chin (the neck below the chin may stick out further back)
    above = ys < chin - 0.15 * (chin - ys.min())
    ear = xs[above].min()
    return float(ear), float(x1), float(chin)


def main(sex):
    a = np.asarray(Image.open(os.path.join(HERE, 'source', f'hair_{sex}_sheet.png')).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    v = a.mean(2)
    green = (g - r > 50) & (g - b > 50)                 # any shade of the green mannequin
    white = v > 238
    # cell bounds from the green mannequin columns/rows
    cx = runs(green.any(0)); cy = runs(green.any(1))
    xb = [0] + [(cx[i][1] + cx[i + 1][0]) // 2 for i in range(len(cx) - 1)] + [a.shape[1]]
    yb = [0] + [(cy[i][1] + cy[i + 1][0]) // 2 for i in range(len(cy) - 1)] + [a.shape[0]]
    assert len(xb) == 5 and len(yb) == 4, (cx, cy)

    base = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))
    b_ear, b_front, b_chin = landmarks(base[..., 3] > 0)

    # one value stretch for the whole sheet
    hair_all = ~white & ~green & ~ndi.binary_dilation(green, iterations=2)
    lo, hi = np.percentile(v[hair_all], [1, 99.5])

    # hair blobs are assigned to the nearest mannequin over the whole sheet (tall hair crosses cell lines)
    labm, nm = ndi.label(green); szm = ndi.sum(green, labm, range(1, nm + 1))
    heads = [i + 1 for i in np.argsort(-szm)[:12]]
    cents = [ndi.center_of_mass(labm == h) for h in heads]
    order = sorted(range(12), key=lambda i: (round(cents[i][0] / 200), cents[i][1]))   # rows, then columns
    heads = [heads[i] for i in order]
    # each mannequin = its face component + every other green piece (neck, ear) closest to it
    big = [int(i) + 1 for i in range(nm) if szm[i] > 200]
    cen = {i: ndi.center_of_mass(labm == i) for i in big}
    mannall = []
    for h in heads:
        parts = [i for i in big if min(heads, key=lambda q: np.hypot(cen[q][0] - cen[i][0], cen[q][1] - cen[i][1])) == h]
        mannall.append(ndi.binary_fill_holes(ndi.binary_closing(np.isin(labm, parts), iterations=6)))
    dist = np.stack([ndi.distance_transform_edt(~m) for m in mannall])
    owner = np.argmin(dist, 0)
    near_g_all = ndi.binary_dilation(green, iterations=6); near_w_all = ndi.binary_dilation(white, iterations=6)
    m_out_all = near_g_all & near_w_all & ~white & (v < 120)
    hair_glob = ~white & ~ndi.binary_dilation(green, iterations=1) & ~m_out_all
    for m in mannall: hair_glob &= ~m
    lab, n = ndi.label(hair_glob); sz = ndi.sum(hair_glob, lab, range(1, n + 1))
    blob_owner = ndi.labeled_comprehension(owner, lab, range(1, n + 1), lambda x: np.bincount(x).argmax(), int, -1)

    out = {}; fits = {}
    for k, style in enumerate(STYLES[sex]):
        # drop the mannequin's inner jaw/neck lines: thin blobs that are almost entirely dark
        dark_frac = ndi.mean(v < 100, lab, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] > 60 and blob_owner[i] == k and dark_frac[i] < 0.7]
        hair_full = np.isin(lab, keep)
        ys_, xs_ = np.where(hair_full | mannall[k])
        sl = (slice(ys_.min(), ys_.max() + 1), slice(xs_.min(), xs_.max() + 1))   # crop to this head + its hair
        cg, cw, cv = green[sl], white[sl], v[sl]
        mann = mannall[k][sl]; hair = hair_full[sl]
        # alignment: mannequin landmarks -> base head landmarks
        m_ear, m_front, m_chin = landmarks(mann | ndi.binary_dilation(mann, iterations=3) & (cv < 120))
        s = (b_front - b_ear) / (m_front - m_ear)
        tx, ty = b_front - m_front * s, b_chin - m_chin * s
        if ty < 0: print(f'  {style}: {-ty:.0f} px of hair above the canvas top')
        val = np.clip((cv - lo) / (hi - lo) * 255, 0, 255)
        H, W = cv.shape
        Wn, Hn = round(W * s), round(H * s)
        down = lambda arr: np.asarray(Image.fromarray(arr.astype(np.float32)).resize((Wn, Hn), Image.BOX))
        pv, pm = down(val * hair), down(hair)
        mann_full = mann | (ndi.binary_dilation(mann, iterations=3) & (cv < 120))
        pmm = down(mann_full)
        # place on a 200x200 canvas at the landmark position, then refine with a small affine fit:
        # the mannequin should cover the base head, and no base-head skin may stick out from under hair + mannequin
        def to_canvas(arr):
            c = np.zeros((200, 200), np.float32); ox, oy = int(round(tx)), int(round(ty))
            ys0, xs0, ys1, xs1 = max(0, oy), max(0, ox), min(200, oy + Hn), min(200, ox + Wn)
            c[ys0:ys1, xs0:xs1] = arr[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]; return c
        Cv, Cm, Cmm = to_canvas(pv), to_canvas(pm), to_canvas(pmm)
        B = base[..., 3] > 0
        cxp, cyp = b_front - 30, b_chin - 40                        # pivot near the middle of the face
        def M(p):
            sx, sy, rot, dx, dy = p
            c, sn = np.cos(rot), np.sin(rot)
            A = np.array([[sx * c, -sy * sn], [sx * sn, sy * c]])
            t = np.array([cxp + dx, cyp + dy]) - A @ np.array([cxp, cyp])
            return np.hstack([A, t[:, None]]).astype(np.float32)
        warp = lambda img, p, interp=cv2.INTER_LINEAR: cv2.warpAffine(img, M(p), (200, 200), flags=interp)
        def cost(p):
            mm, hh = warp(Cmm, p) > 0.5, warp(Cm, p) > 0.5
            poke = (B & ~mm & ~hh).sum()          # base skin not covered by mannequin or hair
            spill = (mm & ~B).sum()               # mannequin where the base head has nothing
            reg = 4000 * ((p[0] - 1) ** 2 + (p[1] - 1) ** 2) + 4000 * p[2] ** 2
            return 3 * poke + 2 * spill + reg
        p0 = np.array([1, 1, 0, 0, 0], float)
        best = minimize(cost, p0, method='Nelder-Mead',
                        options=dict(initial_simplex=[p0, p0 + [.06, 0, 0, 0, 0], p0 + [0, .06, 0, 0, 0],
                                                      p0 + [0, 0, .05, 0, 0], p0 + [0, 0, 0, 3, 0], p0 + [0, 0, 0, 0, 3]],
                                     xatol=1e-3, fatol=1, maxiter=400)).x
        fit = dict(zip(['sx', 'sy', 'rot_deg', 'dx', 'dy'], [round(float(x), 3) for x in best[:2]] +
                       [round(float(np.degrees(best[2])), 2), round(float(best[3]), 1), round(float(best[4]), 1)]))
        wv, wm = warp(Cv, best), warp(Cm, best)
        gray = np.where(wm > 0, wv / np.maximum(wm, 1e-6), 0).clip(0, 255).astype(np.uint8)
        img = np.zeros((200, 200, 4), np.uint8)
        for c in range(3): img[..., c] = gray
        img[..., 3] = np.where(wm > 0.45, 255, 0)
        fits[style] = dict(fit, cost_before=int(cost(p0)), cost_after=int(cost(best)))
        Image.fromarray(img).save(os.path.join(HERE, f'{sex}_hair_{style}.png'))
        out[style] = img
        a3 = img[..., 3]; yy, xx = np.where(a3 > 0)
        clip = 'CLIPPED' if (xx.min() == 0 or yy.min() == 0 or xx.max() == 199 or yy.max() == 199) else ''
        print(f'{sex}_hair_{style}: {fits[style]} bbox {xx.min()},{yy.min()}-{xx.max()},{yy.max()} {clip}')

    json.dump(fits, open(os.path.join(HERE, f'hair_fit_{sex}.json'), 'w'), indent=1)
    # preview: each style on the base head, three hair colours
    pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
    hx = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    def tint(img, ramp):
        rr = np.array([hx(c) for c in ramp], float); t = img[..., 0] / 255 * (len(rr) - 1)
        l = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - l)[..., None]
        return Image.fromarray(np.dstack([rr[l] * (1 - f) + rr[l + 1] * f, img[..., 3]]).astype(np.uint8))
    hairs = list(pal['hair'].values())
    skin = tint(base, pal['skin']['tan'])
    sheet = Image.new('RGBA', (200 * 6, 200 * 4), (52, 56, 66, 255))
    for k, style in enumerate(STYLES[sex]):
        c = Image.new('RGBA', (200, 200), (52, 56, 66, 255)); c.alpha_composite(skin)
        c.alpha_composite(tint(out[style], hairs[(k * 3) % len(hairs)]))
        sheet.paste(c, ((k % 6) * 200, (k // 6) * 200))
    # second half: each style untinted (raw value map) on grey, to check the cut
    for k, style in enumerate(STYLES[sex]):
        c = Image.new('RGBA', (200, 200), (120, 160, 120, 255)); c.alpha_composite(Image.fromarray(out[style]))
        sheet.paste(c, ((k % 6) * 200, 400 + (k // 6) * 200))
    sheet.save(os.path.join(HERE, f'preview_hair_{sex}.png'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'm')
