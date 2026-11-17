"""Writes the Aseprite pack: layer PNGs, meta.json and build_weapons.lua (into ./aseprite_pack)."""
import json, math, os, numpy as np
from PIL import Image, ImageDraw
import merge as M
from pixel_weapons import build, to_rgba
O = 'aseprite_pack'; os.makedirs(f'{O}/layers', exist_ok=True)
import merge2 as M2
W = build()
K = json.load(open('k_meta.json'))
W['sword'] = dict(img=M2.SWORD, grip=tuple(int(round(v)) for v in K['longsword']['grip']))   # longsword from image A (lies at its own angle)
W['shield'] = dict(img=M2.SHIELD[M2.SHIELD[..., 3].nonzero()[0].min():M2.SHIELD[..., 3].nonzero()[0].max() + 1,
                                  M2.SHIELD[..., 3].nonzero()[1].min():M2.SHIELD[..., 3].nonzero()[1].max() + 1], grip=(9, 22))
for n, w in W.items(): to_rgba(w['img']).save(f'{O}/layers/w_{n}.png')

def layers(key, lo):
    return M2.merge(key, lo)[1]

tests = []
for i, (key, lo) in enumerate(M.TESTS):
    for ln, a in layers(key, lo).items(): Image.fromarray(a).save(f'{O}/layers/t{i:02d}_{ln}.png')
    tests.append(f'{key.replace("/", "_")}_{lo.replace("+", "_")}')
cw, ch, cell = M.CELL * 3, M.CH + M.TOP, M.CELL
sq = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(sq)
for i in range(3): d.rectangle([i * cell, ch - 80, (i + 1) * cell - 1, ch - 2], fill=(212, 202, 178, 255) if i == 1 else (226, 218, 198, 255), outline=(170, 160, 140, 255))
sq.save(f'{O}/layers/squares.png')

wl = []; y = 2
for n, w in W.items():
    h, wd = w['img'].shape[:2]; g2 = w.get('grip2')
    wl.append('  {name="%s", w=%d, h=%d, y=%d, grip={%d,%d}%s}' % (n, wd, h, y, w['grip'][0], w['grip'][1], (', grip2={%d,%d}' % tuple(g2)) if g2 else ''))
    y += h + 6
tpl = open('build_weapons_template.lua').read()
lua = tpl.replace('@@WEAPONS@@', ',\n'.join(wl)).replace('@@TESTS@@', ',\n  '.join('"%s"' % t for t in tests)).replace('@@CW@@', str(cw)).replace('@@CH@@', str(ch))
open(f'{O}/build_weapons.lua', 'w').write(lua)
json.dump({'tests': tests, 'canvas': [cw, ch], 'cell': cell}, open(f'{O}/meta.json', 'w'), indent=1)
print('pack written', len(os.listdir(f'{O}/layers')), 'layers')
