"""Cut and polish eye pairs from a ChatGPT eye sheet (4x3 grid of the base head template on green, eyes drawn with
a pure-blue iris) into two 200x200 layers per style, aligned to <sex>_head_skin.png:

  <sex>_eyes_<style>_fixed.png  eye whites, lid/lash lines, pupils, catchlights - full colour (never tinted)
  <sex>_eyes_<style>_iris.png   iris only - GRAYSCALE value map, tinted in game with the 6 eye ramps

Usage: python3 process_eyes.py m|f

Polish (why the result is cleaner than a plain downscale):
- every source pixel is classified first (white / iris / dark line / skin), then each canvas pixel takes the class
  that covers most of it - no muddy in-between colours, crisp pixel-art edges;
- one flat colour per fixed part (white, near-black line), iris values stretched to the full range per sheet;
- stray single pixels removed; every iris pixel is kept inside a closed eye (bordered by line or white).
"""
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
STYLES = {'m': ['neutral_almond', 'sharp_narrow', 'heavy_lidded', 'round_youthful', 'hooded_stern', 'tired_droopy',
                'upturned_fierce', 'downturned_gentle', 'deep_set_brooding', 'wide_alert', 'half_closed_calm',
                'narrowed_squint'],
          'f': ['neutral_almond', 'large_round', 'cat_eye', 'doe', 'sleepy', 'sharp_narrow', 'long_lashed_soft',
                'hooded', 'wide_bright', 'gentle_smiling', 'fierce', 'half_lidded_mysterious']}
WHITE, LINE = (250, 248, 246), (30, 22, 26)
NONE, C_WHITE, C_IRIS, C_LINE = 0, 1, 2, 3


