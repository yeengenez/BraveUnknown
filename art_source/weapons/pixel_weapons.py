"""Hand-placed pixel weapons on one shared palette. Each weapon is a palette-index grid drawn at
sprite scale, lying horizontal with the point/head to the right. Fills only; the dark outline is
added automatically around every shape. grip = (x, y) of the hand centre in the weapon's pixels."""
import numpy as np, json
from PIL import Image

PAL = {  # index: (name, rgb)
 1: ('outline', (34, 30, 38)),
 2: ('steel0', (78, 84, 98)), 3: ('steel1', (128, 136, 150)), 4: ('steel2', (180, 188, 200)), 5: ('steel3', (234, 238, 244)),
 6: ('wood0', (70, 42, 26)), 7: ('wood1', (108, 68, 38)), 8: ('wood2', (148, 98, 56)),
 9: ('leather0', (54, 32, 24)), 10: ('leather1', (100, 56, 34)),
 11: ('gold0', (150, 104, 32)), 12: ('gold1', (216, 172, 66)),
 13: ('blue0', (28, 46, 108)), 14: ('blue1', (46, 80, 166)), 15: ('blue2', (90, 128, 212)),
}
S0, S1, S2, S3, W0, W1, W2, L0, L1, G0, G1, B0, B1, B2 = range(2, 16)

class Grid:
    def __init__(s, w, h): s.a = np.zeros((h, w), np.uint8)
    def rect(s, x0, y0, x1, y1, c): s.a[y0:y1 + 1, x0:x1 + 1] = c
    def px(s, x, y, c): s.a[y, x] = c
    def mask(s, m, c): s.a[m] = c
    def outlined(s):
        a = np.pad(s.a, 1); f = a > 0
        ring = (np.roll(f, 1, 0) | np.roll(f, -1, 0) | np.roll(f, 1, 1) | np.roll(f, -1, 1)) & ~f
        a[ring] = 1; return a

