"""Assemble complete portraits from every new layer (head, body, eyes, brows, mouth, hair) with random looks,
finished with finish.py (the blend pass the game runs when it builds a portrait).
Layer order, back to front: head skin, body skin, body, eyes fixed, iris, brows, mouth, hair.
Writes preview_full.png (2 rows: male, female; one column per class)."""
import os, random
from PIL import Image
from finish import compose, PAL, HERE
def styles(prefix, suffix='.png'):
    return sorted(f[len(prefix):-len(suffix)] for f in os.listdir(HERE) if f.startswith(prefix) and f.endswith(suffix))
rng = random.Random(7)
sheet = Image.new('RGBA', (200 * 6, 400), (52, 56, 66, 255))
for row, sex in enumerate('mf'):
    for col, cls in enumerate(['soldier', 'archer', 'cleric', 'mage', 'warrior', 'rogue']):
        im = compose(sex, cls, rng.choice(list(PAL['skin'])), rng.choice(list(PAL['hair'])), rng.choice(list(PAL['eyes'])),
                     rng.choice(styles(f'{sex}_eyes_', '_fixed.png')),
                     rng.choice(['neutral', 'smile', 'stern', 'grin', 'sleepy', 'worried']), rng.choice(styles(f'{sex}_hair_')))
        sheet.alpha_composite(Image.fromarray(im), (col * 200, row * 200))
sheet.save(os.path.join(HERE, 'preview_full.png'))
