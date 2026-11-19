"""Portrait finish step: put the layers together and blend them into one painted portrait.

The parts are drawn separately (head, outfit, eyes, brows, mouth, hair), so stacked as-is they look pasted on.
compose() stacks them in the game's order and, with finish=True, runs the passes below. Everything works on the
layers' own value maps, so a shadow on skin is the same skin ramp one step darker (correct hue for every tone).
The game will run the same passes once when a hero's portrait is built and cache the result.

  1 lines   eye, lash and mouth lines take the skin's darkest shade instead of fixed near-black
  2 whites  eye whites (and teeth) become a warm off-white from the skin ramp; 1-px shadow under the upper lid
  3 brows   darker hair shade on the lower edge of thick brows
  4 hair    hair edge on skin uses the hair's own dark shade; hair casts a 1-2 px shadow onto the skin
  5 neck    contact shadow on the skin just above the collar / scarf / armour
  6 outline one outer silhouette outline (dark version of the fill colour); seams where the outfit meets skin or
            hair use a dark shade of the outfit's own colour instead of black
  7 grade   shared light: soft warm light from the upper left, shadows pulled toward one cool hue
"""
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
PAL = json.load(open(os.path.join(ROOT, 'portraits', 'palettes.json')))
LINE, WHITE = (30, 22, 26), (250, 248, 246)
N4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def hx(q): return [int(q[i:i + 2], 16) for i in (1, 3, 5)]


def ramp_rgb(ramp, v):
    """Value map (0-255, any shape) -> RGB along the 5-colour ramp, same as the game's tint."""
    rr = np.array([hx(q) for q in ramp], float); t = np.clip(v, 0, 255) / 255 * (len(rr) - 1)
    lo = np.floor(t).astype(int).clip(0, len(rr) - 2); f = (t - lo)[..., None]
    return rr[lo] * (1 - f) + rr[lo + 1] * f


def load(name):
    p = os.path.join(HERE, name)
    return np.asarray(Image.open(p).convert('RGBA')).astype(float) if os.path.exists(p) else None


def is_col(a, c, tol=3): return (np.abs(a[..., :3] - c).max(-1) <= tol) & (a[..., 3] > 0)


def shift(m, dy, dx):
    o = np.zeros_like(m)
    ys, yd = (slice(0, 200 - dy), slice(dy, 200)) if dy >= 0 else (slice(-dy, 200), slice(0, 200 + dy))
    xs, xd = (slice(0, 200 - dx), slice(dx, 200)) if dx >= 0 else (slice(-dx, 200), slice(0, 200 + dx))
    o[yd, xd] = m[ys, xs]; return o


