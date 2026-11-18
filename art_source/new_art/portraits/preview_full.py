"""Assemble complete portraits from every new layer (head, body, eyes, brows, mouth, hair) with random looks.
Layer order, back to front: head skin, body skin, body, eyes fixed, iris, brows, mouth, hair.
Writes preview_full.png (2 rows: male, female; one column per class)."""
import os, json, random, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..', '..')
pal = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
hx = lambda q: [int(q[i:i + 2], 16) for i in (1, 3, 5)]
def tint(path, ramp):
    img = np.asarray(Image.open(path).convert('RGBA'))
    rr = np.array([hx(q) for q in ramp], float); t = img[..., 0] / 255 * (len(rr) - 1)
    l = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - l)[..., None]
    return Image.fromarray(np.dstack([rr[l] * (1 - f) + rr[l + 1] * f, img[..., 3]]).astype(np.uint8))
def styles(prefix, suffix='.png'):
    return sorted(f[len(prefix):-len(suffix)] for f in os.listdir(HERE) if f.startswith(prefix) and f.endswith(suffix))
rng = random.Random(7)
P = lambda n: os.path.join(HERE, n)
sheet = Image.new('RGBA', (200 * 6, 400), (52, 56, 66, 255))
for row, sex in enumerate('mf'):
    for col, cls in enumerate(['soldier', 'archer', 'cleric', 'mage', 'warrior', 'rogue']):
        skin = rng.choice(list(pal['skin'].values())); hair = rng.choice(list(pal['hair'].values()))
        eye = rng.choice(list(pal['eyes'].values()))
        ey = rng.choice(styles(f'{sex}_eyes_', '_fixed.png')); hs = rng.choice(styles(f'{sex}_hair_'))
        ex = rng.choice(['neutral', 'smile', 'stern', 'grin', 'sleepy', 'worried'])
        c = Image.new('RGBA', (200, 200), (52, 56, 66, 255))
        c.alpha_composite(tint(P(f'{sex}_head_skin.png'), skin))
        if os.path.exists(P(f'{sex}_body_{cls}_skin.png')): c.alpha_composite(tint(P(f'{sex}_body_{cls}_skin.png'), skin))
        c.alpha_composite(Image.open(P(f'{sex}_body_{cls}_fixed.png')).convert('RGBA'))
        c.alpha_composite(Image.open(P(f'{sex}_eyes_{ey}_fixed.png')).convert('RGBA'))
        c.alpha_composite(tint(P(f'{sex}_eyes_{ey}_iris.png'), eye))
        c.alpha_composite(tint(P(f'{sex}_brows_{ex}.png'), hair))
        c.alpha_composite(Image.open(P(f'{sex}_mouth_{ex}.png')).convert('RGBA'))
        c.alpha_composite(tint(P(f'{sex}_hair_{hs}.png'), hair))
        sheet.paste(c, (col * 200, row * 200))
sheet.save(P('preview_full.png'))
