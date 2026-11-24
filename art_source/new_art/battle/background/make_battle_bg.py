"""Battle background: isometric grassland with the party's supply cart parked behind the back row.

Drawn in code as pixel art (640 x 200, shown at 2x in the game). Light from the upper left, like the portraits.
Run:  python3 make_battle_bg.py <game repo>   -> <game>/sprites/battle/bg_grassland.png  (+ preview here)
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw

W, H = 640, 200
TW, TH = 32, 16                      # iso tile (2:1)
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))


def h2(i, j, s=0):                   # stable hash per tile -> 0..1
    n = (i * 73856093) ^ (j * 19349663) ^ (s * 83492791)
    return ((n * 2654435761) & 0xffffffff) / 0xffffffff


# ------------------------------------------------------------------ ground
def ground():
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    u = (xs / (TW / 2) + ys / (TH / 2)) / 2
    v = (ys / (TH / 2) - xs / (TW / 2)) / 2
    ti, tj = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - ti, v - tj
    base = np.array([74, 116, 54], float)
    img = np.zeros((H, W, 3))
    tile_l = np.vectorize(lambda a, b: h2(a, b))(ti, tj)
    tile_h = np.vectorize(lambda a, b: h2(a, b, 1))(ti, tj)
    shade = 0.93 + 0.11 * tile_l                                  # tile to tile brightness
    img[:] = base
    img *= shade[..., None]
    img[..., 0] += (tile_h - 0.5) * 10                           # some tiles yellower, some bluer
    img[..., 2] -= (tile_h - 0.5) * 8
    img += rng.normal(0, 3.2, (H, W, 1))                         # fine grain
    # seams: the two lower edges of each diamond a touch darker, upper edges a touch lighter
    img[(fu > 0.955) | (fv > 0.955)] *= 0.86
    img[(fu < 0.035) | (fv < 0.035)] *= 1.07
    # light from the upper left, darker toward the edges (keeps the UI readable at the borders)
    lx = 1.04 - 0.10 * (xs / W) - 0.10 * (ys / H)
    edge = np.minimum.reduce([ys / 26, (H - ys) / 18, np.ones_like(ys)])
    img *= (lx * (0.72 + 0.28 * np.clip(edge, 0, 1)))[..., None]
    return img


def put(img, x, y, c, a=1.0):
    if 0 <= x < W and 0 <= y < H:
        img[y, x] = img[y, x] * (1 - a) + np.array(c, float) * a


def tufts(img, n, box=(0, 0, W, H), avoid=None):
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = int(rng.integers(x0, x1)), int(rng.integers(y0, y1))
        if avoid and avoid(x, y):
            continue
        g = img[min(y, H - 1), min(x, W - 1)]
        light, dark = g * 1.28 + [6, 10, 0], g * 0.66
        for dx, dy in ((0, 0), (-1, -1), (1, -1), (0, -2)):
            put(img, x + dx, y + dy, light if dy < -1 or dx else light * 0.95)
        put(img, x, y + 1, dark)


def flowers(img, n, colours, box=(0, 0, W, H), avoid=None):
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = int(rng.integers(x0, x1)), int(rng.integers(y0, y1))
        if avoid and avoid(x, y):
            continue
        c = colours[int(rng.integers(len(colours)))]
        put(img, x, y, c); put(img, x, y + 1, img[min(y + 1, H - 1), x] * 0.6)


def rock(img, x, y, r):
    for dy in range(-r, r + 1):
        for dx in range(-r - 1, r + 2):
            d = (dx / (r + 1)) ** 2 + (dy / r) ** 2
            if d <= 1:
                lit = 0.5 - 0.35 * (dx + dy) / (r + 1)
                c = np.array([118, 116, 108]) * (0.72 + 0.45 * lit)
                put(img, x + dx, y + dy, c)
    for dx in range(-r - 1, r + 3):                                # contact shadow
        put(img, x + dx + 1, y + r + 1, img[min(y + r + 1, H - 1), max(0, min(W - 1, x + dx + 1))] * 0.55)


def bush(img, x, y, r, base=(52, 92, 42)):
    base = np.array(base, float)
    for dy in range(-r, r + 2):
        for dx in range(-r - 2, r + 3):
            if (dx / (r + 2)) ** 2 + (dy / (r + 0.5)) ** 2 <= 1:
                lit = -(dx + 1.4 * dy) / (r * 2.4)
                n = rng.normal(0, 0.06)
                put(img, x + dx, y + dy, base * (0.85 + 0.5 * lit + n))
    for dx in range(-r - 1, r + 4):
        put(img, x + dx + 2, y + r + 2, img[min(y + r + 2, H - 1), max(0, min(W - 1, x + dx + 2))] * 0.6)


# ------------------------------------------------------------------ cart (own layer, then outlined)
CX, CY = 46, 120                     # ground point under the middle of the cart
def P(u, v, z):
    return (CX + (u - v), CY + (u + v) / 2 - z)


WOOD = [(176, 124, 66), (142, 96, 50), (104, 68, 36), (74, 48, 26)]
CANVAS = [(236, 224, 194), (212, 196, 160), (176, 158, 124), (138, 120, 92)]
IRON = (64, 64, 72)


def quad(d, pts, c):
    d.polygon([P(*p) for p in pts], fill=c)


def box(d, u0, u1, v0, v1, z0, z1, pal):
    quad(d, [(u0, v1, z0), (u1, v1, z0), (u1, v1, z1), (u0, v1, z1)], pal[1])   # +v side (faces left-down, lit)
    quad(d, [(u1, v0, z0), (u1, v1, z0), (u1, v1, z1), (u1, v0, z1)], pal[2])   # +u side (faces right-down)
    quad(d, [(u0, v0, z1), (u1, v0, z1), (u1, v1, z1), (u0, v1, z1)], pal[0])   # top


def planks(d, u0, u1, v, z0, z1, n, c):
    for k in range(1, n):
        z = z0 + (z1 - z0) * k / n
        d.line([P(u0, v, z), P(u1, v, z)], fill=c)


def wheel(d, uc, v, zc, r):
    ring = [P(uc + r * math.cos(t), v, zc + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(ring, fill=WOOD[3])
    inner = [P(uc + (r - 1.6) * math.cos(t), v, zc + (r - 1.6) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(inner, fill=(46, 36, 26))
    for k in range(8):                                            # spokes
        t = k * math.pi / 4 + 0.2
        d.line([P(uc, v, zc), P(uc + (r - 1.4) * math.cos(t), v, zc + (r - 1.4) * math.sin(t))], fill=WOOD[1])
    d.line(ring[8:17], fill=WOOD[0])                              # lit upper-left rim
    hub = [P(uc + 1.6 * math.cos(t), v, zc + 1.6 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 12)]
    d.polygon(hub, fill=IRON)


def cart():
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    U0, U1, V0, V1, Z0, Z1 = -17, 17, -8, 8, 7, 13
    # shafts: forward (-u, up-left), resting on the ground
    for vs in (V0 + 2.5, V1 - 2.5):
        d.line([P(U0 + 2, vs, Z0 + 1), P(U0 - 22, vs, 0.5)], fill=WOOD[2], width=2)
        d.line([P(U0 + 2, vs, Z0 + 2), P(U0 - 22, vs, 1.5)], fill=WOOD[1])
    d.line([P(U0 - 20, V0 + 2.5, 1.2), P(U0 - 20, V1 - 2.5, 1.2)], fill=WOOD[2], width=2)   # yoke bar
    wheel(d, 0, V0 - 1, 8, 8)                                     # far wheel (mostly hidden)
    box(d, U0, U1, V0, V1, Z0 - 2, Z0, WOOD[1:] + [WOOD[3]])      # chassis
    box(d, U0, U1, V0, V1, Z0, Z1, WOOD)                          # bed
    planks(d, U0, U1, V1, Z0, Z1, 3, WOOD[2])
    planks(d, U0, U1, V1, Z0, Z1, 1, WOOD[2])
    # canvas cover: hoops along u, arched over the width
    vc, hw, hh = 0, 8.5, 11
    zt = lambda vv: Z1 + hh * math.sqrt(max(0.0, 1 - ((vv - vc) / hw) ** 2))
    cu0, cu1 = U0 + 3, U1 - 1
    steps = np.linspace(-hw, hw, 18)
    for a, b in zip(steps[:-1], steps[1:]):
        m = (a + b) / 2
        slope = -(m - vc) / hw                                     # >0 on the far side (top-right), <0 toward the viewer
        shade = 0 if m < -3 else (1 if m < 4 else 2)
        quad(d, [(cu0, a, zt(a)), (cu1, a, zt(a)), (cu1, b, zt(b)), (cu0, b, zt(b))], CANVAS[shade])
    for uh in (cu0 + 1, (cu0 + cu1) / 2, cu1 - 1):                 # hoop ribs
        d.line([P(uh, s, zt(s)) for s in steps], fill=CANVAS[2])
    end = [(cu1, s, zt(s)) for s in steps]                         # front end of the cover (+u face)
    d.polygon([P(*p) for p in end], fill=CANVAS[2])
    hole = [(cu1, s * 0.62, Z1 + (zt(s) - Z1) * 0.7) for s in steps]
    d.polygon([P(*p) for p in hole], fill=(70, 52, 36))
    # cargo peeking out of the opening: a sack and a crate corner
    d.ellipse([P(cu1, 1, Z1 + 4)[0] - 3, P(cu1, 1, Z1 + 4)[1] - 2, P(cu1, 1, Z1 + 4)[0] + 2, P(cu1, 1, Z1 + 4)[1] + 2], fill=(190, 170, 128))
    wheel(d, 0, V1 + 1, 8, 8)                                     # near wheel
    # load on the ground beside the cart: crates, a barrel, sacks
    box(d, 20, 27, -6, 1, 0, 7, [(190, 142, 84), (158, 112, 62), (118, 80, 42)])
    box(d, 21, 26, -5, 0, 7, 12, [(196, 150, 90), (162, 116, 66), (122, 84, 46)])
    bx, by = P(24, 9, 0)                                          # barrel
    d.ellipse([bx - 4, by - 4, bx + 4, by], fill=(132, 90, 48))
    d.rectangle([bx - 4, by - 10, bx + 4, by - 2], fill=(152, 106, 58))
    d.rectangle([bx - 4, by - 10, bx - 2, by - 2], fill=(176, 128, 72))
    d.ellipse([bx - 4, by - 12, bx + 4, by - 8], fill=(186, 140, 84))
    d.line([(bx - 4, by - 7), (bx + 4, by - 7)], fill=IRON); d.line([(bx - 4, by - 3), (bx + 4, by - 3)], fill=IRON)
    for (u, v) in ((11, 14), (15, 16)):                           # sacks
        sx, sy = P(u, v, 0)
        d.ellipse([sx - 4, sy - 7, sx + 4, sy], fill=CANVAS[1])
        d.ellipse([sx - 3, sy - 7, sx + 1, sy - 3], fill=CANVAS[0])
        d.line([(sx - 1, sy - 8), (sx + 1, sy - 8)], fill=(120, 92, 60))
    a = np.array(lay)
    # 1-px dark outline around everything
    al = a[..., 3] > 0
    nb = np.zeros_like(al)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb |= np.roll(np.roll(al, dy, 0), dx, 1)
    ol = nb & ~al
    a[ol] = (40, 28, 20, 255)
    return a


def shadow(img, a):
    """Cast shadow of the cart layer down-right onto the grass."""
    al = (a[..., 3] > 0).astype(float)
    sh = np.zeros_like(al)
    sh[3:, 5:] = al[:-3, :-5]
    ys = np.arange(H)[:, None]
    sh *= (ys > CY - 14)                                          # only the part near the ground
    img *= (1 - 0.38 * sh)[..., None]
    # dirt under the cart and two wheel ruts running off to the upper left
    for t in np.linspace(0, 1, 400):
        for vv in (-9, 9):
            x, y = P(-10 - 70 * t, vv, 0)
            x, y = int(round(x)), int(round(y))
            if 0 <= x < W and 0 <= y < H:
                img[y, x] = img[y, x] * 0.55 + np.array([96, 80, 54]) * 0.45


def main():
    img = ground()
    cart_layer = cart()
    cart_mask = cart_layer[..., 3] > 0
    shadow(img, cart_layer)
    near_cart = lambda x, y: x < 110 and abs(y - CY) < 40
    tufts(img, 900, avoid=near_cart)
    flowers(img, 70, [(236, 212, 92), (240, 236, 220), (204, 150, 210)], avoid=near_cart)
    # tree line / bushes along the top edge and a few at the bottom
    for x in range(-4, W + 10, 15):
        bush(img, x + int(rng.integers(-4, 5)), int(rng.integers(2, 7)), int(rng.integers(5, 8)), (44, 80, 38))
    for x in range(8, W, 46):
        bush(img, x + int(rng.integers(-8, 9)), H - int(rng.integers(2, 6)), int(rng.integers(3, 6)))
    # rocks in the no-man's-land between the two lines, and at the far edges
    for x, y, r in ((312, 70, 3), (330, 132, 2), (296, 158, 2), (338, 96, 1), (628, 120, 3), (616, 60, 2)):
        rock(img, x, y, r)
    out = np.clip(img, 0, 255).astype(np.uint8)
    out = np.dstack([out, np.full((H, W), 255, np.uint8)])
    out[cart_mask] = cart_layer[cart_mask]
    im = Image.fromarray(out, 'RGBA')
    game = sys.argv[1] if len(sys.argv) > 1 else None
    if game:
        dst = os.path.join(game, 'sprites', 'battle', 'bg_grassland.png')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst)
        print('->', dst)
    im.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(HERE, 'bg_grassland_preview.png'))
    im.save(os.path.join(HERE, 'bg_grassland.png'))


if __name__ == '__main__':
    main()
