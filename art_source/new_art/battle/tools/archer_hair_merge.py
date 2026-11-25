"""Archer hair under the hood (user, 2026-11-25): the hood hides long hair, so the hair that shows inside the hood
(fringe, locks beside the face) is ONE piece for every hairstyle, coloured with the hero's hair ramp.
Gemini repainted that hair in the red key (source/concepts/archer_<sex>_all_hair_gemini.png, returned at about half
size). Only the red hair is taken from it - scaled back up - and laid on the untouched body sheet in the red key, so the
pipeline's hair cut (skin_split -> hair value map) picks it up. The body without hair is kept as
source/concepts/archer_<sex>_all_sheet_nohair.png. Usage: python3 tools/archer_hair_merge.py m|f"""
import os, sys, json, shutil, numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(sex):
    base_p = os.path.join(HERE, 'source', 'concepts', f'archer_{sex}_all_sheet_nohair.png')
    if not os.path.exists(base_p): shutil.copy(os.path.join(HERE, 'source', f'archer_{sex}_all_sheet.png'), base_p)
    base = np.asarray(Image.open(base_p).convert('RGB'))
    W, H = base.shape[1], base.shape[0]
    o = np.asarray(Image.fromarray(base).resize((1536, 2560), Image.LANCZOS)).astype(int)
    g_im = Image.open(os.path.join(HERE, 'source', 'concepts', f'archer_{sex}_all_hair_gemini.png')).convert('RGB')
    a = np.asarray(g_im.resize((1536, 2560), Image.LANCZOS)).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 90) & (g < 0.38 * r) & (b < 0.4 * r) & (np.abs(a - o).sum(-1) > 60)
    L = json.load(open(os.path.join(HERE, 'source', 'archer_m_all_layout.json')))
    hair = np.zeros(red.shape, bool)
    for c in L:                                          # per cell: the hair blob(s) at the hood only
        x0, y0, x1, y1 = c['box']; m = red[y0:y1, x0:x1]
        fig = ~((o[y0:y1, x0:x1, 1] - o[y0:y1, x0:x1, 0] > 60) & (o[y0:y1, x0:x1, 1] - o[y0:y1, x0:x1, 2] > 60))
        ys = np.where(fig[:int(0.95 * (y1 - y0))].any(1))[0]; top = ys.min()
        hood = np.zeros_like(m); hood[top:top + int(0.22 * (ys.max() - top)) + 30] = True
        m = ndi.binary_opening(m & hood & fig, iterations=1)
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
        if n:
            sz = ndi.sum(m, lab, range(1, n + 1)); m &= np.isin(lab, [i + 1 for i, z in enumerate(sz) if z > 25])
        hair[y0:y1, x0:x1] = m
    # red-key shades from the drawn hair's own brightness (dark outline .. bright highlight)
    v = np.clip((r.astype(float) - 60) / (230 - 60), 0, 1)
    key = np.zeros_like(a); key[..., 0] = np.round(70 + v * 185)
    out = o.copy(); out[hair] = key[hair]
    out = np.asarray(Image.fromarray(out.astype(np.uint8)).resize((W, H), Image.NEAREST))
    hm = np.asarray(Image.fromarray(hair.astype(np.uint8) * 255).resize((W, H), Image.NEAREST)) > 0
    res = base.copy(); res[hm] = out[hm]
    Image.fromarray(res).save(os.path.join(HERE, 'source', f'archer_{sex}_all_sheet.png'))
    print(sex, 'hair px', int(hm.sum()))


if __name__ == '__main__':
    for s in sys.argv[1:] or 'mf': main(s)
