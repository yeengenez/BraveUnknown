"""Painted pixel weapons. Each weapon is rendered with smooth lighting at 4x (material + surface normal),
reduced to sprite size, snapped to a palette sampled from the battle sprite bodies, then given a tinted
outline (a darkened copy of the colour next to it), like the bodies. No AI image generation."""
import numpy as np
from PIL import Image
K = 4
PALETTE = np.load('body_palette.npy').astype(float)
LIGHT = np.array([-0.55, -0.65, 0.53]); LIGHT /= np.linalg.norm(LIGHT)

RAMPS = {   # dark -> light, from the body palette (steel, blue scarf, leather, wood, gold)
    'steel':   [(35, 31, 27), (63, 61, 59), (106, 105, 105), (156, 154, 155), (214, 206, 200), (243, 235, 228)],
    'blue':    [(7, 17, 40), (15, 33, 69), (22, 55, 112), (28, 67, 133), (70, 108, 178)],
    'leather': [(29, 13, 7), (48, 20, 9), (77, 23, 9), (114, 61, 26), (164, 99, 48)],
    'wood':    [(35, 20, 10), (65, 35, 18), (93, 46, 18), (141, 79, 36), (187, 117, 58)],
    'gold':    [(77, 23, 9), (141, 79, 36), (207, 139, 70), (231, 175, 72), (252, 214, 150)],
}
EXTRA = [(70, 108, 178), (252, 214, 150), (255, 250, 240)]
PAL = np.vstack([PALETTE, np.array(EXTRA, float)])

def ramp(name, t):
    c = np.array(RAMPS[name], float); t = np.clip(t, 0, 1) * (len(c) - 1)
    i = np.clip(np.floor(t).astype(int), 0, len(c) - 2); f = (t - i)[..., None]
    return c[i] * (1 - f) + c[i + 1] * f

