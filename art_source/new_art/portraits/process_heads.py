"""Cut the two bald base heads (male left, female right) out of the ChatGPT grayscale sheet and turn them
into 200x200 portrait skin layers in the game's convention.

Source: source/heads_sheet.png (1536x1024, grey heads with a white glow on black).
Output: m_head_skin.png, f_head_skin.png  (grayscale value map: R=G=B, alpha = head)
        preview_heads.png                (tinted with the 5 skin ramps, and over the legacy Soldier bust)

Convention copied from the legacy parts (portraits/parts/*_skin.png):
- the outline stays IN the skin layer as its darkest values (the ramp turns it into a dark skin tone);
- mid skin sits around value 204, highlights ~235;
- placement: top of skull y=20, chin y~111, head centred on x~99, so the head sits on the existing bodies.
"""
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
SKULL_TOP, CHIN, CX = 34, 125, 99          # skull top y=34 leaves room for tall hair (14 px lower than legacy)


def cut(g, x0, x1):
    """Mask of one head: interior (brighter than the glow) + its dark outline ring."""
    sub = g[:, x0:x1]
    inner = sub > 125                                   # the glow next to the edge stays below ~117
    lab, n = ndi.label(inner)
    sizes = ndi.sum(inner, lab, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    skull = ndi.binary_fill_holes(lab == big)               # head without the neck (the jaw line splits them)
    near = ndi.binary_dilation(skull, iterations=25)
    keep = [i + 1 for i in range(n) if sizes[i] > 0.01 * sizes[big - 1] and (near & (lab == i + 1)).any()]
    head = ndi.binary_fill_holes(ndi.binary_closing(np.isin(lab, keep), iterations=6))
    cut.skull = skull
    # add the dark outline found as a thin dip (catches the female neck bottom, whose shading is as dark as the glow)
    import cv2
    bh = cv2.morphologyEx(sub.astype(np.uint8), cv2.MORPH_BLACKHAT,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))).astype(int)
    dip = ndi.binary_closing((bh > 10) & (sub < 150), iterations=2)
    lab2, n2 = ndi.label(dip)
    touch = np.unique(lab2[ndi.binary_dilation(head, iterations=3) & dip]); touch = touch[touch > 0]
    head = ndi.binary_fill_holes(ndi.binary_closing(head | np.isin(lab2, touch), iterations=4))
    ring = ndi.binary_dilation(head, iterations=11) & ~head & (sub < 125)   # the ~1 art-pixel outline
    outline = ring & ndi.binary_dilation(head, iterations=11)
    # keep only outline pixels that are darker than the glow just outside them
    return head, outline


def chin_y(head):
    """Lowest point of the jaw line: the face column furthest right whose bottom is above the neck."""
    ys, xs = np.where(head)
    top = ys.min(); H = ys.max() - top
    # jaw: in the upper 70% of the figure, the right half; take the lowest head pixel at the far-right quarter
    right = xs > np.percentile(xs, 75)
    return top, ys[right & (ys < top + 0.75 * H)].max()


def build(g, x0, x1, scale):
    head, outline = cut(g, x0, x1)
    sub = g[:, x0:x1].astype(float)
    mask = ndi.binary_fill_holes(ndi.binary_closing(head | outline, iterations=8))
    # pixels added by the closing (the jaw line between skull and neck) keep their own shading
    v = sub.copy()
    inside = sub[head]
    # remap the interior so its median lands on 204 (legacy skin convention), keep shading contrast
    med, hi = np.median(inside), np.percentile(inside, 99.5)
    v = 204 + (v - med) * (235 - 204) / max(1.0, hi - med)
    v[outline] = np.clip(sub[outline] * 0.35, 8, 40)     # outline = darkest skin values
    v = np.clip(v, 0, 255)
    ys, xs = np.where(mask)
    y0, y1, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    v, m = v[y0:y1, xa:xb], mask[y0:y1, xa:xb].astype(float)
    W, H = round((xb - xa) * scale), round((y1 - y0) * scale)
    # premultiplied box downsample so the edge does not pick up the background
    pv = Image.fromarray((v * m).astype(np.float32)).resize((W, H), Image.BOX)
    pm = Image.fromarray(m.astype(np.float32)).resize((W, H), Image.BOX)
    pv, pm = np.asarray(pv), np.asarray(pm)
    val = np.where(pm > 0, pv / np.maximum(pm, 1e-6), 0)
    alpha = np.where(pm > 0.5, 255, 0)
    return np.clip(val, 0, 255).astype(np.uint8), alpha.astype(np.uint8), head[y0:y1, xa:xb]


