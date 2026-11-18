"""Fit weapons to grip bodies using the measured grip lines (no guessing of fist anchors)."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'weapons'))
import merge as M
_W = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'weapons')
K = json.load(open(os.path.join(_W, 'k_meta.json')))
SWORD = np.asarray(Image.open(os.path.join(_W, 'k_longsword.png')).convert('RGBA'))
CELL, TOP, CH = M.CELL, M.TOP, M.CH

def body_rgba(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    white = a.min(2) > 232
    lab, _ = ndi.label(white); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return np.dstack([a, ~np.isin(lab, list(edge)) * 255]).astype(np.uint8)

def weapon_at(img, grip, native, angle):
    if abs(angle - native) < 0.5: return img, grip
    return M.rotsprite(img, grip, angle - native)

def fist(body, p, r):
    yy, xx = np.mgrid[0:body.shape[0], 0:body.shape[1]]
    return ((xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= r * r) & (body[..., 3] > 0)

def compose(body, items):
    """items: list of (rgba, grip_xy, body_point, layer, fist_r) with layer 'front' or 'back'."""
    sh = (CH + TOP, CELL * 3, 4); under, over, fl = [np.zeros(sh, np.uint8) for _ in range(3)]
    bod = np.zeros(sh, np.uint8); M.paste(bod, body, CELL, TOP)
    for img, g, p, layer, r in items:
        M.paste(over if layer == 'front' else under, img, CELL + p[0] - g[0], TOP + p[1] - g[1])
        if r:
            m = fist(body, p, r); fl[TOP:TOP + CH, CELL:CELL * 2][m] = body[m]
    out = np.zeros(sh, np.uint8)
    for l in (under, bod, over, fl): M.paste(out, l, 0, 0)
    return out

def strip(img, label):
    bg = Image.new('RGBA', (CELL * 3, CH + TOP + 16), (232, 226, 210, 255)); d = ImageDraw.Draw(bg)
    for i in range(3):
        d.rectangle([i * CELL, TOP + 120, (i + 1) * CELL - 1, CH + TOP - 2], fill=(212, 202, 178) if i == 1 else (222, 214, 194), outline=(170, 160, 140))
    bg.alpha_composite(Image.fromarray(img)); d.text((4, CH + TOP + 2), label, fill=(60, 50, 40)); return bg

if __name__ == '__main__':
    g = json.load(open('grips_soldier_m_1h.json'))['grips']; body = body_rgba('bodies/soldier_m_1h.png')
    sg, sa = K['longsword']['grip'], K['longsword']['angle']
    f_img, f_g = weapon_at(SWORD, sg, sa, g['front']['angle'])
    b_img, b_g = weapon_at(SWORD, sg, sa, g['back']['angle'])
    r = g['front']['fist_gap'] / 2
    a = compose(body, [(f_img, f_g, g['front']['point'], 'front', r)])
    b = compose(body, [(b_img, b_g, g['back']['point'], 'front', g['back']['fist_gap'] / 2)])
    c = compose(body, [(b_img, b_g, g['back']['point'], 'front', g['back']['fist_gap'] / 2), (f_img, f_g, g['front']['point'], 'front', r)])
    s = [strip(a, 'front hand'), strip(b, 'back hand'), strip(c, 'both (dual wield)')]
    sheet = Image.new('RGBA', (CELL * 3 * 3, CH + TOP + 16)); [sheet.alpha_composite(x, (i * CELL * 3, 0)) for i, x in enumerate(s)]
    sheet.save('fit_test_m1h.png')
    z = sheet.crop((CELL - 10, 20, CELL * 2 + 10, 230)); zs = [sheet.crop((i * CELL * 3 + CELL - 10, 20, i * CELL * 3 + CELL * 2 + 10, 230)) for i in range(3)]
    out = Image.new('RGBA', (sum(q.width for q in zs) * 3, zs[0].height * 3), 'white'); x = 0
    for q in zs: out.paste(q.resize((q.width * 3, q.height * 3), Image.NEAREST), (x, 0)); x += q.width * 3
    out.save('previews/fit_zoom.png')
