import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
def split(path, face_box, hide_poly=None):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(-1)
    bg = mx <= 14
    lab, n = ndi.label(bg); edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg_out = np.isin(lab, list(edge))                       # background reachable from the border
    wave = ((b < 0.35 * r) & (r > 60) & (g > 0.35 * r)) | ((g - b > 18) & (np.minimum(r, g) > 200))
    x0, y0, x1, y1 = face_box; wave[y0:y1, x0:x1] = False
    wl, wn = ndi.label(wave, np.ones((3, 3))); ws = ndi.sum(wave, wl, range(1, wn + 1))
    wave = np.isin(wl, [i + 1 for i, z in enumerate(ws) if z > 15000])
    bright = (np.minimum(np.minimum(r, g), b) > 185) & (g >= b) & ~bg       # white core of the streaks
    bright[y0:y1, x0:x1] = False
    for _ in range(40):
        nw = wave | (bright & ndi.binary_dilation(wave, iterations=2))
        if (nw == wave).all(): break
        wave = nw
    # glow fringe: dark warm pixels next to the wave over the background
    fr = ndi.binary_dilation(wave, iterations=6) & ~wave & (r > g) & (g >= b) & (r - b > 12) & (mx < 120)
    fxm = wave | fr
    # thick dark streaks of the glow (not thin outlines) near the wave belong to the glow
    darkb = (mx < 60) & ~bg & ndi.binary_dilation(wave, iterations=30)
    darkb = ndi.binary_opening(darkb, iterations=3)
    darkb = ndi.binary_dilation(darkb, iterations=1) & (mx < 80)
    fxm |= darkb
    body = ~bg & ~fxm
    bl, bn = ndi.label(body, np.ones((3, 3))); bs = ndi.sum(body, bl, range(1, bn + 1))
    body = np.isin(bl, [i + 1 for i, z in enumerate(bs) if z > 400])
    # body hidden under the wave: wave / gap pixels with body above AND below in the same column (within 140 px)
    up = np.zeros_like(body); dn = np.zeros_like(body)
    for k in range(1, 241, 3):
        up[k:] |= body[:-k]; dn[:-k] |= body[k:]
    hid = (fxm | (bg & ~bg_out) | (bg & ndi.binary_dilation(fxm, iterations=8))) & up & dn & ~body
    hid = ndi.binary_closing(hid, iterations=2) & ~body
    if hide_poly is not None:                                   # hand-marked body area under the wave
        from PIL import ImageDraw
        pm = Image.new('L', (a.shape[1], a.shape[0]), 0); ImageDraw.Draw(pm).polygon(hide_poly, fill=1)
        hid = (np.asarray(pm) > 0) & ~body & up & dn
    full = body | hid
    fl, fn = ndi.label(ndi.binary_closing(full, iterations=2), np.ones((3, 3)))
    fs = ndi.sum(full, fl, range(1, fn + 1))
    rodpx = ((g > 170) & (b > 170) & (r < 120)) | ((r > 170) & (b > 170) & (g < 120))     # guide rods stay body
    rid = set(np.unique(fl[rodpx & full])) - {0}
    full = full & np.isin(fl, [i + 1 for i, z in enumerate(fs) if z > 20000 or (i + 1) in rid]); body = body & full; hid = hid & full
    fxm = ~bg & ~body                                          # every leftover bit belongs to the glow layer
    img = a.astype(np.uint8).copy()
    iy, ix = ndi.distance_transform_edt(~body, return_distances=False, return_indices=True)
    img[~body] = img[iy[~body], ix[~body]]                     # every non-body pixel takes the nearest body colour
    sm = cv2.GaussianBlur(img, (0, 0), 6); img[hid] = sm[hid]; img[~full] = 0
    # fx layer: unpremultiply from black
    al = np.where(wave, np.clip(mx / 170, 0, 1), np.clip(mx / 255, 0, 1)) * fxm
    al = np.where(fxm & ~wave & full, 0, al)                   # dark gaps over the body: show the body
    al = np.where(wave & full, 1.0, al)                        # over the body the drawn wave is opaque
    col = np.clip(a / np.maximum(al, 1e-3)[..., None], 0, 255)
    fx = np.dstack([col, al * 255]).astype(np.uint8); fx[al == 0] = 0
    return img, full, fx
if __name__ == '__main__':
    import sys
    P4 = [(600, 548), (880, 515), (965, 600), (1005, 688), (1000, 706), (495, 706), (520, 640)]
    for n, fb, hp in (('gem3', (560, 180, 760, 340), None), ('gem4', (660, 200, 860, 360), P4)):
        img, full, fx = split(n + '.png', fb, hp)
        np.save(n + '_full.npy', full)
        Image.fromarray(img).save(n + '_body.png'); Image.fromarray(fx).save(n + '_fx.png')
        bgc = np.full(img.shape, (236, 230, 216), np.uint8)
        v1 = np.where(full[..., None], img, bgc)
        v2 = Image.fromarray(v1).convert('RGBA'); v2.alpha_composite(Image.fromarray(fx))
        s = Image.new('RGB', (img.shape[1] * 2, img.shape[0])); s.paste(Image.fromarray(v1), (0, 0)); s.paste(v2.convert('RGB'), (img.shape[1], 0))
        s.resize((s.width // 2, s.height // 2), Image.LANCZOS).save(n + '_split.png')
