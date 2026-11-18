"""Attack and get-hit animations for every class, built from layers: tinted body, weapons drawn at each
frame's angle from the measured grip points, fists redrawn over the handles, and simple effects.
Output: sheets/<class>_<sex>_<loadout>_<anim>.png (frames left to right, transparent) and gif/<class>.gif."""
import sys, os, json, math, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'weapons')); sys.path.insert(0, os.path.join(HERE, '..', 'grip_bodies')); os.chdir(HERE)
import merge as M, render_weapons as R, class_weapons as CW
from pixel_weapons import build, to_rgba
from skin_layers import tint
CELL, TOP, CH = 133, 70, 200
CW_, CH_ = CELL * 3, CH + TOP
G = os.path.join(HERE, '..', 'grip_bodies')
_WD = os.path.join(HERE, '..', '..', 'weapons')
K = json.load(open(os.path.join(_WD, 'k_meta.json')))
SWORD = np.asarray(Image.open(os.path.join(_WD, 'k_longsword.png')).convert('RGBA'))
_W = build(); SPEAR = np.asarray(to_rgba(_W['longspear']['img'])); SPEAR_G2 = _W['longspear']['grip2']
import merge2 as M2
SHIELD, SHIELD_FIST = M2.SHIELD, M2.SHIELD_FIST
_cache = {}

def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

# ---- weapons: name -> f(angle) -> (rgba, grip_xy, tip_len) -------------------------------------------
def w_longsword(a):
    a = round(a); g, n = K['longsword']['grip'], K['longsword']['angle']
    img, gp = cached(('sw', a), lambda: (SWORD, g) if abs(a - n) < .5 else M.rotsprite(SWORD, g, a - n))
    return img, gp, 50
def w_greataxe(a):
    a = round(a); img, gp = cached(('ax', a), lambda: R.greataxe(a, R.AXE_GRIP2)); return img, gp, 100
def w_spear(a):
    a = round(a); img, gp = cached(('sp', a), lambda: M.rotsprite(SPEAR, SPEAR_G2, a)); return img, gp, 220
def w_dagger(a):
    a = round(a); img, gp = cached(('dg', a), lambda: CW.dagger(a)); return img, gp, 24
def w_mace(a):
    a = round(a); img, gp = cached(('mc', a), lambda: CW.mace(a)); return img, gp, 32
def w_qstaff(a):
    a = round(a); img, gp = cached(('qs', a), lambda: CW.quarterstaff(a)); return img, gp, 80
def w_mstaff(a):
    a = round(a); img, gp, tip = cached(('ms', a), lambda: CW.mage_staff(a)); return img, gp, 54
WEAPON = dict(longsword=w_longsword, greataxe=w_greataxe, longspear=w_spear, dagger=w_dagger, mace=w_mace,
              quarterstaff=w_qstaff, staff=w_mstaff)

# ---- bodies ---------------------------------------------------------------------------------------------
def body(cls, key, ramp):
    fx = np.asarray(Image.open(f'{G}/layers/{cls}_{key}_fixed.png')); sk = np.asarray(Image.open(f'{G}/layers/{cls}_{key}_skin.png'))
    return tint(fx, sk, ramp)

def grips(cls, key):
    g = json.load(open(f'{G}/grips/grips_{cls}_{key}.json'))['grips']
    if 'front' not in g:                                   # 2h with touching fists: split the single gap
        b = g['back']; th = math.radians(b['angle']); d = np.array([math.cos(th), math.sin(th)]); q = b['fist_gap'] / 4
        p = np.array(b['point']); g['back'] = dict(b, point=(p - d * q).tolist(), fist_gap=b['fist_gap'] / 2)
        g['front'] = dict(b, point=(p + d * q).tolist(), fist_gap=b['fist_gap'] / 2)
    return g

def paste(dst, src, x, y):
    x, y = int(round(x)), int(round(y)); h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0: return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]; m = s[..., 3] > 0; dst[y0:y1, x0:x1][m] = s[m]

def fist(b, p, r):
    yy, xx = np.mgrid[0:b.shape[0], 0:b.shape[1]]
    return ((xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= r * r) & (b[..., 3] > 0)

# ---- effects ----------------------------------------------------------------------------------------------
def arc(d, c, r, a0, a1, col=(255, 255, 255), w=3, alpha=220):
    pts = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 14)]
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 1)
        d.line([pts[i], pts[i + 1]], fill=col + (int(alpha * (0.25 + 0.75 * t)),), width=max(1, int(w * (0.4 + t))))
