"""Animated battle sprites for Expedition: Brave Unknown.
Each unit is a small rig of body-part layers drawn in pixel art (96x72 frame, facing right).
Frames pose the parts (rotate around a pivot, translate), then a dark outline pass is applied,
then effects (slashes, arrows, sparkles) are drawn on top."""
from PIL import Image, ImageDraw
import math, os

FW, FH = 96, 72
PAL = {
 'out': (34, 28, 44),
 'skin': (240, 196, 160), 'skin_d': (206, 150, 118), 'skin_l': (252, 222, 194),
 'hair': (110, 70, 44), 'hair_d': (74, 46, 30), 'hair_t': (52, 110, 128), 'hair_td': (34, 74, 92),
 'eye': (40, 54, 98), 'eye_l': (150, 190, 236),
 'st_l': (214, 224, 236), 'st': (150, 164, 186), 'st_d': (96, 108, 134), 'st_dd': (66, 74, 98),
 'bl_l': (98, 140, 210), 'bl': (52, 92, 170), 'bl_d': (34, 58, 118),
 'le_l': (176, 122, 70), 'le': (134, 88, 50), 'le_d': (92, 58, 34),
 'tr': (104, 74, 52), 'tr_d': (74, 52, 38),
 'gold_l': (250, 214, 112), 'gold': (222, 168, 60), 'gold_d': (156, 108, 36),
 'gr_l': (98, 150, 92), 'gr': (58, 112, 66), 'gr_d': (36, 74, 46),
 'wh': (244, 240, 230), 'wh_d': (206, 198, 184), 'wh_dd': (164, 154, 140),
 'cr': (232, 220, 190), 'wood': (140, 96, 56), 'wood_d': (96, 64, 38),
 'orb': (150, 210, 250), 'orb_l': (236, 248, 255), 'orb_d': (70, 130, 200),
 'red': (220, 70, 60),
}
def col(c, a=255):
    return PAL[c] + (a,) if isinstance(c, str) else c

class Lay:
    def __init__(s):
        s.im = Image.new('RGBA', (FW, FH), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def poly(s, pts, c): s.d.polygon(pts, fill=col(c))
    def rect(s, x0, y0, x1, y1, c): s.d.rectangle([x0, y0, x1, y1], fill=col(c))
    def ell(s, x0, y0, x1, y1, c): s.d.ellipse([x0, y0, x1, y1], fill=col(c))
    def line(s, pts, c, w=1): s.d.line(pts, fill=col(c), width=w)
    def px(s, x, y, c):
        if 0 <= x < FW and 0 <= y < FH: s.im.putpixel((int(x), int(y)), col(c))
    def limb(s, a, b, w, c):
        s.d.line([a, b], fill=col(c), width=w)
        r = (w - 1) / 2
        for p in (a, b): s.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col(c))

# ---------------- shared body pieces ----------------
def face(L, x0, y0, hair='hair', hair_d='hair_d'):
    """Face looking right; x0,y0 = top-left of a 12x12 head box."""
    L.ell(x0, y0, x0 + 11, y0 + 12, 'skin')
    L.rect(x0, y0 + 2, x0 + 3, y0 + 10, 'skin_d')
    L.rect(x0 + 8, y0 + 5, x0 + 9, y0 + 7, 'eye'); L.px(x0 + 9, y0 + 5, 'eye_l')
    L.rect(x0 + 7, y0 + 4, x0 + 9, y0 + 4, hair_d)                    # brow
    L.px(x0 + 11, y0 + 8, 'skin_d'); L.rect(x0 + 8, y0 + 10, x0 + 9, y0 + 10, 'skin_d')
    L.rect(x0 + 1, y0 + 1, x0 + 4, y0 + 9, hair)                       # hair at back of head
    L.rect(x0 + 4, y0 + 1, x0 + 10, y0 + 3, hair)                      # fringe
    L.px(x0 + 6, y0 + 4, hair); L.px(x0 + 10, y0 + 4, hair)
    L.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 9, hair_d)

def boot(L, x0, y0, c='le', cd='le_d', toe='le', steel=False):
    L.rect(x0, y0, x0 + 6, y0 + 5, c); L.rect(x0, y0, x0 + 1, y0 + 5, cd)
    L.rect(x0 + 2, y0 + 3, x0 + 9, y0 + 5, toe if not steel else 'st'); L.rect(x0 + 2, y0 + 5, x0 + 9, y0 + 5, cd)
    if steel: L.rect(x0 + 5, y0 + 3, x0 + 8, y0 + 3, 'st_l')

