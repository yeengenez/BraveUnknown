"""Reference compositor: builds a portrait from the parts library and a hero record."""
import numpy as np, cv2, json, random

LIB = 'library'
PAL = json.load(open('palettes.json'))

def part(name): return cv2.imread(f'{LIB}/{name}.png', cv2.IMREAD_UNCHANGED)

def ramp_map(value_rgba, ramp):
    """Color a grayscale value map with a ramp of hex colors (dark -> light)."""
    cols = np.array([[int(c[i:i + 2], 16) for i in (5, 3, 1)] for c in ramp], np.float32)   # BGR
    v = value_rgba[..., 0].astype(np.float32) / 255 * (len(cols) - 1)
    i0 = np.clip(np.floor(v).astype(int), 0, len(cols) - 2); t = (v - i0)[..., None]
    out = cols[i0] * (1 - t) + cols[i0 + 1] * t
    return np.dstack([out.astype(np.uint8), value_rgba[..., 3]])

def over(dst, src):
    a = src[..., 3:4].astype(np.float32) / 255
    dst[..., :3] = (src[..., :3] * a + dst[..., :3] * (1 - a)).astype(np.uint8)
    dst[..., 3] = np.maximum(dst[..., 3], src[..., 3])

def compose(hero, bg=None):
    S = 200
    img = np.zeros((S, S, 4), np.uint8)
    if bg is not None: img[...] = (*bg[::-1], 255)
    skin, hair, eyes = PAL['skin'][hero['skin']], PAL['hair'][hero['hair_color']], PAL['eyes'][hero['eyes']]
    b, f = f"{hero['body']}_body_{hero['class']}", f"{hero['body']}_face_{hero['face']}"
    over(img, part(b + '_fixed')); over(img, ramp_map(part(b + '_skin'), skin))
    over(img, ramp_map(part(f + '_skin'), skin)); over(img, part(f + '_fixed')); over(img, ramp_map(part(f + '_iris'), eyes))
    for d in hero.get('details', []): over(img, ramp_map(part(f"{hero['body']}_detail_{d}"), skin))
    if hero.get('hair'): over(img, ramp_map(part(f"{hero['body']}_hair_{hero['hair']}"), hair))
    return img

def roll(rng=random, body=None):
    lib = json.load(open(f'{LIB}/library.json'))
    body = body or rng.choice(lib['body_types'])
    return {'body': body, 'class': rng.choice(lib['bodies']), 'skin': rng.choice(list(PAL['skin'])),
            'face': rng.choice(lib['faces']), 'hair': rng.choice(lib['hair'][body]), 'hair_color': rng.choice(list(PAL['hair'])),
            'eyes': rng.choice(list(PAL['eyes'])), 'details': ['scar'] if rng.random() < 0.15 else []}

if __name__ == '__main__':
    rng = random.Random(11); cols, S = 6, 200
    sheet = np.zeros((4 * S, cols * S, 4), np.uint8)
    for i in range(cols * 4):
        hero = roll(rng, body='m' if i < cols * 2 else 'f')
        sheet[(i // cols) * S:(i // cols + 1) * S, (i % cols) * S:(i % cols + 1) * S] = compose(hero, bg=(214, 196, 168))
    cv2.imwrite('contact_sheet.png', sheet)
