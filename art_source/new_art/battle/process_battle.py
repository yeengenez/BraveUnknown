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
from make_refs import CLASSES, cells, states_for, EXTRA_SHEETS, SHEET_ROWS
os.chdir(cwd)

FIG_H = 190                         # stand figure height in sprite pixels (Legacy: ~197 incl. outline)
BODY_W, BODY_H, FEET_Y = 400, 230, 226
CANVAS_FEET = (199, 250)            # where the stand figure's feet go on the 399x270 sprite

def one_hand(w, shield=False):      # same rule as poses/compose.py: weapon in the right hand ('back')
    st = [('back', w, 'under')] + ([('front', 'shield', 'over')] if shield else [])
    at = ([('front', 'shield', 'over')] if shield else []) + [('back', w, 'over')]
    return {'stand': st, 'attack': at, 'hit': st}
LOADOUTS = {
    # a one-handed weapon without a shield uses the dual stance (left hand empty) - shield rule 2026-11-20
    'soldier': [('longsword', 'dual', {s: [('back', 'longsword', 'over')] for s in ('stand', 'attack', 'hit')}),
                # the shield stance always shows the class's own shield, drawn into the body (Soldier: square shield);
                # the equipped shield item (light / heavy / tower) changes rules only, not the look
                ('sword_shield', '1h', {s: [('back', 'longsword', 'over')] for s in ('stand', 'attack', 'hit')}),
                ('dual_swords', 'dual', {s: [('front', 'longsword', 'over'), ('back', 'longsword', 'over')] for s in ('stand', 'attack', 'hit')}),
                ('greataxe', '2h', {s: [('back', 'greataxe', 'over')] for s in ('stand', 'attack', 'hit')}),
                ('longspear', 'reach', {s: [('back', 'longspear', 'over')] for s in ('stand', 'attack', 'hit')})],
}
# classes whose battle sprites wear headgear drawn into the body (user, 2026-11-20): no hair layer on the sprite
HEADGEAR = {'soldier'}
HAIR_LEN = json.load(open(os.path.join(HERE, 'hair_length.json')))
SAMPLE_HAIR = {'m': [('long', 'brown', 'fair'), ('messy', 'black', 'tan'), ('ponytail', 'auburn', 'deep')],
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
    # hair under the headgear, drawn in shades of pure red (user, 2026-11-20): its own value-map layer, tinted with the
    # hero's hair colour and shown only for long portrait hairstyles (hair_length.json)
    red = fgm & ~m & (r > 45) & (g < 0.3 * r) & (b < 0.3 * r)
    lab_r, nr = ndi.label(red, np.ones((3, 3)))
    bright = red & (r > 150) & (g < 0.25 * r) & (b < 0.25 * r)       # the key has bright pure red; maroon leather has none
    red = np.isin(lab_r, [i + 1 for i in range(nr) if (lab_r == i + 1).sum() >= 15 and (bright & (lab_r == i + 1)).sum() >= 8])
    # ...plus its soft edge: reddish pixels right next to it (outline / blend with the outline or background)
    red |= fgm & ~m & ndi.binary_dilation(red, iterations=2) & (r - g > 25) & (r - b > 25)
    near = ndi.binary_dilation(red, iterations=3) & fgm & ~m & ~red
    red |= near & (g - b > 25) & (np.abs(r - g) < 70)            # red + green-screen blends (olive) on the hair edge
    hairp = None
    if red.sum() > 40:
        lo_, hi_ = np.percentile(r[red], [2, 98])
        hv_ = np.clip(25 + (r - lo_) / max(1, hi_ - lo_) * 210, 10, 245)
        hairp = np.zeros(a.shape[:2] + (2,), np.uint8); hairp[..., 0] = hv_.astype(np.uint8); hairp[..., 1] = red * 255
    else:
        red = np.zeros_like(red)
    keep_f = fgm & ~m & ~red
    lab_f, nf = ndi.label(keep_f, np.ones((3, 3)))            # specks left floating where the hair was
    if nf: keep_f &= ~np.isin(lab_f, [i + 1 for i, z in enumerate(ndi.sum(keep_f, lab_f, range(1, nf + 1))) if z <= 4])
    fixed = np.dstack([a, keep_f * 255]).astype(np.uint8)
    skin = np.zeros(a.shape[:2] + (2,), np.uint8); skin[..., 0] = val.astype(np.uint8); skin[..., 1] = m * 255
    # head box for the hair: the skin blob at the top
    hl, hn = ndi.label(m & (np.arange(a.shape[0])[:, None] < top + 0.3 * Hh))
    head = None
    if hn:
        big = np.argmax(ndi.sum(m, hl, range(1, hn + 1))) + 1; hy, hx = np.where(hl == big)
        head = dict(top=int(hy.min()), left=int(hx.min()), right=int(hx.max()), bottom=int(hy.max()))
    return fixed, skin, head, hairp


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
def fist_grip(rod, a):
    """Grip from the (yellow) fist that holds the rod: the fist's centre projected onto the rod axis. More reliable
    than reading the gap in the rod when the two rod pieces do not line up exactly. None if no fist touches the rod."""
    import math
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    key = (a.min(2) < 245) & (r > 120) & (g > 0.5 * r) & (b < 0.55 * r) & (r - b > 70)
    lab, n = ndi.label(key, np.ones((3, 3)))
    near = ndi.binary_dilation(rod, iterations=2)
    best, hits = 0, 0
    for i in range(1, n + 1):
        h = ((lab == i) & near).sum()
        if h > hits and (lab == i).sum() >= 12: best, hits = i, h
    if not best: return None
    pts = np.argwhere(rod)[:, ::-1].astype(float); c0 = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c0); d = vt[0]
    f = np.argwhere(lab == best)[:, ::-1].astype(float)
    p = c0 + d * ((f.mean(0) - c0) @ d)
    t = (f - c0) @ d
    return dict(point=[round(float(p[0]), 1), round(float(p[1]), 1)], angle=round(float(math.degrees(math.atan2(d[1], d[0]))), 1),
                fist_gap=round(float(t.max() - t.min()), 1))


