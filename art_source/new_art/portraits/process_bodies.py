"""Cut class outfits (portrait busts) out of a ChatGPT body sheet and fit them under the base head.

Source: source/body_<sex>_sheet.png - 3x2 grid of 512x512 squares, the base head template on green with an outfit drawn
under it; bare body skin painted in pure cyan. Order: soldier, archer, acolyte / mage, warrior, rogue.
Output (200x200, same canvas and head placement as <sex>_head_skin.png):
  <sex>_body_<id>_fixed.png  outfit in full colour (never tinted)
  <sex>_body_<id>_skin.png   bare body skin (from the cyan) as a GRAYSCALE skin value map (only if the outfit shows skin)
Class ids follow the game's portrait library: soldier, archer, cleric (= Acolyte), mage, warrior, rogue.
Layer order in game for the new art: head skin -> body -> eyes -> hair (the collar sits over the lower neck).

Usage: python3 process_bodies.py m|f
"""
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
IDS = ['soldier', 'archer', 'cleric', 'mage', 'warrior', 'rogue']
CELL = 512


def main(sex):
    a = np.asarray(Image.open(os.path.join(HERE, 'source', f'body_{sex}_sheet.png')).convert('RGB')).astype(int)
    base = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))
    B = base[..., 3] > 0
    by, bx = np.where(B)
    b_top, b_h = by.min(), by.max() - by.min() + 1
    out, fits = {}, {}
    for k, cid in enumerate(IDS):
        ry, rx = divmod(k, 3)
        c = a[ry * CELL:(ry + 1) * CELL, rx * CELL:(rx + 1) * CELL]
        r, g, b = c[..., 0], c[..., 1], c[..., 2]
        fg = ~((g - r > 60) & (g - b > 60))
        fg = ndi.binary_opening(fg, iterations=1)
        # head = the grey part above the shoulders: rows from the top until the figure gets much wider than the skull
        ys, xs = np.where(fg)
        top = ys.min()
        # the template head is gray: measure how gray on this sheet (skull area) and use that as the head colour test
        sat = c.max(2) - c.min(2)
        skull = fg & (np.arange(c.shape[0])[:, None] < top + 60) & (c.mean(2) > 105)
        neutral = sat <= max(6, np.percentile(sat[skull], 97) + 2)
        widths = np.array([fg[y].sum() for y in range(c.shape[0])])
        skull_w = widths[top:top + 60].max()
        shoulder = next(y for y in range(top + 60, c.shape[0]) if widths[y] > 1.8 * skull_w)
        # fit the base head (scale + shift) to the drawn head above the shoulder line
        upper = np.zeros_like(fg); upper[:shoulder] = fg[:shoulder]
        s0 = (shoulder - top) / (by.max() - b_top) * 1.0
        def head_in_cell(p):
            s, tx, ty = p
            W, H = max(1, round(200 * s)), max(1, round(200 * s))
            im = np.asarray(Image.fromarray(B.astype(np.float32)).resize((W, H), Image.NEAREST))
            cc = np.zeros(c.shape[:2], np.float32); ox, oy = int(round(tx)), int(round(ty))
            ys0, xs0, ys1, xs1 = max(0, oy), max(0, ox), min(c.shape[0], oy + H), min(c.shape[1], ox + W)
            if ys1 > ys0 and xs1 > xs0: cc[ys0:ys1, xs0:xs1] = im[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
            return cc > 0.5
        def cost(p):
            hm = head_in_cell(p)
            return ((hm[:shoulder] ^ upper[:shoulder])).sum()
        hx0 = xs[ys < top + 40].mean()
        s_init = 2.6
        p0 = [s_init, hx0 - (bx[by < b_top + 40].mean()) * s_init, top - b_top * s_init]
        best = minimize(cost, p0, method='Nelder-Mead',
                        options=dict(initial_simplex=[p0, [p0[0] * 1.05, p0[1], p0[2]], [p0[0], p0[1] + 6, p0[2]],
                                                      [p0[0], p0[1], p0[2] + 6]], xatol=0.02, fatol=2, maxiter=300)).x
        s, tx, ty = best
        fits[cid] = dict(scale=round(float(s), 4), x=round(float(tx), 1), y=round(float(ty), 1),
                         head_mismatch_px=int(cost(best)), shoulder_row=int(shoulder))
        # body pixels: everything that is not green and not the grey head (the head region keeps coloured collars)
        # the drawn head itself: grey pixels flood-filled from the skull, plus its dark outline. Using the drawn head
        # (not the fitted base head) keeps collars and scarves whole where they overlap the neck.
        v = c.mean(2)
        light = neutral & (v > 105) & (v < 226)          # brighter neutral pixels are white cloth, not the grey head
        labh, nh = ndi.label(light)
        fitted = ndi.binary_dilation(head_in_cell(best), iterations=6)
        inside = ndi.mean(fitted, labh, range(1, nh + 1))          # share of each grey blob inside the fitted head
        head_draw = ndi.binary_fill_holes(np.isin(labh, [i + 1 for i in range(nh) if inside[i] > 0.6]))
        # a white collar can touch the grey neck and join its blob: the drawn head never reaches past the fitted base head
        head_draw &= ndi.binary_dilation(head_in_cell(best), iterations=4)
        outline = ndi.binary_dilation(head_draw, iterations=5) & ~head_draw & neutral & (v <= 105)
        head_draw = ndi.binary_fill_holes(head_draw | outline)
        body = fg & ~head_draw
        # small holes inside the outfit (white cloth or fur that looked like the grey head) belong to the outfit
        holes = ndi.binary_fill_holes(body) & ~body
        lab_h, nh2 = ndi.label(holes); szh = ndi.sum(holes, lab_h, range(1, nh2 + 1))
        body |= np.isin(lab_h, [i + 1 for i in range(nh2) if szh[i] < 600])
        # thin grey slivers between the outfit and the head edge also go to the outfit
        body |= fg & ~head_draw | (fg & ndi.binary_dilation(body, iterations=2) & ~ndi.binary_erosion(head_draw, iterations=3) & ~(neutral & (v > 105) & (v < 226) & ndi.binary_erosion(head_draw, iterations=1)))
        lab, n = ndi.label(body); sz = ndi.sum(body, lab, range(1, n + 1))
        body = np.isin(lab, [i + 1 for i in range(n) if sz[i] > 150])
        # leftover outline of the drawn head (a thin dark gray ring around the skull): drop dark neutral pixels near the
        # head unless they hug the coloured outfit (those are the outfit's own outline, e.g. along the collar)
        darkn = (c.max(2) < 130) & (np.abs(r - g) < 28) & (np.abs(g - b) < 28)
        ring = body & darkn & ndi.binary_dilation(head_draw, iterations=10)
        keep_near = ndi.binary_dilation(body & ~ring, iterations=4)
        body &= ~(ring & ~keep_near)
        lab, n = ndi.label(body); sz = ndi.sum(body, lab, range(1, n + 1))
        dk = ndi.mean(darkn, lab, range(1, n + 1))
        body = np.isin(lab, [i + 1 for i in range(n) if sz[i] > 150 and (dk[i] < 0.6 or sz[i] > 4000)])
        cyan = body & (b - r > 50) & (g - r > 50) & (np.abs(g - b) < 70) & (g > 60)
        # back to the 200x200 canvas: cell pixel (x, y) -> ((x - tx) / s, (y - ty) / s)
        def to_canvas(arr):
            # crop the part of the cell that maps onto the canvas, then box-downsample
            x0, y0 = tx, ty; x1, y1 = tx + 200 * s, ty + 200 * s
            pad = int(max(0, -x0, -y0, x1 - c.shape[1], y1 - c.shape[0])) + 2
            P = np.pad(arr, [(pad, pad), (pad, pad)] + [(0, 0)] * (arr.ndim - 2))
            sl = P[int(round(y0)) + pad:int(round(y0)) + pad + int(round(200 * s)),
                   int(round(x0)) + pad:int(round(x0)) + pad + int(round(200 * s))]
            return np.asarray(Image.fromarray(sl.astype(np.float32)).resize((200, 200), Image.BOX))
        m_all = to_canvas(body.astype(float)); m_cy = to_canvas(cyan.astype(float))
        rgb = np.stack([to_canvas(c[..., i] * body) for i in range(3)], -1) / np.maximum(m_all, 1e-6)[..., None]
        L = (c.mean(2) * cyan)
        lum = to_canvas(L) / np.maximum(m_cy, 1e-6)
        alpha = m_all > 0.45
        skin = alpha & (m_cy > 0.5 * m_all)
        fixed = np.zeros((200, 200, 4), np.uint8)
        fixed[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8); fixed[..., 3] = np.where(alpha & ~skin, 255, 0)
        Image.fromarray(fixed).save(os.path.join(HERE, f'{sex}_body_{cid}_fixed.png'))
        if skin.any():
            vals = lum[skin]
            med, hi = np.median(vals), np.percentile(vals, 99)
            v = 204 + (lum - med) * (235 - 204) / max(1.0, hi - med)
            sk = np.zeros((200, 200, 4), np.uint8)
            for i in range(3): sk[..., i] = np.where(skin, np.clip(v, 0, 255), 0).astype(np.uint8)
            sk[..., 3] = np.where(skin, 255, 0)
            Image.fromarray(sk).save(os.path.join(HERE, f'{sex}_body_{cid}_skin.png'))
        out[cid] = (fixed, sk if skin.any() else None)
        print(f'{sex}_body_{cid}: {fits[cid]}, skin px {int(skin.sum())}')
    json.dump(fits, open(os.path.join(HERE, f'body_fit_{sex}.json'), 'w'), indent=1)

    # preview: head + body (+ body skin) + one eye pair + one hairstyle, three skin tones
    pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
    hxc = lambda q: [int(q[i:i + 2], 16) for i in (1, 3, 5)]
    def tint(img, ramp):
        rr = np.array([hxc(q) for q in ramp], float); t = img[..., 0] / 255 * (len(rr) - 1)
        l = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - l)[..., None]
        return Image.fromarray(np.dstack([rr[l] * (1 - f) + rr[l + 1] * f, img[..., 3]]).astype(np.uint8))
    hair_ids = {'m': ['spiky', 'crewcut', 'long', 'slicked', 'wild_mane', 'shaggy'],
                'f': ['ponytail', 'side_braid', 'long', 'bob', 'curly_mane', 'pixie']}[sex]
    eye_ids = {'m': ['neutral_almond', 'sharp_narrow', 'downturned_gentle', 'half_closed_calm', 'upturned_fierce', 'narrowed_squint'],
               'f': ['neutral_almond', 'cat_eye', 'doe', 'large_round', 'fierce', 'half_lidded_mysterious']}[sex]
    skins, hairs, eyes = list(pal['skin'].values()), list(pal['hair'].values()), list(pal['eyes'].values())
    sheet = Image.new('RGBA', (200 * 6, 200), (52, 56, 66, 255))
    for k, cid in enumerate(IDS):
        sr = skins[(k * 2) % len(skins)]
        cc = Image.new('RGBA', (200, 200), (52, 56, 66, 255))
        cc.alpha_composite(tint(base, sr))
        fx, sk = out[cid]
        if sk is not None: cc.alpha_composite(tint(sk, sr))
        cc.alpha_composite(Image.fromarray(fx))
        e = os.path.join(HERE, f'{sex}_eyes_{eye_ids[k]}')
        cc.alpha_composite(Image.open(e + '_fixed.png')); cc.alpha_composite(tint(np.asarray(Image.open(e + '_iris.png')), eyes[k % len(eyes)]))
        cc.alpha_composite(tint(np.asarray(Image.open(os.path.join(HERE, f'{sex}_hair_{hair_ids[k]}.png'))), hairs[(k * 3) % len(hairs)]))
        sheet.paste(cc, (k * 200, 0))
    sheet.save(os.path.join(HERE, f'preview_bodies_{sex}.png'))


if __name__ == '__main__':
    sex = sys.argv[1] if len(sys.argv) > 1 else 'm'
    main(sex)
    # strip the template head's leftover outline strokes from the chin / throat (see clean_body_necks.py)
    import glob, clean_body_necks as cbn
    B = np.asarray(Image.open(os.path.join(HERE, f'{sex}_head_skin.png')))[..., 3] > 0
    for p in sorted(glob.glob(os.path.join(HERE, f'{sex}_body_*_fixed.png'))): cbn.clean(p, B)
