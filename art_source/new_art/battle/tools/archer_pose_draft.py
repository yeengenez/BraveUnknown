"""Archer pose draft (user, 2026-11-24): grey mannequins on the archer template, one per cell, showing ChatGPT the exact
poses, which arm is NEAR (in front of the body, darker) and which is FAR (behind, lighter), and which stick each hand
holds: cyan = the bow / the far (left) hand, magenta = the arrow or the crossbow stock / the near (right) hand.
Hood up (user's headgear choice c), face in the yellow key, quiver marker = blue stick on the back.
Cell coords: 384 x 512, head-top line y=72, ground line y=471."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAR, BODY, NEAR, OUT = (178, 178, 190), (150, 150, 165), (110, 110, 128), (45, 45, 55)
HOOD, FACE, CYAN, MAG, BLUE = (62, 98, 52), (235, 215, 20), (0, 255, 255), (255, 0, 255), (0, 0, 255)

STAND_LEGS = dict(Hn=(176, 277), Hf=(208, 272), Kn=(160, 370), Fn=(150, 466), Kf=(222, 368), Ff=(236, 466))
WIDE_LEGS = dict(Hn=(174, 277), Hf=(206, 274), Kn=(150, 372), Fn=(124, 466), Kf=(262, 362), Ff=(262, 466))   # front knee bent
UP = dict(head=(198, 108), Sn=(166, 160), Sf=(212, 156))
POSES = {
    # bow row
    (0, 0): dict(UP, **STAND_LEGS, En=(150, 228), Wn=(148, 292), Ef=(234, 222), Wf=(242, 284),
                 rods=[('far', CYAN, (233, 158), (252, 410))], quiver=True),
    (0, 1): dict(head=(200, 110), Sn=(166, 160), Sf=(210, 158), **WIDE_LEGS, En=(124, 150), Wn=(214, 148),
                 Ef=(264, 158), Wf=(318, 156), rods=[('far', CYAN, (318, 26), (318, 290)), ('near', MAG, (206, 149), (336, 156))], quiver=True),
    (0, 2): dict(head=(200, 110), Sn=(166, 160), Sf=(210, 158), **WIDE_LEGS, En=(126, 150), Wn=(96, 140), open_near=True,
                 Ef=(264, 158), Wf=(318, 156), rods=[('far', CYAN, (318, 26), (318, 290))], quiver=True),
    (0, 3): dict(head=(176, 122), Sn=(150, 170), Sf=(194, 164), Hn=(172, 282), Hf=(204, 280), Kn=(150, 376), Fn=(136, 466),
                 Kf=(230, 380), Ff=(252, 466), En=(126, 222), Wn=(108, 268), Ef=(222, 228), Wf=(246, 268),
                 rods=[('far', CYAN, (236, 150), (256, 400))], quiver=True),
    # crossbow row
    (1, 0): dict(UP, **STAND_LEGS, En=(158, 222), Wn=(186, 262), Ef=(236, 216), Wf=(238, 268),
                 rods=[('both', MAG, (166, 258), (292, 272))], quiver=True),
    (1, 1): dict(head=(204, 116), Sn=(166, 162), Sf=(210, 158), **WIDE_LEGS, En=(176, 206), Wn=(196, 170),
                 Ef=(238, 204), Wf=(252, 174), rods=[('both', MAG, (166, 168), (304, 172))], quiver=True),
    (1, 2): dict(head=(200, 114), Sn=(162, 162), Sf=(206, 158), **WIDE_LEGS, En=(172, 204), Wn=(192, 166),
                 Ef=(234, 200), Wf=(250, 160), rods=[('both', MAG, (166, 172), (300, 148))], quiver=True),
    (1, 3): dict(head=(176, 122), Sn=(150, 170), Sf=(194, 164), Hn=(172, 282), Hf=(204, 280), Kn=(150, 376), Fn=(136, 466),
                 Kf=(230, 380), Ff=(252, 466), En=(150, 226), Wn=(176, 238), Ef=(214, 214), Wf=(204, 210),
                 rods=[('both', MAG, (162, 262), (230, 146))], quiver=True),
}


def limb(d, a, b, w, col):
    d.line([a, b], fill=OUT, width=w + 4); d.line([a, b], fill=col, width=w)
    for p in (a, b):
        r = w / 2; d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def fist(d, p, col, r=11):
    d.ellipse([p[0] - r - 2, p[1] - r - 2, p[0] + r + 2, p[1] + r + 2], fill=OUT); d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def draw(d, P, ox, oy):
    o = lambda p: (p[0] + ox, p[1] + oy)
    q = {k: o(v) for k, v in P.items() if isinstance(v, tuple)}
    rod = lambda a, b, col: d.line([o(a), o(b)], fill=col, width=9)
    if P.get('quiver'):                                       # on the back, behind everything
        sn = q['Sn']; d.line([(sn[0] - 22, sn[1] - 44), (sn[0] + 26, sn[1] + 100)], fill=BLUE, width=16)
    limb(d, q['Hf'], q['Kf'], 30, FAR); limb(d, q['Kf'], q['Ff'], 24, FAR)
    d.ellipse([q['Ff'][0] - 6, q['Ff'][1] - 8, q['Ff'][0] + 22, q['Ff'][1] + 4], fill=FAR, outline=OUT, width=2)
    limb(d, q['Sf'], q['Ef'], 22, FAR); limb(d, q['Ef'], q['Wf'], 18, FAR)
    for who, col, a, b in P['rods']:
        if who == 'far': rod(a, b, col)
    if P.get('open_far'):
        w = q['Wf']; d.polygon([(w[0] - 6, w[1] - 8), (w[0] + 16, w[1] - 14), (w[0] + 18, w[1] + 2), (w[0] - 6, w[1] + 8)], fill=FAR, outline=OUT)
    else:
        fist(d, q['Wf'], FAR)
    d.polygon([(q['Sn'][0] - 8, q['Sn'][1] - 4), (q['Sf'][0] + 8, q['Sf'][1] - 4), (q['Sf'][0] + 6, q['Sf'][1] + 44),
               (q['Hf'][0] + 6, q['Hf'][1] + 6), (q['Hn'][0] - 6, q['Hn'][1] + 6), (q['Sn'][0] - 12, q['Sn'][1] + 44)],
              fill=BODY, outline=OUT, width=3)
    h = q['head']                                             # hood up, face open toward the right
    d.ellipse([h[0] - 38, h[1] - 40, h[0] + 34, h[1] + 36], fill=HOOD, outline=OUT, width=3)
    d.polygon([(h[0] - 34, h[1] + 10), (h[0] - 10, h[1] + 48), (h[0] + 20, h[1] + 40), (h[0] - 20, h[1] + 20)], fill=HOOD, outline=OUT)
    d.polygon([(h[0] + 4, h[1] - 14), (h[0] + 24, h[1] - 10), (h[0] + 28, h[1] + 8), (h[0] + 18, h[1] + 24), (h[0] + 6, h[1] + 20)],
              fill=FACE, outline=OUT)                         # face: small, at the front of the hood
    d.line([(h[0] + 14, h[1] - 2), (h[0] + 22, h[1] - 2)], fill=OUT, width=2)
    limb(d, q['Hn'], q['Kn'], 30, NEAR); limb(d, q['Kn'], q['Fn'], 24, NEAR)
    d.ellipse([q['Fn'][0] - 6, q['Fn'][1] - 8, q['Fn'][0] + 22, q['Fn'][1] + 4], fill=NEAR, outline=OUT, width=2)
    limb(d, q['Sn'], q['En'], 22, NEAR); limb(d, q['En'], q['Wn'], 18, NEAR)
    for who, col, a, b in P['rods']:
        if who in ('near', 'both'): rod(a, b, col)
    if P.get('open_near'):                                    # open hand flung back after the release
        w = q['Wn']; d.polygon([(w[0] + 6, w[1] - 8), (w[0] - 16, w[1] - 14), (w[0] - 18, w[1] + 2), (w[0] + 6, w[1] + 8)], fill=NEAR, outline=OUT)
    else:
        fist(d, q['Wn'], NEAR)
    if any(who == 'both' for who, *_ in P['rods']): fist(d, q['Wf'], FAR)


LOW = dict(Hn=(172, 290), Hf=(210, 288), Kn=(140, 372), Fn=(118, 466), Kf=(244, 372), Ff=(266, 466))
LUNGE = dict(Hn=(170, 296), Hf=(204, 292), Kn=(120, 384), Fn=(80, 466), Kf=(270, 372), Ff=(276, 466))
UPL = dict(head=(196, 122), Sn=(164, 172), Sf=(212, 168))
UPD = dict(head=(198, 126), Sn=(164, 178), Sf=(208, 174))
RECOIL = dict(head=(176, 122), Sn=(150, 170), Sf=(194, 164), Hn=(172, 282), Hf=(204, 280), Kn=(150, 376), Fn=(136, 466),
              Kf=(230, 380), Ff=(252, 466))
NEAR_LOW = dict(En=(146, 236), Wn=(132, 290))
FAR_LOW = dict(Ef=(238, 236), Wf=(256, 288))
# dual daggers (2 x 3 cells of 512): the finished Soldier dual poses - magenta = NEAR hand, cyan = FAR hand
DUAL = {
    (0, 0): dict(UPL, **LOW, **NEAR_LOW, Ef=(236, 232), Wf=(254, 286), quiver=True,
                 rods=[('near', MAG, (150, 270), (96, 350)), ('far', CYAN, (240, 268), (300, 350))]),
    (0, 1): dict(UPL, **LOW, **NEAR_LOW, Ef=(238, 118), Wf=(230, 62), quiver=True,
                 rods=[('near', MAG, (150, 270), (96, 350)), ('far', CYAN, (246, 68), (160, 30))]),
    (0, 2): dict(head=(200, 124), Sn=(166, 172), Sf=(212, 168), **LOW, **NEAR_LOW, Ef=(244, 226), Wf=(262, 282), quiver=True,
                 rods=[('near', MAG, (150, 270), (96, 350)), ('far', CYAN, (250, 262), (318, 360))]),
    (1, 0): dict(UPD, **LUNGE, En=(120, 186), Wn=(80, 196), **FAR_LOW, quiver=True,
                 rods=[('near', MAG, (64, 192), (176, 232)), ('far', CYAN, (262, 300), (316, 368))]),
    (1, 1): dict(UPD, **LUNGE, En=(122, 160), Wn=(80, 140), **FAR_LOW, quiver=True,
                 rods=[('near', MAG, (96, 146), (46, 129)), ('far', CYAN, (262, 300), (316, 368))]),
    (1, 2): dict(RECOIL, En=(130, 226), Wn=(124, 280), Ef=(222, 228), Wf=(246, 270), quiver=True,
                 rods=[('near', MAG, (132, 264), (90, 340)), ('far', CYAN, (240, 256), (292, 340))]),
}
# one dagger (2 x 2 cells of 768 x 512): dagger in the NEAR hand (magenta), the FAR hand open and empty
ONE = {
    (0, 0): dict(UP, Hn=(174, 280), Hf=(208, 276), Kn=(150, 372), Fn=(132, 466), Kf=(236, 370), Ff=(254, 466),
                 En=(156, 232), Wn=(184, 262), Ef=(246, 200), Wf=(276, 190), open_far=True, quiver=True,
                 rods=[('near', MAG, (172, 262), (246, 254))]),
    (0, 1): dict(head=(192, 126), Sn=(160, 176), Sf=(206, 172), Hn=(170, 290), Hf=(204, 288), Kn=(136, 378), Fn=(110, 466),
                 Kf=(250, 376), Ff=(262, 466), En=(132, 214), Wn=(118, 250), Ef=(244, 214), Wf=(272, 206), open_far=True,
                 quiver=True, rods=[('near', MAG, (104, 254), (176, 236))]),
    (1, 0): dict(UPD, **LUNGE, En=(214, 214), Wn=(274, 212), Ef=(214, 232), Wf=(198, 268), open_far=True, quiver=True,
                 rods=[('near', MAG, (258, 212), (340, 212))]),
    (1, 1): dict(RECOIL, En=(132, 226), Wn=(140, 272), Ef=(222, 222), Wf=(250, 250), open_far=True, quiver=True,
                 rods=[('near', MAG, (126, 266), (200, 290))]),
}


if __name__ == '__main__':
    # bow + crossbow sheet (2 x 4, done 2026-11-25)
    im = Image.open(os.path.join(HERE, 'templates', 'archer_template.png')).convert('RGB'); d = ImageDraw.Draw(im)
    for (r, c), P in POSES.items(): draw(d, P, c * 384, r * 512)
    im.save(os.path.join(HERE, 'refs', 'archer_pose_draft.png'))
    # dagger sheet (user, 2026-11-25): rows of 341 px - one dagger (draft mannequins) | dual stand, ready, slash 1, slash 2 |
    # dual finish, hit. The dual cells show the Soldier's finished dual figures (same poses as the Soldier, so its drawn
    # slash arcs fit the Archer too), arcs faint, with a blue quiver bar.
    import numpy as np
    from scipy import ndimage as ndi
    im = Image.open(os.path.join(HERE, 'templates', 'archer_dagger_template.png')).convert('RGB')
    RH = 1024 / 3; G = 0.92 * RH; K = RH / 512                         # ground line in the cell; mannequin scale
    for c, P in enumerate([ONE[(0, 0)], ONE[(0, 1)], ONE[(1, 0)], ONE[(1, 1)]]):
        tmp = Image.new('RGBA', (384, 512), (0, 0, 0, 0)); draw(ImageDraw.Draw(tmp), P, 0, 0)
        tmp = tmp.resize((round(384 * K), round(512 * K)), Image.LANCZOS)
        im.paste(tmp.convert('RGB'), (round(c * 384 + (384 - tmp.width) / 2), 0), tmp.getchannel('A').point(lambda v: 255 if v > 110 else 0))
    sol = np.asarray(Image.open(os.path.join(HERE, 'source', 'soldier_dual_m_sheet.png')).convert('RGB').resize((1536, 1024), Image.LANCZOS)).astype(int)
    fx = np.asarray(Image.open(os.path.join(HERE, 'source', 'soldier_dual_m_fx.png')).convert('RGBA').resize((1536, 1024), Image.LANCZOS)).astype(float)
    def figure(k):
        sr, sc = divmod(k, 3)
        cell = sol[sr * 512 + 4:sr * 512 + 508, sc * 512 + 4:sc * 512 + 508]; f = fx[sr * 512 + 4:sr * 512 + 508, sc * 512 + 4:sc * 512 + 508]
        r_, g_, b_ = cell[..., 0], cell[..., 1], cell[..., 2]
        fig = ~((g_ - r_ > 60) & (g_ - b_ > 60))
        dark = cell.sum(-1) < 200
        for y in range(fig.shape[0]):                                   # drop the ground line rows
            if dark[y].mean() > 0.3: fig[y] = False
        fig &= ~((r_ < 80) & (g_ > 120) & (b_ < 120))                    # dashed guide (mid green)
        lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
        fig = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 300])
        rgb = cell.astype(float).copy()
        if k == 3:                                                      # torso hidden under the waist sweep: grey mannequin
            from PIL import ImageDraw as _D
            pm = Image.new('L', (504, 504), 0)
            _D.Draw(pm).polygon([(x - 4, y - 4) for x, y in [(225, 248), (320, 243), (345, 268), (352, 300), (340, 312), (190, 312), (192, 285)]], fill=1)
            hid = np.asarray(pm) > 0
            rgb[hid] = (150, 150, 165); edge = hid & ~ndi.binary_erosion(hid, iterations=2); rgb[edge] = (45, 45, 55)
            fig = fig | hid
        return rgb, fig, fig
    _, _, f0 = figure(0); ys = np.where(f0.any(1))[0]; S = (0.78 * RH) / (ys.max() - ys.min())
    cells_ = [(1, c) for c in range(4)] + [(2, 0), (2, 1)]
    for k, (tr, tc) in enumerate(cells_):
        rgb, show, fig = figure(k)
        cw = 1536 / (4 if tr == 1 else 2)
        ys, xs = np.where(fig); feet = ys.max(); x0, x1 = xs.min(), xs.max()
        ox = round(tc * cw + cw / 2 - (x0 + x1) / 2 * S); oy = round(tr * RH + G - feet * S)
        top = ys.min(); tx = np.where(fig[top:top + 4].any(0))[0].mean()
        hx = np.where(fig[top:top + 50].any(0))[0]; hx = hx[np.abs(hx - tx) < 34]   # the helmet, not a raised arm
        dd = ImageDraw.Draw(im)                                       # quiver bar behind the near shoulder, under the figure
        bx, by = ox + (hx.min() - 16) * S, oy + (top + 30) * S
        dd.line([(bx, by), (bx + 54 * S, by + 130 * S)], fill=(0, 0, 255), width=max(6, round(15 * S)))
        fi = Image.fromarray(np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (show * 255).astype(np.uint8)]), 'RGBA')
        fi = fi.resize((round(fi.width * S), round(fi.height * S)), Image.LANCZOS)
        im.paste(fi.convert('RGB'), (ox, oy), fi.getchannel('A').point(lambda v: 255 if v > 110 else 0))
    out = os.path.join(HERE, 'refs', 'archer_dagger_pose_draft.png'); im.save(out); print(out)
