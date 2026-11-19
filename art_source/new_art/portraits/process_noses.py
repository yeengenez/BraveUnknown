"""Cut noses from a ChatGPT nose sheet (3x2 grid of face_template_<sex>.png, nose drawn in shades of blue) into
200x200 SKIN value-map layers aligned to <sex>_head_skin.png: <sex>_nose_<style>.png (tinted with the skin ramp,
like the head).

The sheet's eyes are blue too: the nose is the big blue (lavender) blob below the eyes; the irises are ignored.
The drawn blue only gives light and shade: each nose pixel = the base head's own value + a shading offset taken from
how dark or light the blue is relative to the nose's median blue (dark blue -> shadow / nostril, light -> highlight,
the median -> plain skin). So the nose keeps the head's shading and works on every skin tone.

Placement like the brows and mouths: one scale per sheet (median of the silhouette fits), each cell shifted so its
drawn near eye lands on the base neutral_almond iris.
Usage: python3 process_noses.py m|f
"""
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
STYLES = {'m': ['straight', 'button', 'aquiline', 'broad', 'pointed', 'crooked'],
          'f': ['straight', 'button', 'snub', 'rounded', 'long_thin', 'sharp']}
# value offset at the darkest / lightest blue (relative to the head's own value); the female sheet's noses are smaller
# and paler, so they get more contrast to read at game size
DARK = {'m': 160, 'f': 190}
LIGHT = 26