def hand(rod, a):
    return fist_grip(rod, a) or PP.hand_of(rod, a)


def toward_longer(v, mask):
    """Point the grip's angle at the longer stretch of rod beyond the fist."""
    import math
    th = math.radians(v['angle']); d = np.array([math.cos(th), math.sin(th)])
    pts = np.argwhere(mask)[:, ::-1] - np.array(v['point'])
    t = pts @ d
    if (t > 0).sum() < (t < 0).sum(): v['angle'] = round(float((v['angle'] + 360) % 360 - 180), 1)
    return v


def one_cell(cls, sex, stance, state, c, fg, s):
    st = state.split('_')[0]
    # attack2 reads like attack; a spear's ready keeps its tip forward (like attack), other wind-ups keep the weapon up
    st = 'attack' if st.startswith('attack') or (st == 'ready' and stance == 'reach') else ('hit' if st == 'ready' else st)
    ground = figure_height(c, fg)[1]
    body, on = to_body(c, fg, s, ground); body = body.astype(int)
    m = PP.rod_mask(body); cy = PP.cyan_mask(body)
    PP.ANIM = st if st != 'stand' else 'hit'
    o = 'attack' if st == 'attack' else 'hit'
    if stance == 'dual' and cy.sum() > 8:
        # two blades: each points along its rod's longer side past the fist (rods are drawn mostly blade-side)
        g = {'back': toward_longer(hand(m, body), m), 'front': toward_longer(hand(cy, body), cy)}
        if (cls, sex, stance, state) in SWAP_HANDS:      # ChatGPT swapped the rod colours between the hands in this pose
            g = {'back': g['front'], 'front': g['back']}
        rods = m | cy
    elif stance == '1h' and cy.sum() > 8:
        g = PP.orient({'back': hand(m, body)}, o); g['front'] = PP.orient({'f': hand(cy, body)}, 'hit')['f']
        rods = m | cy
    elif stance == '1h':                     # shield drawn into the body: only the sword hand has a rod
        g = PP.orient({'back': hand(m, body)}, o); rods = m
    else:
        g = PP.orient(PP.grips_for(m, stance, body), o); rods = m
    clean, on = clean_rods(body, rods, on)
    pts = [v['point'] for v in g.values() if isinstance(v, dict) and 'point' in v]
    fixed, skin, head, hairp = skin_split(clean, on, pts)
    n = f'{cls}_{sex}_{stance}_{state}'
    Image.fromarray(fixed).save(os.path.join(HERE, 'layers', f'{n}_fixed.png'))
    Image.fromarray(skin, 'LA').save(os.path.join(HERE, 'layers', f'{n}_skin.png'))
    json.dump({'grips': g, 'head': head, 'scale': round(s, 4)}, open(os.path.join(HERE, 'grips', f'{n}.json'), 'w'))
    print(n, {k: (v.get('point'), v.get('angle')) for k, v in g.items() if isinstance(v, dict) and 'point' in v}, 'head', head)
    if hairp is not None: Image.fromarray(hairp, 'LA').save(os.path.join(HERE, 'layers', f'{n}_hair.png'))
    return fixed, skin, g, head, hairp