# ---------------- SOLDIER ----------------
def soldier_parts():
    P = {}
    # sword arm (back) + sword, pivot = back shoulder
    L = Lay()
    L.line([(24, 43), (8, 21)], 'st_l', 3); L.line([(22, 44), (7, 23)], 'st_d', 1)
    L.px(7, 20, 'st_l'); L.px(6, 20, 'st_l'); L.line([(24, 42), (11, 24)], 'st_l', 1)
    L.line([(19, 47), (29, 39)], 'gold', 3); L.px(19, 47, 'gold_l'); L.px(29, 39, 'gold_l')
    L.limb((31, 34), (29, 41), 5, 'tr'); L.limb((29, 41), (27, 46), 5, 'le')
    L.ell(23, 43, 29, 49, 'le_d'); L.ell(24, 43, 28, 47, 'le')
    L.ell(26, 48, 29, 51, 'gold'); L.px(27, 48, 'gold_l')
    P['arm_b'] = (L, (31, 34))
    # legs
    L = Lay()
    L.limb((32, 46), (29, 55), 6, 'tr_d'); L.limb((29, 55), (27, 62), 6, 'st_d')
    L.ell(26, 52, 32, 58, 'st'); L.px(30, 53, 'st_l'); boot(L, 22, 62, steel=True)
    P['leg_b'] = (L, (32, 46))
    L = Lay()
    L.limb((38, 46), (41, 55), 6, 'tr'); L.limb((41, 55), (43, 62), 6, 'st')
    L.ell(38, 52, 44, 58, 'st_l'); L.px(42, 53, 'wh'); L.rect(43, 57, 44, 61, 'st_d')
    boot(L, 40, 62, steel=True)
    P['leg_f'] = (L, (38, 46))
    # torso: blue tabard, straps, belt, pauldrons, scarf
    L = Lay()
    L.poly([(28, 31), (42, 31), (43, 47), (27, 47)], 'bl')
    L.poly([(26, 46), (44, 46), (46, 53), (24, 53)], 'bl')
    L.poly([(26, 46), (31, 46), (29, 53), (24, 53)], 'bl_d'); L.rect(28, 31, 30, 46, 'bl_d')
    L.rect(39, 33, 41, 40, 'bl_l')
    for x in range(25, 46, 2): L.px(x, 52, 'wh')
    L.line([(41, 31), (30, 44)], 'le', 2); L.px(36, 37, 'st_l')
    L.rect(27, 42, 43, 44, 'le_d'); L.rect(34, 42, 37, 44, 'gold'); L.px(35, 43, 'le_d')
    L.rect(39, 44, 43, 49, 'le'); L.rect(39, 44, 43, 44, 'le_d')               # pouch
    L.ell(25, 29, 32, 36, 'st_d'); L.ell(26, 29, 31, 34, 'st')
    L.ell(28, 26, 42, 33, 'bl'); L.rect(29, 30, 33, 33, 'bl_d'); L.rect(37, 27, 40, 29, 'bl_l')
    P['torso'] = (L, (35, 46))
    # head with round helmet, cheek guard and visor band
    L = Lay()
    face(L, 30, 15)
    L.ell(27, 6, 42, 20, 'st'); L.ell(33, 7, 40, 13, 'st_l'); L.ell(27, 8, 32, 19, 'st_d')
    L.rect(27, 15, 43, 18, 'st_d'); L.rect(29, 15, 43, 16, 'st'); L.rect(36, 15, 42, 15, 'st_l')
    L.rect(29, 17, 31, 26, 'st_d'); L.rect(30, 17, 31, 24, 'st')
    for x in (31, 35, 39): L.px(x, 17, 'st_dd')
    P['head'] = (L, (35, 28))
    # shield arm (front) + kite shield
    L = Lay()
    L.limb((41, 34), (45, 40), 5, 'tr')
    kite = [(42, 33), (56, 33), (57, 44), (50, 61), (41, 44)]
    L.poly(kite, 'gold_d'); L.poly([(43, 34), (55, 34), (56, 44), (50, 59), (42, 44)], 'gold')
    L.poly([(44, 35), (54, 35), (55, 44), (50, 57), (43, 44)], 'bl')
    L.poly([(44, 35), (48, 35), (48, 55), (43, 44)], 'bl_d'); L.rect(52, 36, 53, 42, 'bl_l')
    L.rect(49, 37, 50, 53, 'wh'); L.ell(48, 36, 51, 40, 'wh')                     # lily emblem
    L.line([(49, 44), (46, 41), (46, 39)], 'wh'); L.line([(50, 44), (53, 41), (53, 39)], 'wh')
    L.rect(46, 45, 53, 46, 'wh'); L.px(49, 54, 'wh_d')
    L.px(55, 34, 'gold_l'); L.px(54, 34, 'gold_l')
    P['arm_f'] = (L, (41, 34))
    order = ['arm_b', 'leg_b', 'leg_f', 'torso', 'head', 'arm_f']
    return P, order

