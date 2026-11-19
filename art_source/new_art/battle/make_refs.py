"""Templates and reference sheets for the ChatGPT battle-sprite sheets (new art, 2026-11-19).

templates/<class>_template.png  1536x1024 flat #00FF00 canvas, one row per stance, one cell per state. Each cell has a
                                ground line (dark green) and a head-top line (mid green) that set the figure height.
                                All greens are background for the cutter.
refs/<class>_<sex>_ref.png      what to draw: the class's new portrait outfit (bald) on the left, and the LEGACY sprite of
                                every cell in the same grid (poses only - Legacy art is reference only).
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, '..', 'portraits')
LEG = os.path.join(HERE, '..', '..', 'battle_sprites', 'poses', 'sprites')
sys.path.insert(0, PORT)
import finish

# stance rows per class (design doc table) and the legacy loadout that shows each row's poses
CLASSES = {
    'soldier': [('1h', 'sword_shield'), ('2h', 'greataxe'), ('reach', 'longspear')],
    'archer':  [('1h', 'dagger'), ('bow', 'bow')],
    'acolyte': [('1h', 'mace_shield'), ('2h', 'quarterstaff'), ('reach', 'longspear')],
    'mage':    [('1h', 'staff')],
    'warrior': [('1h', 'unarmed'), ('2h', 'greataxe'), ('reach', 'longspear')],
    'rogue':   [('1h', 'dual_daggers')],
}
STATES = {'bow': ['stand', 'nock', 'attack', 'hit']}
PORTRAIT_ID = {'acolyte': 'cleric'}
LEGACY_ID = {'warrior': 'brawler'}
W, H = 1536, 1024
GREEN, LINE, GROUND, TOP = (0, 255, 0), (0, 200, 0), (0, 130, 0), (0, 205, 60)


def cells(rows):
    rh = H / len(rows)
    for r, (stance, _) in enumerate(rows):
        states = STATES.get(stance, ['stand', 'attack', 'hit'])
        cw = W / len(states)
        for c, st in enumerate(states):
            yield r, c, stance, st, (round(c * cw), round(r * rh), round((c + 1) * cw), round((r + 1) * rh))


def template(cls):
    rows = CLASSES[cls]
    im = Image.new('RGB', (W, H), GREEN); d = ImageDraw.Draw(im)
    for r, c, stance, st, (x0, y0, x1, y1) in cells(rows):
        h = y1 - y0
        g = y0 + round(h * 0.92); t = g - round(h * 0.78)          # figure = 78% of the cell height
        d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=LINE, width=2)
        d.line([x0 + 12, g, x1 - 12, g], fill=GROUND, width=3)
        for x in range(x0 + 12, x1 - 12, 24): d.line([x, t, x + 12, t], fill=TOP, width=2)
    os.makedirs(os.path.join(HERE, 'templates'), exist_ok=True)
    im.save(os.path.join(HERE, 'templates', f'{cls}_template.png'))


def bust(sex, cls):
    """New portrait outfit, finished, without hair (the sprites are drawn bald; hair is a separate layer later)."""
    real = finish.load
    finish.load = lambda n: (np.zeros((200, 200, 4)) if n.startswith(f'{sex}_hair_') else real(n))
    try:
        im = finish.compose(sex, PORTRAIT_ID.get(cls, cls), 'tan', 'brown', 'brown', 'neutral_almond', 'neutral', 'none',
                            nose='straight')
    finally:
        finish.load = real
    return Image.fromarray(im)


def ref(cls, sex):
    rows = CLASSES[cls]
    side = 360
    im = Image.new('RGB', (side + W // 2, H // 2 + 40), (236, 230, 216)); d = ImageDraw.Draw(im)
    d.text((10, 8), f'{cls} ({sex}) - outfit from the new portrait (draw it bald)', fill=(40, 30, 30))
    b = bust(sex, cls).resize((340, 340), Image.NEAREST); im.paste(b, (10, 30), b)
    d.text((side + 8, 8), 'poses to follow (LEGACY sprites: pose only - old outfit, weapons become guide rods)', fill=(40, 30, 30))
    for r, c, stance, st, (x0, y0, x1, y1) in cells(rows):
        loadout = dict(rows)[stance]
        p = os.path.join(LEG, f'{LEGACY_ID.get(cls, cls)}_{sex}_{loadout}_{st}.png')
        X0, Y0, X1, Y1 = side + x0 // 2, 30 + y0 // 2, side + x1 // 2, 30 + y1 // 2
        d.rectangle([X0, Y0, X1 - 1, Y1 - 1], outline=(180, 170, 150))
        d.text((X0 + 4, Y0 + 2), f'{stance} {st}', fill=(90, 70, 60))
        if os.path.exists(p):
            s = Image.open(p).convert('RGBA'); s = s.crop(s.getbbox())
            k = min((X1 - X0 - 8) / s.width, (Y1 - Y0 - 18) / s.height)
            s = s.resize((max(1, round(s.width * k)), max(1, round(s.height * k))), Image.LANCZOS)
            im.paste(s, (X0 + (X1 - X0 - s.width) // 2, Y1 - s.height - 3), s)
    os.makedirs(os.path.join(HERE, 'refs'), exist_ok=True)
    im.save(os.path.join(HERE, 'refs', f'{cls}_{sex}_ref.png'))


if __name__ == '__main__':
    for cls in CLASSES:
        template(cls)
        for sex in 'mf': ref(cls, sex)
    print('ok')