# fix sheets: (sex, stance, state, tag, file) -> extra state '<state>_<tag>'. 'shield' = the 1h attack with the shield
# arm braced at the chest; loadouts with a shield use it, the others keep the plain attack.
EXTRA = {}
# poses where the drawn rod colours are on the wrong hands (the arm that held magenta in STAND holds cyan here):
# the grips are swapped back so each weapon stays in its own hand
SWAP_HANDS = set()   # (the v5 male dual row needed stand/hit swapped; the dual stance now comes from its own sheet)
# rows waiting for a new ChatGPT drawing: not cut, and their loadouts are not built (Soldier shield row: old code-shield
# poses removed 2026-11-20, waiting for the drawn-in square shield)
PENDING = {}


def process(cls):
    for d in ('layers', 'grips', 'sprites', 'source'): os.makedirs(os.path.join(HERE, d), exist_ok=True)
    data = {}
    for sex in 'mf':
        rows = SHEET_ROWS.get((cls, sex), CLASSES[cls])
        sheets = [(f'{cls}_{sex}_sheet.png', rows)] + [(f'{cls}_{nm}_{sex}_sheet.png', r_) for nm, r_ in EXTRA_SHEETS.get(cls, {}).items()]
        have = [(f, r_) for f, r_ in sheets if os.path.exists(os.path.join(HERE, 'source', f))]
        if not have: print('no sheet yet:', cls, sex); continue
        extra_stances = {st for f, r_ in have[1:] if f != sheets[0][0] for st, _ in r_}
        s = None
        for fname, rws in have:
            a = np.asarray(Image.open(os.path.join(HERE, 'source', fname)).convert('RGB'))
            sx, sy = a.shape[1] / 1536, a.shape[0] / 1024
            main = fname == sheets[0][0]
            cut = {}
            for r, c, stance, state, (x0, y0, x1, y1) in cells(rws, cls):
                if main and stance in extra_stances: continue          # that stance comes from its own sheet now
                box = (round(x0 * sx), round(y0 * sy), round(x1 * sx), round(y1 * sy))
                cut[(stance, state)] = cut_cell(a, box)
            hs = [figure_height(*cut[k])[0] for k in cut if k[1] == 'stand']
            s_sheet = FIG_H / float(np.median(hs))                  # each sheet scaled by its own stand figures
            if main: s = s_sheet
            for (stance, state), (c, fg) in cut.items():
                if stance in PENDING.get(cls, ()): continue
                data[(sex, stance, state)] = one_cell(cls, sex, stance, state, c, fg, s_sheet)
        if s is None: s = s_sheet
        # extra cells from fix sheets (same grid): e.g. the shield-braced 1h attack, used only with a shield
        for (xs, stance, state, tag, fname) in EXTRA.get(cls, []):
            if xs != sex or not os.path.exists(os.path.join(HERE, 'source', fname)): continue
            b2 = np.asarray(Image.open(os.path.join(HERE, 'source', fname)).convert('RGB'))
            box = [bx for _, _, st, sta, bx in cells(rows, cls) if (st, sta) == (stance, state)][0]
            k2 = (b2.shape[1] / 1536, b2.shape[0] / 1024)
            c, fg = cut_cell(b2, (round(box[0] * k2[0]), round(box[1] * k2[1]), round(box[2] * k2[0]), round(box[3] * k2[1])))
            name = f'{state}_{tag}' if tag else state          # empty tag = the fix sheet REPLACES that cell
            data[(sex, stance, name)] = one_cell(cls, sex, stance, name, c, fg, s)
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


