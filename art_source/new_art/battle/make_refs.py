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
    # v6 (2026-11-21): main sheet = shield, two-handed, spear; the dual weapons get their own sheet (EXTRA_SHEETS)
    'soldier': [('1h', 'sword_shield'), ('2h', 'greataxe'), ('reach', 'longspear')],
    # (2026-11-24) the dagger has no shield -> dual stance on its own sheet, like the Soldier's dual weapons
    'archer':  [('bow', 'bow'), ('crossbow', None)],
    'acolyte': [('1h', 'mace_shield'), ('2h', 'quarterstaff'), ('reach', 'longspear')],
    'mage':    [('1h', 'staff')],
    'warrior': [('1h', 'unarmed'), ('2h', 'greataxe'), ('reach', 'longspear')],
    'rogue':   [('1h', 'dual_daggers')],
}
STATES = {'bow': ['stand', 'nock', 'attack', 'hit'], 'crossbow': ['stand', 'aim', 'attack', 'hit']}   # attack = release
PORTRAIT_ID = {'acolyte': 'cleric'}
LEGACY_ID = {'warrior': 'brawler'}
W, H = 1536, 1024
GREEN, LINE, GROUND, TOP = (0, 255, 0), (0, 200, 0), (0, 130, 0), (0, 205, 60)


# per-class cell order (user, 2026-11-20): Soldier rows get a READY (wind-up just before the attack) cell; the dual row
# gets two attacks instead (ATTACK = main hand, ATTACK2 = off-hand)
CLASS_STATES = {'soldier': {'1h': ['stand', 'ready', 'attack', 'hit'], 'dual': ['stand', 'attack', 'attack2', 'hit'],
                            '2h': ['stand', 'ready', 'attack', 'hit'], 'reach': ['stand', 'ready', 'attack', 'hit']}}


# extra sheets per class: name -> rows of (stance, [cell states]). Soldier dual = user's dual-slash concept (2026-11-21):
# stand, ready (front/cyan arm winds up), slash_left (cyan slashes down), slash_right (magenta sweeps), finish, hit
EXTRA_SHEETS = {'soldier': {'dual': [('dual', ['stand', 'ready', 'slash_left']), ('dual', ['slash_right', 'finish', 'hit'])]},
                'archer': {'dual': [('dual', ['stand', 'ready', 'slash_left']), ('dual', ['slash_right', 'finish', 'hit'])],
                           # (user, 2026-11-25) the Archer gets its own one-handed sheet: one dagger, off-hand empty
                           '1h': [('1h', ['stand', 'ready']), ('1h', ['attack', 'hit'])]}}
# older sheets drawn on an earlier layout: (class, sex) -> rows
SHEET_ROWS = {('soldier', 'm'): [('1h', 'sword_shield'), ('dual', None), ('2h', 'greataxe'), ('reach', 'longspear')],   # v5 male
              ('soldier', 'f'): [('1h', 'sword_shield'), ('dual', None), ('2h', 'greataxe'), ('reach', 'longspear')]}   # Gemini edit of v5 male


def states_for(cls, stance):
    return CLASS_STATES.get(cls, {}).get(stance) or STATES.get(stance, ['stand', 'attack', 'hit'])


def cells(rows, cls=None):
    rh = H / len(rows)
    for r, (stance, extra) in enumerate(rows):
        states = extra if isinstance(extra, list) else states_for(cls, stance)
        cw = W / len(states)
        for c, st in enumerate(states):
            yield r, c, stance, st, (round(c * cw), round(r * rh), round((c + 1) * cw), round((r + 1) * rh))


def template(cls, rows=None, name=None):
    rows = rows or CLASSES[cls]
    im = Image.new('RGB', (W, H), GREEN); d = ImageDraw.Draw(im)
    for r, c, stance, st, (x0, y0, x1, y1) in cells(rows, cls):
        h = y1 - y0
        g = y0 + round(h * 0.92); t = g - round(h * 0.78)          # figure = 78% of the cell height
        d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=LINE, width=2)
        d.line([x0 + 12, g, x1 - 12, g], fill=GROUND, width=3)
        for x in range(x0 + 12, x1 - 12, 24): d.line([x, t, x + 12, t], fill=TOP, width=2)
    os.makedirs(os.path.join(HERE, 'templates'), exist_ok=True)
    im.save(os.path.join(HERE, 'templates', f'{name or cls}_template.png'))


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
    for r, c, stance, st, (x0, y0, x1, y1) in cells(rows, cls):
        loadout = dict(rows)[stance]
        p = os.path.join(LEG, f'{LEGACY_ID.get(cls, cls)}_{sex}_{loadout}_{st}.png') if loadout else ''
        X0, Y0, X1, Y1 = side + x0 // 2, 30 + y0 // 2, side + x1 // 2, 30 + y1 // 2
        d.rectangle([X0, Y0, X1 - 1, Y1 - 1], outline=(180, 170, 150))
        d.text((X0 + 4, Y0 + 2), f'{stance} {"release" if st == "attack" and stance != "1h" else st}', fill=(90, 70, 60))
        if not loadout:
            d.text((X0 + 6, Y0 + 24), 'new pose -\nsee the prompt', fill=(150, 60, 50))
        if p and os.path.exists(p):
            s = Image.open(p).convert('RGBA'); s = s.crop(s.getbbox())
            k = min((X1 - X0 - 8) / s.width, (Y1 - Y0 - 18) / s.height)
            s = s.resize((max(1, round(s.width * k)), max(1, round(s.height * k))), Image.LANCZOS)
            im.paste(s, (X0 + (X1 - X0 - s.width) // 2, Y1 - s.height - 3), s)
    os.makedirs(os.path.join(HERE, 'refs'), exist_ok=True)
    im.save(os.path.join(HERE, 'refs', f'{cls}_{sex}_ref.png'))


def ammo_template():
    """Archer back equipment: 3 x 2 cells (quiver full / partial / empty, bolt case full / partial / empty), each with a
    vertical guide showing the container's length (top tick and bottom tick)."""
    im = Image.new('RGB', (W, H), GREEN); d = ImageDraw.Draw(im)
    cw, ch = W // 3, H // 2
    for r in range(2):
        for c in range(3):
            x0, y0 = c * cw, r * ch
            d.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], outline=LINE, width=2)
            cx, t, b = x0 + cw // 2, y0 + round(ch * 0.12), y0 + round(ch * 0.88)
            for y in range(t, b, 20): d.line([cx - 110, y, cx - 110, y + 10], fill=TOP, width=2)
            d.line([cx - 125, t, cx - 95, t], fill=GROUND, width=3); d.line([cx - 125, b, cx - 95, b], fill=GROUND, width=3)
    im.save(os.path.join(HERE, 'templates', 'archer_ammo_template.png'))


if __name__ == '__main__':
    ammo_template()
    for cls in CLASSES:
        template(cls)
        for nm, rows_x in EXTRA_SHEETS.get(cls, {}).items(): template(cls, rows_x, f'{cls}_{nm}')
        for sex in 'mf': ref(cls, sex)
    print('ok')
