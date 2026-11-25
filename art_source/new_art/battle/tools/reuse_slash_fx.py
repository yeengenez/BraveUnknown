"""Reuse the Soldier's drawn slash arc + weapon smear on another class whose dual poses copy the Soldier's
(user, 2026-11-25: the Archer's slash 1 / slash 2 had no wave). The Soldier's effect cell (source/soldier_dual_<sex>_fx.png)
is scaled by the ratio of the two classes' dual STAND figure heights and placed so the Soldier's feet land on the
target figure's feet. Arcs reach past the target cell, so each effect is saved whole with its offset from the cell's
top-left: source/<cls>_dagger_<sex>_fx/<state>.png + offsets.json. Also writes a preview of the sheet with the effects.
Usage: python3 tools/reuse_slash_fx.py archer m"""
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import make_refs as M


# hand-placed corrections after the feet alignment, in target-cell px (the smear must start at the swinging hand)
NUDGE = {('archer', 'm', 'slash_left'): (-28, -8),
         ('archer', 'm', 'slash_right'): (2, -24)}   # the arm was raised 12 deg to the finish angle (archer_fix_slash2_arm.py)   # user, 2026-11-25: "on pose 7, move slash to match the hands"


def figure(cell):
    a = cell.astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fig = ~((g - r > 60) & (g - b > 60)) & ~((r < 80) & (g > 120) & (b < 120))
    for y in range(fig.shape[0]):
        if (a[y].sum(-1) < 200).mean() > 0.3: fig[y] = False          # ground line
    fig[:6] = fig[-6:] = False; fig[:, :6] = fig[:, -6:] = False
    lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
    fig = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 300])
    ys, xs = np.where(fig); feet = ys.max()
    fx_ = xs[ys > feet - 14].mean()
    return ys.min(), feet, fx_


def main(cls, sex):
    sol = np.asarray(Image.open(os.path.join(HERE, 'source', f'soldier_dual_{sex}_sheet.png')).convert('RGB'))
    sfx = np.asarray(Image.open(os.path.join(HERE, 'source', f'soldier_dual_{sex}_fx.png')).convert('RGBA'))
    k = sol.shape[1] / 1536
    scell = lambda r, c: (round(c * 512 * k), round(r * 512 * k), round((c + 1) * 512 * k), round((r + 1) * 512 * k))
    sbox = {'stand': scell(0, 0), 'slash_left': scell(0, 2), 'slash_right': scell(1, 0)}
    tgt = np.asarray(Image.open(os.path.join(HERE, 'source', f'{cls}_dagger_{sex}_sheet.png')).convert('RGB'))
    kx, ky = tgt.shape[1] / 1536, tgt.shape[0] / 1024
    tbox = {(st, sa): (round(x0 * kx), round(y0 * ky), round(x1 * kx), round(y1 * ky))
            for _, _, st, sa, (x0, y0, x1, y1) in M.cells(M.EXTRA_SHEETS[cls]['dagger'], cls)}
    crop = lambda a, b: a[b[1]:b[3], b[0]:b[2]]
    st, sf, _ = figure(crop(sol, sbox['stand'])); tt, tf, _ = figure(crop(tgt, tbox[('dual', 'stand')]))
    s = (tf - tt) / (sf - st)
    outd = os.path.join(HERE, 'source', f'{cls}_dagger_{sex}_fx'); os.makedirs(outd, exist_ok=True)
    offs, prev = {}, Image.fromarray(tgt).convert('RGBA')
    for state in ('slash_left', 'slash_right'):
        _, sfeet, sfx_ = figure(crop(sol, sbox[state])); _, tfeet, tfx_ = figure(crop(tgt, tbox[('dual', state)]))
        f = crop(sfx, sbox[state]).astype(np.float32); al = f[..., 3:] / 255
        W, H = round(f.shape[1] * s), round(f.shape[0] * s)
        pm = np.dstack([np.asarray(Image.fromarray(f[..., i] * al[..., 0]).resize((W, H), Image.BOX)) for i in range(3)])
        am = np.asarray(Image.fromarray(al[..., 0]).resize((W, H), Image.BOX))
        rgb = pm / np.maximum(am, 1e-6)[..., None]
        lay = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(am * 255, 0, 255)]).astype(np.uint8), 'RGBA')
        ox, oy = round(tfx_ - sfx_ * s), round(tfeet - sfeet * s)          # cell-local offset of the effect's top-left
        nx, ny = NUDGE.get((cls, sex, state), (0, 0)); ox += nx; oy += ny
        lay.save(os.path.join(outd, f'{state}.png')); offs[state] = [ox, oy]
        b = tbox[('dual', state)]; prev.alpha_composite(lay, (b[0] + ox, b[1] + oy)) if b[0] + ox >= 0 else None
        if b[0] + ox < 0:
            c_ = lay.crop((-(b[0] + ox), 0, lay.width, lay.height)); prev.alpha_composite(c_, (0, b[1] + oy))
    json.dump({'scale': round(s, 4), 'offsets': offs}, open(os.path.join(outd, 'offsets.json'), 'w'), indent=1)
    prev.convert('RGB').save(os.path.join(HERE, f'review_{cls}_dagger_fx.png'))
    print('scale', round(s, 3), offs)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
