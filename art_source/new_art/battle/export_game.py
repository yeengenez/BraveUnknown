"""Exports battle sprites for the game (Godot, branch main: res://sprites/battle/).

Same frames as process_battle.py render() (same cut bodies, grips, weapons drawn in code, feet aligned),
but instead of baking one sample skin and hair colour, each frame keeps the hero-specific pixels marked:

    alpha 254 -> skin   (value in R; the game tints it with the hero's portrait skin ramp)
    alpha 253 -> hair   (value in R; the hair piece under the helmet, tinted with the hero's hair ramp,
                         shown only for long portrait hairstyles, see hair_length.json)
    alpha 255 -> fixed colours, alpha 0 -> empty

The user's drawn slash arc + weapon smear (dual slash frames) is written as a separate soft-alpha layer
<frame>_fx.png on the same canvas, so its blending never touches the marked pixels.

    python3 export_game.py <game repo> [class]

Writes <game>/sprites/battle/<class>/<sex>_<loadout>_<state>.png (+ _fx.png) and <class>.json.
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import process_battle as PB
A = PB.A

# Loadouts the game uses (weapons all drawn in code; no Legacy Canva weapon art).
# (name, stance, items) as in process_battle.LOADOUTS; one weapon in the dual stance = main hand only.
GAME_LOADOUTS = {
    'soldier': [
        ('sword_shield', '1h', {s: [('back', 'sword', 'over')] for s in ('stand', 'attack', 'hit')}),
        ('dual_shortswords', 'dual', {s: [('front', 'shortsword', 'over'), ('back', 'shortsword', 'over')]
                                      for s in ('stand', 'attack', 'hit')}),
        ('greatsword', '2h', {s: [('back', 'greatsword', 'over')] for s in ('stand', 'attack', 'hit')}),
        ('greataxe', '2h', {s: [('back', 'greataxe', 'over')] for s in ('stand', 'attack', 'hit')}),
        ('spear', 'reach', {s: [('back', 'longspear', 'over')] for s in ('stand', 'attack', 'hit')}),
    ],
}
ORDER = ['stand', 'ready', 'attack', 'attack2', 'slash_left', 'slash_right', 'finish', 'hit']
SKIN_A, HAIR_A = 254, 253


def keyed_body(fixed, skin, hairp):
    """Body image with skin and hair pixels marked by alpha (value kept in R)."""
    b = fixed.copy()
    b[b[..., 3] > 0, 3] = 255
    m = skin[..., 1] > 0
    b[m, 0] = skin[..., 0][m]; b[m, 1] = 0; b[m, 2] = 0; b[m, 3] = SKIN_A
    if hairp is not None:
        h = hairp[..., 1] > 0
        b[h, 0] = hairp[..., 0][h]; b[h, 1] = 0; b[h, 2] = 0; b[h, 3] = HAIR_A
    return b


def export(cls, game):
    data = PB.process(cls)
    out_dir = os.path.join(game, 'sprites', 'battle', cls)
    os.makedirs(out_dir, exist_ok=True)
    manifest = {'canvas': [A.CW_, A.CH_], 'feet': list(PB.CANVAS_FEET), 'skin_alpha': SKIN_A, 'hair_alpha': HAIR_A,
                'hair_long': {s: PB.HAIR_LEN[s]['long'] for s in 'mf'}, 'loadouts': {}}
    count = 0
    for load, stance, items in GAME_LOADOUTS[cls]:
        entry = {'stance': stance, 'sexes': {}}
        for sex in 'mf':
            if not any(k[0] == sex and k[1] == stance for k in data):
                continue
            sts = [t for t in ORDER if (sex, stance, t) in data]
            if not any(w for h_, w, _ in items['attack'] if h_ == 'front'):
                sts = [t for t in sts if t not in ('attack2', 'slash_left')] if 'slash_right' not in sts else \
                      [t for t in sts if t not in ('ready', 'slash_left')]
            ref = None
            states = []
            for state in sts:
                its = items.get(state) or items['attack']
                fixed, skin, g, head, hairp = data[(sex, stance, state)]
                b = keyed_body(fixed, skin, hairp)
                fx_, fy = PB.feet(b)
                if ref is None:
                    ref = (PB.CANVAS_FEET[0] - fx_, PB.CANVAS_FEET[1] - fy)
                dx = round(ref[0]) - A.CELL; dy = round(ref[1]) - A.TOP
                g2 = PB.split2h(g) if stance != 'dual' else dict(g)
                hide, kind = PB.SLASH_HIDE.get(state, (None, None))
                hidden = [w for h_, w, _ in its if h_ == hide]
                im = A.frame(cls, f'{sex}_{stance}', 'fair', [i for i in its if i[0] != hide],
                             (dx, dy, 0, 0, None), [], 'attack', g2, b)
                name = f'{sex}_{load}_{state}'
                fx_file = None
                if hidden:
                    fxl = PB.FX_LAYERS.get((sex, stance, state))
                    if fxl is not None:
                        lay = np.zeros((A.CH_, A.CW_, 4), np.uint8)
                        o_ = Image.new('RGBA', (A.CW_, A.CH_)); o_.alpha_composite(Image.fromarray(fxl), (int(A.CELL + dx), int(A.TOP + dy)))
                        o_.save(os.path.join(out_dir, name + '_fx.png'), optimize=True); fx_file = name + '_fx.png'
                    elif hide in g2:
                        p, ang = g2[hide]['point'], g2[hide]['angle']
                        im = PB.slash_wave(im, kind, (A.CELL + dx + p[0], A.TOP + dy + p[1]), ang, A.WEAPON[hidden[0]](ang)[2])
                Image.fromarray(np.ascontiguousarray(im)).save(os.path.join(out_dir, name + '.png'), optimize=True)
                states.append({'state': state, 'file': name + '.png', 'fx': fx_file})
                count += 1
            entry['sexes'][sex] = states
        manifest['loadouts'][load] = entry
    with open(os.path.join(game, 'sprites', 'battle', cls + '.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    print(count, 'frames ->', out_dir)


if __name__ == '__main__':
    export(sys.argv[2] if len(sys.argv) > 2 else 'soldier', os.path.abspath(sys.argv[1]))
