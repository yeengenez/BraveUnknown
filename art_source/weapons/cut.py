"""Cut a weapon drawn on white into a transparent, tightly cropped PNG."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
near_white = (a.min(2) > 225) & (a.max(2) - a.min(2) < 18)
lab, _ = ndi.label(near_white)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
fg = ~bg
lab2, n = ndi.label(fg); sizes = ndi.sum(fg, lab2, range(1, n + 1))
fg = lab2 == (1 + int(np.argmax(sizes)))          # keep the weapon only
fg = ndi.binary_fill_holes(fg)
ys, xs = np.where(fg)
rgba = np.dstack([a, fg * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
Image.fromarray(rgba).save(out)
print(out, rgba.shape[1], 'x', rgba.shape[0])