# ---------------- ARCHER ----------------
BOW_X, BOW_TOP, BOW_BOT, BOW_GRIP = 58, 10, 56, 33
def archer_parts():
    P = {}
    L = Lay()  # cape behind
    L.poly([(30, 30), (37, 31), (31, 56), (25, 62), (21, 58), (17, 61), (16, 54), (24, 38)], 'gr_d')
    L.poly([(31, 31), (36, 32), (31, 50), (27, 57), (24, 44)], 'gr')
    P['cape'] = (L, (32, 31))
    L = Lay()  # quiver on the back
    L.line([(22, 26), (30, 44)], 'le', 6); L.line([(21, 27), (28, 43)], 'le_d', 2)
    for (x, y) in ((17, 21), (20, 19), (23, 20), (19, 23)):
        L.line([(x, y), (x + 4, y + 7)], 'wood', 1); L.ell(x - 1, y - 1, x + 2, y + 2, 'cr'); L.px(x, y, 'wh')
    L.rect(19, 25, 25, 27, 'gold_d')
    P['quiver'] = (L, (26, 35))
    L = Lay()
    L.limb((32, 46), (27, 55), 6, 'tr_d'); L.limb((27, 55), (24, 61), 6, 'tr_d')
    boot(L, 19, 60, 'le', 'le_d'); L.rect(20, 59, 26, 60, 'gold_d')
    P['leg_b'] = (L, (32, 46))
    L = Lay()
    L.limb((38, 46), (43, 55), 6, 'tr'); L.limb((43, 55), (46, 61), 6, 'tr')
    boot(L, 43, 60, 'le', 'le_d'); L.rect(43, 59, 50, 60, 'gold_d')
    P['leg_f'] = (L, (38, 46))
    L = Lay()  # tunic
    L.poly([(29, 31), (41, 31), (42, 46), (28, 46)], 'gr')
    L.poly([(27, 45), (43, 45), (46, 53), (41, 51), (36, 54), (31, 51), (25, 53)], 'cr')
    L.poly([(27, 45), (31, 45), (31, 51), (25, 53)], 'wh_d')
    L.rect(29, 31, 31, 45, 'gr_d'); L.rect(38, 33, 40, 40, 'gr_l')
    L.line([(40, 31), (30, 43)], 'le_d', 2)
    L.rect(28, 43, 42, 45, 'le_d'); L.rect(34, 43, 36, 45, 'gold')
    L.rect(39, 45, 42, 49, 'le'); L.rect(28, 45, 31, 49, 'le')
    P['torso'] = (L, (35, 46))
    L = Lay()  # head in a hood
    face(L, 31, 15, 'hair_t', 'hair_td')
    L.poly([(27, 10), (33, 6), (40, 7), (44, 12), (44, 17), (41, 13), (34, 12), (31, 15), (30, 28), (26, 30), (25, 18)], 'gr')
    L.poly([(25, 18), (27, 10), (30, 9), (29, 28), (26, 30)], 'gr_d')
    L.line([(33, 7), (40, 7), (44, 12), (44, 16)], 'gold', 1)
    L.ell(34, 7, 39, 10, 'gr_l'); L.px(22, 13, 'gr_d'); L.line([(26, 11), (22, 14)], 'gr_d', 2)
    P['head'] = (L, (35, 28))
    # drawing arm: rest (hand at bow grip, arrow nocked low) and pulled (hand at cheek)
    L = Lay()
    L.limb((32, 34), (40, 38), 5, 'gr'); L.limb((40, 38), (48, 35), 5, 'le')
    L.ell(47, 32, 52, 37, 'skin'); L.px(51, 33, 'skin_l')
    P['arm_d'] = (L, (32, 34))
    L = Lay()
    L.limb((32, 34), (25, 31), 5, 'gr'); L.limb((25, 31), (36, 30), 5, 'le')
    L.ell(35, 28, 40, 33, 'skin'); L.px(39, 29, 'skin_l')
    P['arm_pull'] = (L, (32, 34))
    L = Lay()  # bow arm + bow
    L.limb((40, 33), (48, 33), 5, 'gr'); L.limb((48, 33), (55, 33), 5, 'le'); L.rect(49, 31, 52, 35, 'le_d')
    for y in range(BOW_TOP, BOW_BOT + 1):
        t = (y - BOW_GRIP) / (BOW_GRIP - BOW_TOP)
        x = BOW_X + round(4 * (1 - t * t))
        L.px(x, y, 'wood'); L.px(x + 1, y, 'wood_d')
    for (x, y) in ((BOW_X + 1, BOW_TOP - 1), (BOW_X + 2, BOW_TOP - 2), (BOW_X + 1, BOW_BOT + 1), (BOW_X + 2, BOW_BOT + 2)):
        L.px(x, y, 'gold')
    L.rect(BOW_X + 2, BOW_GRIP - 4, BOW_X + 4, BOW_GRIP + 4, 'gold'); L.px(BOW_X + 3, BOW_GRIP - 3, 'gold_l')
    L.ell(54, 30, 59, 36, 'skin'); L.px(58, 31, 'skin_l')
    P['arm_bow'] = (L, (40, 33))
    order = ['cape', 'quiver', 'leg_b', 'leg_f', 'torso', 'head', 'arm_d', 'arm_pull', 'arm_bow']
    return P, order

