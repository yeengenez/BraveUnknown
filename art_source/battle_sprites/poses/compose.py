"""Three single-frame battle sprites per loadout: stand (the grip body), attack and hit (the new poses).
Weapons are drawn at each pose's measured grip points and angles; no tweening, the game swaps the three.
Feet are aligned to the stand sprite so swapping does not make the character jump.
Output: sprites/<class>_<sex>_<loadout>_<stand|attack|hit>.png (399x270, transparent) and review sheets."""
import sys, os, json, math, numpy as np
from PIL import Image, ImageDraw
_H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(_H, '../animation')); sys.path.insert(0, os.path.join(_H, '../grip_bodies'))
import anim as A, class_weapons as CW
from skin_layers import tint
import headscale
P = os.path.dirname(os.path.abspath(__file__)); os.chdir(P)

SCALE = {('reach', 'attack'): 1.25}

def split2h(g):
    g = {k: dict(v) if isinstance(v, dict) else v for k, v in g.items()}
    if 'front' not in g and 'back' in g:
        b = g['back']; th = math.radians(b['angle']); d = np.array([math.cos(th), math.sin(th)]); q = b['fist_gap'] / 4
        p = np.array(b['point']); g['back'] = dict(b, point=(p - d * q).tolist(), fist_gap=b['fist_gap'] / 2)
        g['front'] = dict(b, point=(p + d * q).tolist(), fist_gap=b['fist_gap'] / 2)
    return g

def load_state(cls, key, state, ramp):
    if state == 'stand':
        return A.grips(cls, key), A.body(cls, key, ramp)
    n = f'{cls}_{key}_{state.replace("_pose", "")}'
    g = split2h(json.load(open(f'grips_{n}.json'))['grips'])
    fx = np.asarray(Image.open(f'layers/{n}_fixed.png')); sk = np.asarray(Image.open(f'layers/{n}_skin.png'))
    b = tint(fx, sk, ramp)
    k = SCALE.get((key.split('_')[1], state), 1.0)
    if key.endswith('1h') and state == 'attack':     # some lunges came back drawn smaller: match the stand's head size
        r = headscale.ratio(n); k = r if r and 1.08 < r < 1.4 else 1.0
    if k != 1.0:                                   # Canva drew the deep spear lunge smaller than the stand
        im = Image.fromarray(b); W, H = im.size
        im = im.resize((round(W * k), round(H * k)), Image.LANCZOS); a = np.asarray(im).copy()
        a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
        b = a
        for v in g.values():
            if isinstance(v, dict) and 'point' in v: v['point'] = [v['point'][0] * k, v['point'][1] * k]; v['fist_gap'] *= k
    return g, b

def feet(b):
    ys, xs = np.where(b[..., 3] > 0); bot = ys.max(); low = ys > bot - 12
    return float(xs[low].mean()), float(bot)

# 1h loadouts: the weapon is always in the right hand ('back' = right, the raised fist in the stand; 'front' = left).
# Per state: list of (hand, weapon, layer). Shield attacks follow the user's reference (shield braced in front,
# weapon arm swinging forward over it, so the weapon is drawn last).
def one_hand(w, shield=False):
    st = [('back', w, 'under')] + ([('front', 'shield', 'over')] if shield else [])
    at = ([('front', 'shield', 'over')] if shield else []) + [('back', w, 'over')]
    return {'stand': st, 'attack': at, 'hit': st}
ITEMS = {'longsword': one_hand('longsword'), 'sword_shield': one_hand('longsword', True),
         'mace_shield': one_hand('mace', True), 'dagger': one_hand('dagger'), 'staff': one_hand('staff'),
         'dual_daggers': {k: [('front', 'dagger', 'over'), ('back', 'dagger', 'over')] for k in ('stand', 'attack', 'hit')},
         'unarmed': {k: [] for k in ('stand', 'attack', 'hit')}}
STATES = {'bow': ('stand', 'nock', 'attack', 'hit')}

def render(cls, sex, load, ramp):
    name, stance, items, _, _ = load; key = f'{sex}_{stance}'; out = {}
    ref = None
    for state in STATES.get(stance, ('stand', 'attack', 'hit')):
        if stance == 'bow':   # stand = new relaxed pose, nock = the full-draw grip body, attack = release
            g, b = load_state(cls, key, {'stand': 'stand_pose', 'nock': 'stand'}.get(state, state), ramp)
        else:
            g, b = load_state(cls, key, state, ramp)
        fx_, fy = feet(b)
        if ref is None: ref = (fx_, fy)
        dx, dy = round(ref[0] - fx_), round(ref[1] - fy)
        bowinfo = None; fx = None
        if stance == 'bow':
            L = g['bow_rod']['bottom'] - g['bow_rod']['top']
            bowinfo = dict(length=L, bow=CW.bow(int(L), -90.0), arrow=CW.arrow(int(g['front']['point'][0] - g['back']['point'][0] + 14)),
                           arrow_y=g.get('arrow', {}).get('y', g['front']['point'][1]))
            fx = 'nock' if state == 'nock' else None
        its = ITEMS[name][state] if name in ITEMS else items
        if cls == 'mage' and state == 'hit':            # recoil pulls the staff up across the face: keep it behind the head
            its = [(h, w, 'under') for h, w, _ in its]
        out[state] = A.frame(cls, key, ramp, its, (dx, dy, 0, 0, fx), [], 'attack', g, b, bowinfo, 0)
    return out

if __name__ == '__main__':
    os.makedirs('sprites', exist_ok=True)
    only = sys.argv[1:] or list(A.LOADOUTS)
    rows = []
    for cls in only:
        for sex, ramp in zip('mf', A.RAMPS[cls]):
            for load in A.LOADOUTS[cls]:
                s = render(cls, sex, load, ramp)
                for st, im in s.items(): Image.fromarray(im).save(f'sprites/{cls}_{sex}_{load[0]}_{st}.png')
                rows.append((f'{cls} {sex} {load[0]}', s))
    # review sheet: one row per loadout, stand | attack | hit, cropped to the body area
    x0, x1 = 90, 330; cw = x1 - x0; ch = A.CH_
    cols = 2; R = (len(rows) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (cw * 4 + 12), R * (ch + 16)), (236, 230, 216)); d = ImageDraw.Draw(sheet)
    for i, (lab, s) in enumerate(rows):
        ox = (i % cols) * (cw * 4 + 12); oy = (i // cols) * (ch + 16)
        d.text((ox + 4, oy + 2), lab + '   (' + ' | '.join(s) + ')', fill=(60, 50, 40))
        for j, st in enumerate(s):
            sheet.paste(Image.fromarray(s[st][:, x0:x1]), (ox + j * cw, oy + 14), Image.fromarray(s[st][:, x0:x1]))
    sheet.save('review.png'); print(len(rows), 'loadouts', sheet.size)
