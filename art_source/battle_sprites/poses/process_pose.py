"""Attack / get-hit pose images (Canva edits with magenta guide rods) -> clean bodies, grip data, skin layers.
Same rod reading as grips/process2.py. There is no weapon-less original for a new pose, so the pixels under the
rods are inpainted from their neighbours (the weapon is drawn over most of them anyway)."""
import sys, os, json, glob, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../grip_bodies'))
from keyrod import load, magenta_mask
from process import shared_rod
from process2 import pieces, group_collinear, hand_from
import skin_layers as SL
SL.HEAD_REL = 0.34; SL.BRAWLER_REL = 0.62
ANIM = 'attack'
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def clean(a, m):
    zone = ndi.binary_dilation(m, iterations=3)
    mm = ndi.binary_dilation(m, iterations=1) | zone & (a[..., 0] - a[..., 1] > 6) & (a[..., 2] - a[..., 1] > 6)
    out = cv2.inpaint(a.astype(np.uint8), mm.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    return out

def rod_mask(a):
    """Magenta mask grown only from pure guide-rod pixels, so violet robes are not taken for rods."""
    m = magenta_mask(a)
    seed = (a[..., 0] >= 200) & (a[..., 1] <= 110) & (a[..., 2] >= 170) & (np.abs(a[..., 0] - a[..., 2]) < 70)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    keep = np.unique(lab[seed & m]); keep = keep[keep > 0]
    return np.isin(lab, keep)

def cyan_mask(a):
    """Off-hand (left) guide rod: flat cyan #00FFFF."""
    near = (a[..., 1] - a[..., 0] > 60) & (a[..., 2] - a[..., 0] > 60) & (a[..., 1] > 120) & (a[..., 2] > 120)
    seed = (a[..., 0] <= 120) & (a[..., 1] >= 190) & (a[..., 2] >= 190)
    m = ndi.binary_dilation(near, iterations=1) & (near | ndi.binary_dilation(seed, iterations=1))
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    keep = np.unique(lab[seed & m]); keep = keep[keep > 0]
    return np.isin(lab, keep)

def hand_of(m, a):
    groups = group_collinear(pieces(m, 3)); groups.sort(key=lambda gr: -sum(len(p) for p in gr))
    gr = groups[0]
    if len(gr) >= 2: return hand_from(gr)
    # rod seen on one side of the fist only: the fist is at the end nearer the body
    pts = gr[0]; c = pts.mean(0); _, _, vt = np.linalg.svd(pts - c); d = vt[0]
    body = np.argwhere(a.min(2) < 230)[:, ::-1].mean(0)
    t = (pts - c) @ d; e0, e1 = c + d * t.min(), c + d * t.max()
    near, far = (e0, e1) if np.linalg.norm(e0 - body) < np.linalg.norm(e1 - body) else (e1, e0)
    u = (far - near) / max(1e-6, np.linalg.norm(far - near)); p = near - u * 5
    return dict(point=[round(float(p[0]), 1), round(float(p[1]), 1)], angle=round(float(np.degrees(np.arctan2(u[1], u[0]))), 1), fist_gap=10.0)

def one_sided(m, a):
    """2h rod that only sticks out in front of the fists: the fists sit at the end nearer the body."""
    ps = pieces(m); pts = max(ps, key=len); c = pts.mean(0); _, _, vt = np.linalg.svd(pts - c); d = vt[0]
    body = np.argwhere(a.min(2) < 230)[:, ::-1].mean(0)
    t = (pts - c) @ d; e0, e1 = c + d * t.min(), c + d * t.max()
    near, far = (e0, e1) if np.linalg.norm(e0 - body) < np.linalg.norm(e1 - body) else (e1, e0)
    u = (far - near) / np.linalg.norm(far - near); p = near - u * 6
    return {'back': dict(point=[round(float(p[0]), 1), round(float(p[1]), 1)], angle=round(float(np.degrees(np.arctan2(u[1], u[0]))), 1), fist_gap=12.0)}

def orient(g, anim):
    """A rod gives an axis, not which end is the weapon head: attacks point forward, hit poses point up."""
    for k, v in g.items():
        if not (isinstance(v, dict) and 'angle' in v) or k == 'bow_rod': continue
        th = np.radians(v['angle']); dx, dy = np.cos(th), np.sin(th)
        flip = (dx < -0.05) if anim == 'attack' else (dy > 0.05)
        if flip: v['angle'] = round(float((v['angle'] + 360) % 360 - 180), 1)
    return g

def grips_for(m, stance, a):
    if stance in ('2h', 'reach'):
        g = shared_rod(m)
        return g if 'back' in g else one_sided(m, a)
    if stance == 'bow':
        ys, xs = np.where(m)
        col = np.bincount(xs, minlength=a.shape[1]); rx = int(np.argmax(col))
        on = np.abs(xs - rx) <= 2; vy = np.unique(ys[on])
        runs = np.split(vy, np.where(np.diff(vy) > 2)[0] + 1)
        if len(runs) >= 2:
            k = int(np.argmax([runs[i + 1][0] - runs[i][-1] for i in range(len(runs) - 1)]))
            gy = (runs[k][-1] + runs[k + 1][0]) / 2; fg = runs[k + 1][0] - runs[k][-1]
        else:
            gy = vy.mean(); fg = 10
        f = dict(point=[float(rx), round(float(gy), 1)], angle=-90.0, fist_gap=float(fg))
        return {'front': f, 'back': dict(f, fist_gap=0.0), 'bow_rod': dict(top=float(vy.min()), bottom=float(vy.max()))}
    groups = group_collinear(pieces(m)); groups.sort(key=lambda gr: -sum(len(p) for p in gr)); groups = groups[:2]
    hs = [hand_from(gr) for gr in groups]; hs.sort(key=lambda h: h['point'][0] if ANIM == 'hit' else h['point'][1])
    return {'back': hs[0], 'front': hs[-1]} if len(hs) == 2 else {'front': hs[0], 'back': hs[0]}

def process(n):
    cls, rest = n.split('_', 1); stance = rest.split('_')[1]
    global ANIM; ANIM = rest.split('_')[2]
    a = load(f'raw/{n}.png'); m = rod_mask(a); c = cyan_mask(a)
    if stance == '1h' and c.sum() > 8:
        # right hand (weapon) = magenta -> 'back'; left hand (shield / off-hand) = cyan -> 'front'
        g = orient({'back': hand_of(m, a)}, ANIM); g['front'] = orient({'f': hand_of(c, a)}, 'hit')['f']
        m = m | c
    else:
        g = orient(grips_for(m, stance, a), ANIM)
    Image.fromarray(clean(a, m)).save(f'bodies/{n}.png')
    json.dump({'grips': g}, open(f'grips/grips_{n}.json', 'w'))
    fixed, skin = SL.split(f'bodies/{n}.png', f'grips/grips_{n}.json')
    Image.fromarray(fixed).save(f'layers/{n}_fixed.png'); Image.fromarray(skin, 'LA').save(f'layers/{n}_skin.png')
    return g

if __name__ == '__main__':
    for d in ('bodies', 'layers', 'grips'): os.makedirs(d, exist_ok=True)
    todo = sys.argv[1:] or sorted(os.path.basename(f)[:-4] for f in glob.glob('raw/*.png') if 'rejected' not in f)
    for n in todo:
        g = process(n)
        print(n, {k: (v.get('point'), v.get('angle')) for k, v in g.items() if isinstance(v, dict) and 'point' in v})