def place(val, alpha, top_off, cx_off):
    out = np.zeros((200, 200, 4), np.uint8)
    H, W = val.shape
    oy, ox = SKULL_TOP - top_off, CX - cx_off
    ys, xs = slice(max(0, oy), min(200, oy + H)), slice(max(0, ox), min(200, ox + W))
    sy, sx = slice(ys.start - oy, ys.stop - oy), slice(xs.start - ox, xs.stop - ox)
    for c in range(3): out[ys, xs, c] = val[sy, sx]
    out[ys, xs, 3] = alpha[sy, sx]
    return out


if __name__ == '__main__':
    g = np.asarray(Image.open(os.path.join(HERE, 'source', 'heads_sheet.png')).convert('L')).astype(int)
    mid = g.shape[1] // 2
    # one scale for both, set by the male head (skull top -> chin = 91 px like the legacy head)
    cut(g, 0, mid); ys = np.where(cut.skull)[0]
    t, c = ys.min(), ys.max()                                 # skull top and chin of the male head
    scale = (CHIN - SKULL_TOP) / (c - t)
    res = {}
    for sex, (x0, x1) in {'m': (0, mid), 'f': (mid, g.shape[1])}.items():
        val, alpha, _ = build(g, x0, x1, scale)
        ys, xs = np.where(alpha > 0)
        # centre the skull (not the neck) on CX: use the top 60% of the head
        top = ys.min(); upper = ys < top + 0.6 * (ys.max() - top)
        cx = int(round((xs[upper].min() + xs[upper].max()) / 2))
        img = place(val, alpha, top, cx)
        Image.fromarray(img).save(os.path.join(HERE, f'{sex}_head_skin.png'))
        res[sex] = img
        a = img[..., 3]; yy, xx = np.where(a > 0)
        print(sex, 'bbox', xx.min(), yy.min(), xx.max(), yy.max(), 'scale %.4f' % scale)

    # preview: 5 skin ramps per head, then each head over the legacy Soldier bust
    pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))['skin']
    hx = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    def tint(img, ramp):
        r = np.array([hx(c) for c in ramp], float); v = img[..., 0] / 255 * (len(r) - 1)
        lo = np.floor(v).astype(int).clip(0, len(r) - 2); t = (v - lo)[..., None]
        return Image.fromarray(np.dstack([r[lo] * (1 - t) + r[lo + 1] * t, img[..., 3]]).astype(np.uint8))
    tiles = []
    for sex in 'mf':
        for name in pal:
            c = Image.new('RGBA', (200, 200), (52, 56, 66, 255)); c.alpha_composite(tint(res[sex], pal[name])); tiles.append(c)
        c = Image.new('RGBA', (200, 200), (52, 56, 66, 255))
        P = os.path.join(ROOT, 'portraits', 'parts')
        c.alpha_composite(tint(np.asarray(Image.open(f'{P}/{sex}_body_soldier_skin.png').convert('RGBA')), pal['tan']))
        c.alpha_composite(Image.open(f'{P}/{sex}_body_soldier_fixed.png').convert('RGBA'))
        c.alpha_composite(tint(res[sex], pal['tan'])); tiles.append(c)
    sheet = Image.new('RGBA', (200 * 6, 400))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 6) * 200, (i // 6) * 200))
    sheet.save(os.path.join(HERE, 'preview_heads.png'))