# slash frames: the swinging hand's weapon is hidden behind a slash wave (user, 2026-11-21);
# both weapons show again in FINISH. slash_left = off-hand (cyan, 'front') chop, slash_right = main hand (magenta, 'back') sweep.
SLASH_HIDE = {'slash_left': ('front', 'chop'), 'slash_right': ('back', 'sweep')}


def slash_wave(im, kind, F, ang, L, SS=4):
    """Crescent slash trail on a frame (RGBA uint8 array). F = fist (frame px), ang = blade angle (deg), L = blade length.
    The thick bright end is where the blade is now; it thins and fades along the path it came from."""
    import math
    F = np.array(F, float); d = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
    T = F + d * L
    n = 64
    if kind == 'chop':          # tip came down from overhead: circle around a point above and behind the fist
        C = F + np.array([-0.15 * L, -0.6 * L]); R = np.linalg.norm(T - C) * 1.02
        th1 = math.atan2(*(T - C)[::-1]); th0 = th1 - math.radians(155)
        ts = np.linspace(th1, th0, n)                                    # u = 0 at the blade, 1 at the oldest end
        outer = C + R * np.stack([np.cos(ts), np.sin(ts)], 1); inward = (C - outer) / R
        wmax = 0.42 * L
    else:                       # sweep: flat ellipse at waist height, from the hand round the front of the body and curling up
        a_ = 1.5 * L; b_ = 0.3 * a_
        C = F + np.array([a_, 0.0])
        ph = np.linspace(math.pi, -math.radians(25), n)                 # pi = at the hand, pi/2 = in front of the body
        outer = C + np.stack([a_ * np.cos(ph), b_ * np.sin(ph)], 1)
        inward = np.stack([np.zeros(n), -np.ones(n)], 1)                 # thickness goes up (the blurred inner side)
        wmax = 0.36 * L
    u = np.linspace(0, 1, n)
    w = wmax * np.minimum(1, u / 0.05) * (1 - u) ** 0.8
    fade = 1 - 0.7 * u
    H, W = im.shape[:2]
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    bands = [(0.0, 0.16, (255, 255, 246), 1.0), (0.16, 0.45, (255, 212, 118), 0.95), (0.45, 1.0, (118, 104, 122), 0.5)]
    for i in range(n - 1):
        for f0, f1, col, al in bands:
            q = [outer[i] + inward[i] * w[i] * f0, outer[i + 1] + inward[i + 1] * w[i + 1] * f0,
                 outer[i + 1] + inward[i + 1] * w[i + 1] * f1, outer[i] + inward[i] * w[i] * f1]
            dr.polygon([tuple(p * SS) for p in q], fill=col + (int(255 * al * fade[i]),))
    lay = lay.resize((W, H), Image.BOX)
    out = Image.fromarray(im).convert('RGBA'); out.alpha_composite(lay)
    return np.asarray(out)


def feet(b):
    ys, xs = np.where(b[..., 3] > 0); bot = ys.max(); low = ys > bot - 10
    return float(xs[low].mean()), float(bot)