class Canvas:
    """4x canvas. Coordinates passed to shapes are in final sprite pixels (the weapon's own, flat frame).
    With angle != 0 the weapon is drawn already rotated about `pivot`, so no pixel rotation is needed;
    s.pivot_out is where the pivot lands in the output image (before the 1px outline border)."""
    def __init__(s, w, h, angle=0.0, pivot=(0.0, 0.0)):
        th = np.radians(angle); ca, sa = np.cos(th), np.sin(th)
        if angle:
            cs = np.array([[0, 0], [w, 0], [0, h], [w, h]], float) - pivot
            rc = cs @ np.array([[ca, -sa], [sa, ca]]).T
            x0, y0 = np.floor(rc.min(0)) - 1; x1, y1 = np.ceil(rc.max(0)) + 1
            ow, oh = int(x1 - x0), int(y1 - y0); s.pivot_out = (-x0, -y0)
        else:
            ow, oh = w, h; s.pivot_out = pivot; x0 = y0 = 0
        s.w, s.h = ow, oh
        yy, xx = np.mgrid[0:oh * K, 0:ow * K]
        X, Y = (xx + 0.5) / K, (yy + 0.5) / K
        if angle:
            dx, dy = X - s.pivot_out[0], Y - s.pivot_out[1]
            s.x, s.y = ca * dx + sa * dy + pivot[0], -sa * dx + ca * dy + pivot[1]
            s.rot = (ca, sa)
        else:
            s.x, s.y = X, Y; s.rot = (1.0, 0.0)
        s.rgb = np.zeros((s.h * K, s.w * K, 3)); s.a = np.zeros((s.h * K, s.w * K), bool)
    def paint(s, mask, material, normal=None, base=0.0, spec=0.0, flat=None):
        if normal is None: normal = (np.zeros_like(s.x), np.zeros_like(s.x), np.ones_like(s.x))
        nx, ny, nz = normal; ca, sa = s.rot
        nx, ny = ca * nx - sa * ny, sa * nx + ca * ny            # normals follow the weapon's rotation
        n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2) + 1e-9
        lam = (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / n
        t = np.clip(0.18 + 0.82 * lam + base, 0, 1) if flat is None else flat
        col = ramp(material, t)
        if spec:
            h = np.clip(lam, 0, 1) ** 24 * spec
            col = col + (255 - col) * h[..., None]
        s.rgb[mask] = col[mask]; s.a |= mask
    def finish(s):
        h, w = s.h, s.w
        rgb = s.rgb.reshape(h, K, w, K, 3); a = s.a.reshape(h, K, w, K).astype(float)
        cov = a.mean((1, 3)); col = (rgb * a[..., None]).sum((1, 3)) / np.maximum(a.sum((1, 3)), 1)[..., None]
        on = cov >= 0.45
        d = ((col[:, :, None, :] - PAL[None, None]) ** 2).sum(-1); q = PAL[d.argmin(-1)]
        out = np.zeros((h + 2, w + 2, 4), np.uint8)
        out[1:-1, 1:-1, :3][on] = q[on]; out[1:-1, 1:-1, 3][on] = 255
        m = out[..., 3] > 0
        acc = np.zeros((h + 2, w + 2, 3)); n = np.zeros((h + 2, w + 2))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sm = np.roll(np.roll(m, dy, 0), dx, 1); sc = np.roll(np.roll(out[..., :3].astype(float), dy, 0), dx, 1)
            acc += sc * sm[..., None]; n += sm
        ring = (n > 0) & ~m
        tint = acc[ring] / n[ring][:, None] * 0.28 + np.array([10, 7, 8]) * 0.72   # dark, tinted by the neighbour
        out[ring, :3] = tint.astype(np.uint8); out[ring, 3] = 255
        return out

def shield():
    W, H = 30, 40; c = Canvas(W + 2, H + 2); x, y = c.x - 1, c.y - 1
    cx = W / 2; yh = H * 0.42
    half = np.where(y < yh, W / 2, W / 2 * np.clip(1 - np.clip((y - yh) / (H - yh), 0, 1) ** 1.5, 0, 1) ** 0.75)
    top = 1.2 + 1.2 * ((x - cx) / (W / 2)) ** 2                   # top edge curves down at the corners
    body = (np.abs(x - cx) <= half) & (y >= top) & (y <= H)
    # distance to the edge (approx.) for the rim
    edge = np.minimum(half - np.abs(x - cx), y - top)
    edge = np.minimum(edge, np.where(y > yh, (half - np.abs(x - cx)) * 0.9, 99))
    nx = (x - cx) / (W / 2) * 0.75; ny = (y - H * 0.45) / H * 0.35; nz = np.ones_like(x)
    rim = body & (edge < 2.4); trim = body & (edge >= 2.4) & (edge < 3.4); face = body & (edge >= 3.4)
    c.paint(face, 'blue', (nx, ny, nz), base=0.05)
    c.paint(trim, 'gold', (nx, ny, nz), base=0.1, spec=0.4)
    c.paint(rim, 'steel', (nx - np.sign(x - cx) * 0.3 * (edge < 1.2), ny, nz), base=0.05, spec=0.9)
    # rivets on the rim
    for rx, ry in [(3, 4), (cx, 2.4), (W - 3, 4), (2.0, 13), (W - 2.0, 13), (5.5, 26), (W - 5.5, 26), (cx, H - 2.6)]:
        rr = (x - rx) ** 2 + (y - ry) ** 2; m = body & (rr < 0.95 ** 2)
        c.paint(m, 'steel', (x - rx, y - ry, np.sqrt(np.clip(1 - rr, 0.05, 1))), base=0.15, spec=1)
    # central gold cross-band and steel boss
    band = face & (np.abs(y - 17.0) < 1.1 + 0 * x); c.paint(band, 'gold', (nx, ny, nz), base=0.1, spec=0.5)
    vband = face & (np.abs(x - cx) < 1.1) & (y > 4) & (y < H - 4); c.paint(vband, 'gold', (nx, ny, nz), base=0.1, spec=0.5)
    br = 4.6; rr = ((x - cx) ** 2 + (y - 17.0) ** 2) / br ** 2; boss = body & (rr < 1)
    c.paint(boss, 'steel', ((x - cx) / br, (y - 17) / br, np.sqrt(np.clip(1 - rr, 0.02, 1))), base=0.0, spec=1.2)
    img = c.finish()
    return img, (int(cx) + 2, 17 + 2)

AXE_GRIP, AXE_GRIP2 = (20.5, 8.0), (11.5, 8.0)
def greataxe(angle=0.0, pivot=AXE_GRIP2):
    L, Hh = 120, 46; cy = 8.0; c = Canvas(L, Hh, angle, pivot); x, y = c.x, c.y
    # haft: a cylinder lit from above
    r = 1.7; dyh = (y - cy) / r; haft = (np.abs(dyh) <= 1) & (x >= 3) & (x <= L - 6)
    cyl = (np.zeros_like(x), dyh, np.sqrt(np.clip(1 - dyh ** 2, 0.05, 1)))
    c.paint(haft, 'wood', cyl, base=-0.02)
    grain = haft & (((x * 0.7 + y * 2.3) % 5.0) < 0.6); c.paint(grain, 'wood', cyl, base=-0.25)
    wrap = haft & (x >= 7) & (x <= 34)                                                   # leather wrap at the grip
    c.paint(wrap, 'leather', cyl, base=0.05)
    seam = wrap & (((x - (y - cy) * 0.9) % 3.6) < 0.7); c.paint(seam, 'leather', cyl, base=-0.35)
    cap = (np.abs(dyh) <= 1.25) & (x >= 0.5) & (x <= 4)                                  # steel butt cap
    c.paint(cap, 'steel', cyl, spec=1)
    # head (blade hangs below the haft; after the weapon is raised forward the edge faces the enemy)
    sx = L - 22.0                                                                        # socket centre
    u = x - sx; v = y - cy
    back = u < 0
    span = np.where(back, 21.0, 15.0)                                                    # beard sweeps toward the grip
    reach = 32 - (np.abs(u) / span) ** 2 * 7 - np.where(back, 0, 2)
    low = np.where(np.abs(u) < 3.2, 0, (np.clip(np.abs(u) - 3.2, 0, None) / (span - 3.2)) ** 0.62 * (reach - 1.5))
    blade = (np.abs(u) <= span) & (v >= np.maximum(low, 2.0)) & (v <= reach)
    d_edge = reach - v
    face_n = (u * -0.02, np.full_like(x, -0.15), np.ones_like(x))
    c.paint(blade, 'steel', face_n, base=-0.22 + 0.2 * np.clip(v / 30, 0, 1))
    bevel = blade & (d_edge < 4.2)
    c.paint(bevel, 'steel', (u / span * 0.4, np.full_like(x, 0.55), np.ones_like(x)), base=0.12, spec=0.8)
    keen = blade & (d_edge < 1.2); c.paint(keen, 'steel', face_n, flat=np.full_like(x, 0.97))
    etch = blade & (np.abs(d_edge - 7.2) < 0.45) & (np.abs(u) < span - 2.5); c.paint(etch, 'steel', face_n, base=-0.35)
    # socket block with gold band and rivets
    sock = (np.abs(u) <= 4.2) & (np.abs(v) <= 4.0)
    c.paint(sock, 'steel', (u / 4.2 * 0.6, v / 4.0 * 0.6, np.ones_like(x)), base=-0.15, spec=0.6)
    gb = sock & (np.abs(u + 2.2) < 0.9); c.paint(gb, 'gold', (np.zeros_like(x), v / 4, np.ones_like(x)), spec=0.5)
    for rv in (-2.2, 2.2):
        rr = (u - 1.6) ** 2 + (v - rv) ** 2; m = rr < 0.8 ** 2
        c.paint(m, 'steel', (u - 1.6, v - rv, np.sqrt(np.clip(1 - rr, 0.05, 1))), base=0.2, spec=1)
    spike = (u > 4.2) & (u < 9.5) & (np.abs(v) < 1.6 * (1 - (u - 4.2) / 5.6) + 0.2)     # small top spike
    c.paint(spike, 'steel', (np.zeros_like(x), np.sign(v) * 0.6, np.ones_like(x)), spec=0.8)
    img = c.finish()
    if angle: return img, (c.pivot_out[0] + 1, c.pivot_out[1] + 1)
    return img, (int(AXE_GRIP[0]) + 1, int(cy) + 1), (int(AXE_GRIP2[0]) + 1, int(cy) + 1)

if __name__ == '__main__':
    s, g = shield(); a, g1, g2 = greataxe()
    Image.fromarray(s).save('pt_shield.png'); Image.fromarray(a).save('pt_greataxe.png')
    print('shield', s.shape, g, 'axe', a.shape, g1, g2)
    Z = 5; ims = [Image.fromarray(a), Image.fromarray(s)]
    sheet = Image.new('RGBA', (sum(i.width * Z + 20 for i in ims) + 20, max(i.height for i in ims) * Z + 20), (226, 220, 204, 255)); xo = 10
    for i in ims: sheet.alpha_composite(i.resize((i.width * Z, i.height * Z), Image.NEAREST), (xo, 10)); xo += i.width * Z + 20
    sheet.save('previews/pt_zoom.png')
