"""New-art battle sprites: cut a ChatGPT sheet (templates/<class>_template.png filled in, guide rods in the fists)
into per-state body layers + grip data, then build the sprites with the existing weapon/frame code.

  python3 process_battle.py soldier            # both sexes
Writes
  layers/<class>_<sex>_<stance>_<state>_fixed.png / _skin.png   (skin = value map, LA; tinted with the portrait ramp)
  grips/<class>_<sex>_<stance>_<state>.json
  sprites/<class>_<sex>_<loadout>_<state>.png   (399x270, same frame as the Legacy sprites: feet at y~250, centred)
  review_<class>.png

Reused, not rewritten: rod reading, grip fitting and rod inpainting from battle_sprites/poses/process_pose.py, the
weapons and frame() from battle_sprites/animation/anim.py (scripts are not Legacy; only the Canva images are).
New here: cutting a sheet, the yellow skin key, and a SAMPLE hair layer (the portrait hair scaled onto the sprite
head - a stand-in until sprite hair is drawn).
"""
import os, sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
BS = os.path.join(HERE, '..', '..', 'battle_sprites')
PORT = os.path.join(HERE, '..', 'portraits')
cwd = os.getcwd()
sys.path.insert(0, os.path.join(BS, 'poses')); sys.path.insert(0, os.path.join(BS, 'grip_bodies'))
sys.path.insert(0, os.path.join(BS, 'animation')); sys.path.insert(0, PORT); sys.path.insert(0, HERE)
import process_pose as PP          # (chdirs to poses/)
import anim as A                   # (chdirs to animation/)
from skin_layers import tint
import finish
from make_refs import CLASSES, cells
os.chdir(cwd)

FIG_H = 190                         # stand figure height in sprite pixels (Legacy: ~197 incl. outline)
BODY_W, BODY_H, FEET_Y = 400, 230, 226
CANVAS_FEET = (199, 250)            # where the stand figure's feet go on the 399x270 sprite

def one_hand(w, shield=False):      # same rule as poses/compose.py: weapon in the right hand ('back')
    st = [('back', w, 'under')] + ([('front', 'shield', 'over')] if shield else [])
    at = ([('front', 'shield', 'over')] if shield else []) + [('back', w, 'over')]
    return {'stand': st, 'attack': at, 'hit': st}
LOADOUTS = {
    'soldier': [('longsword', '1h', one_hand('longsword')), ('sword_shield', '1h', one_hand('longsword', True)),
                ('greataxe', '2h', {s: [('back', 'greataxe', 'over')] for s in ('stand', 'attack', 'hit')}),
                ('longspear', 'reach', {s: [('back', 'longspear', 'over')] for s in ('stand', 'attack', 'hit')})],
}
SAMPLE_HAIR = {'m': [('sidepart', 'brown', 'fair'), ('messy', 'black', 'tan'), ('slicked', 'auburn', 'deep')],
               'f': [('ponytail', 'auburn', 'fair'), ('bob', 'black', 'tan'), ('braids', 'blonde', 'bronze')]}


# ---------------------------------------------------------------- cutting
def cut_cell(a, box):
    x0, y0, x1, y1 = box
    c = a[y0 + 4:y1 - 4, x0 + 4:x1 - 4].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    fg = ~((g - r > 50) & (g - b > 50))
    # ground line: long dark horizontal runs in the lower part of the cell
    dark = fg & (c.max(2) < 90)
    H = c.shape[0]
    for y in range(int(H * 0.8), H):
        row = dark[y]; runs = np.split(np.arange(len(row)), np.where(np.diff(row.astype(int)) != 0)[0] + 1)
        for run in runs:
            if row[run[0]] and len(run) > 60: fg[max(0, y - 1):y + 2, run] = False
    # ...and its short pieces left under the feet: every dark pixel on the ground row and just below it
    linepx = (c.max(2) < 130) & (r < 45) & (b < 45)          # the line: dark green, black where it meets the feet
    lower = linepx[int(H * 0.8):]
    if lower.any():
        yg = int(H * 0.8) + int(np.argmax(lower.sum(1)))
        band = np.zeros_like(fg); band[yg - 2:yg + 3] = True
        fg &= ~(band & (c.max(2) < 100))
    lab, n = ndi.label(fg, np.ones((3, 3))); sz = ndi.sum(fg, lab, range(1, n + 1))
    fg = np.isin(lab, [i + 1 for i in range(n) if sz[i] > 40])
    return c, fg


