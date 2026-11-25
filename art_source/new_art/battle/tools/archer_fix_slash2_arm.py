"""Archer slash 2 (user, 2026-11-25): the near arm must be raised at the same angle as in FINISH, only without the stick.
Rotates the near arm (with its open hand) of the dagger sheet's slash 2 cell about the shoulder. Works on the ChatGPT
original (source/concepts/archer_dagger_m_sheet_gpt_raw.png) and writes source/archer_dagger_m_sheet.png."""
import os, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = np.asarray(Image.open(os.path.join(HERE, 'source', 'concepts', 'archer_dagger_m_sheet_gpt_raw.png')).convert('RGB')).copy()
r, g, b = [a[..., i].astype(int) for i in range(3)]
green = (g - r > 60) & (g - b > 60)
PIV = np.array([1328.0, 468.0])                 # near shoulder
DEG = 12.0                                      # raise the arm (finish arm ~13 deg above horizontal, slash 2 ~1 deg)
pm = Image.new('L', (a.shape[1], a.shape[0]), 0)
ImageDraw.Draw(pm).polygon([(1164, 434), (1300, 432), (1318, 442), (1330, 452), (1330, 492), (1300, 494), (1240, 492), (1164, 488)], fill=1)
arm = (np.asarray(pm) > 0) & ~green
t = math.radians(DEG); yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
# inverse map: a destination pixel takes the source pixel rotated back (arm tip pointing left goes up)
dx, dy = xx - PIV[0], yy - PIV[1]
sx = np.rint(PIV[0] + dx * math.cos(t) + dy * math.sin(t)).astype(int).clip(0, a.shape[1] - 1)
sy = np.rint(PIV[1] - dx * math.sin(t) + dy * math.cos(t)).astype(int).clip(0, a.shape[0] - 1)
new = arm[sy, sx]; newc = a[sy, sx]
out = a.copy()
old = arm & ~new
behind = (np.asarray(pm) > 0) & ~new & (xx > 1290) & (yy > 470)                                 # near the shoulder: fill from the body around it
body = ~green & ~arm
iy, ix = ndi.distance_transform_edt(~body, return_distances=False, return_indices=True)
out[behind] = a[iy[behind], ix[behind]]
poly = np.asarray(pm) > 0
out[poly & ~new & ~behind] = (0, 255, 0)                    # incl. the soft green-tinted edge pixels
out[new] = newc[new]
# drop loose specks left in the air around the arm
fig = ~((out[..., 1].astype(int) - out[..., 0] > 60) & (out[..., 1].astype(int) - out[..., 2] > 60))
zone = np.zeros_like(fig); zone[420:510, 1155:1300] = True
lab, n = ndi.label(fig & zone, np.ones((3, 3))); sz = ndi.sum(fig & zone, lab, range(1, n + 1))
for i, z in enumerate(sz):
    if z < 60: out[lab == i + 1] = (0, 255, 0)
Image.fromarray(out).save(os.path.join(HERE, 'source', 'archer_dagger_m_sheet.png'))
print('done')
