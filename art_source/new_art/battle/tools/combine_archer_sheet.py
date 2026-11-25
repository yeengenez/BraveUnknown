"""All male Archer poses on ONE sheet (user, 2026-11-25: "Combine archer sheet into one but only Male Archer").
Figures are lifted from the three finished sheets, scaled to one size (the bow sheet's) and stood on the ground line of
fresh 512-tall cells; slash arcs are not included (they are a separate layer).
Rows: bow (4) | crossbow (4) | one dagger (4) | dual stand, ready, slash 1 + downed | dual slash 2, finish, hit (wide cells).
Output: source/archer_m_all_sheet.png (1536 x 2560) + archer_m_all_layout.json (cell -> stance/state)."""
import os, sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import make_refs as M
GREEN, LINE, DASH, BORDER = (0, 255, 0), (20, 20, 20), (0, 200, 60), (0, 190, 0)
G_Y, T_Y = round(0.92 * 512), round(0.92 * 512 - 0.78 * 512)


def lift(img, box):
    c = np.asarray(img.crop(box).convert('RGB')).astype(int); r, g, b = c[..., 0], c[..., 1], c[..., 2]
    fig = ~((g - r > 60) & (g - b > 60)) & ~((r < 80) & (g > 120) & (b < 120))
    H = c.shape[0]
    for y in range(H):
        if y > 0.8 * H and (c[y].sum(-1) < 200).mean() > 0.3: fig[y] = False
    fig[:4] = fig[-4:] = False; fig[:, :4] = fig[:, -4:] = False
    lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
    fig = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 150])
    ys, xs = np.where(fig); feet = ys.max(); fx = xs[ys > feet - 14].mean()
    return c, fig, feet, fx


def body_height(img, box):
    c, fig, feet, _ = lift(img, box); return feet - np.where(fig.any(1))[0].min()


src = lambda n: Image.open(os.path.join(HERE, 'source', n)).convert('RGB')
bow, dag, down = src('archer_m_sheet.png').resize((1536, 1024)), src('archer_dagger_m_sheet.png').resize((1536, 1024)), src('archer_downed_sheet.png').resize((1536, 1024))
bcell = {(st, sa): b for _, _, st, sa, b in M.cells(M.CLASSES['archer'], 'archer')}
dcell = {(st, sa): b for _, _, st, sa, b in M.cells(M.EXTRA_SHEETS['archer']['dagger'], 'archer')}
ref = body_height(bow, bcell[('bow', 'stand')])
s_dag = ref / body_height(dag, dcell[('1h', 'stand')])
s_down = ref / body_height(down, (0, 512, 512, 1024))        # the downed sheet's male standing reference
ROWS = [[(bow, bcell[('bow', s)], 1.0, 'bow', s) for s in ('stand', 'nock', 'attack', 'hit')],
        [(bow, bcell[('crossbow', s)], 1.0, 'crossbow', s) for s in ('stand', 'aim', 'attack', 'hit')],
        [(dag, dcell[('1h', s)], s_dag, '1h', s) for s in ('stand', 'ready', 'attack', 'hit')],
        [(dag, dcell[('dual', s)], s_dag, 'dual', s) for s in ('stand', 'ready', 'slash_left')]
        + [(down, (0, 0, 512, 512), s_down, 'downed', 'downed')],
        [(dag, dcell[('dual', s)], s_dag, 'dual', s) for s in ('slash_right', 'finish', 'hit')]]
out = Image.new('RGB', (1536, 512 * len(ROWS)), GREEN); d = ImageDraw.Draw(out); layout = []
for r, row in enumerate(ROWS):
    cw = 1536 / len(row)
    for c, (img, box, s, stance, state) in enumerate(row):
        x0, y0 = round(c * cw), r * 512
        d.rectangle([x0, y0, round((c + 1) * cw) - 1, y0 + 511], outline=BORDER, width=3)
        d.line([(x0 + 14, y0 + G_Y), (round((c + 1) * cw) - 14, y0 + G_Y)], fill=LINE, width=3)
        for x in range(x0 + 14, round((c + 1) * cw) - 14, 16): d.line([(x, y0 + T_Y), (x + 8, y0 + T_Y)], fill=DASH, width=1)
        cell, fig, feet, fx = lift(img, box)
        fi = Image.fromarray(np.dstack([cell.astype(np.uint8), (fig * 255).astype(np.uint8)]), 'RGBA')
        if abs(s - 1) > 0.01: fi = fi.resize((round(fi.width * s), round(fi.height * s)), Image.LANCZOS)
        ox, oy = round(x0 + cw / 2 - fx * s), round(y0 + G_Y - feet * s)
        xs_ = np.where(fig.any(0))[0]; L, R = ox + xs_.min() * s, ox + xs_.max() * s   # keep the sticks inside the cell
        if L < x0 + 6: ox += round(x0 + 6 - L)
        elif R > x0 + cw - 6: ox -= round(R - (x0 + cw - 6))
        out.paste(fi.convert('RGB'), (ox, oy), fi.getchannel('A').point(lambda v: 255 if v > 128 else 0))
        layout.append(dict(row=r, col=c, box=[x0, y0, round((c + 1) * cw), y0 + 512], stance=stance, state=state))
out.save(os.path.join(HERE, 'source', 'archer_m_all_sheet.png'))
json.dump(layout, open(os.path.join(HERE, 'source', 'archer_m_all_layout.json'), 'w'), indent=1)
print('scales: dagger', round(s_dag, 3), 'downed', round(s_down, 3))
