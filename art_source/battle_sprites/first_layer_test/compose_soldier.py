import numpy as np, cv2, json
OUT = 'soldier_test'; rig = json.load(open(f'{OUT}/rig.json'))
def ld(n): return cv2.imread(f'{OUT}/{n}.png', cv2.IMREAD_UNCHANGED)
def shift(img, dx, dy): return cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, dy]]), (img.shape[1], img.shape[0]))
def over(dst, src):
    a = src[..., 3:4] / 255.0; dst[..., :3] = (src[..., :3] * a + dst[..., :3] * (1 - a)).astype(np.uint8)
def place(name, body, hand):
    src_stance, src_hand = rig['weapons'][name]
    sx, sy = rig['anchors'][src_stance][src_hand]; tx, ty = rig['anchors'][body][hand]
    return shift(ld(name if name.startswith('shield') else 'w_' + name), tx - sx, ty - sy)
def build(sex, weapon, shield=None, two_handed=False):
    body = f'{sex}_{"2h" if two_handed else "1h"}'
    img = np.full((200, 133, 4), (233, 222, 205, 255), np.uint8)   # beige test background
    over(img, ld('body_' + body))
    fist = lambda h: over(img, ld(f'fist_{body}_{h}'))
    if two_handed:
        over(img, place(weapon, body, 'grip')); fist('grip')
    elif shield:
        over(img, place(weapon, body, 'back')); fist('back'); over(img, place(shield, body, 'front'))
    else:
        over(img, place(weapon, body, 'front')); fist('front')
    return img[..., :3]
combos = [('longsword', 'shield_kite', False), ('greatsword', None, True), ('rapier', None, False), ('glaive', None, True),
          ('rapier', 'shield_kite', False), ('longsword', None, False)]
rows = [np.hstack([build(sex, w, s, t) for w, s, t in combos]) for sex in 'mf']
sheet = np.vstack(rows); cv2.imwrite('soldier_test_sheet.png', cv2.resize(sheet, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