def sword():
    g = Grid(66, 11); cy = 5
    # pommel (round, steel)
    g.rect(0, cy - 2, 3, cy + 2, S1); g.rect(1, cy - 2, 2, cy - 1, S3); g.px(0, cy - 2, 0); g.px(0, cy + 2, 0); g.px(3, cy + 2, S0)
    g.rect(4, cy - 1, 4, cy + 1, S0)                                  # pommel neck
    for x in range(5, 17):                                            # leather-wrapped grip, diagonal wraps
        g.rect(x, cy - 1, x, cy + 1, L1 if (x % 3) else L0); g.px(x, cy - 1, L1 if x % 3 == 1 else L0 if x % 3 == 0 else L1)
    for x in range(5, 17, 3): g.px(x, cy + 1, L0)
    g.rect(17, 0, 19, 10, S1); g.rect(17, 0, 17, 10, S3); g.rect(19, 0, 19, 10, S0)   # cross guard
    g.px(18, cy, G1)                                                  # small gold stud
    g.rect(20, cy - 2, 57, cy + 2, S2)                                # blade
    g.rect(20, cy - 2, 57, cy - 2, S3); g.rect(20, cy + 2, 57, cy + 2, S0); g.rect(22, cy, 52, cy, S1)  # edge light, shade, fuller
    for i, x in enumerate(range(58, 65)):                             # tapering point
        h = max(0, 2 - (i + 1) // 3)
        g.rect(x, cy - h, x, cy + h, S2); g.px(x, cy - h, S3)
    return g.outlined(), (11 + 1, cy + 1)

def shield():
    w, h = 26, 36; g = Grid(w, h)
    yy, xx = np.mgrid[0:h, 0:w]
    body = (yy < 16) | (((xx - 12.5) / 13.0) ** 2 + ((yy - 14) / 22.0) ** 2 <= 1)    # flat top, rounded point
    body &= (yy >= 1) | ((xx > 1) & (xx < w - 2))
    g.mask(body, S1)
    inner = (yy >= 2) & (xx >= 2) & (xx <= w - 3) & (((xx - 12.5) / 10.6) ** 2 + ((yy - 14) / 19.6) ** 2 <= 1) | ((yy >= 2) & (yy < 15) & (xx >= 2) & (xx <= w - 3))
    g.mask(body & inner, B1)
    g.mask(body & inner & (xx <= 6), B2)                              # light from the left
    g.mask(body & inner & (xx >= w - 8), B0)
    g.mask(body & ~inner & ((xx <= 3) | (yy <= 2)), S3)              # rim highlight top-left
    g.mask(body & ~inner & (xx >= w - 4), S0)
    # gold chevron and boss
    for x in range(3, w - 3):
        y = 6 + abs(x - 12) // 2
        if inner[y, x]: g.rect(x, y, x, min(y + 2, h - 1), G1); g.px(x, min(y + 2, h - 1), G0)
    g.rect(11, 15, 14, 18, G1); g.rect(13, 17, 14, 18, G0); g.px(11, 15, S3)
    return g.outlined(), (13 + 1, 17 + 1)        # handle behind the boss

def greataxe():
    L, H = 118, 34; cy = 29; g = Grid(L, H)
    g.rect(3, cy - 1, L - 4, cy + 1, W1); g.rect(3, cy - 1, L - 4, cy - 1, W2); g.rect(3, cy + 1, L - 4, cy + 1, W0)   # haft
    g.rect(0, cy - 2, 2, cy + 2, S1); g.rect(0, cy - 2, 1, cy - 1, S3)                                                   # butt cap
    for x in range(6, 30):                                                                                            # wrap at the grip
        g.rect(x, cy - 1, x, cy + 1, L1 if x % 4 else L0)
    # crescent head: u runs along the haft, v rises above the socket. Edge convex on top, horns curl down.
    hx0 = L - 22; top = cy - 4
    for v in range(0, 25):
        for u in range(-16, 17):
            edge = 24 - (u / 16) ** 2 * 7
            low = 0 if abs(u) <= 4 else ((abs(u) - 4) / 12) ** 1.6 * 17
            if low <= v <= edge:
                d = edge - v
                c = S3 if d < 1.6 else S2 if d < 4 else (S0 if u > 6 else S1)
                if c == S1 and u < -7: c = S2
                if low > 0 and v - low < 1.2 and c not in (S3,): c = S0
                g.px(hx0 + u, top - v, c)
    hx = hx0 - 9
    g.rect(hx + 6, cy - 4, hx + 13, cy + 3, S0); g.rect(hx + 6, cy - 4, hx + 13, cy - 4, S2)   # socket
    g.rect(hx + 6, cy - 1, hx + 13, cy - 1, G1)                                                # gold band
    g.rect(L - 3, cy - 1, L - 1, cy + 1, S1); g.px(L - 3, cy - 1, S3)                                                 # top spike
    return g.outlined(), (17 + 1, cy + 1), (8 + 1, cy + 1)

def longspear():
    L, H = 240, 9; cy = 4; g = Grid(L, H)
    g.rect(4, cy - 1, L - 24, cy + 1, W1); g.rect(4, cy - 1, L - 24, cy - 1, W2); g.rect(4, cy + 1, L - 24, cy + 1, W0)
    g.rect(0, cy - 1, 3, cy + 1, S1); g.rect(0, cy - 1, 3, cy - 1, S3)                     # butt cap
    sx = L - 24
    g.rect(sx, cy - 2, sx + 5, cy + 2, S0); g.rect(sx, cy - 2, sx + 5, cy - 2, S2)        # socket
    g.rect(sx + 1, cy - 2, sx + 1, cy + 2, G1); g.rect(sx + 4, cy - 2, sx + 4, cy + 2, G1)
    hx = sx + 6; hl = L - hx                                                               # leaf blade
    for i in range(hl):
        t = i / (hl - 1); half = int(round(4 * np.sin(np.pi * min(1, t * 1.25)) if t < 0.8 else 4 * (1 - t) / 0.2 * 0.75))
        half = max(0, min(4, half))
        g.rect(hx + i, cy - half, hx + i, cy + half, S2)
        g.px(hx + i, cy - half, S3)
        if half >= 2: g.px(hx + i, cy + half, S0)
    g.rect(hx + 1, cy, L - 3, cy, S3)                                                      # midrib
    return g.outlined(), (L - 60 + 1, cy + 1), (18 + 1, cy + 1)

WEAPONS = {}
def build():
    s, grip = sword(); WEAPONS['sword'] = dict(img=s, grip=grip)
    import render_weapons as R                       # shield and great axe: painted renders (render_weapons.py)
    sh, grip = R.shield(); WEAPONS['shield'] = dict(img=sh, grip=grip)
    a, front, back = R.greataxe(); WEAPONS['greataxe'] = dict(img=a, grip=front, grip2=back)
    sp, front, back = longspear(); WEAPONS['longspear'] = dict(img=sp, grip=front, grip2=back)
    return WEAPONS

def to_rgba(idx):
    if idx.ndim == 3: return Image.fromarray(idx)   # already RGBA (painted weapons)
    out = np.zeros(idx.shape + (4,), np.uint8)
    for k, (_, c) in PAL.items(): out[idx == k] = (*c, 255)
    return Image.fromarray(out)

if __name__ == '__main__':
    W = build()
    meta = {}
    for n, w in W.items():
        to_rgba(w['img']).save(f'px_{n}.png'); np.save(f'px_{n}.npy', w['img'])
        meta[n] = {k: list(map(int, v)) for k, v in w.items() if k.startswith('grip')}
    json.dump({'palette': {k: v[1] for k, v in PAL.items()}, 'weapons': meta}, open('px_meta.json', 'w'), indent=1)
    # zoom preview
    Z = 4; ims = [to_rgba(W[n]['img']) for n in ['sword', 'shield', 'greataxe', 'longspear']]
    sheet = Image.new('RGBA', (240 * Z + 20, sum(i.height * Z + 12 for i in ims) + 10), (220, 228, 214, 255)); y = 8
    for im in ims: sheet.alpha_composite(im.resize((im.width * Z, im.height * Z), Image.NEAREST), (8, y)); y += im.height * Z + 12
    sheet.save('previews/px_zoom.png')