def main(sex, scale=None):
    a = np.asarray(Image.open(os.path.join(HERE, 'source', f'nose_{sex}_sheet.png')).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g - r > 60) & (g - b > 60)
    lab, n = ndi.label(~green); sz = ndi.sum(~green, lab, range(1, n + 1))
    heads = [int(i) + 1 for i in np.argsort(-sz)[:6]]
    cen = {h: ndi.center_of_mass(lab == h) for h in heads}
    heads.sort(key=lambda h: (cen[h][0] > a.shape[0] / 2, cen[h][1]))
    base = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))
    B = base[..., 3] > 0; by, bx = np.where(B); hv = base[..., 0].astype(float)
    iris = np.asarray(Image.open(os.path.join(HERE, f'{sex}_eyes_neutral_almond_iris.png')))[..., 3] > 0
    iy, ix = np.where(iris); bnear = ix < ix.min() + 0.6 * (ix.max() - ix.min())

    cells, Ls = [], []
    for k, h in enumerate(heads):
        hm = ndi.binary_fill_holes(lab == h)
        ys, xs = np.where(hm); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        hmc, ac = hm[y0:y1, x0:x1], a[y0:y1, x0:x1]
        cr, cg, cb = ac[..., 0], ac[..., 1], ac[..., 2]
        blue = (cb - cr > 40) & (cb - cg > 20) & hmc
        bl, nb = ndi.label(blue, np.ones((3, 3)))
        comps = [(int((bl == i + 1).sum()), i + 1) for i in range(nb)]
        # irises: saturated, dark-ish (r low); nose: lavender (r high), below the eyes
        med_r = {i: np.median(cr[bl == i]) for _, i in comps}
        eyes = [i for s, i in comps if s > 30 and med_r[i] < 60]
        nose_ids = [i for s, i in comps if s > 30 and med_r[i] >= 60]
        eye = np.isin(bl, eyes); nose = np.isin(bl, nose_ids)
        # soft edge / highlight pixels: bluish tint next to the nose blob
        tint = (cb - cr > 10) & ~eye & hmc & ndi.binary_dilation(nose, iterations=3)
        nose = ndi.binary_fill_holes(nose | tint)
        cells.append((hmc, ac, eye, nose)); Ls.append(ac.mean(2)[nose])
    L = np.concatenate(Ls); lo, med, hi = np.percentile(L, [2, 50, 99])

    fits, out = {}, {}
    for k, (hmc, ac, eye, nose) in enumerate(cells):
        style = STYLES[sex][k]
        s0 = (by.max() - by.min() + 1) / hmc.shape[0]
        def place(p, arr, mode=Image.BOX):
            s, tx, ty = p
            W, H = max(1, round(arr.shape[1] * s)), max(1, round(arr.shape[0] * s))
            im = np.asarray(Image.fromarray(arr.astype(np.float32)).resize((W, H), mode))
            c = np.zeros((200, 200), np.float32); ox, oy = int(round(tx)), int(round(ty))
            ys0, xs0, ys1, xs1 = max(0, oy), max(0, ox), min(200, oy + H), min(200, ox + W)
            if ys1 > ys0 and xs1 > xs0: c[ys0:ys1, xs0:xs1] = im[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
            return c
        if scale is None:
            cost = lambda p: ((place(p, hmc, Image.NEAREST) > 0.5) ^ B).sum() + 2000 * (p[0] / s0 - 1) ** 2
            p0 = [s0, bx.min(), by.min()]
            S = minimize(cost, p0, method='Nelder-Mead', options=dict(
                initial_simplex=[p0, [s0 * 1.04, p0[1], p0[2]], [s0, p0[1] + 3, p0[2]], [s0, p0[1], p0[2] + 3]],
                xatol=0.05, fatol=1)).x[0]
        else:
            S = scale
        ey, ex = np.where(eye); near = ex < ex.min() + 0.6 * (ex.max() - ex.min())
        p = [S, ix[bnear].mean() - ex[near].mean() * S, iy[bnear].mean() - ey[near].mean() * S]
        fits[style] = dict(scale=round(float(S), 4), x=round(float(p[1]), 1), y=round(float(p[2]), 1))
        Lc = ac.mean(2)
        off = np.where(Lc < med, -(med - Lc) / max(1, med - lo) * DARK[sex], (Lc - med) / max(1, hi - med) * LIGHT)
        off = np.clip(off, -DARK[sex], LIGHT) * nose
        cov = place(p, nose.astype(float)); offc = place(p, off) / np.maximum(cov, 1e-6)
        on = (cov > 0.45) & ndi.binary_erosion(B, iterations=1)
        v = np.clip(hv + offc, 8, 245)
        img = np.zeros((200, 200, 4), np.uint8)
        for c in range(3): img[..., c] = np.where(on, v, 0).astype(np.uint8)
        img[..., 3] = np.where(on, 255, 0)
        Image.fromarray(img).save(os.path.join(HERE, f'{sex}_nose_{style}.png'))
        out[style] = img
        yy, xx = np.where(on)
        print(f'{sex}_nose_{style}: {fits[style]} px {int(on.sum())} bbox x{xx.min()}-{xx.max()} y{yy.min()}-{yy.max()}')
    json.dump(fits, open(os.path.join(HERE, f'nose_fit_{sex}.json'), 'w'), indent=1)
    return out


def preview():
    import finish
    P = finish.PAL
    tiles = []
    for sex in 'mf':
        for k, style in enumerate(STYLES[sex]):
            for tone in ('fair', 'deep'):
                im = finish.compose(sex, 'soldier', tone, list(P['hair'])[k + 2], list(P['eyes'])[k % 6], 'neutral_almond',
                                    'neutral', 'crewcut' if sex == 'm' else 'pixie', nose=style)
                tiles.append(Image.fromarray(im).crop((95, 75, 145, 125)).resize((150, 150), Image.NEAREST))
    sheet = Image.new('RGBA', (150 * 12, 300), (52, 56, 66, 255))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 12) * 150, (i // 12) * 150))
    sheet.save(os.path.join(HERE, 'preview_noses.png'))


if __name__ == '__main__':
    sx = sys.argv[1] if len(sys.argv) > 1 else 'm'
    main(sx)
    sc = float(np.median([v['scale'] for v in json.load(open(os.path.join(HERE, f'nose_fit_{sx}.json'))).values()]))
    main(sx, sc)
