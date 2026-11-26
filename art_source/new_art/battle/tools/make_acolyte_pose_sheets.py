"""Acolyte pose sheets (user, 2026-11-26: "create a template for each combat animation and prompt for Gemini").
Each sheet holds the finished SOLDIER figures of one combat animation, laid out on the Acolyte sheet layout
(make_refs.EXTRA_SHEETS['acolyte']) on clean green cells; Gemini re-dresses them as the Acolyte. The Soldier's red
ponytail is removed (the Acolyte wears its hood up). Output: templates/acolyte_<anim>_<sex>_pose.png
Sources: shield / 2h / reach = rows 1, 3, 4 of source/soldier_<sex>_sheet.png (4 x 4 v5 layout, figures enlarged);
dual = source/soldier_dual_<sex>_sheet.png (slash arcs already lifted off); downed = source/soldier_downed_sheet.png."""
import os, sys, shutil, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import make_refs as M
GREEN, LINE, DASH, BORDER = (0, 255, 0), (20, 20, 20), (0, 200, 60), (0, 190, 0)
FIG_H = round(0.78 * 512)          # standing figure height in a 512-tall cell
G_Y, T_Y = round(0.92 * 512), round(0.92 * 512) - FIG_H


def lift(c):
    c = c.astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    fig = ~((g - r > 60) & (g - b > 60)) & ~((r < 80) & (g > 120) & (b < 120))
    for y in range(c.shape[0]):
        if y > 0.75 * c.shape[0] and (c[y].sum(-1) < 200).mean() > 0.3: fig[y] = False
    fig[:4] = fig[-4:] = False; fig[:, :4] = fig[:, -4:] = False
    hair = (r > 110) & (g < 0.2 * r) & (b < 0.2 * r)                   # red ponytail key -> drop (hood up)
    hl, hn = ndi.label(ndi.binary_dilation(hair, iterations=2))       # only the ponytail itself, not specks in the leather
    if hn: hair &= np.isin(hl, [i + 1 for i, z in enumerate(ndi.sum(hair, hl, range(1, hn + 1))) if z > 60])
    hair = ndi.binary_dilation(hair, iterations=1) & ((r > 70) & (g < 0.35 * r) & (b < 0.35 * r))
    fig &= ~ndi.binary_dilation(hair, iterations=1)
    lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
    fig = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 120])
    # green holes and greenish edge pixels inside the figure (ponytail cut, anti-aliasing) -> nearest figure colour
    solid = fig & ~((g > r + 15) & (g > b + 15))
    full = ndi.binary_fill_holes(ndi.binary_closing(fig, iterations=2)) & ~ndi.binary_dilation(hair, iterations=1)
    iy, ix = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    c = c.copy(); bad = full & ~solid; c[bad] = c[iy[bad], ix[bad]]
    fig = full
    ys, xs = np.where(fig); feet = ys.max()
    return c, fig, feet, xs[ys > feet - 10].mean()


def stand_height(c):
    _, fig, feet, _ = lift(c); return feet - np.where(fig.any(1))[0].min()


def blank(rows):
    im = Image.new('RGB', (1536, 1024), GREEN); d = ImageDraw.Draw(im); boxes = []
    rh = 1024 / len(rows)
    for r, (stance, states) in enumerate(rows):
        cw = 1536 / len(states)
        for c, st in enumerate(states):
            x0, y0, x1, y1 = round(c * cw), round(r * rh), round((c + 1) * cw), round((r + 1) * rh)
            d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=BORDER, width=3)
            d.line([(x0 + 14, y0 + G_Y), (x1 - 14, y0 + G_Y)], fill=LINE, width=3)
            for x in range(x0 + 14, x1 - 14, 16): d.line([(x, y0 + T_Y), (x + 8, y0 + T_Y)], fill=DASH, width=1)
            boxes.append(((stance, st), (x0, y0, x1, y1)))
    return im, boxes


