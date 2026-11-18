"""Find the magenta guide rods in a grip body, fit one axis per rod, and remove the magenta.
Magenta pixels over the body are refilled from the original (registered) weapon-less body."""
import sys, json, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi

def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)

def magenta_mask(a):
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int)
    m = (hsv[..., 0] >= 135) & (hsv[..., 0] <= 170) & (hsv[..., 1] > 90) & (hsv[..., 2] > 110)
    return ndi.binary_dilation(m, iterations=1) & ((hsv[..., 0] >= 125) | (hsv[..., 0] <= 5) | (hsv[..., 1] < 120) | True) & \
        ((np.abs(a[..., 0] - a[..., 2]) < 90) & (a[..., 0] > a[..., 1] + 40) | m)

def rods(m, min_px=8):
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) < min_px: continue
        pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0)
        u, s, vt = np.linalg.svd(pts - c); d = vt[0]
        if d[1] > 0: d = -d                                   # point "up" (negative y)
        t = (pts - c) @ d
        out.append(dict(center=c.tolist(), dir=d.tolist(), angle=float(np.degrees(np.arctan2(d[1], d[0]))),
                        ends=[(c + d * t.min()).tolist(), (c + d * t.max()).tolist()], n=int(len(xs))))
    return out

if __name__ == '__main__':
    src = sys.argv[1]; a = load(src); m = magenta_mask(a)
    R = rods(m); print(json.dumps(R, indent=1))
