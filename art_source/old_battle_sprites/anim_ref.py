"""Battle animations built from the user's reference art.
The three characters were cut from the reference, background removed and reduced to their native
pixel size (base_*.png, ~120 px tall). Weapons and props are cut into separate parts, the holes they
leave are filled from surrounding pixels, and frames pose those parts plus the whole body, then add
effects (slashes, arrows, sparkles, flashes)."""
from PIL import Image, ImageDraw
import numpy as np, cv2, math, os

FW, FH = 210, 140          # frame size
OX, OY = 46, 14            # where the base sprite sits inside the frame
PAL = {'wh': (255, 255, 255), 'gold_l': (250, 216, 120), 'gold': (226, 170, 64), 'blue_l': (200, 228, 255),
       'wood_d': (92, 60, 36), 'st_l': (220, 230, 242), 'st': (150, 164, 186), 'cr': (236, 226, 200), 'string': (214, 208, 196)}
def col(c, a=255): return PAL[c] + (a,) if isinstance(c, str) else c

# ---------------- part cutting ----------------
def load(n): return np.array(Image.open(f'base_{n}.png').convert('RGBA'))

def poly_mask(shape, poly):
    m = Image.new('L', (shape[1], shape[0]), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    return np.array(m) > 0

def cut(base, mask, k=13):
    """Return (part, rest). Hole pixels inside the body are refilled from neighbours."""
    part = base.copy(); part[~mask, 3] = 0
    rest = base.copy(); rest[mask, 3] = 0
    alpha = (rest[..., 3] > 0).astype(np.uint8)
    closed = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    hole = mask & (base[..., 3] > 0) & (closed > 0)
    if hole.any():
        from scipy import ndimage as ndi
        _, (iy, ix) = ndi.distance_transform_edt(~(rest[..., 3] > 0), return_indices=True)
        rest[hole, :3] = rest[iy[hole], ix[hole], :3]; rest[hole, 3] = 255
    return part, rest

def to_layer(arr):
    L = Image.new('RGBA', (FW, FH), (0, 0, 0, 0)); L.alpha_composite(Image.fromarray(arr), (OX, OY)); return L

# ---------------- drawing helpers for effects ----------------
class FX:
    def __init__(s): s.im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def px(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < FW and 0 <= y < FH: s.im.putpixel((x, y), col(c))
    def line(s, a, b, c, w=1): s.d.line([a, b], fill=col(c), width=w)

def P(x, y): return (x + OX, y + OY)           # base coords -> frame coords

def arc(F, cx, cy, r, a0, a1, c=(236, 246, 255), w=4):
    for rr, al in ((r, 255), (r - 2, 190), (r - 4, 110), (r - 6, 50)):
        steps = max(10, int(abs(a1 - a0) / 2))
        for k in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * k / steps); taper = math.sin(math.pi * k / steps)
            for t in range(max(1, int(w * taper))):
                F.px(cx + (rr - t) * math.cos(a), cy + (rr - t) * math.sin(a), c[:3] + (al,))

def star(F, x, y, s, c='wh', c2='gold_l'):
    for i in range(-s, s + 1):
        cc = c if abs(i) <= s // 2 else c2; F.px(x + i, y, cc); F.px(x, y + i, cc)
    for i in range(-(s // 3), s // 3 + 1): F.px(x + i, y + i, c2); F.px(x + i, y - i, c2)
    F.px(x - 1, y, c); F.px(x + 1, y, c); F.px(x, y - 1, c); F.px(x, y + 1, c)

def burst(F, x, y, r, c='wh'):
    for ang in range(0, 360, 30):
        a = math.radians(ang + 15); r0 = r * (0.45 if ang % 60 else 0.3)
        for d in np.arange(r0, r + 0.1, 0.5): F.px(x + d * math.cos(a), y + d * math.sin(a), c)
    star(F, x, y, 4)

def ring(F, cx, cy, r, c='gold_l'):
    for ang in np.arange(0, 360, 2.5):
        a = math.radians(ang); F.px(cx + r * math.cos(a), cy + r * math.sin(a), c)

def plus(F, x, y, s, c='gold_l'):
    F.d.rectangle([x - s, y - 1, x + s, y + 1], fill=col(c)); F.d.rectangle([x - 1, y - s, x + 1, y + s], fill=col(c))
    F.d.rectangle([x - s + 2, y, x + s - 2, y], fill=col('wh')); F.d.rectangle([x, y - s + 2, x, y + s - 2], fill=col('wh'))

def speed(F, y0, y1, x0, x1, c=(255, 255, 255, 160)):
    for i, y in enumerate(range(y0, y1, 5)): F.line((x0 + (i * 7) % 11, y), (x1 - (i * 5) % 13, y), c)

def arrow(F, x0, x1, y, glow=False):
    if glow:
        F.line((x0 - 22, y), (x1, y), (255, 228, 140, 110), 5); F.line((x0 - 12, y), (x1, y), (255, 240, 190, 200), 3)
    F.line((x0, y), (x1 - 6, y), 'wood_d', 1); F.line((x0, y + 1), (x1 - 6, y + 1), (140, 100, 60, 255), 1)
    for i in range(6): F.line((x1 - 6 + i, y - (2 - i // 3)), (x1 - 6 + i, y + 1 + (2 - i // 3)), 'st_l' if i < 4 else 'st')
    for i in range(4): F.px(x0 + i, y - 1 - i // 2, 'cr'); F.px(x0 + i, y + 2 + i // 2, 'cr')

# ---------------- frame rendering ----------------
def tint(im, rgb, k):
    a = np.array(im).astype(float); m = a[..., 3] > 0
    for i in range(3): a[..., i][m] += (rgb[i] - a[..., i][m]) * k
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def place(layer, pivot, ang=0, dx=0, dy=0):
    pv = P(*pivot)
    if ang: return layer.rotate(ang, resample=Image.NEAREST, center=pv, translate=(dx, dy))
    return layer.transform(layer.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.NEAREST)

def render(rig, f):
    bx, by = f.get('body', (0, 0))
    char = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    under = [n for n in rig['order'] if n not in f.get('front', [])] + f.get('front', [])
    for name in under:
        if name in f.get('hide', []): continue
        layer, pivot = rig['parts'][name]
        ang, dx, dy = f.get('parts', {}).get(name, (0, 0, 0))
        char.alpha_composite(place(layer, pivot, ang, bx + dx, by + dy))
    if f.get('tilt'):  # lean the whole body around the feet
        char = char.rotate(f['tilt'], resample=Image.NEAREST, center=P(58 + bx, 120 + by))
    pre = FX(); [fn(pre) for fn in f.get('pre', [])]; char.alpha_composite(pre.im)
    if 'tint' in f: char = tint(char, *f['tint'])
    if f.get('alpha') is not None:
        a = np.array(char); a[..., 3] = (a[..., 3] * f['alpha']).astype(np.uint8); char = Image.fromarray(a)
    frame = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    sh = FX(); cx = OX + 58 + bx; sh.d.ellipse([cx - 34, OY + 114, cx + 34, OY + 124], fill=(0, 0, 0, 55 if by > -4 else 30))
    frame.alpha_composite(sh.im); frame.alpha_composite(char)
    fx = FX(); [fn(fx) for fn in f.get('fx', [])]; frame.alpha_composite(fx.im)
    return frame

def hit_frames(spot, base_extra=None):
    e = base_extra or {}
    return [
        dict(e, body=(-5, 0), tilt=4, tint=((255, 255, 255), .85), fx=[lambda F: burst(F, *P(*spot), 10)], dur=80),
        dict(e, body=(-8, 1), tilt=6, tint=((235, 60, 50), .45), dur=110),
        dict(e, body=(-5, 0), tilt=3, dur=120),
        dict(e, body=(-2, 0), tilt=1, dur=150),
    ]

# ---------------- SOLDIER ----------------
def soldier():
    base = load('soldier')
    sword_poly = [(0, 18), (11, 18), (38, 46), (44, 50), (53, 51), (54, 60), (47, 67), (44, 77), (35, 77), (20, 70), (17, 63), (24, 58), (0, 32)]
    shield_poly = [(84, 42), (113, 42), (113, 93), (100, 93), (86, 82), (84, 62)]
    sword, rest = cut(base, poly_mask(base.shape, sword_poly))
    shield, rest = cut(rest, poly_mask(base.shape, shield_poly))
    rig = {'parts': {'body': (to_layer(rest), (58, 120)), 'sword': (to_layer(sword), (48, 58)), 'shield': (to_layer(shield), (92, 60))},
           'order': ['body', 'sword', 'shield']}
    A = {}; idle = dict(dur=220)
    tip = P(4, 22)
    A['attack'] = [
        idle,
        dict(body=(-3, 1), tilt=3, parts={'sword': (-35, 0, -2)}, dur=200),
        dict(body=(9, 0), tilt=-3, front=['sword'], parts={'sword': (-150, 0, 0), 'shield': (0, -2, 0)},
             fx=[lambda F: arc(F, *P(58, 56), 50, -130, 40, w=5), lambda F: speed(F, OY + 30, OY + 90, 4, 40)], dur=90),
        dict(body=(9, 1), tilt=-3, front=['sword'], parts={'sword': (-170, 0, 0)},
             fx=[lambda F: arc(F, *P(58, 57), 50, -40, 60, (200, 222, 244), 3)], dur=150),
        dict(body=(3, 0), parts={'sword': (-20, 0, 0)}, dur=170),
        idle,
    ]
    A['hit'] = [idle] + hit_frames((70, 55)) + [idle]
    A['skill'] = [  # Shield Bash
        idle,
        dict(body=(-4, 2), tilt=4, parts={'shield': (6, -4, 0), 'sword': (15, 0, 0)}, dur=220),
        dict(body=(12, 0), tilt=-4, parts={'shield': (-6, 8, -1), 'sword': (20, 0, 0)},
             fx=[lambda F: burst(F, *P(124, 64), 14, 'gold_l'), lambda F: star(F, *P(124, 64), 6), lambda F: speed(F, OY + 40, OY + 100, 2, 44)], dur=110),
        dict(body=(12, 0), tilt=-3, parts={'shield': (-5, 7, 0), 'sword': (20, 0, 0)},
             fx=[lambda F: ring(F, *P(124, 64), 15, 'gold'), lambda F: ring(F, *P(124, 64), 9, 'wh')], dur=180),
        dict(body=(5, 0), parts={'shield': (0, 3, 0)}, dur=170),
        idle,
    ]
    A['critical'] = [  # Leaping Cleave
        idle,
        dict(body=(-3, 4), tilt=5, parts={'sword': (-25, 0, 0)}, tint=((255, 236, 170), .22),
             fx=[lambda F: star(F, tip[0] + 6, tip[1] - 8, 8)], dur=300),
        dict(body=(6, -12), tilt=-2, parts={'sword': (-70, 0, 0)}, fx=[lambda F: speed(F, OY + 100, OY + 130, 40, 110)], dur=150),
        dict(body=(16, 0), tilt=-5, front=['sword'], parts={'sword': (-175, 0, 0)},
             fx=[lambda F: arc(F, *P(66, 50), 62, -120, 80, (255, 250, 222), 6), lambda F: arc(F, *P(66, 50), 52, -110, 70, (250, 216, 120), 3),
                 lambda F: burst(F, *P(132, 92), 16)], dur=110),
        dict(body=(16, 2), tilt=-4, front=['sword'], parts={'sword': (-185, 0, 0)},
             fx=[lambda F: ring(F, *P(130, 92), 16, 'wh'), lambda F: ring(F, *P(130, 92), 22, 'gold_l')], dur=220),
        dict(body=(5, 0), parts={'sword': (-25, 0, 0)}, dur=190),
        idle,
    ]
    return rig, A

# ---------------- ARCHER ----------------
def archer():
    base = load('archer')
    H, W = base.shape[:2]
    # released version: arrow and drawn string removed, bow string straightened
    rel = base.copy()
    arrow_m = np.zeros((H, W), bool); arrow_m[40:45, 62:] = True
    bow_keep = poly_mask(base.shape, [(84, 0), (104, 0), (104, 100), (84, 100), (88, 70), (92, 46), (88, 20)])
    hand_keep = poly_mask(base.shape, [(62, 38), (80, 38), (100, 40), (100, 52), (62, 52)])
    rgb = rel[..., :3].astype(int); dark = rgb.sum(2) < 380
    arrow_px = arrow_m & ~(bow_keep & ~dark)
    string_m = np.zeros((H, W), np.uint8)
    cv2.line(string_m, (79, 10), (58, 43), 1, 2); cv2.line(string_m, (58, 45), (80, 82), 1, 2)
    string_px = (string_m > 0) & ~poly_mask(base.shape, [(40, 30), (70, 36), (70, 54), (40, 54)])
    _, rel = cut(rel, (arrow_px | string_px) & ~(hand_keep & (np.arange(W)[None, :] < 75)))
    rel[39:47, 105:, 3] = 0
    rest_layer = to_layer(rel)
    rig = {'parts': {'drawn': (to_layer(base), (58, 120)), 'released': (rest_layer, (58, 120))}, 'order': ['drawn', 'released']}
    straight = lambda F, dx=0, dy=0: F.line((P(79, 11)[0] + dx, P(79, 11)[1] + dy), (P(80, 81)[0] + dx, P(80, 81)[1] + dy), 'string')
    tipx, tipy = P(117, 43)
    A = {}
    idle = dict(hide=['released'], dur=220)
    def rel_frame(dx=0, fx=None, dur=100, body=(0, 0), tilt=0, **k):
        b = body
        return dict(k, body=b, tilt=tilt, hide=['drawn'], pre=[lambda F: straight(F, b[0], b[1])], fx=fx or [], dur=dur)
    A['attack'] = [
        idle,
        dict(hide=['released'], body=(-2, 0), fx=[lambda F: star(F, tipx - 2, tipy, 4)], dur=200),
        rel_frame(body=(-3, 0), fx=[lambda F: arrow(F, tipx + 6, tipx + 46, tipy), lambda F: speed(F, tipy - 6, tipy + 8, tipx - 10, tipx + 4)], dur=90),
        rel_frame(body=(-2, 0), fx=[lambda F: burst(F, FW - 10, tipy, 8)], dur=160),
        rel_frame(dur=200),
        idle,
    ]
    A['hit'] = [idle] + hit_frames((52, 50), dict(hide=['released'])) + [idle]
    A['skill'] = [  # Power Shot
        idle,
        dict(hide=['released'], body=(-1, 0), tint=((255, 232, 150), .12),
             fx=[lambda F: ring(F, tipx, tipy, 7), lambda F: star(F, tipx, tipy, 4)], dur=200),
        dict(hide=['released'], body=(-2, 0), tint=((255, 232, 150), .22),
             fx=[lambda F: ring(F, tipx, tipy, 11, 'wh'), lambda F: ring(F, tipx, tipy, 6), lambda F: star(F, tipx, tipy, 7),
                 lambda F: F.line(P(60, 43), (tipx, tipy), (255, 230, 140, 160), 3)], dur=240),
        rel_frame(body=(-4, 0), fx=[lambda F: arrow(F, tipx + 10, tipx + 50, tipy, True), lambda F: speed(F, tipy - 10, tipy + 12, tipx - 30, tipx)], dur=90),
        rel_frame(body=(-3, 0), fx=[lambda F: burst(F, FW - 12, tipy, 12, 'gold_l'), lambda F: ring(F, FW - 12, tipy, 9, 'wh')], dur=180),
        rel_frame(dur=180),
        idle,
    ]
    A['critical'] = [  # Piercing Shot
        idle,
        dict(hide=['released'], body=(-2, 4), tilt=3, tint=((255, 236, 170), .25), fx=[lambda F: star(F, *P(56, 36), 7)], dur=300),
        dict(hide=['released'], body=(-3, 4), tilt=3, fx=[lambda F: star(F, tipx - 3 - 3, tipy + 4, 9), lambda F: ring(F, tipx - 6, tipy + 4, 13, 'wh')], dur=200),
        rel_frame(body=(-8, 4), tilt=4,
                  fx=[lambda F: F.line((tipx - 14, tipy + 4), (FW, tipy + 4), (255, 248, 220, 255), 5),
                      lambda F: F.line((tipx - 14, tipy + 4), (FW, tipy + 4), 'gold_l', 2), lambda F: burst(F, FW - 16, tipy + 4, 15)], dur=120),
        rel_frame(body=(-5, 2), tilt=2, fx=[lambda F: ring(F, FW - 16, tipy + 4, 14, 'wh'), lambda F: ring(F, FW - 16, tipy + 4, 19, 'gold_l')], dur=200),
        rel_frame(dur=180),
        idle,
    ]
    return rig, A

# ---------------- CLERIC ----------------
def cleric():
    base = load('cleric')
    H, W = base.shape[:2]
    rgb = base[..., :3].astype(int)
    # sparkles above the open hand
    zone = poly_mask(base.shape, [(78, 20), (111, 20), (111, 62), (100, 62), (99, 49), (82, 49), (78, 40)])
    bright = (rgb.mean(2) > 165) & (rgb[..., 0] > 200)
    spark_m = zone & bright & (base[..., 3] > 0)
    spark_m = cv2.dilate(spark_m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & zone & (base[..., 3] > 0)
    sparks, rest = cut(base, spark_m)
    m = poly_mask(base.shape, [(0, 3), (38, 3), (37, 40), (30, 46), (16, 44), (0, 44)])
    band = np.zeros((H, W), np.uint8); cv2.line(band, (24, 42), (39, 114), 1, 6)
    m |= band.astype(bool) | poly_mask(base.shape, [(23, 55), (34, 55), (34, 65), (23, 65)])
    staff, rest = cut(rest, m)
    rig = {'parts': {'body': (to_layer(rest), (58, 120)), 'staff': (to_layer(staff), (28, 60)), 'sparks': (to_layer(sparks), (92, 40))},
           'order': ['body', 'staff', 'sparks']}
    A = {}; idle = dict(hide=['sparks'], dur=220)
    orb = P(18, 22); hand = P(92, 50)
    def bolt(F, x, y, r=4):
        F.line((x - 26, y), (x, y), (255, 236, 170, 120), 5); F.line((x - 16, y), (x, y), (255, 248, 220, 220), 3)
        F.d.ellipse([x - r, y - r, x + r, y + r], fill=col('gold_l')); F.d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=col('wh'))
    hx, hy = hand[0] + 6, hand[1] - 4
    A['attack'] = [  # Holy Light bolt
        idle,
        dict(hide=['sparks'], body=(-2, 0), tilt=2, fx=[lambda F: ring(F, hx, hy, 6), lambda F: star(F, hx, hy, 4)], dur=200),
        dict(hide=['sparks'], body=(-3, 0), tilt=3, fx=[lambda F: ring(F, hx, hy, 9, 'wh'), lambda F: ring(F, hx, hy, 5), lambda F: star(F, hx, hy, 6)], dur=160),
        dict(hide=['sparks'], body=(2, 0), tilt=-2, fx=[lambda F: bolt(F, hx + 34, hy), lambda F: star(F, hx, hy, 3)], dur=80),
        dict(hide=['sparks'], body=(2, 0), tilt=-1, fx=[lambda F: bolt(F, FW - 30, hy), lambda F: burst(F, FW - 14, hy, 11, 'gold_l')], dur=110),
        dict(hide=['sparks'], fx=[lambda F: ring(F, FW - 14, hy, 12, 'wh')], dur=180),
        idle,
    ]
    A['hit'] = [idle] + hit_frames((60, 60), dict(hide=['sparks'])) + [idle]
    A['skill'] = [  # Heal
        idle,
        dict(alpha=None, parts={'sparks': (0, 0, 6)}, fx=[lambda F: ring(F, *orb, 12, 'blue_l')], dur=170,
             pre=[]),
        dict(parts={'sparks': (0, 0, 2)}, fx=[lambda F: ring(F, *orb, 16, 'blue_l'), lambda F: ring(F, *orb, 10, 'wh'), lambda F: ring(F, *hand, 12)], dur=190),
        dict(parts={'sparks': (0, 0, -3)}, tint=((255, 240, 190), .12),
             fx=[lambda F: ring(F, *hand, 18), lambda F: ring(F, *hand, 11, 'wh'), lambda F: plus(F, hand[0] + 24, hand[1] - 30, 4),
                 lambda F: plus(F, hand[0] - 8, hand[1] - 38, 3)], dur=230),
        dict(parts={'sparks': (0, 0, -9)}, fx=[lambda F: plus(F, hand[0] + 26, hand[1] - 40, 3), lambda F: plus(F, hand[0] - 6, hand[1] - 46, 2),
                                               lambda F: plus(F, hand[0] + 10, hand[1] - 52, 2)], dur=220),
        dict(hide=['sparks'], fx=[lambda F: plus(F, hand[0] + 12, hand[1] - 58, 2), lambda F: star(F, hand[0] + 28, hand[1] - 50, 3)], dur=200),
        idle,
    ]
    A['critical'] = [  # Smite
        idle,
        dict(hide=['sparks'], body=(-3, 1), tilt=4, parts={'staff': (0, 0, -6)}, tint=((255, 238, 176), .25),
             fx=[lambda F: star(F, orb[0] - 3, orb[1] - 7, 9), lambda F: ring(F, orb[0] - 3, orb[1] - 7, 14, 'gold_l')], dur=300),
        dict(hide=['sparks'], body=(-3, 1), tilt=4, parts={'staff': (0, 0, -9)},
             fx=[lambda F: star(F, orb[0] - 3, orb[1] - 10, 11), lambda F: ring(F, orb[0] - 3, orb[1] - 10, 20, 'wh'), lambda F: ring(F, orb[0] - 3, orb[1] - 10, 13, 'gold_l'),
                 lambda F: ring(F, hx, hy, 8), lambda F: star(F, hx, hy, 6)], dur=200),
        dict(hide=['sparks'], body=(4, 0), tilt=-3, parts={'staff': (0, 0, -3)},
             fx=[lambda F: F.line((hx, hy), (FW, hy), (255, 236, 160, 150), 11), lambda F: F.line((hx, hy), (FW, hy), (255, 250, 228, 255), 5),
                 lambda F: burst(F, FW - 20, hy, 18, 'gold_l'), lambda F: plus(F, FW - 20, hy, 8)], dur=130),
        dict(hide=['sparks'], body=(3, 0), tilt=-2,
             fx=[lambda F: ring(F, FW - 20, hy, 16, 'gold_l'), lambda F: ring(F, FW - 20, hy, 23, 'wh'), lambda F: plus(F, FW - 34, hy - 20, 3),
                 lambda F: plus(F, FW - 10, hy - 26, 2)], dur=220),
        dict(hide=['sparks'], dur=180),
        idle,
    ]
    return rig, A

UNITS = {'soldier': soldier, 'archer': archer, 'cleric': cleric}
ORDER = ['attack', 'hit', 'skill', 'critical']

def build(out='ref_anim', scale=3):
    os.makedirs(out, exist_ok=True); bg = (222, 210, 186, 255)
    for unit, fn in UNITS.items():
        rig, A = fn()
        cols = max(len(A[a]) for a in ORDER)
        sheet = Image.new('RGBA', (FW * cols, FH * len(ORDER)), (0, 0, 0, 0))
        for r, an in enumerate(ORDER):
            frames = [render(rig, f) for f in A[an]]
            for c, fr in enumerate(frames): sheet.alpha_composite(fr, (c * FW, r * FH))
            gif = []
            for fr in frames:
                g = Image.new('RGBA', (FW, FH), bg); g.alpha_composite(fr)
                gif.append(g.resize((FW * scale, FH * scale), Image.NEAREST).convert('RGB'))
            durs = [f.get('dur', 150) for f in A[an]]; durs[-1] = 500
            gif[0].save(f'{out}/{unit}_{an}.gif', save_all=True, append_images=gif[1:], duration=durs, loop=0)
        sheet.save(f'{out}/{unit}_sheet.png')
        prev = Image.new('RGBA', sheet.size, bg); prev.alpha_composite(sheet)
        prev.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(f'{out}/{unit}_sheet_preview.png')
    print('done')

if __name__ == '__main__':
    build()