def place(out, c, box, s):
    c, fig, feet, fx = lift(c); x0, y0, x1, y1 = box; cw = x1 - x0
    fi = Image.fromarray(np.dstack([c.astype(np.uint8), (fig * 255).astype(np.uint8)]), 'RGBA')
    fi = fi.resize((round(fi.width * s), round(fi.height * s)), Image.LANCZOS)
    ox, oy = round(x0 + cw / 2 - fx * s), round(y0 + G_Y - feet * s)
    xs = np.where(fig.any(0))[0]; L, R = ox + xs.min() * s, ox + xs.max() * s
    if L < x0 + 6: ox += round(x0 + 6 - L)
    elif R > x1 - 6: ox -= round(R - (x1 - 6))
    out.paste(fi.convert('RGB'), (ox, oy), fi.getchannel('A').point(lambda v: 255 if v > 128 else 0))


def main():
    for sex in 'mf':
        main_ = np.asarray(Image.open(os.path.join(HERE, 'source', f'soldier_{sex}_sheet.png')).convert('RGB').resize((1536, 1024)))
        cell = lambda r, c: main_[r * 256:(r + 1) * 256, c * 384:(c + 1) * 384]
        s_main = FIG_H / stand_height(cell(0, 0))
        for anim, row in (('shield', 0), ('2h', 2), ('reach', 3)):
            out, boxes = blank(M.EXTRA_SHEETS['acolyte'][anim])
            for k, (_, box) in enumerate(boxes): place(out, cell(row, k), box, s_main)
            out.save(os.path.join(HERE, 'templates', f'acolyte_{anim}_{sex}_pose.png'))
        dual = np.asarray(Image.open(os.path.join(HERE, 'source', f'soldier_dual_{sex}_sheet.png')).convert('RGB').resize((1536, 1024)))
        dcell = lambda r, c: dual[r * 512:(r + 1) * 512, c * 512:(c + 1) * 512]
        s_d = FIG_H / stand_height(dcell(0, 0))
        out, boxes = blank(M.EXTRA_SHEETS['acolyte']['dual'])
        for k, (_, box) in enumerate(boxes):
            if k == 3:          # slash 2 = the FINISH figure with its magenta stick removed (as for the Archer)
                f = dcell(1, 1).copy(); fr, fg_, fb = [f[..., i].astype(int) for i in range(3)]
                mag = ndi.binary_dilation((fr > 150) & (fb > 150) & (fg_ < 140), iterations=2)
                f[mag] = GREEN; place(out, f, box, s_d)
            else:
                place(out, dcell(k // 3, k % 3), box, s_d)
        out.save(os.path.join(HERE, 'templates', f'acolyte_dual_{sex}_pose.png'))
    # downed: the Soldier's downed sheet already has both sexes (downed above their stand); ponytails removed
    dn = np.asarray(Image.open(os.path.join(HERE, 'source', 'soldier_downed_sheet.png')).convert('RGB').resize((1536, 1024))).copy()
    r, g, b = [dn[..., i].astype(int) for i in range(3)]
    hair = (r > 110) & (g < 0.2 * r) & (b < 0.2 * r)
    hl, hn = ndi.label(ndi.binary_dilation(hair, iterations=2))
    if hn: hair &= np.isin(hl, [i + 1 for i, z in enumerate(ndi.sum(hair, hl, range(1, hn + 1))) if z > 60])
    gone = ndi.binary_dilation(hair, iterations=1) & ((r > 70) & (g < 0.35 * r) & (b < 0.35 * r))
    dn[gone] = GREEN
    # the ponytail's dark outline left floating on the green: thin dark strokes near where it was
    r, g, b = [dn[..., i].astype(int) for i in range(3)]
    fig = ~((g - r > 60) & (g - b > 60))
    near = ndi.binary_dilation(gone, iterations=6) & ~gone
    thin = fig & ~ndi.binary_opening(fig, iterations=2)
    dn[near & thin & (dn.astype(int).sum(-1) < 330)] = GREEN
    dn[ndi.binary_dilation(gone, iterations=10) & (g > r + 25) & (g > b + 25)] = GREEN     # faint green-tinted ghosts
    Image.fromarray(dn).save(os.path.join(HERE, 'templates', 'acolyte_downed_pose.png'))
    print('ok')


if __name__ == '__main__':
    main()