def figure_height(c, fg):
    rods = PP.rod_mask(c) | PP.cyan_mask(c)
    ys = np.where((fg & ~ndi.binary_dilation(rods, iterations=2)).any(1))[0]
    return ys.max() - ys.min(), ys.max()


def to_body(c, fg, s, ground):
    """Scale a cell (premultiplied box filter) onto a white BODY_W x BODY_H canvas, ground at FEET_Y."""
    al = fg.astype(np.float32)
    W, H = round(c.shape[1] * s), round(c.shape[0] * s)
    pm = [np.asarray(Image.fromarray((c[..., k] * al).astype(np.float32)).resize((W, H), Image.BOX)) for k in range(3)]
    am = np.asarray(Image.fromarray(al).resize((W, H), Image.BOX))
    rgb = np.dstack(pm) / np.maximum(am, 1e-6)[..., None]
    on = am > 0.5
    out = np.full((BODY_H, BODY_W, 3), 255, np.uint8)
    oy = FEET_Y - round(ground * s); ox = (BODY_W - W) // 2
    ys, xs = np.where(on)
    ty, tx = ys + oy, xs + ox; k = (ty >= 0) & (ty < BODY_H) & (tx >= 0) & (tx < BODY_W)
    out[ty[k], tx[k]] = np.clip(rgb[ys[k], xs[k]], 0, 255).astype(np.uint8)
    mask = np.zeros((BODY_H, BODY_W), bool); mask[ty[k], tx[k]] = True     # the real silhouette (white highlights stay)
    return out, mask


