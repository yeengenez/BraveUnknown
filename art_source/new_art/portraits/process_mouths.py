"""Cut mouths from a ChatGPT mouth sheet (3x2 grid of face_template_<sex>.png with a mouth drawn per expression)
into 200x200 FIXED-colour layers aligned to <sex>_head_skin.png: <sex>_mouth_<expr>.png (never tinted).
Same placement as process_brows.py: one scale per sheet, each cell placed so its drawn near eye sits on the base eye.
Mouth pixels = dark lines, white teeth and the red mouth inside, in small blobs inside the face (the long jaw line of
the template head is ignored).

Alignment: silhouette fit of each drawn head to the base head, then a shift so the drawn (blue) eyes land on the
base neutral_almond iris - brows must sit right above the eyes.
Usage: python3 process_brows.py m|f
"""
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
EXPR = ['neutral', 'smile', 'stern', 'grin', 'sleepy', 'worried']


SCALE = None


def main(sex, scale=None):
    global SCALE; SCALE = scale
    a = np.asarray(Image.open(os.path.join(HERE, 'source', f'mouth_{sex}_sheet.png')).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g - r > 60) & (g - b > 60)
    lab, n = ndi.label(~green); sz = ndi.sum(~green, lab, range(1, n + 1))
    heads = [int(i) + 1 for i in np.argsort(-sz)[:6]]
    cen = {h: ndi.center_of_mass(lab == h) for h in heads}
    heads.sort(key=lambda h: (cen[h][0] > a.shape[0] / 2, cen[h][1]))
    base = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))
    B = base[..., 3] > 0; by, bx = np.where(B)
    iris = np.asarray(Image.open(os.path.join(HERE, f'{sex}_eyes_neutral_almond_iris.png')))[..., 3] > 0
    iy, ix = np.where(iris)
    red_all = (r - g > 60) & (r - b > 50)
    lo, hi = (np.percentile(r[red_all], [2, 98]) if red_all.sum() > 20 else (0, 255))
    out, fits = {}, {}
    for k, h in enumerate(heads):
        expr = EXPR[k]
        hm = ndi.binary_fill_holes(lab == h)
        ys, xs = np.where(hm); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        hmc, ac = hm[y0:y1, x0:x1], a[y0:y1, x0:x1]
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
        cr, cg, cb = ac[..., 0], ac[..., 1], ac[..., 2]
        cblue = (cb - cr > 40) & (cb - cg > 20)
        # eye refinement: drawn blue iris centroid -> base iris centroid
        # brows must keep their distance to the eyes: place the cell so its drawn iris lands exactly on the base iris
        # (scale from the silhouette fit, median over the sheet; position from the eyes only)
        cyy, cxx = np.where(cblue & (np.indices(cblue.shape)[1] < np.percentile(np.where(cblue)[1], 100)))
        near = cxx < cxx.min() + 0.6 * (cxx.max() - cxx.min())         # near (left) eye only: the far eye is clipped
        S = SCALE if SCALE else best[0]
        bnear = ix < ix.min() + 0.6 * (ix.max() - ix.min())
        best = [S, ix[bnear].mean() - cxx[near].mean() * S, iy[bnear].mean() - cyy[near].mean() * S]
        fits[expr] = dict(scale=round(float(best[0]), 4), x=round(float(best[1]), 1), y=round(float(best[2]), 1))
        inner = ndi.binary_erosion(hmc, iterations=10)
        dark = (ac.max(2) < 100) & inner
        redm = (cr - cg > 50) & (cr - cb > 40) & inner
        below = np.indices(hmc.shape)[0] > (np.where(cblue)[0].max() + 15)
        cand = (dark | redm) & below
        labm, nm = ndi.label(cand, structure=np.ones((3, 3)))
        keep = []
        for i, sl in enumerate(ndi.find_objects(labm)):
            hgt, wid = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            ex = np.where(cblue)[1]; near_x = ex[ex < ex.min() + 0.6 * (ex.max() - ex.min())].mean()
            right_of_eye = (sl[1].start + sl[1].stop) / 2 > near_x       # the mouth is toward the face, not by the ear
            if wid < 110 and hgt < 70 and (labm[sl] == i + 1).sum() > 15 and right_of_eye: keep.append(i + 1)
        mouth = np.isin(labm, keep)
        zone = ndi.binary_fill_holes(ndi.binary_closing(mouth, iterations=6)) | ndi.binary_dilation(mouth, iterations=2)
        white = (ac.min(2) > 225) & zone
        mouth |= white | (redm & zone)
        mouth = ndi.binary_fill_holes(ndi.binary_closing(mouth, iterations=2)) & (zone | mouth)
        # classify for crisp colours: line / teeth / inside
        cls = np.zeros(hmc.shape, np.uint8)
        cls[mouth & (ac.max(2) < 110)] = 1
        cls[mouth & white] = 2
        cls[mouth & (cls == 0)] = 3
        covs = [place(best, cls == q, Image.BOX) for q in (1, 2, 3)]
        tot = covs[0] + covs[1] + covs[2]
        pick = np.argmax(np.stack(covs), 0) + 1
        pick[covs[0] > 0.33] = 1
        on = (tot > 0.3) & ndi.binary_erosion(B, iterations=1)
        insidecol = place(best, np.stack([cr, cg, cb], -1)[..., 0] * (cls == 3), Image.BOX)
        img = np.zeros((200, 200, 4), np.uint8)
        img[on & (pick == 1)] = (30, 22, 26, 255)
        img[on & (pick == 2)] = (250, 248, 246, 255)
        img[on & (pick == 3)] = (110, 40, 42, 255)
        m = on
        Image.fromarray(img).save(os.path.join(HERE, f'{sex}_mouth_{expr}.png'))
        out[expr] = img
        print(f'{sex}_mouth_{expr}: {fits[expr]} px {int(m.sum())}')
    json.dump(fits, open(os.path.join(HERE, f'mouth_fit_{sex}.json'), 'w'), indent=1)
    # preview: head + eyes + brows (hair colours) + a hairstyle
    pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
    hx = lambda q: [int(q[i:i + 2], 16) for i in (1, 3, 5)]
    def tint(img, ramp):
        rr = np.array([hx(q) for q in ramp], float); t = img[..., 0] / 255 * (len(rr) - 1)
        l = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - l)[..., None]
        return Image.fromarray(np.dstack([rr[l] * (1 - f) + rr[l + 1] * f, img[..., 3]]).astype(np.uint8))
    hairs = list(pal['hair'].values()); skin = tint(base, pal['skin']['fair'])
    e = os.path.join(HERE, f'{sex}_eyes_neutral_almond')
    hair = np.asarray(Image.open(os.path.join(HERE, f'{sex}_hair_{"crewcut" if sex == "m" else "pixie"}.png')))
    sheet = Image.new('RGBA', (300 * 6, 480), (52, 56, 66, 255))
    for k, expr in enumerate(EXPR):
        for row, with_hair in enumerate((False, True)):
            c = Image.new('RGBA', (200, 200), (52, 56, 66, 255)); c.alpha_composite(skin)
            c.alpha_composite(Image.open(e + '_fixed.png')); c.alpha_composite(tint(np.asarray(Image.open(e + '_iris.png')), list(pal['eyes'].values())[1]))
            hr = hairs[(k * 3 + 1) % len(hairs)]
            c.alpha_composite(tint(np.asarray(Image.open(os.path.join(HERE, f'{sex}_brows_{expr}.png'))), hr))
            c.alpha_composite(Image.fromarray(out[expr]))
            if with_hair: c.alpha_composite(tint(hair, hr))
            sheet.paste(c.crop((60, 50, 160, 130)).resize((300, 240), Image.NEAREST), (k * 300, row * 240))
    sheet.save(os.path.join(HERE, f'preview_mouth_{sex}.png'))


if __name__ == '__main__':
    sx = sys.argv[1] if len(sys.argv) > 1 else 'm'
    main(sx)                                          # first pass: per-cell silhouette scales
    sc = float(np.median([v['scale'] for v in json.load(open(os.path.join(HERE, f'mouth_fit_{sx}.json'))).values()]))
    main(sx, sc)                                      # second pass: one scale for the sheet, eyes as anchor
