"""Give the base heads a readable nose (the ChatGPT heads only had a faint bridge highlight, invisible in game).
Edits the skin value maps in place: brighter tip highlight, a dark under-tip / nostril accent and a soft side shade.
Values are skin-ramp values, so the nose is the right shade on every skin tone. Run once after process_heads.py
(re-running is safe: it writes fixed values, not offsets).
"""
import os, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
# (x, y): value.  Light from the left: the tip catches light, the underside and nostril sit in shadow.
NOSE = {
    # tip highlight, side line down the shaded side of the bridge, dark under-tip / nostril accent
    'm': {(127, 102): 238, (128, 102): 238, (127, 103): 238, (128, 103): 232, (127, 98): 99, (128, 99): 90, (128, 100): 87, (129, 101): 84, (129, 102): 81, (129, 103): 72, (128, 104): 90, (129, 104): 43, (127, 105): 52, (128, 105): 37, (126, 105): 90, (126, 106): 105},
    'f': {(125, 101): 238, (126, 101): 238, (125, 102): 238, (126, 102): 232, (126, 97): 102, (126, 98): 96, (127, 99): 90, (127, 100): 87, (127, 101): 84, (127, 102): 75, (126, 103): 90, (127, 103): 46, (125, 104): 55, (126, 104): 39, (124, 104): 93, (124, 105): 106},
}
def main():
    for sex, px in NOSE.items():
        p = os.path.join(HERE, f'{sex}_head_skin.png')
        a = np.asarray(Image.open(p)).copy()
        for (x, y), v in px.items():
            assert a[y, x, 3] > 0
            a[y, x, :3] = v
        Image.fromarray(a).save(p)
        print(sex, len(px), 'nose pixels')
if __name__ == '__main__':
    main()