def burst(d, c, r, col=(255, 240, 180)):
    for k in range(8):
        a = math.radians(k * 45 + 22); d.line([(c[0] + math.cos(a) * r * .4, c[1] + math.sin(a) * r * .4), (c[0] + math.cos(a) * r, c[1] + math.sin(a) * r)], fill=col + (230,), width=2)
    d.ellipse([c[0] - r * .35, c[1] - r * .35, c[0] + r * .35, c[1] + r * .35], fill=(255, 255, 255, 220))
def glow(d, c, r, col=(190, 150, 255)):
    for k, a in ((1.0, 70), (0.7, 120), (0.4, 220)):
        d.ellipse([c[0] - r * k, c[1] - r * k, c[0] + r * k, c[1] + r * k], fill=col + (a,))
def speed(d, x0, x1, y, col=(255, 255, 255)):
    for o in (-4, 0, 4): d.line([(x0, y + o), (x1, y + o)], fill=col + (150,), width=1)

# ---- loadouts and their attack motion ------------------------------------------------------------------
# Each frame: (dx, dy, {hand: angle offset}, slide, effect)
SLASH = [(0, 0, -0, 0, None), (-3, 1, -35, 0, None), (-4, 1, -45, 0, None), (8, 0, 40, 0, 'arc'), (12, 0, 75, 0, 'arc'),
         (10, 0, 70, 0, None), (5, 0, 30, 0, None), (1, 0, 5, 0, None)]
CHOP = [(0, 0, 0, 0, None), (-4, -1, -12, 0, None), (-7, -2, -22, 0, None), (6, 1, 10, 0, 'arc'), (15, 3, 28, 0, 'arc'),
        (14, 3, 28, 0, None), (6, 1, 12, 0, None), (1, 0, 2, 0, None)]   # two hands on the haft: small turn, big lunge
THRUST = [(0, 0, 0, 0, None), (-4, 0, 0, -8, None), (-6, 0, 0, -12, None), (10, 0, 0, 18, 'speed'), (16, 0, 0, 26, 'speed'),
          (14, 0, 0, 22, None), (6, 0, 0, 8, None), (1, 0, 0, 0, None)]
PUNCH = [(0, 0, 0, 0, None), (-3, 1, 0, 0, None), (-5, 1, 0, 0, None), (10, 0, 0, 0, None), (16, 0, 0, 0, 'burst'),
         (13, 0, 0, 0, None), (6, 0, 0, 0, None), (1, 0, 0, 0, None)]
CAST = [(0, 0, 0, 0, None), (-2, 0, -12, 0, 'glow1'), (-3, 0, -18, 0, 'glow2'), (2, 0, 8, 0, 'shot0'), (4, 0, 12, 0, 'shot1'),
        (3, 0, 8, 0, 'shot2'), (1, 0, 3, 0, 'shot3'), (0, 0, 0, 0, None)]
SHOOT = [(0, 0, 0, 0, 'nock'), (-1, 0, 0, 0, 'nock'), (-2, 0, 0, 0, 'nock'), (0, 0, 0, 0, 'loose0'), (1, 0, 0, 0, 'loose1'),
         (1, 0, 0, 0, 'loose2'), (0, 0, 0, 0, 'loose3'), (0, 0, 0, 0, 'empty')]
HIT = [(0, 0, 0, 0, None), (-6, 0, -8, 0, 'red'), (-9, -1, -10, 0, 'white'), (-7, 0, -6, 0, 'shake'), (-4, 0, -3, 0, None),
       (-1, 0, 0, 0, None)]

# class -> list of (loadout name, stance, [(hand, weapon, layer)], attack motion, which hands move)
LOADOUTS = {
 'soldier': [('longsword', '1h', [('front', 'longsword', 'over')], SLASH, ['front']),
             ('sword_shield', '1h', [('back', 'longsword', 'under'), ('front', 'shield', 'over')], SLASH, ['back']),
             ('greataxe', '2h', [('back', 'greataxe', 'over')], CHOP, ['back']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], THRUST, ['back'])],
 'archer': [('bow', 'bow', [], SHOOT, []), ('dagger', '1h', [('front', 'dagger', 'over')], SLASH, ['front'])],
 'acolyte': [('mace_shield', '1h', [('back', 'mace', 'under'), ('front', 'shield', 'over')], SLASH, ['back']),
             ('quarterstaff', '2h', [('back', 'quarterstaff', 'over')], CHOP, ['back']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], THRUST, ['back'])],
 'mage': [('staff', '1h', [('front', 'staff', 'over')], CAST, ['front'])],
 'brawler': [('unarmed', '1h', [], PUNCH, []), ('greataxe', '2h', [('back', 'greataxe', 'over')], CHOP, ['back']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], THRUST, ['back'])],
 'rogue': [('dual_daggers', '1h', [('front', 'dagger', 'over'), ('back', 'dagger', 'over')], SLASH, ['front', 'back'])],
}