def render(cls, data):
    rows = []
    for sex in 'mf':
        for li, (load, stance, items) in enumerate(LOADOUTS[cls]):
            if stance in PENDING.get(cls, ()) or not any(k[0] == sex and k[1] == stance for k in data): continue
            hair, hramp, sramp = SAMPLE_HAIR[sex][li % len(SAMPLE_HAIR[sex])]
            frames = {}
            ref = None
            ORDER = ['stand', 'ready', 'attack', 'attack2', 'slash_left', 'slash_right', 'finish', 'hit']
            sts = [t for t in ORDER if (sex, stance, t) in data]
            if not any(w for h_, w, _ in items['attack'] if h_ == 'front'):   # one weapon: only the main-hand (magenta) moves
                sts = [t for t in sts if t not in ('attack2', 'slash_left')] if 'slash_right' not in sts else \
                      [t for t in sts if t not in ('ready', 'slash_left')]
            for state in sts:
                its = items.get(state) or items['attack']
                shielded = any(w == 'shield' for _, w, _ in its)
                fixed, skin, g, head, hairp = data.get((sex, stance, f'{state}_shield') if shielded else None) or data[(sex, stance, state)]
                b = tint(fixed, skin, sramp)
                if hairp is not None and hair in HAIR_LEN[sex]['long']:     # long hair shows under the helmet
                    hm = hairp[..., 1] > 0
                    b = b.copy(); b[hm, :3] = finish.ramp_rgb(finish.PAL['hair'][hramp], hairp[..., 0][hm].astype(float)).astype(np.uint8); b[hm, 3] = 255
                fx_, fy = feet(b)
                if ref is None: ref = (CANVAS_FEET[0] - fx_, CANVAS_FEET[1] - fy)
                dx = round(ref[0]) - A.CELL; dy = round(ref[1]) - A.TOP
                g2 = split2h(g)
                hide, kind = SLASH_HIDE.get(state, (None, None))
                hidden = [w for h_, w, _ in its if h_ == hide]
                im = A.frame(cls, f'{sex}_{stance}', sramp, [i for i in its if i[0] != hide], (dx, dy, 0, 0, None), [], 'attack', g2, b)
                if hidden:
                    p, ang = g2[hide]['point'], g2[hide]['angle']
                    L = A.WEAPON[hidden[0]](ang)[2]
                    im = slash_wave(im, kind, (A.CELL + dx + p[0], A.TOP + dy + p[1]), ang, L)
                if head and hair and cls not in HEADGEAR:
                    hl, hx, hy = hair_layer(sex, hair, hramp, head)
                    A.paste(im := im.copy(), hl, A.CELL + dx + hx, A.TOP + dy + hy)
                frames[state] = im
                Image.fromarray(im).save(os.path.join(HERE, 'sprites', f'{cls}_{sex}_{load}_{state}.png'))
            rows.append((f'{cls} {sex} {load}  (sample hair: {hair}, {hramp}; skin {sramp})', frames))
    x0, x1 = 20, 399
    cw = x1 - x0; ch = 270
    NC = max(len(fr) for _, fr in rows) if rows else 4
    sheet = Image.new('RGB', (2 * (cw * NC + 12), ((len(rows) + 1) // 2) * (ch + 16)), (236, 230, 216)); d = ImageDraw.Draw(sheet)
    for i, (lab, fr) in enumerate(rows):
        ox = (i % 2) * (cw * NC + 12); oy = (i // 2) * (ch + 16)
        d.text((ox + 4, oy + 2), lab, fill=(60, 50, 40))
        for j, st in enumerate(fr):
            t = Image.fromarray(fr[st][:, x0:x1]); sheet.paste(t, (ox + j * cw, oy + 14), t)
    sheet.save(os.path.join(HERE, f'review_{cls}.png'))


if __name__ == '__main__':
    cls = sys.argv[1] if len(sys.argv) > 1 else 'soldier'
    render(cls, process(cls))
