"""Acolyte pose drafts (user, 2026-11-26): calmer priest stances, not the Soldier's. One sheet per stance, 2 x 3 cells of
512: stand | ready | attack / hit | channel | cast.
Weapon attacks = prepare (ready) + attack; spells and cantrips = channel + cast, with the held weapon raised as the holy
focus (user's choice); the far arm keeps what it has (round shield / open hand). Stances (user's picks): one-handed +
round shield, one-handed without shield (off-hand open), two-handed staff, reach (longspear). (Crossbow dropped 2026-11-27:
crossbows are Archer-only.)
Mannequins as for the Archer (archer_pose_draft.draw): NEAR arm darker, FAR arm lighter, hood up, face in the yellow key.
Output: refs/acolyte_<stance>_pose_draft.png on templates/acolyte_<stance>_template.png. Cell coords 384 x 512 (+64)."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, 'tools')); sys.path.insert(0, HERE)
import archer_pose_draft as A
import make_refs as M
A.HOOD = (232, 228, 214)                                # white hood
MAG = A.MAG
STAND = dict(head=(198, 108), Sn=(166, 160), Sf=(212, 156), Hn=(176, 277), Hf=(208, 272), Kn=(164, 372), Fn=(156, 466),
             Kf=(222, 370), Ff=(240, 466))
STEP = dict(head=(210, 116), Sn=(176, 166), Sf=(222, 162), Hn=(180, 282), Hf=(212, 278), Kn=(152, 374), Fn=(132, 466),
            Kf=(246, 368), Ff=(262, 466))                         # a calm step forward, not a lunge
BRACE = dict(head=(194, 112), Sn=(162, 164), Sf=(208, 160), Hn=(174, 280), Hf=(206, 276), Kn=(156, 374), Fn=(140, 466),
             Kf=(232, 372), Ff=(252, 466))
RECOIL = dict(A.RECOIL)
UPWARD = dict(head=(200, 104), Sn=(166, 158), Sf=(212, 154), Hn=(176, 277), Hf=(208, 272), Kn=(164, 372), Fn=(156, 466),
              Kf=(222, 370), Ff=(240, 466))                       # channel: upright, chin up
LEAN = dict(head=(208, 112), Sn=(174, 162), Sf=(220, 158), Hn=(180, 280), Hf=(212, 276), Kn=(158, 372), Fn=(146, 466),
            Kf=(238, 370), Ff=(254, 466))                         # cast: leaning toward the target
MACE_LOW = dict(En=(150, 226), Wn=(158, 284), rods=[('near', MAG, (150, 304), (178, 226))])
MACE_UP = dict(En=(150, 140), Wn=(168, 88), rods=[('near', MAG, (176, 102), (136, 34))])       # wound up over the head
MACE_DOWN = dict(En=(206, 200), Wn=(256, 236), rods=[('near', MAG, (244, 224), (304, 294))])   # struck down in front
MACE_HIT = dict(En=(132, 226), Wn=(126, 280), rods=[('near', MAG, (134, 262), (102, 334))])
# spell frames with a one-handed weapon (user, 2026-11-27: the raised / pointed mace looked like a wand): the mace is held
# upright against the chest like a holy symbol, head bowed; for the cast the off hand thrusts forward (shield: raised)
PRAY = dict(head=(206, 116), Sn=(168, 162), Sf=(214, 158), Hn=(176, 277), Hf=(208, 272), Kn=(164, 372), Fn=(156, 466),
            Kf=(222, 370), Ff=(240, 466))
MACE_CHEST = dict(En=(170, 236), Wn=(200, 206), rods=[('near', MAG, (200, 236), (200, 146))])

SHIELD = {
    (0, 0): dict(STAND, **MACE_LOW, Ef=(238, 212), Wf=(254, 232), shield=(262, 228, 46)),
    (0, 1): dict(BRACE, **MACE_UP, Ef=(236, 206), Wf=(254, 220), shield=(262, 214, 46)),
    (0, 2): dict(STEP, **MACE_DOWN, Ef=(248, 216), Wf=(262, 252), shield=(272, 250, 46)),
    (1, 0): dict(RECOIL, **MACE_HIT, Ef=(220, 218), Wf=(236, 204), shield=(244, 204, 46)),
    (1, 1): dict(PRAY, **MACE_CHEST, Ef=(240, 214), Wf=(258, 240), shield=(268, 240, 44)),
    (1, 2): dict(LEAN, En=(178, 238), Wn=(208, 208), rods=[('near', MAG, (208, 238), (208, 148))], Ef=(248, 192), Wf=(266, 200), shield=(276, 196, 46)),
}
ONE = {
    (0, 0): dict(STAND, **MACE_LOW, Ef=(236, 222), Wf=(244, 276), open_far=True),
    (0, 1): dict(BRACE, **MACE_UP, Ef=(242, 202), Wf=(274, 196), open_far=True),
    (0, 2): dict(STEP, **MACE_DOWN, Ef=(222, 226), Wf=(212, 268), open_far=True),
    (1, 0): dict(RECOIL, **MACE_HIT, Ef=(222, 222), Wf=(250, 250), open_far=True),
    (1, 1): dict(PRAY, **MACE_CHEST, Ef=(234, 224), Wf=(240, 276), open_far=True),
    (1, 2): dict(LEAN, En=(178, 238), Wn=(208, 208), rods=[('near', MAG, (208, 238), (208, 148))], Ef=(256, 176), Wf=(300, 166), open_far=True),
}
STAFF = {
    (0, 0): dict(STAND, En=(172, 224), Wn=(198, 216), Ef=(232, 230), Wf=(214, 258), rods=[('both', MAG, (198, 80), (222, 440))]),
    (0, 1): dict(BRACE, En=(150, 132), Wn=(176, 104), Ef=(232, 132), Wf=(204, 94), rods=[('both', MAG, (250, 66), (84, 150))]),
    (0, 2): dict(STEP, En=(190, 210), Wn=(216, 240), Ef=(244, 214), Wf=(248, 252), rods=[('both', MAG, (166, 222), (342, 310))]),
    (1, 0): dict(RECOIL, En=(136, 214), Wn=(150, 250), Ef=(214, 204), Wf=(196, 214), rods=[('both', MAG, (116, 286), (236, 156))]),
    (1, 1): dict(UPWARD, En=(182, 200), Wn=(206, 182), Ef=(236, 202), Wf=(216, 214), rods=[('both', MAG, (204, 34), (222, 382))]),
    (1, 2): dict(LEAN, En=(198, 188), Wn=(222, 190), Ef=(246, 182), Wf=(254, 176), rods=[('both', MAG, (166, 214), (342, 140))]),
}
REACH = {
    (0, 0): dict(STAND, En=(150, 232), Wn=(168, 262), Ef=(228, 214), Wf=(236, 256), rods=[('both', MAG, (60, 268), (380, 248))]),
    (0, 1): dict(BRACE, En=(140, 236), Wn=(140, 268), Ef=(214, 220), Wf=(196, 256), rods=[('both', MAG, (10, 282), (344, 244))]),
    (0, 2): dict(STEP, En=(190, 218), Wn=(206, 238), Ef=(248, 204), Wf=(270, 226), rods=[('both', MAG, (100, 250), (440, 208))]),
    (1, 0): dict(RECOIL, En=(132, 226), Wn=(146, 262), Ef=(210, 214), Wf=(204, 236), rods=[('both', MAG, (60, 306), (334, 176))]),
    (1, 1): dict(UPWARD, En=(180, 214), Wn=(204, 226), Ef=(234, 192), Wf=(214, 182), rods=[('both', MAG, (196, 430), (222, 12))]),
    (1, 2): dict(LEAN, En=(186, 204), Wn=(206, 200), Ef=(242, 184), Wf=(250, 178), rods=[('both', MAG, (110, 246), (390, 104))]),
}
SHEETS = {'shield': SHIELD, '1h': ONE, 'staff': STAFF, 'reach': REACH}   # no crossbow (Archer-only, user 2026-11-27)

if __name__ == '__main__':
    for name, poses in SHEETS.items():
        M.template('acolyte', M.EXTRA_SHEETS['acolyte'][name], f'acolyte_{name}')
        im = Image.open(os.path.join(HERE, 'templates', f'acolyte_{name}_template.png')).convert('RGB'); d = ImageDraw.Draw(im)
        for (r, c), P in poses.items(): A.draw(d, P, c * 512 + 64, r * 512)
        out = os.path.join(HERE, 'refs', f'acolyte_{name}_pose_draft.png'); im.save(out); print(out)