# ---------------- CLERIC ----------------
def cleric_parts():
    P = {}
    L = Lay()  # staff + holding arm (back)
    L.line([(24, 14), (24, 67)], 'wood', 2); L.line([(23, 14), (23, 67)], 'wood_d', 1)
    for y in (20, 44, 60): L.rect(23, y, 25, y + 1, 'gold')
    L.ell(17, 1, 31, 15, 'gold_d'); L.ell(18, 2, 30, 14, 'gold'); L.ell(20, 4, 28, 12, (0, 0, 0, 0))
    L.ell(21, 5, 27, 11, 'orb_d'); L.ell(21, 5, 26, 10, 'orb'); L.rect(22, 6, 23, 7, 'orb_l')
    for (a, b) in (((24, 0), (24, -3)), ((16, 8), (12, 8)), ((32, 8), (36, 8)), ((19, 3), (16, 0)), ((29, 3), (32, 0))):
        L.line([a, b], 'gold', 2)
    L.rect(22, 15, 26, 17, 'gold_d')
    L.limb((30, 33), (27, 39), 6, 'wh'); L.ell(22, 36, 28, 42, 'wh_d'); L.ell(22, 37, 27, 41, 'skin')
    P['arm_b'] = (L, (30, 33))
    L = Lay()
    L.rect(27, 63, 33, 67, 'le_d'); L.rect(38, 63, 45, 67, 'le'); L.rect(38, 67, 45, 67, 'le_d')
    P['legs'] = (L, (35, 50))
    L = Lay()  # robe
    L.poly([(28, 30), (42, 30), (49, 65), (21, 65)], 'wh')
    L.poly([(28, 30), (31, 30), (27, 65), (21, 65)], 'wh_d'); L.line([(25, 50), (23, 64)], 'wh_dd')
    L.line([(46, 52), (47, 64)], 'wh_d')
    L.poly([(32, 33), (39, 33), (41, 65), (30, 65)], 'bl'); L.poly([(32, 33), (34, 33), (32, 65), (30, 65)], 'bl_d')
    L.line([(32, 33), (30, 65)], 'gold'); L.line([(39, 33), (41, 65)], 'gold')
    L.rect(35, 54, 36, 61, 'gold'); L.rect(33, 56, 38, 57, 'gold')            # embroidered cross
    L.line([(21, 65), (49, 65)], 'gold')
    L.rect(29, 43, 42, 45, 'le_d'); L.rect(34, 43, 37, 45, 'gold')
    L.rect(39, 45, 43, 50, 'le'); L.rect(39, 45, 43, 45, 'le_d')
    L.ell(26, 28, 44, 38, 'wh'); L.ell(26, 30, 32, 38, 'wh_d'); L.line([(27, 35), (43, 35)], 'gold')
    L.ell(34, 31, 37, 34, 'orb_d')                                             # clasp
    P['torso'] = (L, (35, 46))
    L = Lay()  # hooded head
    L.poly([(26, 14), (31, 7), (39, 6), (45, 11), (46, 22), (43, 31), (27, 32), (24, 24)], 'wh')
    L.poly([(26, 14), (31, 8), (31, 31), (27, 32), (24, 24)], 'wh_d')
    face(L, 32, 15)
    L.rect(32, 13, 43, 15, 'hair')
    L.line([(31, 13), (36, 10), (42, 11), (45, 15)], 'gold'); L.line([(45, 15), (44, 28)], 'gold')
    P['head'] = (L, (35, 28))
    L = Lay()  # casting arm with wide sleeve
    L.poly([(39, 31), (44, 32), (51, 42), (45, 45), (40, 38)], 'wh')
    L.poly([(45, 42), (51, 40), (52, 43), (46, 46)], 'bl'); L.line([(45, 45), (51, 42)], 'gold')
    L.ell(50, 37, 55, 42, 'skin'); L.px(54, 38, 'skin_l'); L.px(55, 37, 'skin')
    P['arm_f'] = (L, (41, 33))
    order = ['arm_b', 'legs', 'torso', 'head', 'arm_f']
    return P, order

