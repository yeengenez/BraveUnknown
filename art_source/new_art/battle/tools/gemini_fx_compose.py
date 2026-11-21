"""Put the user's Gemini slash poses (cells 3 and 4) into the male dual sheet: body on green, slash wave as a separate
RGBA layer (soldier_dual_m_fx.png, same size as the sheet), and a rod for the hidden hand so the grip is measured."""
import numpy as np, math
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
SHEET = 'soldier_dual_m_sheet.png'
sheet = np.asarray(Image.open(SHEET).convert('RGB')).copy()
fxs = np.zeros(sheet.shape[:2] + (4,), np.uint8)
def isgreen(a): a = a.astype(int); return (a[..., 1] - a[..., 0] > 60) & (a[..., 1] - a[..., 2] > 60)
def rods(a):
    a = a.astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r > 170) & (b > 170) & (g < 120)) | ((g > 170) & (b > 170) & (r < 120))
def fig_box(mask, rodm):
    m = mask & ~ndi.binary_dilation(rodm, iterations=3)
    ys, xs = np.where(m); bot = ys.max(); low = ys > bot - 12
    return ys.min(), bot, xs[low].mean()
# (cell index, gemini name, hidden-hand fist in gemini px, blade angle, rod colour)
JOBS = [(3, 'gem3', (840, 595), 60, (0, 255, 255)), (4, 'gem4', (255, 515), 18, (255, 0, 255))]
STATE = {3: ('slash_left', 'front'), 4: ('slash_right', 'back')}
GRIPS = {}
c1 = sheet[0:512, 0:512]
for idx, name, fist, ang, rc in JOBS:
    r_, c_ = divmod(idx - 1, 3); y0, x0 = r_ * 512, c_ * 512
    cell = sheet[y0:y0 + 512, x0:x0 + 512]
    cm = ~isgreen(cell); cm[:6] = cm[-6:] = False; cm[:, :6] = cm[:, -6:] = False
    gyc = 380 + int(np.argmax((cm[380:450] & (cell[380:450].astype(int).sum(-1) < 150)).sum(1)))
    cm[gyc - 2:gyc + 3] &= ~(cell[gyc - 2:gyc + 3].astype(int).sum(-1) < 120)   # the ground line itself
    lab, n = ndi.label(cm, np.ones((3, 3))); sz = ndi.sum(cm, lab, range(1, n + 1))
    cm = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 200])
    t, bot, fx_ = fig_box(cm, rods(cell))
    g = np.asarray(Image.open(name + '_body.png').convert('RGB')); full = np.load(name + '_full.npy')
    gfx = np.asarray(Image.open(name + '_fx.png'))
    gt, gb, gx = fig_box(full, rods(g))
    s = (bot - t) / (gb - gt)
    W, H = round(g.shape[1] * s), round(g.shape[0] * s)
    al = full.astype(np.float32)
    pm = np.dstack([np.asarray(Image.fromarray(g[..., k].astype(np.float32) * al).resize((W, H), Image.BOX)) for k in range(3)])
    am = np.asarray(Image.fromarray(al).resize((W, H), Image.BOX))
    rgb = pm / np.maximum(am, 1e-6)[..., None]
    fa = gfx[..., 3].astype(np.float32) / 255
    fpm = np.dstack([np.asarray(Image.fromarray(gfx[..., k].astype(np.float32) * fa).resize((W, H), Image.BOX)) for k in range(3)])
    fam = np.asarray(Image.fromarray(fa).resize((W, H), Image.BOX))
    frgb = fpm / np.maximum(fam, 1e-6)[..., None]
    ox, oy = round(fx_ - gx * s), round(bot - gb * s)
    # clean cell: green + the template lines of cell 1 (ground line drawn full width)
    new = np.zeros_like(cell); new[:] = (0, 255, 0)
    gy = 400 + int(np.argmax((c1[400:430].astype(int).sum(-1) < 150).sum(1)))
    new[gy - 1:gy + 2, 14:498] = c1[gy, 14:498].min(0) if False else (20, 20, 20)
    dash = (c1[110:140].astype(int).sum(-1) < 300) & ~isgreen(c1[110:140])
    dash[:, 200:340] = False                                         # skip cell 1's helmet
    new[110:140][dash] = c1[110:140][dash]
    new[:3] = cell[:3]; new[-3:] = cell[-3:]; new[:, :3] = cell[:, :3]; new[:, -3:] = cell[:, -3:]
    ys, xs = np.where(am > 0.5)
    ty, tx = ys + oy, xs + ox; k = (ty >= 3) & (ty < 509) & (tx >= 3) & (tx < 509)
    new[ty[k], tx[k]] = np.clip(rgb[ys[k], xs[k]], 0, 255).astype(np.uint8)
    # rod for the hidden hand: through the fist, mostly on the blade side; fist pixels stay on top
    F = np.array(fist, float) * s + (ox, oy); d = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
    fistm = np.zeros((512, 512), bool); yy, xx = np.mgrid[:512, :512]
    fistm = (np.hypot(xx - F[0], yy - F[1]) < 9) & ~isgreen(new)
    keep = new[fistm].copy()
    im = Image.fromarray(new); ImageDraw.Draw(im).line([tuple(F - d * 16), tuple(F + d * 70)], fill=rc, width=8)
    new = np.asarray(im).copy(); new[fistm] = keep
    sheet[y0:y0 + 512, x0:x0 + 512] = new
    ys, xs = np.where(fam > 0.003)
    ty, tx = ys + oy, xs + ox; k = (ty >= 0) & (ty < 512) & (tx >= 0) & (tx < 512)
    fxs[y0 + ty[k], x0 + tx[k], :3] = np.clip(frgb[ys[k], xs[k]], 0, 255).astype(np.uint8)
    fxs[y0 + ty[k], x0 + tx[k], 3] = (fam[ys[k], xs[k]] * 255).astype(np.uint8)
    GRIPS.setdefault(STATE[idx][0], {})[STATE[idx][1]] = [round(float(F[0]), 1), round(float(F[1]), 1)]
    print(name, 'scale', round(s, 4), 'offset', ox, oy, 'fist', F.round(1))
import json; json.dump(GRIPS, open('soldier_dual_m_grips.json', 'w'), indent=1)
Image.fromarray(sheet).save('soldier_dual_m_sheet_gem.png'); Image.fromarray(fxs).save('soldier_dual_m_fx.png')
v = Image.fromarray(sheet).convert('RGBA'); v.alpha_composite(Image.fromarray(fxs)); v.convert('RGB').resize((1152, 768), Image.LANCZOS).save('gem_sheet_view.png')
