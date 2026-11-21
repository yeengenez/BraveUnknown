"""Class weapons drawn in code (never generated): dagger, mace, quarterstaff, mage staff, bow, arrow.
Same painted method as the great axe (render_weapons.py): lit at 4x, palette sampled from the bodies, tinted
outline. Each weapon lies flat with its point/head to the right; draw(name, angle, pivot) renders it already
rotated about a grip point, so animation frames stay crisp. GRIPS gives each weapon's hand points."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'weapons'))
import render_weapons as R
from render_weapons import Canvas

R.RAMPS['violet'] = [(30, 14, 52), (62, 30, 104), (104, 60, 168), (160, 120, 224), (226, 206, 255)]
R.RAMPS['ash'] = [(40, 28, 20), (76, 56, 40), (112, 86, 62), (150, 120, 90), (192, 162, 124)]
R.PAL = np.vstack([R.PAL, np.array(R.RAMPS['violet'] + R.RAMPS['ash'], float)])   # let the staff keep its colours

def cyl(c, y, cy, r):
    d = (y - cy) / r
    return d, (np.zeros_like(y), d, np.sqrt(np.clip(1 - d ** 2, 0.05, 1)))

def dagger(angle=0.0, pivot=(6.0, 4.0)):
    L, H, cy = 32, 9, 4.0; c = Canvas(L, H, angle, pivot); x, y = c.x, c.y
    d, n = cyl(c, y, cy, 1.4)
    c.paint((np.abs(d) <= 1) & (x >= 2) & (x <= 10), 'leather', n)                       # grip
    c.paint(((x - 1.5) ** 2 + (y - cy) ** 2) < 2.0 ** 2, 'steel', ((x - 1.5), (y - cy), np.ones_like(x)), spec=1)
    c.paint((np.abs(x - 11) <= 0.9) & (np.abs(y - cy) <= 3.4), 'gold', n, spec=0.6)           # guard
    half = np.clip(1.9 * (1 - np.clip((x - 12) / 19, 0, 1) ** 2.2), 0, 2)                                  # tapering blade
    blade = (x >= 12) & (x <= 31) & (np.abs(y - cy) <= half)
    c.paint(blade, 'steel', (np.zeros_like(x), np.sign(y - cy) * 0.5, np.ones_like(x)), spec=0.9)
    c.paint(blade & (np.abs(y - cy) < 0.45), 'steel', None, flat=np.full_like(x, 0.95))
    return c.finish(), (c.pivot_out[0] + 1, c.pivot_out[1] + 1)

def mace(angle=0.0, pivot=(6.0, 6.0)):
    L, H, cy = 40, 13, 6.0; c = Canvas(L, H, angle, pivot); x, y = c.x, c.y
    d, n = cyl(c, y, cy, 1.5)
    c.paint((np.abs(d) <= 1) & (x >= 1) & (x <= 31), 'wood', n)
    c.paint((np.abs(d) <= 1.1) & (x >= 2) & (x <= 11), 'leather', n)
    for fy in (-4.6, -2.3, 0, 2.3, 4.6):                                                     # flanged head
        f = (x >= 30) & (x <= 38) & (np.abs(y - cy - fy) <= 1.0 + 0.6 * (fy == 0))
        c.paint(f, 'steel', (np.zeros_like(x), np.full_like(x, fy / 5), np.ones_like(x)), spec=0.9)
    rr = ((x - 34) / 4.2) ** 2 + ((y - cy) / 3.4) ** 2
    c.paint(rr < 1, 'steel', ((x - 34) / 4.2, (y - cy) / 3.4, np.sqrt(np.clip(1 - rr, 0.05, 1))), base=-0.1, spec=1)
    c.paint(((x - 39) ** 2 + (y - cy) ** 2) < 1.4 ** 2, 'steel', None, flat=np.full_like(x, 0.8))
    return c.finish(), (c.pivot_out[0] + 1, c.pivot_out[1] + 1)

def quarterstaff(angle=0.0, pivot=(42.0, 4.0)):
    L, H, cy = 124, 9, 4.0; c = Canvas(L, H, angle, pivot); x, y = c.x, c.y
    d, n = cyl(c, y, cy, 1.7)
    c.paint((np.abs(d) <= 1) & (x >= 1) & (x <= L - 1), 'wood', n)
    c.paint((np.abs(d) <= 1) & (x >= 1) & (x <= L - 1) & (((x * 0.6 + y * 2) % 7) < 0.7), 'wood', n, base=-0.25)
    for a0, a1 in ((1, 7), (L - 7, L - 1)):                                                  # iron caps
        c.paint((np.abs(d) <= 1.2) & (x >= a0) & (x <= a1), 'steel', n, spec=0.8)
    for g0 in (36, 58):                                                                       # leather grips
        c.paint((np.abs(d) <= 1.05) & (x >= g0) & (x <= g0 + 12), 'leather', n)
    return c.finish(), (c.pivot_out[0] + 1, c.pivot_out[1] + 1)

def mage_staff(angle=0.0, pivot=(34.0, 6.0)):
    L, H, cy = 96, 15, 7.0; c = Canvas(L, H, angle, pivot); x, y = c.x, c.y
    wob = 0.35 * np.sin(x / 9.0)                                                               # gnarled shaft
    d, n = cyl(c, y, cy + wob, 1.5)
    c.paint((np.abs(d) <= 1) & (x >= 1) & (x <= 82), 'ash', n)
    c.paint((np.abs(d) <= 1.05) & (x >= 28) & (x <= 40), 'leather', n)
    claw = (x >= 78) & (x <= 86) & (np.abs(y - cy) <= 4.6) & (np.abs(y - cy) >= 3.0 - (x - 78) * 0.2)
    c.paint(claw, 'ash', (np.zeros_like(x), np.sign(y - cy) * 0.6, np.ones_like(x)))
    rr = ((x - 88) / 5.2) ** 2 + ((y - cy) / 5.2) ** 2                                        # crystal orb
    c.paint(rr < 1, 'violet', ((x - 88) / 5.2, (y - cy) / 5.2, np.sqrt(np.clip(1 - rr, 0.05, 1))), base=0.1, spec=1.3)
    img = c.finish()
    tip = np.array([88.0, cy]) - np.array(pivot); th = np.radians(angle)
    tip = np.array([np.cos(th) * tip[0] - np.sin(th) * tip[1], np.sin(th) * tip[0] + np.cos(th) * tip[1]])
    return img, (c.pivot_out[0] + 1, c.pivot_out[1] + 1), (c.pivot_out[0] + 1 + tip[0], c.pivot_out[1] + 1 + tip[1])

def bow(length, angle=-90.0, draw=0.0):
    """Recurve-ish bow, flat along x with the grip in the middle and the limbs bending back (−y) toward the
    archer. Returns image, grip point, and the two limb tips (for the string)."""
    L = length; H = 20; cy = 13.0; c = Canvas(L + 2, H, angle, (L / 2 + 1, cy)); x, y = c.x, c.y
    u = (x - (L / 2 + 1)) / (L / 2)                                                           # -1..1 along the bow
    bend = (u ** 2) * (8 + 2 * draw) - (np.abs(u) ** 6) * 1.5                                 # tips sweep back
    mid = cy - bend; thick = 1.6 * (1 - 0.55 * np.abs(u)) + 0.4
    limb = (np.abs(u) <= 1) & (np.abs(y - mid) <= thick)
    c.paint(limb, 'wood', (np.zeros_like(x), (y - mid) / (thick + 1e-6), np.ones_like(x)))
    c.paint(limb & (np.abs(u) < 0.12), 'leather', (np.zeros_like(x), (y - mid) / 2, np.ones_like(x)))
    c.paint(limb & (np.abs(u) > 0.93), 'steel', None, flat=np.full_like(x, 0.7))
    img = c.finish()
    th = np.radians(angle); R_ = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    tb = (8 + 2 * draw) - 1.5
    tips = [R_ @ np.array([s * L / 2, -tb]) for s in (-1, 1)]
    gp = (c.pivot_out[0] + 1, c.pivot_out[1] + 1)
    return img, gp, [(gp[0] + t[0], gp[1] + t[1]) for t in tips]

def arrow(length=58):
    L, H, cy = length, 9, 4.0; c = Canvas(L, H); x, y = c.x, c.y
    c.paint((np.abs(y - cy) <= 0.7) & (x >= 4) & (x <= L - 6), 'wood', None, flat=np.full_like(x, 0.55))
    head = (x >= L - 7) & (np.abs(y - cy) <= (L - x) * 0.45)
    c.paint(head, 'steel', None, flat=np.full_like(x, 0.8))
    fl = (x >= 1) & (x <= 7) & (np.abs(y - cy) <= 1 + (7 - x) * 0.35) & (np.abs(y - cy) >= 0.5)
    c.paint(fl, 'blue', None, flat=np.full_like(x, 0.75))
    return c.finish(), (1 + 1, cy + 1)

if __name__ == '__main__':
    from PIL import Image
    items = [dagger()[0], mace()[0], quarterstaff()[0], mage_staff()[0], bow(100, angle=0)[0], arrow()[0]]
    Z = 4; W = max(i.shape[1] for i in items) * Z + 20; Hh = sum(i.shape[0] * Z + 10 for i in items) + 10
    sheet = Image.new('RGBA', (W, Hh), (226, 220, 204, 255)); yy = 10
    for i in items:
        im = Image.fromarray(i); sheet.alpha_composite(im.resize((im.width * Z, im.height * Z), Image.NEAREST), (10, yy)); yy += im.height * Z + 10
    sheet.save('class_weapons.png'); print(sheet.size)


def _sword(L, grip_end, guard_x, guard_h, half_w, angle, pivot, cy, pommel=1.9, grip_r=1.5, taper=2.6):
    """Shared straight-sword painter (short sword, longsword, greatsword): pommel, leather grip, gold
    cross-guard, steel blade with a bright fuller line, tapering to the point at x = L - 1."""
    H = int(2 * cy + 1); c = Canvas(L, H, angle, pivot); x, y = c.x, c.y
    d, n = cyl(c, y, cy, grip_r)
    c.paint((np.abs(d) <= 1) & (x >= 2) & (x <= grip_end), 'leather', n)                                  # grip
    c.paint(((x - 1.4) ** 2 + (y - cy) ** 2) < pommel ** 2, 'gold', ((x - 1.4), (y - cy), np.ones_like(x)), spec=0.7)
    c.paint((np.abs(x - guard_x) <= 1.0) & (np.abs(y - cy) <= guard_h), 'gold', n, spec=0.6)              # cross-guard
    b0 = guard_x + 1.2; point = half_w * taper                                                         # point length
    narrow = 1 - 0.12 * np.clip((x - b0) / max((L - 1 - point) - b0, 1), 0, 1)                         # slight distal taper
    half = np.where(x < L - 1 - point, half_w * narrow, half_w * 0.88 * np.clip((L - 1 - x) / point, 0, 1))
    blade = (x >= b0) & (x <= L - 1) & (np.abs(y - cy) <= half)
    c.paint(blade, 'steel', (np.zeros_like(x), np.sign(y - cy) * 0.55, np.ones_like(x)), spec=0.9)
    c.paint(blade & (np.abs(y - cy) < 0.5) & (x < L - 1 - point), 'steel', None, flat=np.full_like(x, 0.97))  # fuller
    return c.finish(), (c.pivot_out[0] + 1, c.pivot_out[1] + 1)

def shortsword(angle=0.0, pivot=(6.0, 5.0)):
    """Short sword (light, one-handed): broad leaf-straight blade, short grip. Tip ~44 px from the hand."""
    return _sword(50, 10, 11.5, 4.4, 3.0, angle, pivot, cy=5.0, taper=2.6)

def longsword(angle=0.0, pivot=(6.5, 5.0)):
    """Longsword (one-handed), code-drawn replacement for the Legacy Canva-cut sword. Tip ~58 px from the hand."""
    return _sword(65, 11, 12.5, 4.8, 2.8, angle, pivot, cy=5.0, taper=2.8)

def greatsword(angle=0.0, pivot=(8.0, 6.0)):
    """Greatsword (two-handed): long grip for two stacked fists (~21 px apart), wide guard, long blade.
    Pivot = the rear (lower) fist, like the great axe."""
    return _sword(112, 30, 31.5, 6.2, 3.8, angle, pivot, cy=6.0, pommel=2.4, grip_r=1.7, taper=3.0)
