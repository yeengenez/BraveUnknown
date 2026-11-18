import numpy as np, glob, os
from PIL import Image
from scipy import ndimage as ndi
def head(p):
    s = np.asarray(Image.open(p)); m = s[..., 1] > 0
    lab, n = ndi.label(m)
    if n == 0: return None
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 40: continue
        t = ys.min(); w = [np.ptp(xs[ys == y]) + 1 for y in range(t + 8, t + 16) if (ys == y).any()]
        if best is None or t < best[0]: best = (t, np.median(w))
    return best and best[1]
def ratio(n):
    c, r = n.split('_', 1); k = '_'.join(r.split('_')[:2])
    a, b = head(f'layers/{n}_skin.png'), head(f'../grip_bodies/layers/{c}_{k}_skin.png')
    return a and b and b / a
if __name__ == '__main__':
    for f in sorted(glob.glob('layers/*_skin.png')):
        n = os.path.basename(f)[:-9]; print(n, ratio(n) and round(ratio(n), 2))
