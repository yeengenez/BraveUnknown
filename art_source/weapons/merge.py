"""Merge pixel weapons onto battle sprite bodies. Pixel-art-safe rotation (scale2x x3, rotate, sample).
Body sits in the middle square of a 3-square strip so long weapons can cross into the next square."""
import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from pixel_weapons import build, to_rgba
import os as _os
B = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'battle_sprites')
RIG = json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'rig.json'))); W = build()
CELL, CH, TOP = 133, 200, 70          # square width, body height, extra room above for raised weapons

def body_rgba(key):
    c, n = key.split('/')
    a = np.asarray(Image.open(f'{B}/{c}/bodies/{n}.png').convert('RGB')).astype(int)
    white = (a.min(2) > 232)
    lab, _ = ndi.label(white); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ~np.isin(lab, list(edge))
    return np.dstack([a, fg * 255]).astype(np.uint8)

def scale2x(a):
    h, w = a.shape[:2]; p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    B_, D, E, F, H_ = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda x, y: np.all(x == y, axis=2)
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    c = eq(B_, H_) | eq(D, F)
    e0 = np.where((~c & eq(D, B_))[..., None], D, E); e1 = np.where((~c & eq(B_, F))[..., None], F, E)
    e2 = np.where((~c & eq(D, H_))[..., None], D, E); e3 = np.where((~c & eq(H_, F))[..., None], F, E)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out

def rotsprite(img, grip, deg):
    """Rotate an RGBA weapon about its grip; returns (rgba, new grip position)."""
    a = np.pad(img, ((2, 2), (2, 2), (0, 0))); g = (grip[0] + 2, grip[1] + 2)
    big = scale2x(scale2x(scale2x(a)))
    k = 8; h, w = big.shape[:2]; th = math.radians(deg)
    corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], float) - [g[0] * k, g[1] * k]
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    rc = corners @ R.T; x0, y0 = np.floor(rc.min(0) / k) - 1; x1, y1 = np.ceil(rc.max(0) / k) + 1
    ow, oh = int(x1 - x0), int(y1 - y0)
    yy, xx = np.mgrid[0:oh, 0:ow] + 0.5
    px = np.stack([(xx + x0) * k, (yy + y0) * k], -1)                    # output pixel centres, rel. to grip, in big px
    src = px @ np.linalg.inv(R).T + [g[0] * k, g[1] * k]
    sx, sy = np.floor(src[..., 0]).astype(int), np.floor(src[..., 1]).astype(int)
    ok = (sx >= 0) & (sy >= 0) & (sx < w) & (sy < h)
    out = np.zeros((oh, ow, 4), np.uint8); out[ok] = big[sy[ok], sx[ok]]
    return out, (-x0, -y0)

def paste(dst, src, x, y):
    x, y = int(round(x)), int(round(y)); h, w = src.shape[:2]
    m = src[..., 3] > 0; region = dst[y:y + h, x:x + w]
    region[m] = src[m]

def fist_mask(body, p, r=6):
    yy, xx = np.mgrid[0:body.shape[0], 0:body.shape[1]]
    return ((xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= r * r) & (body[..., 3] > 0)

def place(canvas, wname, anchor, deg, grip=None, ox=CELL, oy=TOP):
    w = W[wname]; img = np.asarray(to_rgba(w['img'])); gp = grip or w['grip']
    r, g = rotsprite(img, gp, deg)
    paste(canvas, r, ox + anchor[0] - g[0], oy + anchor[1] - g[1])

def merge(key, loadout):
    body = body_rgba(key); rig = RIG[key]
    canvas = np.zeros((CH + TOP, CELL * 3, 4), np.uint8)
    under, over = np.zeros_like(canvas), np.zeros_like(canvas)
    fists = []
    if loadout == 'sword':                       # one weapon, front hand, over the body, fist redrawn on top
        place(over, 'sword', rig['front'], rig['angle_1h']); fists = ['front']
    elif loadout == 'sword+shield':              # sword in the raised back hand (behind body), shield on front arm
        place(under, 'sword', rig['back'], -75)
        sx, sy = rig['front']; place(over, 'shield', (sx - 6, sy + 2), 0)
    elif loadout in ('greataxe', 'longspear'):   # both hands on the haft: anchor the back hand, aim at the front hand
        (fx, fy), (bx, by) = rig['front'], rig['back']
        deg = math.degrees(math.atan2(fy - by, fx - bx))
        if loadout == 'greataxe':                # painted weapon: drawn at the angle, not pixel-rotated
            import render_weapons as R
            img, g = R.greataxe(deg, R.AXE_GRIP2)
            paste(over, img, CELL + rig['back'][0] - g[0], TOP + rig['back'][1] - g[1])
        else:
            place(over, loadout, rig['back'], deg, grip=W[loadout]['grip2'])
        fists = ['front', 'back']
    out = canvas.copy(); paste(out, under, 0, 0)
    paste(out, body, CELL, TOP); paste(out, over, 0, 0)
    for f in fists:
        m = fist_mask(body, rig[f]); bb = np.zeros_like(canvas); bb[TOP:TOP + CH, CELL:CELL * 2][m] = body[m]; paste(out, bb, 0, 0)
    return out

TESTS = [('soldier/m_1h', 'sword+shield'), ('soldier/f_1h', 'sword+shield'), ('soldier/m_1h', 'sword'), ('soldier/f_1h', 'sword'),
         ('soldier/m_2h', 'greataxe'), ('soldier/f_2h', 'greataxe'), ('brawler/m_2h', 'greataxe'), ('brawler/f_2h', 'greataxe'),
         ('soldier/m_reach', 'longspear'), ('soldier/f_reach', 'longspear'), ('acolyte/m_reach', 'longspear'), ('acolyte/f_reach', 'longspear')]

if __name__ == '__main__':
    import sys
    strips = []
    for key, lo in TESTS:
        img = merge(key, lo)
        Image.fromarray(img).save(f'merged_{key.replace("/", "_")}_{lo.replace("+", "_")}.png')
        bg = Image.new('RGBA', (CELL * 3, CH + TOP + 16), (232, 226, 210, 255)); d = ImageDraw.Draw(bg)
        for i in range(3):
            d.rectangle([i * CELL, TOP + 120, (i + 1) * CELL - 1, CH + TOP - 2], fill=(212, 202, 178) if i == 1 else (222, 214, 194), outline=(170, 160, 140))
        bg.alpha_composite(Image.fromarray(img)); d.text((4, CH + TOP + 2), f'{key}  {lo}', fill=(60, 50, 40))
        strips.append(bg)
    cols = 2; sw, sh = strips[0].size
    sheet = Image.new('RGBA', (sw * cols, sh * ((len(strips) + 1) // cols)), (255, 255, 255, 255))
    for i, s in enumerate(strips): sheet.alpha_composite(s, ((i % cols) * sw, (i // cols) * sh))
    sheet.save('weapon_merge_test.png'); print(sheet.size)
