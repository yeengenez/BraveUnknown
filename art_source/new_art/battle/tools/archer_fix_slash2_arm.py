"""Archer slash 2 (user, 2026-11-25: "copy 2nd pic of 5th row to 1st pic of the 5th row, then remove purple stick"):
slash 2 = the FINISH figure with its magenta stick removed (hand empty), feet where the original slash 2 stood.
Works on the ChatGPT original (source/concepts/archer_dagger_m_sheet_gpt_raw.png), writes source/archer_dagger_m_sheet.png."""
import os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = np.asarray(Image.open(os.path.join(HERE, 'source', 'concepts', 'archer_dagger_m_sheet_gpt_raw.png')).convert('RGB')).copy()
assert a.shape[:2] == (1024, 1536)
FIN = (0, 683, 768, 1024)            # dual finish cell (row 3, left)
S2 = (1152, 341, 1536, 683)          # dual slash 2 cell (row 2, right)


def figure(c):
    r, g, b = [c[..., i].astype(int) for i in range(3)]
    fig = ~((g - r > 60) & (g - b > 60)) & ~((r < 80) & (g > 120) & (b < 120))
    for y in range(c.shape[0]):
        if y > 0.8 * c.shape[0] and (c[y].astype(int).sum(-1) < 200).mean() > 0.3: fig[y] = False
    fig[:4] = fig[-4:] = False; fig[:, :4] = fig[:, -4:] = False
    lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 150])


crop = lambda b: a[b[1]:b[3], b[0]:b[2]].copy()
fc = crop(FIN); fm = figure(fc)
r, g, b = [fc[..., i].astype(int) for i in range(3)]
mag = (r > 150) & (b > 150) & (g < 140); mag = ndi.binary_dilation(mag, iterations=2) & fm
inside = mag & ndi.binary_closing(fm & ~mag, iterations=5)     # stick pixels inside the fist -> fill with the fist
fc = cv2.inpaint(fc, inside.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
fm = (fm & ~mag) | inside
lab, n = ndi.label(fm, np.ones((3, 3))); sz = ndi.sum(fm, lab, range(1, n + 1)); fm = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 150])
sc = crop(S2); sm = figure(sc)
ys, xs = np.where(sm); s_feet = ys.max(); s_fx = xs[ys > s_feet - 14].mean()
ys, xs = np.where(fm); f_feet = ys.max(); f_fx = xs[ys > f_feet - 14].mean()
dx, dy = round(s_fx - f_fx), round(s_feet - f_feet)
xs_ = np.where(fm.any(0))[0]
if xs_.min() + dx < 6: dx = 6 - xs_.min()
if xs_.max() + dx > sc.shape[1] - 6: dx = sc.shape[1] - 6 - xs_.max()
new = sc.copy(); H_ = sc.shape[0]
keep = np.zeros(sc.shape[:2], bool)                               # only the template's own lines and the cell border stay
keep[round(0.92 * H_ - 0.78 * H_) - 3:round(0.92 * H_ - 0.78 * H_) + 4] = True
keep[round(0.92 * H_) - 4:round(0.92 * H_) + 5] = True
keep[:4] = keep[-4:] = True; keep[:, :4] = keep[:, -4:] = True
new[~keep] = (0, 255, 0)                                          # wipe the old figure completely
ys, xs = np.where(fm); ty, tx = ys + dy, xs + dx; k = (ty >= 0) & (ty < sc.shape[0]) & (tx >= 0) & (tx < sc.shape[1])
new[ty[k], tx[k]] = fc[ys[k], xs[k]]
out = a.copy(); out[S2[1]:S2[3], S2[0]:S2[2]] = new
Image.fromarray(out).save(os.path.join(HERE, 'source', 'archer_dagger_m_sheet.png'))
print('shift', dx, dy)
