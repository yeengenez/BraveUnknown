"""Cut the longsword (image A) and rapier (image B) out of the kept first-test images along their axes.
Pixels inside a band around the weapon axis are kept if they are steel, gold or outline next to those.
The grip hidden under the fist is filled with dark leather so the weapon is whole. Output: weapon PNG
lying in its original angle, plus the grip point and axis angle."""
import json, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'battle_sprites', 'first_layer_test') + '/source'

BODY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'battle_sprites', 'soldier', 'bodies', 'm_1h.png')
def cut(src, p0, p1, hw, guard_t, guard_hw, grip_t, extra_gold_t=(), GLOVE_V=135, KEEP_RING=False):
    a = np.asarray(Image.open(f'{S}/{src}').convert('RGB')).astype(int)
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    p0, p1 = np.array(p0, float), np.array(p1, float); L = np.linalg.norm(p1 - p0); u = (p1 - p0) / L
    rel = np.dstack([xx - p0[0], yy - p0[1]]); t = rel @ u; n = rel @ np.array([-u[1], u[0]])
    width = np.where((t >= guard_t[0]) & (t <= guard_t[1]), guard_hw, hw)
    band = (t >= -1.5) & (t <= L + 1.5) & (np.abs(n) <= width)
    white = a.min(2) > 228
    lab0, _ = ndi.label(white); edge = set(np.unique(np.concatenate([lab0[0], lab0[-1], lab0[:, 0], lab0[:, -1]]))) - {0}
    bg = np.isin(lab0, list(edge))
    steel = (hsv[..., 1] < 70) & (hsv[..., 2] > 85) & ~bg
    gold = (hsv[..., 0] >= 8) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 70) & (hsv[..., 2] > 105)
    goldzone = ((t >= guard_t[0]) & (t <= guard_t[1])) | (t < grip_t[0])
    for g in extra_gold_t: goldzone |= (t >= g[0]) & (t <= g[1])
    # the plain body these images were edited from, registered by the legs (which never change)
    body = np.asarray(Image.open(BODY).convert('RGB')).astype(int); best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            sh = np.roll(np.roll(body, dy, 0), dx, 1); e = np.abs(sh[130:190] - a[130:190]).sum()
            if best is None or e < best[0]: best = (e, dx, dy)
    body = np.roll(np.roll(body, best[2], 0), best[1], 1)
    differs = np.abs(body - a).max(2) > 38
    keep = band & ~bg & (differs | (steel | (gold & goldzone)) & ~differs & False)
    keep = ndi.binary_opening(keep, iterations=0) if False else keep
    keep = ndi.binary_closing(keep, iterations=1) & band & ~bg
    glove = (hsv[..., 0] <= 20) & (hsv[..., 1] > 80) & (hsv[..., 2] < GLOVE_V)
    ring = (hsv[..., 0] >= 8) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 60) & (hsv[..., 2] > GLOVE_V)
    keep &= ~((t >= grip_t[0]) & (t <= grip_t[1]) & ~(ring & KEEP_RING))          # handle: replaced below (guard ring kept)
    keep &= ~(glove & (t >= grip_t[0] - 2) & (t <= guard_t[1]) & ~gold)            # no glove pixels around the guard
    lab, nl = ndi.label(keep); sizes = ndi.sum(keep, lab, range(1, nl + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 3])
    out = np.dstack([a, keep * 255]).astype(np.uint8)
    # leather grip under the fist (hidden in play, but keeps the weapon whole when the fist moves)
    gm = (t >= grip_t[0]) & (t <= grip_t[1]) & (np.abs(n) <= 1.6) & ~keep
    out[gm] = (60, 34, 22, 255); out[gm & (np.abs(n) <= 0.6)] = (98, 58, 34, 255)
    gp = p0 + u * (grip_t[1] - 3)          # hand sits right under the guard
    ys, xs = np.where(out[..., 3] > 0); x0, y0 = xs.min(), ys.min()
    crop = out[y0:ys.max() + 1, x0:xs.max() + 1]
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    return crop, (float(gp[0] - x0), float(gp[1] - y0)), ang

if __name__ == '__main__':
    meta = {}
    # A: pommel end -> tip. Crossguard near t 30..40, grip t 12..30 (under the glove)
    sw, g, ang = cut('w_longsword_shield.png', (20.5, 75.5), (64.5, 3.5), 3.2, (19, 33), 10.0, (4, 22))
    Image.fromarray(sw).save('k_longsword.png'); meta['longsword'] = dict(grip=g, angle=ang, size=sw.shape[1::-1])
    # B: pommel -> tip. Ring guard around t 14..26
    rp, g, ang = cut('w_rapier.png', (102.0, 93.5), (130.8, 30.0), 3.4, (6, 27), 8.5, (4, 18), GLOVE_V=92, KEEP_RING=True)
    Image.fromarray(rp).save('k_rapier.png'); meta['rapier'] = dict(grip=g, angle=ang, size=rp.shape[1::-1])
    json.dump(meta, open('k_meta.json', 'w'), indent=1); print(json.dumps(meta))
    Z = 6; ims = [Image.fromarray(sw), Image.fromarray(rp)]
    s = Image.new('RGBA', (sum(i.width * Z + 20 for i in ims), max(i.height for i in ims) * Z), (200, 228, 200, 255)); x = 0
    for i in ims: s.alpha_composite(i.resize((i.width * Z, i.height * Z), Image.NEAREST), (x, 0)); x += i.width * Z + 20
    s.save('previews/kept_cut.png')