def clean_rods(a, rods, on):
    """PP.clean inpaints the rod pixels from their neighbours; on its own that leaves grey smears where a rod stuck
    out over the background. The coverage (body / background) is inpainted the same way, and rod pixels that come
    out as background are cleared."""
    import cv2
    zone = ndi.binary_dilation(rods, iterations=3)
    mm = ndi.binary_dilation(rods, iterations=1) | zone & (a[..., 0] - a[..., 1] > 6) & (a[..., 2] - a[..., 1] > 6)
    mm |= zone & (a[..., 1] - a[..., 0] > 25) & (a[..., 2] - a[..., 0] > 25)          # cyan glints left on the fist
    out = cv2.inpaint(a.astype(np.uint8), mm.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    cover = (on & ~mm).astype(np.uint8) * 255
    est = cv2.inpaint(cover, mm.astype(np.uint8) * 255, 4, cv2.INPAINT_TELEA)
    gone = mm & (est < 128)
    out[gone] = 255; on = on & ~gone
    # leftover ground-line slivers: thin flat pieces at the very bottom
    lab, n = ndi.label(on, np.ones((3, 3)))
    for i, sl in enumerate(ndi.find_objects(lab)):
        h = sl[0].stop - sl[0].start
        if sl[0].start >= FEET_Y - 6 and h <= 3: on[lab == i + 1] = False
    return out, on


# ---------------------------------------------------------------- skin key (shades of yellow/orange)
def skin_split(a, fgm, grips):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    key = fgm & (r > 120) & (g > 0.5 * r) & (b < 0.55 * r) & (r - b > 70)
    lab, n = ndi.label(key, np.ones((3, 3)))
    ys = np.where(fgm.any(1))[0]; top, bot = ys.min(), ys.max(); Hh = bot - top
    keep = []
    for i in range(1, n + 1):
        m = lab == i; sz = m.sum()
        if sz < 6: continue
        cy, cx = np.argwhere(m).mean(0)
        head = (cy - top) / Hh < 0.24 and sz >= 25
        hand = any(m[max(0, int(p[1]) - 6):int(p[1]) + 7, max(0, int(p[0]) - 6):int(p[0]) + 7].any() for p in grips)
        if head or hand: keep.append(i)
    m = np.isin(lab, keep)
    lum = a[..., 0] * 0.35 + a[..., 1] * 0.45 + a[..., 2] * 0.2
    med = np.median(lum[m]) if m.any() else 180
    val = np.clip(204 + (lum - med) * 1.15, 40, 245)
    fixed = np.dstack([a, (fgm & ~m) * 255]).astype(np.uint8)
    skin = np.zeros(a.shape[:2] + (2,), np.uint8); skin[..., 0] = val.astype(np.uint8); skin[..., 1] = m * 255
    # head box for the hair: the skin blob at the top
    hl, hn = ndi.label(m & (np.arange(a.shape[0])[:, None] < top + 0.3 * Hh))
    head = None
    if hn:
        big = np.argmax(ndi.sum(m, hl, range(1, hn + 1))) + 1; hy, hx = np.where(hl == big)
        head = dict(top=int(hy.min()), left=int(hx.min()), right=int(hx.max()), bottom=int(hy.max()))
    return fixed, skin, head


# ---------------------------------------------------------------- sample hair (portrait hair scaled to the sprite head)
PH = {}
def portrait_head(sex):
    if sex not in PH:
        B = np.asarray(Image.open(os.path.join(PORT, f'{sex}_head_skin.png')))[..., 3] > 0
        ys, xs = np.where(B[:100]); PH[sex] = dict(top=34, left=int(xs.min()), right=int(xs.max()))
    return PH[sex]

def hair_layer(sex, style, ramp, head):
    hv = np.asarray(Image.open(os.path.join(PORT, f'{sex}_hair_{style}.png')).convert('RGBA')).astype(np.float32)
    P = portrait_head(sex)
    k = (head['right'] - head['left'] + 3) / (P['right'] - P['left'])
    W = max(1, round(200 * k))
    al = hv[..., 3] / 255
    v = np.asarray(Image.fromarray(hv[..., 0] * al).resize((W, W), Image.BOX))
    am = np.asarray(Image.fromarray(al).resize((W, W), Image.BOX))
    val = v / np.maximum(am, 1e-6)
    rgb = finish.ramp_rgb(finish.PAL['hair'][ramp], val)
    out = np.dstack([rgb, (am > 0.5) * 255]).astype(np.uint8)
    ox = head['left'] - 1 - round(P['left'] * k); oy = head['top'] - 1 - round(P['top'] * k)
    return out, ox, oy


# ---------------------------------------------------------------- main
def one_cell(cls, sex, stance, state, c, fg, s):
    st = state.split('_')[0]
    ground = figure_height(c, fg)[1]
    body, on = to_body(c, fg, s, ground); body = body.astype(int)
    m = PP.rod_mask(body); cy = PP.cyan_mask(body)
    PP.ANIM = st if st != 'stand' else 'hit'
    o = 'attack' if st == 'attack' else 'hit'
    if stance == '1h' and cy.sum() > 8:
        g = PP.orient({'back': PP.hand_of(m, body)}, o); g['front'] = PP.orient({'f': PP.hand_of(cy, body)}, 'hit')['f']
        rods = m | cy
    else:
        g = PP.orient(PP.grips_for(m, stance, body), o); rods = m
    clean, on = clean_rods(body, rods, on)
    pts = [v['point'] for v in g.values() if isinstance(v, dict) and 'point' in v]
    if state.endswith('_shield') and 'front' in g:
        on = strip_drawn_shield(clean, on, g['front']['point'])
    fixed, skin, head = skin_split(clean, on, pts)
    n = f'{cls}_{sex}_{stance}_{state}'
    Image.fromarray(fixed).save(os.path.join(HERE, 'layers', f'{n}_fixed.png'))
    Image.fromarray(skin, 'LA').save(os.path.join(HERE, 'layers', f'{n}_skin.png'))
    json.dump({'grips': g, 'head': head, 'scale': round(s, 4)}, open(os.path.join(HERE, 'grips', f'{n}.json'), 'w'))
    print(n, {k: (v.get('point'), v.get('angle')) for k, v in g.items() if isinstance(v, dict) and 'point' in v}, 'head', head)
    return fixed, skin, g, head


def strip_drawn_shield(a, on, p):
    """ChatGPT sometimes draws a shield on the braced arm. The code shield (anim.SHIELD at the left fist) covers most
    of it; the rim that sticks out past the code shield on the far side (dark or orange pixels right of the shield's
    centre, within 10 px) is cleared."""
    H, W = on.shape; S = np.zeros((H + 400, W + 400), bool)
    x0 = int(round(p[0] - A.SHIELD_FIST[0])) + 200; y0 = int(round(p[1] - A.SHIELD_FIST[1])) + 200
    sa = A.SHIELD[..., 3] > 0; S[y0:y0 + sa.shape[0], x0:x0 + sa.shape[1]] = sa; S = S[200:200 + H, 200:200 + W]
    ys, xs = np.where(S)
    if not len(xs): return on
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    rim = (lum < 90) | ((r > 140) & (b < 0.6 * r))            # dark body of the drawn shield, orange/gold rim
    xx = np.arange(W)[None, :]
    zone = ndi.binary_dilation(S, iterations=12) & ~S & (xx > xs.min() + 0.4 * (xs.max() - xs.min()))
    on = on & ~(zone & rim & on)
    # leftover rim crumbs: small pieces outside the code shield, on its far side
    far = ndi.binary_dilation(S, iterations=20) & ~S & (xx > xs.min() + 0.4 * (xs.max() - xs.min()))
    lab, n = ndi.label(on & ~S, np.ones((3, 3)))
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 80 and (m & far).sum() > 0.6 * m.sum(): on &= ~m
    # nothing of the body reaches past the shield's far edge at chest height: what is there is the drawn rim
    yy = np.arange(H)[:, None]
    past = (xx >= xs.max() - 1) & (xx < xs.max() + 16) & (yy > ys.min() - 16) & (yy < ys.max() + 8)
    past |= (xx > (xs.min() + xs.max()) / 2 + 2) & (xx < xs.max() + 16) & (yy < ys.min()) & (yy > ys.min() - 14)
    return on & ~(past & ~S)


# fix sheets: (sex, stance, state, tag, file) -> extra state '<state>_<tag>'. 'shield' = the 1h attack with the shield
# arm braced at the chest; loadouts with a shield use it, the others keep the plain attack.
EXTRA = {'soldier': [('f', '1h', 'attack', 'shield', 'soldier_f_sheet_fix1.png')]}


def process(cls):
    for d in ('layers', 'grips', 'sprites', 'source'): os.makedirs(os.path.join(HERE, d), exist_ok=True)
    rows = CLASSES[cls]; data = {}
    for sex in 'mf':
        a = np.asarray(Image.open(os.path.join(HERE, 'source', f'{cls}_{sex}_sheet.png')).convert('RGB'))
        sx, sy = a.shape[1] / 1536, a.shape[0] / 1024
        cut = {}
        for r, c, stance, state, (x0, y0, x1, y1) in cells(rows):
            box = (round(x0 * sx), round(y0 * sy), round(x1 * sx), round(y1 * sy))
            cut[(stance, state)] = cut_cell(a, box)
        hs = [figure_height(*cut[k])[0] for k in cut if k[1] == 'stand']
        s = FIG_H / float(np.median(hs))
        for (stance, state), (c, fg) in cut.items():
            data[(sex, stance, state)] = one_cell(cls, sex, stance, state, c, fg, s)
        # extra cells from fix sheets (same grid): e.g. the shield-braced 1h attack, used only with a shield
        for (xs, stance, state, tag, fname) in EXTRA.get(cls, []):
            if xs != sex or not os.path.exists(os.path.join(HERE, 'source', fname)): continue
            b2 = np.asarray(Image.open(os.path.join(HERE, 'source', fname)).convert('RGB'))
            box = [bx for _, _, st, sta, bx in cells(rows) if (st, sta) == (stance, state)][0]
            k2 = (b2.shape[1] / 1536, b2.shape[0] / 1024)
            c, fg = cut_cell(b2, (round(box[0] * k2[0]), round(box[1] * k2[1]), round(box[2] * k2[0]), round(box[3] * k2[1])))
            data[(sex, stance, f'{state}_{tag}')] = one_cell(cls, sex, stance, f'{state}_{tag}', c, fg, s)
    return data


def split2h(g):
    """Same as poses/compose.py: a 2h rod read as one gap is split into two touching fists."""
    import math
    g = {k: dict(v) if isinstance(v, dict) else v for k, v in g.items()}
    if 'front' not in g and 'back' in g:
        b = g['back']; th = math.radians(b['angle']); d = np.array([math.cos(th), math.sin(th)]); q = b['fist_gap'] / 4
        p = np.array(b['point']); g['back'] = dict(b, point=(p - d * q).tolist(), fist_gap=b['fist_gap'] / 2)
        g['front'] = dict(b, point=(p + d * q).tolist(), fist_gap=b['fist_gap'] / 2)
    return g


def feet(b):
    ys, xs = np.where(b[..., 3] > 0); bot = ys.max(); low = ys > bot - 10
    return float(xs[low].mean()), float(bot)


def render(cls, data):
    rows = []
    for sex in 'mf':
        for li, (load, stance, items) in enumerate(LOADOUTS[cls]):
            hair, hramp, sramp = SAMPLE_HAIR[sex][li % len(SAMPLE_HAIR[sex])]
            frames = {}
            ref = None
            for state in ('stand', 'attack', 'hit'):
                shielded = any(w == 'shield' for _, w, _ in items[state])
                fixed, skin, g, head = data.get((sex, stance, f'{state}_shield') if shielded else None) or data[(sex, stance, state)]
                b = tint(fixed, skin, sramp)
                fx_, fy = feet(b)
                if ref is None: ref = (CANVAS_FEET[0] - fx_, CANVAS_FEET[1] - fy)
                dx = round(ref[0]) - A.CELL; dy = round(ref[1]) - A.TOP
                g2 = split2h(g)
                im =A.frame(cls, f'{sex}_{stance}', sramp, items[state], (dx, dy, 0, 0, None), [], 'attack', g2, b)
                if head and hair:
                    hl, hx, hy = hair_layer(sex, hair, hramp, head)
                    A.paste(im := im.copy(), hl, A.CELL + dx + hx, A.TOP + dy + hy)
                frames[state] = im
                Image.fromarray(im).save(os.path.join(HERE, 'sprites', f'{cls}_{sex}_{load}_{state}.png'))
            rows.append((f'{cls} {sex} {load}  (sample hair: {hair}, {hramp}; skin {sramp})', frames))
    x0, x1 = 20, 399
    cw = x1 - x0; ch = 270
    sheet = Image.new('RGB', (2 * (cw * 3 + 12), ((len(rows) + 1) // 2) * (ch + 16)), (236, 230, 216)); d = ImageDraw.Draw(sheet)
    for i, (lab, fr) in enumerate(rows):
        ox = (i % 2) * (cw * 3 + 12); oy = (i // 2) * (ch + 16)
        d.text((ox + 4, oy + 2), lab, fill=(60, 50, 40))
        for j, st in enumerate(('stand', 'attack', 'hit')):
            t = Image.fromarray(fr[st][:, x0:x1]); sheet.paste(t, (ox + j * cw, oy + 14), t)
    sheet.save(os.path.join(HERE, f'review_{cls}.png'))


if __name__ == '__main__':
    cls = sys.argv[1] if len(sys.argv) > 1 else 'soldier'
    render(cls, process(cls))
