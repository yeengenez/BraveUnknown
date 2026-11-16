"""Pixel sprites for Expedition: Brave Unknown starter classes.
Native size 40x48, facing right (toward the enemy line). Drawn as layered shapes,
then given a dark outline pass. Output: native PNGs, 6x previews, and a lineup sheet."""
from PIL import Image, ImageDraw
import math, os

W, H = 40, 48
C = {
 'out':(29,26,36),
 'skin':(232,180,138),'skin_d':(192,130,98),
 'hair':(90,58,38),
 'st_l':(208,216,224),'st':(142,154,168),'st_d':(93,104,120),
 'tm_l':(84,166,168),'tm':(47,127,134),'tm_d':(30,84,88),
 'le_l':(168,116,63),'le':(138,90,52),'le_d':(94,59,34),
 'wd':(154,107,60),'wd_d':(107,69,36),
 'cr':(236,229,210),'cr_d':(196,185,160),'cr_dd':(160,148,124),
 'gr_l':(109,138,76),'gr':(79,107,58),'gr_d':(52,72,42),
 'boot':(59,42,32),'gold':(217,164,65),'gold_d':(160,112,40),
 'eye':(36,30,40),'str':(222,214,190),'glow':(255,236,160),
}

class S:
    def __init__(s): s.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    def p(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.im.putpixel((x, y), C[c] + (255,))
    def r(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.p(x, y, c)
    def line(s, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            s.p(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)
    def disc(s, cx, cy, rad, c):
        for y in range(H):
            for x in range(W):
                if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad + rad * 0.6: s.p(x, y, c)
    def outline(s):
        src = s.im.copy(); px = src.load()
        for y in range(H):
            for x in range(W):
                if px[x, y][3] == 0:
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and px[nx, ny][3]:
                            s.im.putpixel((x, y), C['out'] + (255,)); break
        return s.im

def shadow(s):
    for x in range(11, 28):
        a = 1 - abs(x - 19) / 9
        if a > 0.15: s.im.putpixel((x, 46), (0, 0, 0, int(70 * a)))

def head(s, x=15):
    s.r(x, 12, x + 7, 20, 'skin')
    s.r(x, 12, x + 1, 20, 'skin_d')          # back of head in shade
    s.p(x + 4, 16, 'eye'); s.p(x + 6, 16, 'eye')
    s.p(x + 7, 18, 'skin_d')                  # nose shadow
    s.r(x + 4, 19, x + 6, 19, 'skin_d')

# ---------- Soldier ----------
def soldier(weapon):
    s = S()
    # weapon behind the body (held in far hand)
    if weapon == 'sword':
        s.r(9, 10, 10, 28, 'st_l'); s.r(9, 10, 9, 28, 'st'); s.p(10, 9, 'st_l')
        s.r(7, 29, 12, 29, 'gold_d'); s.r(9, 30, 10, 32, 'le_d'); s.p(9, 33, 'gold'); s.p(10, 33, 'gold')
    elif weapon == 'axe':
        s.r(11, 13, 12, 34, 'wd'); s.r(11, 13, 11, 34, 'wd_d')
        s.r(6, 13, 10, 20, 'st'); s.r(5, 14, 5, 19, 'st_l'); s.r(6, 13, 7, 20, 'st_l'); s.r(9, 15, 10, 18, 'st_d')
    elif weapon == 'spear':
        s.r(11, 6, 12, 38, 'wd'); s.r(11, 6, 11, 38, 'wd_d')
        s.r(11, 1, 12, 5, 'st_l'); s.p(11, 0, 'st_l'); s.p(12, 0, 'st_l'); s.r(10, 3, 10, 5, 'st'); s.r(13, 3, 13, 5, 'st')
        s.r(10, 6, 13, 6, 'tm')
    # far arm holding the weapon
    s.r(11, 22, 14, 28, 'st_d'); s.r(9, 29, 12, 31, 'le')
    # legs
    s.r(15, 33, 17, 41, 'le_d'); s.r(19, 33, 21, 41, 'le')
    s.r(14, 41, 17, 44, 'boot'); s.r(19, 41, 23, 44, 'boot'); s.r(20, 41, 22, 41, 'le_d')
    # torso: mail with team tabard
    s.r(14, 21, 23, 33, 'st'); s.r(14, 21, 15, 33, 'st_d')
    for y in range(22, 33, 2): s.r(16, y, 23, y, 'st_d')      # mail rows
    s.r(16, 22, 22, 34, 'tm'); s.r(16, 22, 17, 34, 'tm_d'); s.r(21, 22, 22, 25, 'tm_l')
    s.r(15, 30, 23, 30, 'le_d'); s.p(20, 30, 'gold')            # belt
    # neck and head
    s.r(17, 20, 20, 21, 'skin_d'); head(s, 15)
    # kettle helmet: dome + wide brim
    s.r(15, 9, 22, 13, 'st'); s.r(16, 8, 21, 8, 'st'); s.r(18, 7, 19, 7, 'st_l')
    s.r(19, 9, 21, 11, 'st_l'); s.r(15, 9, 16, 13, 'st_d')
    s.r(12, 14, 25, 14, 'st'); s.r(13, 15, 24, 15, 'st_d'); s.r(20, 14, 24, 14, 'st_l')
    s.r(15, 16, 15, 19, 'hair')
    # near pauldron
    s.r(21, 21, 25, 24, 'st'); s.r(22, 21, 25, 21, 'st_l'); s.r(21, 24, 25, 24, 'st_d')
    # round shield on near arm, covering the torso
    s.disc(25, 28, 6, 'st_d'); s.disc(25, 28, 5, 'tm'); s.disc(26, 27, 3, 'tm_l')
    s.r(21, 28, 29, 28, 'cr'); s.r(25, 24, 25, 32, 'cr')         # painted cross
    s.disc(25, 28, 1, 'st_l'); s.p(26, 27, 'cr')                  # iron boss
    s.p(22, 32, 'tm_d'); s.p(21, 31, 'tm_d'); s.p(23, 33, 'tm_d')
    img = s.outline(); shadow(s); return img

# ---------- Archer ----------
def archer():
    s = S()
    # quiver on the back
    s.r(9, 14, 12, 29, 'le'); s.r(9, 14, 9, 29, 'le_d'); s.r(9, 22, 12, 22, 'le_d')
    for x, h in ((9, 9), (10, 10), (11, 9)):
        s.p(x, h, 'cr'); s.p(x, h + 1, 'cr_d'); s.r(x, h + 2, x, 14, 'wd')
    # legs (slim, light)
    s.r(15, 32, 17, 41, 'gr_d'); s.r(19, 32, 21, 41, 'gr')
    s.r(15, 41, 17, 44, 'le_d'); s.r(19, 41, 23, 44, 'le_d'); s.r(15, 41, 17, 41, 'le'); s.r(19, 41, 21, 41, 'le')
    # leather jerkin over green tunic
    s.r(15, 21, 22, 33, 'gr'); s.r(15, 21, 16, 33, 'gr_d')
    s.r(16, 22, 22, 30, 'le'); s.r(16, 22, 17, 30, 'le_d'); s.r(21, 23, 22, 26, 'le_l')
    s.r(15, 30, 22, 30, 'le_d'); s.p(19, 30, 'gold')
    s.line(16, 21, 22, 29, 'le_d')                                # quiver strap
    s.r(17, 20, 20, 21, 'skin_d'); head(s, 15)
    s.r(15, 16, 16, 19, 'hair'); s.r(21, 13, 22, 14, 'hair')     # fringe
    # hood and short cape
    s.r(14, 10, 22, 12, 'gr'); s.r(15, 9, 21, 9, 'gr'); s.r(17, 8, 19, 8, 'gr')
    s.r(18, 9, 21, 10, 'gr_l'); s.r(14, 10, 15, 21, 'gr_d'); s.r(14, 13, 14, 23, 'gr_d')
    s.r(13, 20, 15, 25, 'gr_d')
    # near arm reaching forward to the bow
    s.r(20, 22, 26, 24, 'gr'); s.r(20, 22, 26, 22, 'gr_l'); s.r(27, 22, 28, 24, 'skin')
    s.r(24, 22, 26, 24, 'le')                                     # bracer
    # longbow held upright in front
    pts = []
    for y in range(9, 39):
        t = (y - 24) / 15.0
        pts.append((round(29 + 3 * (1 - t * t)), y))
    for x, y in pts: s.p(x, y, 'wd'); s.p(x + 1, y, 'wd_d')
    s.r(30, 22, 32, 25, 'le_d')                                   # grip
    s.line(29, 9, 29, 38, 'str')
    s.r(27, 22, 28, 24, 'skin')
    img = s.outline(); shadow(s); return img

# ---------- Cleric ----------
def cleric():
    s = S()
    # staff held in the near hand, taller than the cleric
    s.r(27, 8, 28, 44, 'wd'); s.r(27, 8, 27, 44, 'wd_d')
    s.disc(27, 6, 4, 'gold_d'); s.disc(27, 6, 3, 'gold'); s.disc(27, 6, 1, 'glow'); s.p(27, 6, 'cr')
    s.r(26, 11, 29, 11, 'tm'); s.p(29, 12, 'tm'); s.p(29, 13, 'tm_d')   # ribbon
    # satchel on the far hip
    s.r(12, 28, 15, 33, 'le'); s.r(12, 28, 12, 33, 'le_d'); s.r(12, 28, 15, 28, 'le_d')
    # long robe flaring to the ground
    for y in range(21, 45):
        spread = (y - 21) // 6
        s.r(15 - spread, y, 22 + spread, y, 'cr')
        s.r(15 - spread, y, 16 - spread, y, 'cr_d')
    s.r(16, 36, 16, 44, 'cr_dd'); s.r(20, 38, 20, 44, 'cr_d')    # folds
    s.r(17, 21, 20, 44, 'tm'); s.r(17, 21, 17, 44, 'tm_d')       # front stole
    s.r(18, 25, 19, 26, 'gold'); s.p(18, 24, 'gold_d')          # stole emblem (sun)
    s.r(14, 30, 23, 30, 'le_d')                                  # rope belt
    s.p(16, 31, 'le_d'); s.p(16, 32, 'le_d')
    s.r(15, 44, 17, 45, 'boot'); s.r(20, 44, 23, 45, 'boot')     # toes
    # head under a cowl
    s.r(17, 20, 20, 21, 'skin_d'); head(s, 15)
    s.r(14, 10, 22, 12, 'cr'); s.r(15, 9, 21, 9, 'cr'); s.r(17, 8, 19, 8, 'cr')
    s.r(14, 10, 15, 22, 'cr_d'); s.r(13, 14, 14, 24, 'cr_d'); s.r(19, 9, 21, 10, 'cr')
    s.r(14, 12, 22, 12, 'tm')                                    # cowl trim
    s.r(16, 13, 16, 19, 'hair')
    # wide sleeve of the near arm reaching to the staff
    s.r(20, 23, 26, 27, 'cr'); s.r(20, 27, 26, 27, 'cr_d'); s.r(25, 23, 26, 27, 'tm')
    s.r(26, 24, 27, 26, 'skin'); s.p(28, 25, 'skin')
    img = s.outline(); shadow(s); return img

sprites = {
 'soldier_sword': soldier('sword'), 'soldier_axe': soldier('axe'), 'soldier_spear': soldier('spear'),
 'archer': archer(), 'cleric': cleric(),
}
os.makedirs('out', exist_ok=True)
for name, im in sprites.items():
    im.save(f'out/{name}.png')
    im.resize((W * 6, H * 6), Image.NEAREST).save(f'out/{name}_x6.png')

# lineup sheet: soldier (sword), archer, cleric, then soldier weapon variants
order = ['soldier_sword', 'archer', 'cleric', 'soldier_axe', 'soldier_spear']
sc = 6; pad = 12
sheet = Image.new('RGBA', (len(order) * (W * sc + pad) + pad, H * sc + pad * 2), (226, 216, 196, 255))
for i, n in enumerate(order):
    sheet.alpha_composite(sprites[n].resize((W * sc, H * sc), Image.NEAREST), (pad + i * (W * sc + pad), pad))
sheet.save('out/lineup_preview.png')
print('ok')
