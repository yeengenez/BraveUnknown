"""Second weapon merge test, using the art the user picked: the longsword and kite shield from the first
test image A, the rapier-style front grip from image B, and spear lines measured from the kept reach
previews (the shaft passes through the middle of both fists)."""
import json, math, os, numpy as np
from PIL import Image, ImageDraw
import merge as M
import render_weapons as R
from pixel_weapons import build, to_rgba
W = build(); K = json.load(open('k_meta.json'))
SWORD = np.asarray(Image.open('k_longsword.png').convert('RGBA'))
SHIELD = np.asarray(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'battle_sprites', 'first_layer_test') + '/layers/shield_kite.png').convert('RGBA'))
from scipy import ndimage as _ndi
_lab, _n = _ndi.label(SHIELD[..., 3] > 0); _big = _lab == (1 + int(np.argmax(_ndi.sum(SHIELD[..., 3] > 0, _lab, range(1, _n + 1)))))
SHIELD = SHIELD.copy(); SHIELD[~_big] = 0                       # drop stray specks from the old cut
SHIELD_FIST = (105, 78)                              # front fist of the body the shield was cut from (m_1h)
# spear line through both fists, measured from prev_<sex>_reach_spear: y = k x + c (body pixels)
SHAFT = {'soldier/m_reach': (-0.108, 99.6), 'soldier/f_reach': (-0.166, 103.9)}
for k in ('m', 'f'):                                 # Acolyte reach bodies: same pose, shifted by the fist offset
    s, a = M.RIG[f'soldier/{k}_reach'], M.RIG[f'acolyte/{k}_reach']
    dy = ((a['front'][1] - s['front'][1]) + (a['back'][1] - s['back'][1])) / 2
    SHAFT[f'acolyte/{k}_reach'] = (SHAFT[f'soldier/{k}_reach'][0], SHAFT[f'soldier/{k}_reach'][1] + dy)
FRONT_ANGLE = -66.0                                  # like the rapier in B: steep, guard just above the fist
BACK_ANGLE = -78.0                                   # raised behind the head, as in A

def sword_at(angle):
    g = K['longsword']['grip']; d = angle - K['longsword']['angle']
    if abs(d) < 0.5: return SWORD, g
    return M.rotsprite(SWORD, g, d)

def merge(key, lo):
    body = M.body_rgba(key); rig = M.RIG[key]
    sh = (M.CH + M.TOP, M.CELL * 3, 4)
    under, over, fist, bod = [np.zeros(sh, np.uint8) for _ in range(4)]
    M.paste(bod, body, M.CELL, M.TOP); fl = []
    if lo == 'sword':
        img, g = sword_at(FRONT_ANGLE); f = rig['front']
        M.paste(over, img, M.CELL + f[0] - g[0], M.TOP + f[1] - g[1]); fl = ['front']
    elif lo == 'sword+shield':
        img, g = sword_at(BACK_ANGLE); b = rig['back']
        M.paste(under, img, M.CELL + b[0] - g[0], M.TOP + b[1] - g[1])
        dx, dy = rig['front'][0] - SHIELD_FIST[0], rig['front'][1] - SHIELD_FIST[1]
        M.paste(over, SHIELD, M.CELL + dx, M.TOP + dy)
    elif lo == 'greataxe':
        (fx, fy), (bx, by) = rig['front'], rig['back']; deg = math.degrees(math.atan2(fy - by, fx - bx))
        img, g = R.greataxe(deg, R.AXE_GRIP2); M.paste(under, img, M.CELL + bx - g[0], M.TOP + by - g[1])
    elif lo == 'longspear':
        (fx, fy), (bx, by) = rig['front'], rig['back']; deg = math.degrees(math.atan2(fy - by, fx - bx))
        img = np.asarray(to_rgba(W['longspear']['img'])); g = W['longspear']['grip2']
        r, gg = M.rotsprite(img, g, deg); M.paste(under, r, M.CELL + bx - gg[0], M.TOP + by - gg[1])   # behind: the arms wrap over it
    for f in fl:
        m = M.fist_mask(body, rig[f], r=5); fist[M.TOP:M.TOP + M.CH, M.CELL:M.CELL * 2][m] = body[m]
    out = np.zeros(sh, np.uint8)
    for layer in (under, bod, over, fist): M.paste(out, layer, 0, 0)
    return out, dict(weapon_back=under, body=bod, weapon_front=over, fists=fist)

if __name__ == '__main__':
    strips = []
    for key, lo in M.TESTS:
        img, _ = merge(key, lo)
        bg = Image.new('RGBA', (M.CELL * 3, M.CH + M.TOP + 16), (232, 226, 210, 255)); d = ImageDraw.Draw(bg)
        for i in range(3):
            d.rectangle([i * M.CELL, M.TOP + 120, (i + 1) * M.CELL - 1, M.CH + M.TOP - 2], fill=(212, 202, 178) if i == 1 else (222, 214, 194), outline=(170, 160, 140))
        bg.alpha_composite(Image.fromarray(img)); d.text((4, M.CH + M.TOP + 2), f'{key}  {lo}', fill=(60, 50, 40)); strips.append(bg)
    sw, shh = strips[0].size; sheet = Image.new('RGBA', (sw * 2, shh * 6), 'white')
    for i, s in enumerate(strips): sheet.alpha_composite(s, ((i % 2) * sw, (i // 2) * shh))
    sheet.save('previews/weapon_merge_test2.png'); print(sheet.size)