def main(sex):
    a = np.asarray(Image.open(os.path.join(HERE, 'source', f'eyes_{sex}_sheet.png')).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g - r > 60) & (g - b > 60)
    lab, n = ndi.label(~green); sz = ndi.sum(~green, lab, range(1, n + 1))
    heads = [int(i) + 1 for i in np.argsort(-sz)[:12]]
    cents = {h: ndi.center_of_mass(lab == h) for h in heads}
    ys_c = sorted(c[0] for c in cents.values())
    gaps = [i for i in range(11) if ys_c[i + 1] - ys_c[i] > 150]
    row_cut = [(ys_c[i] + ys_c[i + 1]) / 2 for i in gaps]
    heads.sort(key=lambda h: (sum(cents[h][0] > c for c in row_cut), cents[h][1]))

    base = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))
    B = base[..., 3] > 0
    by, bx = np.where(B)

    blue = (b - r > 40) & (b - g > 20)
    L = a.mean(2)
    lo, hi = np.percentile(L[blue], [2, 98])

    out, fits = {}, {}
    for k, h in enumerate(heads):
        style = STYLES[sex][k]
        hm = ndi.binary_fill_holes(lab == h)
        ys, xs = np.where(hm)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        hmc, ac = hm[y0:y1, x0:x1], a[y0:y1, x0:x1]
        # --- align the drawn head to the base head (scale + shift), by silhouette overlap
        s0 = (by.max() - by.min() + 1) / (y1 - y0)
        def place(p, arr, mode=Image.NEAREST):
            s, tx, ty = p
            W, H = max(1, round(arr.shape[1] * s)), max(1, round(arr.shape[0] * s))
            im = np.asarray(Image.fromarray(arr.astype(np.float32)).resize((W, H), mode))
            c = np.zeros((200, 200), np.float32); ox, oy = int(round(tx)), int(round(ty))
            ys0, xs0, ys1, xs1 = max(0, oy), max(0, ox), min(200, oy + H), min(200, ox + W)
            if ys1 > ys0 and xs1 > xs0: c[ys0:ys1, xs0:xs1] = im[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
            return c
        cost = lambda p: ((place(p, hmc) > 0.5) ^ B).sum() + 2000 * (p[0] / s0 - 1) ** 2
        p0 = [s0, bx.min(), by.min()]
        best = minimize(cost, p0, method='Nelder-Mead',
                        options=dict(initial_simplex=[p0, [s0 * 1.04, p0[1], p0[2]], [s0, p0[1] + 3, p0[2]],
                                                      [s0, p0[1], p0[2] + 3]], xatol=0.05, fatol=1)).x
        fits[style] = dict(scale=round(float(best[0]), 4), x=round(float(best[1]), 1), y=round(float(best[2]), 1),
                           overlap_error_px=int(cost(best)))
        # --- classify the drawn pixels
        cr, cg, cb = ac[..., 0], ac[..., 1], ac[..., 2]
        cblue = (cb - cr > 40) & (cb - cg > 20)
        eye_zone = ndi.binary_dilation(cblue, iterations=28) & ndi.binary_erosion(hmc, iterations=10)
        cwhite = (ac.min(2) > 225) & (np.abs(cr - cb) < 25) & eye_zone
        cline = (ac.max(2) < 85) & eye_zone & ~cblue
        cls = np.zeros(hmc.shape, np.uint8)
        cls[cwhite] = C_WHITE; cls[cblue] = C_IRIS; cls[cline] = C_LINE
        ival = np.clip((ac.mean(2) - lo) / (hi - lo) * 255, 0, 255)
        # --- majority class per canvas pixel
        cov = {c: place(best, cls == c, Image.BOX) for c in (C_WHITE, C_IRIS, C_LINE)}
        stack = np.stack([cov[C_WHITE], cov[C_IRIS], cov[C_LINE]])
        tot = stack.sum(0)
        pick = np.argmax(stack, 0) + 1
        # lines are thin: let a line win when it covers at least a third of the pixel
        pick[(cov[C_LINE] > 0.33)] = C_LINE
        cls_c = np.where(tot > 0.3, pick, NONE)
        iris_v = place(best, ival * (cls == C_IRIS), Image.BOX) / np.maximum(cov[C_IRIS], 1e-6)
        # --- polish
        for c in (C_WHITE, C_IRIS, C_LINE):                       # isolated pixels of a class
            m = cls_c == c
            nb = ndi.convolve(m.astype(int), np.ones((3, 3), int), mode='constant') - m
            cls_c[m & (nb == 0)] = NONE
        cls_c[~ndi.binary_erosion(B, iterations=1)] = NONE          # keep the far eye inside the face outline
        eyes_any = cls_c != NONE
        lab2, n2 = ndi.label(eyes_any, structure=np.ones((3, 3)))
        sz2 = ndi.sum(eyes_any, lab2, range(1, n2 + 1))
        cls_c[np.isin(lab2, [i + 1 for i in range(n2) if sz2[i] < 4])] = NONE
        fixed = np.zeros((200, 200, 4), np.uint8)
        fixed[cls_c == C_WHITE] = (*WHITE, 255)
        fixed[cls_c == C_LINE] = (*LINE, 255)
        iris = np.zeros((200, 200, 4), np.uint8)
        im = cls_c == C_IRIS
        v = np.clip(iris_v, 0, 255).astype(np.uint8)
        for c in range(3): iris[..., c] = np.where(im, v, 0)
        iris[..., 3] = np.where(im, 255, 0)
        Image.fromarray(fixed).save(os.path.join(HERE, f'{sex}_eyes_{style}_fixed.png'))
        Image.fromarray(iris).save(os.path.join(HERE, f'{sex}_eyes_{style}_iris.png'))
        out[style] = (fixed, iris)
        print(f'{sex}_eyes_{style}: {fits[style]}, px white {int((cls_c == 1).sum())} iris {int(im.sum())} line {int((cls_c == 3).sum())}')
    json.dump(fits, open(os.path.join(HERE, f'eyes_fit_{sex}.json'), 'w'), indent=1)

    # preview: each pair on the tinted base head (zoomed on the face), eye colours cycling
    pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
    hx = lambda c: [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    def tint(img, ramp):
        rr = np.array([hx(c) for c in ramp], float); t = img[..., 0] / 255 * (len(rr) - 1)
        l = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - l)[..., None]
        return Image.fromarray(np.dstack([rr[l] * (1 - f) + rr[l + 1] * f, img[..., 3]]).astype(np.uint8))
    eyes = list(pal['eyes'].values()); skin = tint(base, pal['skin']['fair'])
    tiles = []
    for k, style in enumerate(STYLES[sex]):
        c = Image.new('RGBA', (200, 200), (52, 56, 66, 255)); c.alpha_composite(skin)
        fx, ir = out[style]
        c.alpha_composite(Image.fromarray(fx)); c.alpha_composite(tint(ir, eyes[k % len(eyes)]))
        tiles.append(c.crop((60, 40, 160, 120)).resize((300, 240), Image.NEAREST))
    sheet = Image.new('RGBA', (300 * 4, 240 * 3))
    for k, t in enumerate(tiles): sheet.paste(t, ((k % 4) * 300, (k // 4) * 240))
    sheet.save(os.path.join(HERE, f'preview_eyes_{sex}.png'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'm')
