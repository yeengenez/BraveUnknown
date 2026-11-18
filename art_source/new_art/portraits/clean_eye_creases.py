"""Remove eyelid-crease lines from the eye layers. At portrait size a crease line drawn above the upper lid reads as a
second eyebrow (user report 2026-11-19). In each column only the lowest continuous run of dark line pixels above the
eye (the lid / lash line) is kept; any dark run separated from it by skin is a crease and is removed.
Runs on every <sex>_eyes_<style>_fixed.png in place (re-run safe)."""
import glob, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
# male eyes only: the female sheets have no creases, and their separate lash strokes must stay
for f in sorted(glob.glob(os.path.join(HERE, 'm_eyes_*_fixed.png'))):
    img = np.asarray(Image.open(f)).copy(); a = img[..., 3] > 0
    ir = np.asarray(Image.open(f.replace('_fixed', '_iris')))[..., 3] > 0
    eye = (a & (img[..., 0] > 200)) | ir                   # eye white + iris
    line = a & ~(img[..., 0] > 200)
    removed = 0
    for x in range(200):
        col_line, col_eye = line[:, x], eye[:, x]
        ys = np.where(col_line | col_eye)[0]
        if len(ys) == 0: continue
        # lowest run of line pixels that sits on top of the eye (or the lowest run if the column has no eye)
        top_eye = np.where(col_eye)[0].min() if col_eye.any() else None
        runs = np.split(np.where(col_line)[0], np.where(np.diff(np.where(col_line)[0]) > 1)[0] + 1) if col_line.any() else []
        runs = [r for r in runs if len(r)]
        if top_eye is not None:
            above = [r for r in runs if r[-1] < top_eye]
            for r in above[:-1]:                                       # keep the lowest run (lid / lash line)
                img[r, x] = 0; removed += len(r)
        else:
            if len(runs) > 1:
                for r in runs[:-1]: img[r, x] = 0; removed += len(r)
    a2 = img[..., 3] > 0; lab, n = ndi.label(a2, structure=np.ones((3, 3))); sz = ndi.sum(a2, lab, range(1, n + 1))
    img[np.isin(lab, [i + 1 for i in range(n) if sz[i] < 3])] = 0
    Image.fromarray(img).save(f)
    print(os.path.basename(f), 'crease px removed', removed)