def frame(cls, key, ramp, items, f, moving, anim, g, bodyimg, bowinfo=None, t=0):
    dx, dy, dang, slide, fx = f
    if fx == 'shake': dx += (2 if t % 2 else -2)
    canvas = np.zeros((CH_, CW_, 4), np.uint8); under = canvas.copy(); over = canvas.copy()
    b = bodyimg.copy()
    if fx in ('red', 'white'):                                      # hit flash
        col = np.array((255, 70, 60) if fx == 'red' else (255, 255, 255), float); k = 0.55 if fx == 'red' else 0.45
        m = b[..., 3] > 0; b[m, :3] = (b[m, :3] * (1 - k) + col * k).astype(np.uint8)
    ox, oy = CELL + dx, TOP + dy
    fist_pts = []; tips = []
    for hand, wname, layer in items:
        p = g[hand]['point']; base = g[hand]['angle']
        if wname == 'shield':
            paste(over, SHIELD, ox + p[0] - SHIELD_FIST[0], oy + p[1] - SHIELD_FIST[1]); continue
        a = base + (dang if hand in moving else 0) * (1 if anim == 'attack' else 0.35)
        if anim == 'attack' and len(moving) == 2:                   # dual: front swings first, back follows
            a = base + (dang if (hand == 'front') == (t < 5) else 0)
        img, gp, L = WEAPON[wname](a)
        sx = slide * math.cos(math.radians(a)); sy = slide * math.sin(math.radians(a))
        paste(under if layer == 'under' else over, img, ox + p[0] - gp[0] + sx, oy + p[1] - gp[1] + sy)
        fist_pts.append((hand, p)); tips.append((p, a, L))
    if cls == 'brawler' and not items: fist_pts = [('front', g['front']['point']), ('back', g['back']['point'])]
    out = canvas.copy(); paste(out, under, 0, 0); paste(out, b, ox, oy); paste(out, over, 0, 0)
    fl = np.zeros_like(canvas)
    for hand, p in fist_pts:
        m = fist(b, p, max(4.5, g[hand]['fist_gap'] / 2)); blk = np.zeros_like(b); blk[m] = b[m]; paste(fl, blk, ox, oy)
    paste(out, fl, 0, 0)
    im = Image.fromarray(out); d = ImageDraw.Draw(im, 'RGBA')
    if fx == 'arc' and anim == 'attack':
        for (p, a, L) in tips[-1:] if len(moving) < 2 else tips[:1] if t < 5 else tips[1:]:
            arc(d, (ox + p[0], oy + p[1]), L * 0.95, a - 55, a, w=3)
    if fx == 'speed':
        p, a, L = tips[0]; tx = ox + p[0] + L * 0.55; speed(d, tx - 40, tx + 10, oy + p[1] - 2)
    if fx == 'burst':
        p = g['front']['point']; burst(d, (ox + p[0] + 8, oy + p[1]), 12)
    if bowinfo is not None:
        draw_bow(im, d, g, ox, oy, fx, bowinfo, b)
    if fx and fx.startswith(('glow', 'shot')):
        p, a, L = tips[0]; tip = (ox + p[0] + L * math.cos(math.radians(a)), oy + p[1] + L * math.sin(math.radians(a)))
        if fx.startswith('glow'): glow(d, tip, 5 if fx == 'glow1' else 8)
        else:
            k = int(fx[-1]); c = (tip[0] + 18 + k * 34, tip[1] + 6 + k * 4); glow(d, c, 7)
            d.line([(c[0] - 26, c[1]), (c[0] - 6, c[1])], fill=(200, 170, 255, 140), width=3)
    return np.asarray(im)