def compose(sex, cls, skin, hair_ramp, eye_ramp, eyes, expr, hair, finish=True, nose=None):
    """skin/hair_ramp/eye_ramp: palette names. eyes/expr/hair/nose: style ids. Returns a 200x200 RGBA uint8 array.
    The nose is a skin value map drawn right over the head skin (it counts as skin for every pass)."""
    S, Hr, E = PAL['skin'][skin], PAL['hair'][hair_ramp], PAL['eyes'][eye_ramp]
    nl = load(f'{sex}_nose_{nose}.png') if nose else None
    head, bskin, body = load(f'{sex}_head_skin.png'), load(f'{sex}_body_{cls}_skin.png'), load(f'{sex}_body_{cls}_fixed.png')
    efix, iris = load(f'{sex}_eyes_{eyes}_fixed.png'), load(f'{sex}_eyes_{eyes}_iris.png')
    brow, mouth, hl = load(f'{sex}_brows_{expr}.png'), load(f'{sex}_mouth_{expr}.png'), load(f'{sex}_hair_{hair}.png')

    rgb = np.zeros((200, 200, 3)); A = np.zeros((200, 200), bool)
    top = np.zeros((200, 200), 'U5')                       # which layer is on top: skin, body, eyes, iris, brow, mouth, hair
    sv = np.zeros((200, 200))                               # skin value map under everything
    bv = np.zeros((200, 200)); hv = np.zeros((200, 200))    # brow / hair value maps
    def put(layer, colour, tag):
        m = layer[..., 3] > 127
        rgb[m] = colour[m]; A[m] = True; top[m] = tag
        return m
    for sk in (head, nl, bskin):
        if sk is not None:
            m = put(sk, ramp_rgb(S, sk[..., 0]), 'skin'); sv[m] = sk[..., 0][m]
    put(body, body[..., :3], 'body')
    put(efix, efix[..., :3], 'eyes'); put(iris, ramp_rgb(E, iris[..., 0]), 'iris')
    m = put(brow, ramp_rgb(Hr, brow[..., 0]), 'brow'); bv[m] = brow[..., 0][m]
    put(mouth, mouth[..., :3], 'mouth')
    m = put(hl, ramp_rgb(Hr, hl[..., 0]), 'hair'); hv[m] = hl[..., 0][m]
    if not finish:
        return np.dstack([rgb, A * 255]).astype(np.uint8)

    skin_m, hair_m, body_m = top == 'skin', top == 'hair', top == 'body'
    sk = lambda v: ramp_rgb(S, v)

    # 1 lines -> darkest skin shade (a touch above the outline's own value so they still read on deep skin)
    line_c = sk(np.full((1,), 14.0))[0]
    for lay, tag in ((efix, 'eyes'), (mouth, 'mouth')):
        m = is_col(lay, LINE, 12) & (top == tag); rgb[m] = line_c
    # 2 whites -> warm off-white from the lightest skin colour; shadow under the upper lid
    white_c = 0.78 * np.array([247, 244, 240.]) + 0.22 * np.array(hx(S[4]))
    lid_c = 0.55 * white_c + 0.45 * np.array(hx(S[3]))
    wm = is_col(efix, WHITE, 6) & (top == 'eyes'); rgb[wm] = white_c
    lid = wm & shift(is_col(efix, LINE, 12), 1, 0); rgb[lid] = lid_c
    tm = is_col(mouth, WHITE, 6) & (top == 'mouth'); rgb[tm] = white_c
    # 3 brows: lower edge one hair shade darker where the brow is 2+ px thick
    bm = top == 'brow'
    low = bm & ~shift(bm, -1, 0) & shift(bm, 1, 0)
    rgb[low] = ramp_rgb(Hr, bv[low] * 0.55)

    # 4 hair on skin: edge in the hair's own dark shade; cast shadow (light from upper left) + contact shadow
    near_skin = ndi.binary_dilation(skin_m, N4)
    edge = hair_m & near_skin
    rgb[edge] = ramp_rgb(Hr, np.maximum(hv[edge], 40))
    cast = skin_m & (shift(hair_m, 1, 1) | shift(hair_m, 2, 1) | shift(hair_m, 2, 2))
    touch = skin_m & ndi.binary_dilation(hair_m, N4)
    # 5 neck: contact shadow on skin right above (and beside) the outfit
    collar1 = skin_m & (shift(body_m, -1, 0) | ndi.binary_dilation(body_m, N4))
    collar2 = skin_m & shift(body_m, -2, 0) & ~collar1
    dark = np.zeros((200, 200))
    dark[collar2] = 22; dark[collar1] = 40; dark[cast] = np.maximum(dark[cast], 34); dark[touch] = np.maximum(dark[touch], 44)
    # keep the drawn outline pixels (already the darkest value) as they are
    sh = skin_m & (dark > 0) & (sv > 60)
    rgb[sh] = sk(np.maximum(sv[sh] - dark[sh], 45))

    # 6 outline: seams of the outfit against skin / hair -> dark outfit colour; outer silhouette -> dark fill colour
    lum = rgb @ [0.3, 0.59, 0.11]
    body_fill = body_m & (lum > 70)
    if body_fill.any():
        idx = ndi.distance_transform_edt(~body_fill, return_distances=False, return_indices=True)
        seam = body_m & (lum <= 70) & ndi.binary_dilation(skin_m | hair_m, N4)
        rgb[seam] = rgb[idx[0][seam], idx[1][seam]] * 0.42
    outer = A & ~ndi.binary_erosion(A, N4)
    fill = A & ~outer & (lum > 70)
    idx = ndi.distance_transform_edt(~fill, return_distances=False, return_indices=True)
    rgb[outer] = rgb[idx[0][outer], idx[1][outer]] * 0.24 + np.array([18, 13, 24.]) * 0.6

    # 7 grade: warm light from the upper left, shadows toward one cool hue
    yy, xx = np.mgrid[:200, :200]
    light = 1.04 - 0.08 * (xx + yy) / 300
    lum = (rgb @ [0.3, 0.59, 0.11]) / 255
    rgb = rgb * light[..., None]
    rgb = rgb + ((1 - lum) ** 2 * 0.10)[..., None] * (np.array([58, 48, 92.]) - rgb)
    rgb = rgb + (lum ** 2 * 0.07)[..., None] * (np.array([255, 238, 212.]) - rgb)
    return np.dstack([np.clip(rgb, 0, 255) * A[..., None], A * 255]).astype(np.uint8)


if __name__ == '__main__':
    # before / after sheet: per class, male then female, unfinished and finished side by side
    import random
    rng = random.Random(11)
    def styles(prefix, suffix='.png'):
        return sorted(f[len(prefix):-len(suffix)] for f in os.listdir(HERE) if f.startswith(prefix) and f.endswith(suffix))
    classes = ['soldier', 'archer', 'cleric', 'mage', 'warrior', 'rogue']
    sheet = Image.new('RGBA', (200 * 6, 200 * 4), (52, 56, 66, 255))
    for r, sex in enumerate('mf'):
        for c, cls in enumerate(classes):
            args = (sex, cls, rng.choice(list(PAL['skin'])), rng.choice(list(PAL['hair'])), rng.choice(list(PAL['eyes'])),
                    rng.choice(styles(f'{sex}_eyes_', '_fixed.png')), rng.choice(['neutral', 'smile', 'stern', 'grin', 'sleepy', 'worried']),
                    rng.choice(styles(f'{sex}_hair_')))
            nz = rng.choice(styles(f'{sex}_nose_'))
            for k, fin in enumerate((False, True)):
                im = Image.fromarray(compose(*args, finish=fin, nose=nz))
                sheet.alpha_composite(im, (c * 200, (r * 2 + k) * 200))
    sheet.save(os.path.join(HERE, 'preview_finish.png'))
    print('preview_finish.png')
