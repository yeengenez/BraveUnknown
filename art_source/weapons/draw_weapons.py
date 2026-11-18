"""Code-drawn weapons (fallback while Canva is unavailable). Drawn at 4x, reduced to sprite scale.
Palette taken from the Canva longsword so they match it. All weapons lie horizontal, tip to the right."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SW = np.asarray(Image.open('sword_full.png').convert('RGBA'))
OUT = (36, 34, 40, 255)                     # outline
STEEL = [(96, 100, 110), (150, 155, 165), (205, 208, 214), (240, 241, 244)]
WOOD = [(70, 42, 24), (104, 64, 34), (138, 90, 50)]
WRAP = [(60, 34, 20), (112, 60, 30)]
K = 4

def finish(big, length_px):
    """Reduce the 4x drawing, then add a crisp 1px dark outline."""
    h = max(1, round(big.height * length_px / big.width))
    small = big.resize((length_px, h), Image.LANCZOS)
    a = np.asarray(small).copy(); alpha = a[..., 3] > 110
    a[..., 3] = alpha * 255
    pad = np.zeros((a.shape[0] + 2, a.shape[1] + 2, 4), np.uint8); pad[1:-1, 1:-1] = a
    m = pad[..., 3] > 0
    ring = (np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)) & ~m
    pad[ring] = OUT
    return Image.fromarray(pad)

def shaft(d, x0, x1, cy, r, cols):
    for i, c in enumerate(cols):                       # dark at the bottom, light at the top
        t = r * (1 - i / len(cols))
        d.rectangle([x0, cy - t, x1, cy + r], fill=c)
    d.rectangle([x0, cy - r, x1, cy - r + max(1, r // 3)], fill=cols[-1])

def longspear(length=240):
    L, H = length * K, 16 * K; cy = H // 2
    im = Image.new('RGBA', (L, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    head = 22 * K
    shaft(d, 4 * K, L - head, cy, int(1.6 * K), WOOD)
    d.rectangle([0, cy - 2.2 * K, 5 * K, cy + 2.2 * K], fill=STEEL[1])          # butt cap
    d.rectangle([0, cy - 2.2 * K, 5 * K, cy - 1.2 * K], fill=STEEL[3])
    sx = L - head - 4 * K
    d.rectangle([sx, cy - 2.4 * K, sx + 6 * K, cy + 2.4 * K], fill=STEEL[0])      # socket
    d.rectangle([sx, cy - 2.4 * K, sx + 6 * K, cy - 1.2 * K], fill=STEEL[2])
    hx = L - head + 2 * K                                                        # leaf blade
    d.polygon([(hx, cy), (hx + head * 0.35, cy - 4.2 * K), (L - 1, cy), (hx + head * 0.35, cy + 4.2 * K)], fill=STEEL[1])
    d.polygon([(hx, cy), (hx + head * 0.35, cy - 4.2 * K), (L - 1, cy)], fill=STEEL[2])
    d.line([(hx + 2 * K, cy), (L - 2 * K, cy)], fill=STEEL[3], width=K)
    return finish(im, length)

def greataxe(length=118):
    L, H = length * K, 46 * K; cy = 34 * K
    im = Image.new('RGBA', (L, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    shaft(d, 2 * K, L - 6 * K, cy, int(2.0 * K), WOOD)
    for x in range(8 * K, 34 * K, 5 * K):                                        # leather wrap at the grip end
        d.rectangle([x, cy - 2.2 * K, x + 3 * K, cy + 2.2 * K], fill=WRAP[1])
        d.rectangle([x + 3 * K, cy - 2.2 * K, x + 4 * K, cy + 2.2 * K], fill=WRAP[0])
    d.ellipse([0, cy - 3 * K, 6 * K, cy + 3 * K], fill=STEEL[1])                 # pommel cap
    bx = L - 26 * K                                                              # crescent head, edge up
    d.rectangle([bx + 6 * K, cy - 7 * K, bx + 15 * K, cy + 4 * K], fill=STEEL[0])
    d.polygon([(bx, cy - 8 * K), (bx + 4 * K, cy - 30 * K), (bx + 12 * K, cy - 33 * K), (bx + 22 * K, cy - 30 * K),
               (bx + 25 * K, cy - 8 * K), (bx + 15 * K, cy - 12 * K), (bx + 9 * K, cy - 12 * K)], fill=STEEL[1])
    d.polygon([(bx + 3 * K, cy - 24 * K), (bx + 5 * K, cy - 30 * K), (bx + 12 * K, cy - 33 * K), (bx + 20 * K, cy - 30 * K),
               (bx + 22 * K, cy - 24 * K)], fill=STEEL[3])                            # bright edge
    d.polygon([(bx + 7 * K, cy - 14 * K), (bx + 12 * K, cy - 22 * K), (bx + 18 * K, cy - 14 * K)], fill=STEEL[2])
    d.rectangle([L - 7 * K, cy - 3 * K, L - 2 * K, cy + 3 * K], fill=STEEL[1])     # top spike
    return finish(im, length)

if __name__ == '__main__':
    longspear().save('longspear_code.png'); greataxe().save('greataxe_code.png')
    for n in ['longspear_code', 'greataxe_code']:
        im = Image.open(n + '.png'); print(n, im.size)