def draw_bow(im, d, g, ox, oy, fx, info, b):
    p = g['front']['point']; back = g['back']['point']; length = info['length']
    bimg, gp, tips = info['bow']
    paste_arr = np.asarray(im).copy(); paste(paste_arr, bimg, ox + p[0] - gp[0], oy + p[1] - gp[1])
    im.paste(Image.fromarray(paste_arr)); d2 = ImageDraw.Draw(im, 'RGBA')
    T = [(ox + p[0] - gp[0] + t[0], oy + p[1] - gp[1] + t[1]) for t in tips]
    nocked = fx in ('nock',)
    hand = (ox + back[0], oy + back[1])
    if nocked:
        for t in T: d2.line([t, hand], fill=(230, 225, 210, 255), width=1)
        aimg, ag = info['arrow']; arr = np.asarray(im).copy()
        paste(arr, aimg, hand[0] - ag[0], oy + info['arrow_y'] - ag[1]); im.paste(Image.fromarray(arr))
    else:
        d2.line([T[0], T[1]], fill=(230, 225, 210, 255), width=1)
    if fx and fx.startswith('loose'):
        k = int(fx[-1]); aimg, ag = info['arrow']; arr = np.asarray(im).copy()
        paste(arr, aimg, ox + p[0] + 4 + k * 46, oy + info['arrow_y'] - ag[1]); im.paste(Image.fromarray(arr))
        ImageDraw.Draw(im, 'RGBA').line([(ox + p[0] + k * 46 - 20, oy + info['arrow_y']), (ox + p[0] + k * 46, oy + info['arrow_y'])], fill=(255, 255, 255, 120), width=1)
    fl = np.zeros_like(np.asarray(im))
    for hp, r in ((p, 5), (back, 4)):
        m = fist(b, hp, r); blk = np.zeros_like(b); blk[m] = b[m]; paste(fl, blk, ox, oy)
    arr = np.asarray(im).copy(); paste(arr, fl, 0, 0); im.paste(Image.fromarray(arr))

def render(cls, sex, load, ramp):
    name, stance, items, motion, moving = load
    key = f'{sex}_{stance}'; g = grips(cls, key); b = body(cls, key, ramp)
    bowinfo = None
    if stance == 'bow':
        L = g['bow_rod']['bottom'] - g['bow_rod']['top']
        bowinfo = dict(length=L, bow=CW.bow(int(L), -90.0), arrow=CW.arrow(int(g['front']['point'][0] - g['back']['point'][0] + 14)),
                       arrow_y=g['arrow']['y'])
    seqs = {}
    for anim, frames in (('attack', motion), ('hit', HIT)):
        seqs[anim] = [frame(cls, key, ramp, items, f, moving, anim, g, b, bowinfo, t) for t, f in enumerate(frames)]
    return seqs

RAMPS = {'soldier': ('fair', 'tan'), 'archer': ('tan', 'porcelain'), 'acolyte': ('porcelain', 'bronze'),
         'mage': ('bronze', 'fair'), 'brawler': ('deep', 'tan'), 'rogue': ('fair', 'deep')}

if __name__ == '__main__':
    os.makedirs('sheets', exist_ok=True); os.makedirs('gif', exist_ok=True)
    only = sys.argv[1:] or list(LOADOUTS)
    for cls in only:
        rows = []
        for sex, ramp in zip('mf', RAMPS[cls]):
            for load in LOADOUTS[cls]:
                seqs = render(cls, sex, load, ramp)
                for anim, fr in seqs.items():
                    Image.fromarray(np.hstack(fr)).save(f'sheets/{cls}_{sex}_{load[0]}_{anim}.png')
                rows.append((f'{sex} {load[0]}', seqs['attack'] + seqs['hit']))
        # GIF: every loadout of the class stacked, attack then hit
        n = max(len(r[1]) for r in rows); frames = []
        for t in range(n):
            sheet = Image.new('RGBA', (CW_, (CH_ + 4) * len(rows)), (232, 226, 210, 255)); dd = ImageDraw.Draw(sheet)
            for i, (label, fr) in enumerate(rows):
                y0 = i * (CH_ + 4)
                for c in range(3):
                    dd.rectangle([c * CELL, y0 + TOP + 128, (c + 1) * CELL - 1, y0 + CH_ - 2], fill=(212, 202, 178) if c == 1 else (222, 214, 194), outline=(170, 160, 140))
                sheet.alpha_composite(Image.fromarray(fr[min(t, len(fr) - 1)]), (0, y0)); dd.text((4, y0 + 4), label, fill=(60, 50, 40))
            frames.append(sheet.convert('P', palette=Image.ADAPTIVE, colors=255))
        durs = [90] * n; durs[0] = 300; durs[len(rows[0][1]) - len(HIT) - 1] = 200
        frames[0].save(f'gif/{cls}.gif', save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
        print(cls, len(rows), 'loadouts,', n, 'frames')
