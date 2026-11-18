"""Fit the test weapons to the grip bodies along the measured grip lines.
1h: longsword in the front hand; longsword in the raised back hand + kite shield on the front arm.
2h: great axe.  reach: longspear.  Weapons are drawn in front of the body (the guide rods were in
front, so the fists wrap over them) and the fists are redrawn on top."""
import sys, json, glob, numpy as np
from PIL import Image
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'weapons'))
import merge as M, render_weapons as R
from pixel_weapons import build, to_rgba
from fit import body_rgba, weapon_at, compose, strip, SWORD, K, CELL, TOP, CH
import merge2 as M2
W = build()
SPEAR = np.asarray(to_rgba(W['longspear']['img']))

def hands(g):
    """Back/front grip points; a single long gap (2h: fists touching) is split in two."""
    if 'front' in g and 'back' in g: return g['back'], g['front']
    b = g['back']; th = np.radians(b['angle']); d = np.array([np.cos(th), np.sin(th)]); q = b['fist_gap'] / 4
    p = np.array(b['point'])
    return (dict(point=(p - d * q).tolist(), angle=b['angle'], fist_gap=b['fist_gap'] / 2),
            dict(point=(p + d * q).tolist(), angle=b['angle'], fist_gap=b['fist_gap'] / 2))

def loadouts(key):
    g = json.load(open(f'grips/grips_soldier_{key}.json'))['grips']; body = body_rgba(f'bodies/soldier_{key}.png')
    sg, sa = K['longsword']['grip'], K['longsword']['angle']; out = []
    if key.endswith('1h'):
        f, b = g['front'], g['back']
        fi, fg = weapon_at(SWORD, sg, sa, f['angle']); bi, bg = weapon_at(SWORD, sg, sa, b['angle'])
        out.append(('sword', compose(body, [(fi, fg, f['point'], 'front', f['fist_gap'] / 2)])))
        dx, dy = f['point'][0] - M2.SHIELD_FIST[0], f['point'][1] - M2.SHIELD_FIST[1]
        sh = M2.SHIELD; shg = (M2.SHIELD_FIST[0] - 0, M2.SHIELD_FIST[1] - 0)
        out.append(('sword+shield', compose(body, [(bi, bg, b['point'], 'front', b['fist_gap'] / 2),
                                                    (sh, shg, f['point'], 'front', 0)])))
    else:
        b, f = hands(g); ang = b['angle']
        if key.endswith('2h'):
            img, gp = R.greataxe(ang, R.AXE_GRIP2); name = 'greataxe'
        else:
            img, gp = M.rotsprite(SPEAR, W['longspear']['grip2'], ang); name = 'longspear'
        out.append((name, compose(body, [(img, gp, b['point'], 'front', b['fist_gap'] / 2),
                                         (np.zeros((1, 1, 4), np.uint8), (0, 0), f['point'], 'front', f['fist_gap'] / 2)])))
    return out

if __name__ == '__main__':
    strips = []
    for key in ['m_1h', 'f_1h', 'm_2h', 'f_2h', 'm_reach', 'f_reach']:
        for name, img in loadouts(key):
            pass  # Image.fromarray(img).save(f'fit_soldier_{key}_{name.replace("+", "_")}.png')
            strips.append(strip(img, f'soldier {key}  {name}'))
    sw, sh = strips[0].size; cols = 2; rows = (len(strips) + 1) // 2
    sheet = Image.new('RGBA', (sw * cols, sh * rows), 'white')
    for i, s in enumerate(strips): sheet.alpha_composite(s, ((i % cols) * sw, (i // cols) * sh))
    sheet.save('previews/soldier_grip_sheet.png'); print(sheet.size, len(strips))