# ---------------- effects ----------------
def fx_arc(L, cx, cy, r, a0, a1, c=(236, 246, 255), w=3):
    for i, (rr, al) in enumerate(((r, 255), (r - 2, 170), (r - 4, 90))):
        if rr <= 0: continue
        steps = max(8, int(abs(a1 - a0) / 3))
        for k in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * k / steps)
            taper = math.sin(math.pi * k / steps)
            for t in range(max(1, int(w * taper))):
                L.px(cx + (rr - t) * math.cos(a), cy + (rr - t) * math.sin(a), c[:3] + (al,))

def fx_star(L, x, y, s, c='wh', c2='gold_l'):
    for i in range(-s, s + 1):
        L.px(x + i, y, c2 if abs(i) > s // 2 else c); L.px(x, y + i, c2 if abs(i) > s // 2 else c)
    for i in range(-s // 2, s // 2 + 1): L.px(x + i, y + i, c2); L.px(x + i, y - i, c2)
    L.px(x, y, c)

def fx_burst(L, x, y, r, c='wh'):
    for ang in range(0, 360, 45):
        a = math.radians(ang + 22)
        for d in range(r // 2, r + 1): L.px(x + d * math.cos(a), y + d * math.sin(a), c)
    fx_star(L, x, y, 3)

def fx_plus(L, x, y, s, c='gold_l'):
    L.rect(x - s, y - 1, x + s, y + 1, c); L.rect(x - 1, y - s, x + 1, y + s, c); L.px(x, y, 'wh')

def fx_lines(L, y0, y1, x0, x1, c=(255, 255, 255, 150)):
    for y in range(y0, y1, 4): L.line([(x0 + (y * 7) % 9, y), (x1 - (y * 5) % 11, y)], c)

def fx_ring(L, cx, cy, r, c='gold_l'):
    for ang in range(0, 360, 4):
        a = math.radians(ang); L.px(cx + r * math.cos(a), cy + r * math.sin(a), c)

def fx_arrow(L, x0, x1, y, glow=False):
    if glow: L.line([(x0 - 14, y), (x1, y)], (255, 230, 140, 140), 3)
    L.line([(x0, y), (x1 - 4, y)], 'wood_d'); L.line([(x1 - 4, y - 1), (x1, y), (x1 - 4, y + 1)], 'st_l')
    L.rect(x1 - 4, y - 1, x1 - 3, y + 1, 'st'); L.px(x0, y - 1, 'cr'); L.px(x0, y + 1, 'cr'); L.px(x0 + 1, y - 1, 'cr'); L.px(x0 + 1, y + 1, 'cr')

def fx_string(L, hand):
    top = (BOW_X, BOW_TOP); bot = (BOW_X, BOW_BOT)
    L.line([top, hand], (226, 222, 210)); L.line([hand, bot], (226, 222, 210))

# ---------------- frame assembly ----------------
def outline(im):
    out = im.copy(); px = im.load()
    for y in range(FH):
        for x in range(FW):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < FW and 0 <= ny < FH and px[nx, ny][3] > 200:
                        out.putpixel((x, y), PAL['out'] + (255,)); break
    return out

def tint(im, rgb, k):
    px = im.load()
    for y in range(FH):
        for x in range(FW):
            r, g, b, a = px[x, y]
            if a: px[x, y] = (int(r + (rgb[0] - r) * k), int(g + (rgb[1] - g) * k), int(b + (rgb[2] - b) * k), a)
    return im

def render(rig, f):
    P, order = rig
    bx, by = f.get('body', (0, 0))
    char = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    hide = set(f.get('hide', []))
    front = f.get('front', [])
    for name in [n for n in order if n not in front] + front:
        if name in hide: continue
        L, pv = P[name]
        ang, dx, dy = f.get('parts', {}).get(name, (0, 0, 0))
        img = L.im.rotate(ang, resample=Image.NEAREST, center=pv, translate=(bx + dx, by + dy)) if ang else \
              L.im.transform(L.im.size, Image.AFFINE, (1, 0, -(bx + dx), 0, 1, -(by + dy)), resample=Image.NEAREST)
        char.alpha_composite(img)
    pre = Lay(); [fn(pre) for fn in f.get('pre', [])]
    char.alpha_composite(pre.im)
    char = outline(char)
    if 'tint' in f: tint(char, *f['tint'])
    frame = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    sh = Lay(); sx = 35 + bx; sh.ell(sx - 14, 65, sx + 14, 70, (0, 0, 0, 60 if by > -3 else 35))
    frame.alpha_composite(sh.im); frame.alpha_composite(char)
    fx = Lay(); [fn(fx) for fn in f.get('fx', [])]
    frame.alpha_composite(fx.im)
    return frame

# ---------------- animations ----------------
def hit_anim(side_star=(40, 38)):
    return [
        dict(body=(-3, 0), parts={'head': (8, 0, 0)}, tint=((255, 255, 255), .85), fx=[lambda L: fx_burst(L, *side_star, 7)], dur=80),
        dict(body=(-5, 1), parts={'head': (10, 0, 1)}, tint=((230, 60, 50), .45), dur=110),
        dict(body=(-3, 0), parts={'head': (4, 0, 0)}, dur=130),
        dict(body=(-1, 0), dur=160),
    ]

def soldier_anims():
    A = {}
    idle = dict(dur=200)
    A['attack'] = [
        idle,
        dict(body=(-2, 1), parts={'arm_b': (-35, 0, 0), 'arm_f': (5, -1, 0), 'head': (3, 0, 0)}, dur=180),
        dict(body=(5, 0), front=['arm_b'], parts={'arm_b': (-150, 0, 0), 'arm_f': (-4, 1, 0), 'head': (-4, 0, 0), 'leg_f': (-10, 1, 0)},
             fx=[lambda L: fx_arc(L, 37, 34, 26, -120, 40), lambda L: fx_lines(L, 20, 50, 60, 92)], dur=90),
        dict(body=(5, 1), front=['arm_b'], parts={'arm_b': (-170, 0, 0), 'head': (-4, 0, 0), 'leg_f': (-10, 1, 0)},
             fx=[lambda L: fx_arc(L, 37, 35, 26, -40, 60, (200, 220, 240), 2)], dur=140),
        dict(body=(2, 0), parts={'arm_b': (-40, 0, 0)}, dur=160),
        idle,
    ]
    A['hit'] = [idle] + hit_anim((46, 40)) + [idle]
    A['skill'] = [  # Shield Bash
        idle,
        dict(body=(-3, 2), parts={'arm_f': (12, -3, 0), 'arm_b': (10, 0, 0), 'head': (5, 0, 0)}, dur=200),
        dict(body=(9, 0), parts={'arm_f': (-8, 5, -1), 'arm_b': (25, 0, 0), 'head': (-6, 1, 0), 'leg_b': (15, 0, 0)},
             fx=[lambda L: fx_burst(L, 68, 44, 9, 'gold_l'), lambda L: fx_star(L, 68, 44, 4), lambda L: fx_lines(L, 30, 58, 4, 26)], dur=110),
        dict(body=(9, 0), parts={'arm_f': (-6, 4, 0), 'arm_b': (25, 0, 0), 'head': (-6, 1, 0), 'leg_b': (15, 0, 0)},
             fx=[lambda L: fx_ring(L, 68, 44, 11, 'gold'), lambda L: fx_ring(L, 68, 44, 7, 'wh')], dur=170),
        dict(body=(4, 0), parts={'arm_f': (0, 2, 0)}, dur=160),
        idle,
    ]
    A['critical'] = [  # Leaping Cleave
        idle,
        dict(body=(-2, 3), parts={'arm_b': (-60, 0, 0), 'head': (6, 0, 0)},
             fx=[lambda L: fx_star(L, 26, 6, 5)], tint=((255, 240, 180), .25), dur=260),
        dict(body=(4, -9), parts={'arm_b': (-80, 0, 0), 'leg_b': (25, 0, -2), 'leg_f': (-25, 0, -2), 'head': (-3, 0, 0)},
             fx=[lambda L: fx_star(L, 35, 2, 4), lambda L: fx_lines(L, 46, 70, 20, 50)], dur=150),
        dict(body=(10, 0), front=['arm_b'], parts={'arm_b': (-185, 0, 0), 'head': (-8, 0, 0), 'leg_f': (-15, 2, 0)},
             fx=[lambda L: fx_arc(L, 42, 30, 33, -110, 80, (255, 250, 220), 4), lambda L: fx_arc(L, 42, 30, 25, -100, 70, (255, 214, 112), 2),
                 lambda L: fx_burst(L, 76, 52, 10)], dur=110),
        dict(body=(10, 2), front=['arm_b'], parts={'arm_b': (-195, 0, 0), 'head': (-8, 0, 0), 'leg_f': (-15, 2, 0)},
             fx=[lambda L: fx_ring(L, 74, 52, 12, 'wh'), lambda L: fx_ring(L, 74, 52, 16, 'gold_l')], dur=200),
        dict(body=(4, 0), parts={'arm_b': (-40, 0, 0)}, dur=180),
        idle,
    ]
    return A

def archer_anims():
    A = {}
    idle = dict(hide=['arm_pull'], pre=[lambda L: fx_string(L, (BOW_X, 33))], dur=200)
    nock = dict(hide=['arm_pull'], pre=[lambda L: fx_string(L, (BOW_X, 33))],
                fx=[lambda L: fx_arrow(L, 47, 64, 34)], dur=170)
    def drawn(glow=False, extra=None, body=(-1, 0), dur=240, tintv=None):
        f = dict(body=body, hide=['arm_d'], pre=[lambda L: fx_string(L, (37, 31))],
                 fx=[lambda L: fx_arrow(L, 36, 64, 31, glow)] + (extra or []), dur=dur)
        if tintv: f['tint'] = tintv
        return f
    def release(x0, glow=False, extra=None):
        return dict(hide=['arm_pull'], parts={'arm_d': (-25, 0, 0)}, pre=[lambda L: fx_string(L, (BOW_X - 2, 33))],
                    fx=[lambda L: fx_arrow(L, x0, x0 + 22, 31, glow)] + (extra or []), dur=90)
    A['attack'] = [idle, nock, drawn(), release(70, extra=[lambda L: fx_lines(L, 26, 37, 62, 70)]),
                   dict(hide=['arm_pull'], parts={'arm_d': (-15, 0, 0)}, pre=[lambda L: fx_string(L, (BOW_X + 1, 33))], dur=160), idle]
    A['hit'] = [idle] + [dict(f, hide=['arm_pull'], pre=[lambda L: fx_string(L, (BOW_X, 33))]) for f in hit_anim((44, 38))] + [idle]
    gl = lambda L: [fx_star(L, 64, 31, 3), fx_ring(L, 64, 31, 6, 'gold_l')]
    A['skill'] = [  # Power Shot
        idle, nock,
        drawn(True, [gl], tintv=((255, 230, 150), .15), dur=260),
        drawn(True, [lambda L: [fx_star(L, 64, 31, 5), fx_ring(L, 64, 31, 9, 'gold_l'), fx_ring(L, 64, 31, 5, 'wh')]], body=(-2, 0), dur=200),
        release(68, True, [lambda L: fx_lines(L, 24, 40, 50, 66)]),
        dict(hide=['arm_pull'], parts={'arm_d': (-20, 0, 0)}, pre=[lambda L: fx_string(L, (BOW_X + 1, 33))],
             fx=[lambda L: fx_burst(L, 90, 31, 7, 'gold_l')], dur=170),
        idle,
    ]
    A['critical'] = [  # Piercing Shot
        idle,
        dict(body=(-2, 4), hide=['arm_d'], parts={'leg_f': (-20, 2, -2), 'leg_b': (20, 0, -2)},
             pre=[lambda L: fx_string(L, (37, 31))], fx=[lambda L: fx_arrow(L, 36, 64, 31), lambda L: fx_star(L, 40, 22, 4)],
             tint=((255, 240, 180), .25), dur=280),
        dict(body=(-3, 4), hide=['arm_d'], parts={'leg_f': (-20, 2, -2), 'leg_b': (20, 0, -2)},
             pre=[lambda L: fx_string(L, (35, 31))], fx=[lambda L: fx_arrow(L, 34, 62, 31, True), lambda L: fx_star(L, 62, 31, 6)], dur=200),
        dict(body=(-6, 4), hide=['arm_pull'], parts={'arm_d': (-25, 0, 0), 'leg_f': (-20, 2, -2), 'leg_b': (20, 0, -2)},
             pre=[lambda L: fx_string(L, (BOW_X - 2, 33))],
             fx=[lambda L: L.line([(60, 31), (95, 31)], (255, 250, 220), 3), lambda L: L.line([(60, 31), (95, 31)], 'gold_l', 1),
                 lambda L: fx_burst(L, 86, 31, 9)], dur=120),
        dict(body=(-4, 2), hide=['arm_pull'], parts={'arm_d': (-15, 0, 0)}, pre=[lambda L: fx_string(L, (BOW_X + 1, 33))],
             fx=[lambda L: fx_ring(L, 86, 31, 12, 'wh')], dur=180),
        idle,
    ]
    return A

def cleric_anims():
    A = {}
    idle = dict(dur=200)
    A['attack'] = [  # staff strike
        idle,
        dict(body=(-2, 0), parts={'arm_b': (25, 0, 0), 'head': (4, 0, 0)}, dur=200),
        dict(body=(5, 0), parts={'arm_b': (-95, 3, 0), 'head': (-4, 0, 0), 'arm_f': (20, 0, 0)},
             fx=[lambda L: fx_arc(L, 33, 34, 30, -150, -20, (230, 240, 255), 2), lambda L: fx_burst(L, 66, 34, 6)], dur=110),
        dict(body=(4, 0), parts={'arm_b': (-100, 3, 1), 'arm_f': (20, 0, 0)}, dur=160),
        dict(body=(1, 0), parts={'arm_b': (-20, 0, 0)}, dur=160),
        idle,
    ]
    A['hit'] = [idle] + hit_anim((42, 38)) + [idle]
    sp = lambda pts: (lambda L: [fx_plus(L, x, y, s) for x, y, s in pts])
    A['skill'] = [  # Heal
        idle,
        dict(parts={'arm_f': (-25, 0, -1), 'arm_b': (5, 0, -2)}, fx=[sp([(57, 34, 2)])], dur=180),
        dict(parts={'arm_f': (-30, 0, -2), 'arm_b': (5, 0, -2)},
             fx=[sp([(58, 30, 3), (64, 38, 2), (55, 22, 2)]), lambda L: fx_ring(L, 25, 8, 9, 'orb_l')], dur=180),
        dict(parts={'arm_f': (-30, 0, -2), 'arm_b': (5, 0, -2)},
             fx=[sp([(60, 26, 4), (67, 36, 2), (54, 18, 2), (70, 22, 3)]), lambda L: fx_ring(L, 25, 8, 12, 'orb_l'),
                 lambda L: fx_ring(L, 62, 30, 10, 'gold_l')], tint=((255, 240, 190), .15), dur=220),
        dict(parts={'arm_f': (-15, 0, -1)}, fx=[sp([(66, 20, 2), (72, 30, 2), (60, 14, 1)])], dur=200),
        idle,
    ]
    A['critical'] = [  # Smite
        idle,
        dict(body=(-2, 1), parts={'arm_b': (35, 0, -2), 'head': (5, 0, 0)},
             fx=[lambda L: fx_star(L, 12, 10, 5), lambda L: fx_ring(L, 14, 12, 10, 'gold_l')], tint=((255, 240, 180), .3), dur=280),
        dict(body=(-2, 1), parts={'arm_b': (40, 0, -3), 'head': (5, 0, 0)},
             fx=[lambda L: fx_star(L, 10, 12, 7), lambda L: fx_ring(L, 12, 13, 14, 'wh'), lambda L: fx_ring(L, 12, 13, 9, 'gold_l')], dur=180),
        dict(body=(6, 0), parts={'arm_b': (-100, 3, 0), 'head': (-5, 0, 0), 'arm_f': (20, 0, 0)},
             fx=[lambda L: fx_arc(L, 34, 34, 34, -170, -10, (255, 246, 210), 4), lambda L: fx_burst(L, 72, 36, 11, 'gold_l'),
                 lambda L: fx_plus(L, 72, 36, 5)], dur=120),
        dict(body=(5, 0), parts={'arm_b': (-105, 3, 1), 'arm_f': (20, 0, 0)},
             fx=[lambda L: fx_ring(L, 72, 36, 13, 'gold_l'), lambda L: fx_ring(L, 72, 36, 18, 'wh')], dur=200),
        dict(body=(1, 0), parts={'arm_b': (-20, 0, 0)}, dur=180),
        idle,
    ]
    return A

UNITS = {'soldier': (soldier_parts, soldier_anims), 'archer': (archer_parts, archer_anims), 'cleric': (cleric_parts, cleric_anims)}
ANIM_ORDER = ['attack', 'hit', 'skill', 'critical']

def build(outdir='anim_out', scale=4):
    os.makedirs(outdir, exist_ok=True)
    bg = (222, 210, 186, 255)
    for unit, (pf, af) in UNITS.items():
        rig = pf(); A = af()
        if unit == 'archer':
            for anim in A.values():
                for f in anim: f.setdefault('hide', ['arm_pull'])
        cols = max(len(A[a]) for a in ANIM_ORDER)
        sheet = Image.new('RGBA', (FW * cols, FH * len(ANIM_ORDER)), (0, 0, 0, 0))
        for r, an in enumerate(ANIM_ORDER):
            frames = [render(rig, f) for f in A[an]]
            for c, fr in enumerate(frames): sheet.alpha_composite(fr, (c * FW, r * FH))
            gif = []
            for fr in frames:
                g = Image.new('RGBA', (FW, FH), bg); g.alpha_composite(fr)
                gif.append(g.resize((FW * scale, FH * scale), Image.NEAREST).convert('RGB'))
            durs = [f.get('dur', 150) for f in A[an]]; durs[-1] = 450
            gif[0].save(f'{outdir}/{unit}_{an}.gif', save_all=True, append_images=gif[1:], duration=durs, loop=0, disposal=2)
        sheet.save(f'{outdir}/{unit}_sheet.png')
        prev = Image.new('RGBA', sheet.size, bg); prev.alpha_composite(sheet)
        prev.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(f'{outdir}/{unit}_sheet_preview.png')
    print('done')

if __name__ == '__main__':
    build()
