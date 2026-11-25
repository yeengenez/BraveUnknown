"""Archer downed canvas (user, 2026-11-25): the dual template (2 x 3 cells of 512) with standing references in the bottom
row - male = the bow STAND of source/archer_m_sheet.png with its stick painted out; female = the female from the design
sheet (no Archer female sheet yet), scaled to the male's height. ChatGPT draws the downed poses in the empty top row."""
import os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = np.asarray(Image.open(os.path.join(HERE, 'templates', 'soldier_dual_template.png')).convert('RGB')).copy()
GREEN = np.array([0, 255, 0])

def paste(fig_rgb, mask, col, height):
    ys, xs = np.where(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = height / (y1 - y0)
    im = Image.fromarray(fig_rgb[y0:y1, x0:x1].astype(np.uint8)); m = Image.fromarray((mask[y0:y1, x0:x1] * 255).astype(np.uint8))
    W, H = round(im.width * s), round(im.height * s)
    im, m = im.resize((W, H), Image.LANCZOS), m.resize((W, H), Image.LANCZOS)
    ox, oy = col * 512 + 256 - W // 2, 512 + 471 - H
    tt = Image.fromarray(t); tt.paste(im, (ox, oy), m.point(lambda v: 255 if v > 128 else 0)); return np.asarray(tt).copy()

# male: bow stand cell, cyan stick inpainted from the figure
a = np.asarray(Image.open(os.path.join(HERE, 'source', 'archer_m_sheet.png')).convert('RGB').resize((1536, 1024), Image.LANCZOS)).copy()
c = a[4:508, 4:380].copy(); r, g, b = [c[..., i].astype(int) for i in range(3)]
cyan = (g > 150) & (b > 150) & (r < 140); cyan = ndi.binary_dilation(cyan, iterations=2)
green = (g - r > 60) & (g - b > 60)
c = cv2.inpaint(c, cyan.astype(np.uint8) * 255, 4, cv2.INPAINT_TELEA)
fig = ~green & ~cyan
for y in range(fig.shape[0]):
    if y > 440 and (c[y].astype(int).sum(-1) < 200).mean() > 0.3: fig[y] = False   # ground line
fig &= ~((r < 80) & (g > 120) & (b < 120))                                 # dashed guide
lab, n = ndi.label(fig, np.ones((3, 3))); sz = ndi.sum(fig, lab, range(1, n + 1))
fig = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 300])
fig |= cyan & ndi.binary_closing(fig, iterations=6)                        # stick pixels over the body -> inpainted body
ys = np.where(fig.any(1))[0]; H_M = ys.max() - ys.min()
t = paste(c, fig, 0, H_M)
# female: design sheet, light background
d = np.asarray(Image.open(os.path.join(HERE, 'source', 'concepts', 'archer_design.png')).convert('RGB')).astype(int)
bg = (np.abs(d - d[5, 5]).sum(-1) < 30)
half = d.shape[1] // 2; top = d[: int(d.shape[0] * 0.62), half:]; fm = ~bg[: int(d.shape[0] * 0.62), half:]
lab, n = ndi.label(fm, np.ones((3, 3))); sz = ndi.sum(fm, lab, range(1, n + 1)); fm = ndi.binary_fill_holes(lab == np.argmax(sz) + 1)
t = paste(top, fm, 1, H_M * 0.96)
Image.fromarray(t).save(os.path.join(HERE, 'templates', 'archer_downed_template.png')); print('ok')
