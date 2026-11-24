"""Downed-pose canvas: the dual template (2 x 3 cells of 512 on green) with the finished male and female STAND figures
in the bottom row as outfit / scale / colour-key reference. ChatGPT draws the downed poses in the empty top row
(cell 1 male, cell 2 female). Cells 3 and 6 stay empty."""
import os, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = np.asarray(Image.open(os.path.join(HERE, 'templates', 'soldier_dual_template.png')).convert('RGB')).copy()
H, W = t.shape[:2]; ch, cw = H // 2, W // 3
for col, sex in ((0, 'm'), (1, 'f')):
    s = Image.open(os.path.join(HERE, 'source', f'soldier_dual_{sex}_sheet.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    s = np.asarray(s)
    t[ch:2 * ch, col * cw:(col + 1) * cw] = s[0:ch, 0:cw]          # the sheet's STAND cell (top-left)
Image.fromarray(t).save(os.path.join(HERE, 'templates', 'soldier_downed_template.png'))
print('templates/soldier_downed_template.png', W, H)
