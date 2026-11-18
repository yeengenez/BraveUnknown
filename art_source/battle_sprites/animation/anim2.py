"""Attack animations v2, in the spirit of the first reference animations: the arm moves WITH the weapon.
The attacking forearm and fist are cut out of the grip body as one part (the hole is refilled from the
neighbouring pixels), then swung about the elbow with the weapon locked in the fist; spears and punches push
the arms forward. The whole body leans and lunges, with a ground shadow and per-frame timing.
Attack and get-hit are separate animations."""
import sys, os, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import anim as A
import merge as M
CELL, TOP, CH, CW_, CH_ = A.CELL, A.TOP, A.CH, A.CW_, A.CH_

# ---------------- cutting the attacking arm(s) out of the body -----------------------------------------
def torso_center(b):
    m = b[..., 3] > 0; ys, xs = np.where(m); top, bot = ys.min(), ys.max()
    band = m & (np.arange(m.shape[0])[:, None] > top + (bot - top) * 0.18) & (np.arange(m.shape[0])[:, None] < top + (bot - top) * 0.45)
    yy, xx = np.where(band); return np.array([xx.mean(), yy.mean()])

def arm_part(b, fist, r_fist, length=15, width=4.5):
    """Mask of fist + forearm, and the elbow (pivot). The forearm runs from the fist toward the torso."""
    tc = torso_center(b); f = np.array(fist, float); d = tc - f; d /= np.linalg.norm(d) + 1e-9
    elbow = f + d * length
    yy, xx = np.mgrid[0:b.shape[0], 0:b.shape[1]]; P = np.stack([xx, yy], -1).astype(float)
    t = np.clip(((P - f) @ d) / length, 0, 1); near = f + t[..., None] * (elbow - f)[None, None]
    cap = np.linalg.norm(P - near, axis=-1) <= width
    disc = np.linalg.norm(P - f, axis=-1) <= r_fist + 3.5
    return (cap | disc) & (b[..., 3] > 0), elbow

def cut(b, mask):
    part = b.copy(); part[~mask] = 0
    rest = b.copy(); rest[mask] = 0
    sil = ndi.binary_closing(rest[..., 3] > 0, iterations=4)        # the body's own outline without the arm
    hole = mask & sil
    if hole.any():                                     # refill from the nearest remaining body pixels
        _, (iy, ix) = ndi.distance_transform_edt(~(rest[..., 3] > 0), return_indices=True)
        rest[hole] = rest[iy[hole], ix[hole]]
    return part, rest

def rot_part(part, pivot, deg):
    """Rotate a part (full-size RGBA) about pivot; returns (rgba, top-left offset)."""
    ys, xs = np.where(part[..., 3] > 0)
    if not len(xs): return part, (0, 0)
    x0, y0 = max(0, xs.min() - 2), max(0, ys.min() - 2); crop = part[y0:ys.max() + 3, x0:xs.max() + 3]
    pv = (pivot[0] - x0, pivot[1] - y0)
    if abs(deg) < 0.5: return crop, (x0, y0)
    r, npv = M.rotsprite(crop, pv, deg)
    return r, (pivot[0] - npv[0], pivot[1] - npv[1])

def rotp(p, c, deg):
    th = math.radians(deg); v = np.array(p, float) - c
    return c + np.array([math.cos(th) * v[0] - math.sin(th) * v[1], math.sin(th) * v[0] + math.cos(th) * v[1]])

# ---------------- motions -------------------------------------------------------------------------------
# key: dict(body=(dx,dy), tilt=deg (+ = lean back), arm=deg (swing about the elbow), push=px (arms forward
#      along the weapon), smear=bool, fx=..., dur=ms)
IDLE = dict(dur=220)
MOTION = {
 'slash': [IDLE, dict(body=(-3, 1), tilt=3, arm=-55, dur=200),
           dict(body=(9, 0), tilt=-3, arm=45, fx='arc', dur=80), dict(body=(10, 1), tilt=-4, arm=75, fx='arc2', dur=150),
           dict(body=(4, 0), tilt=-1, arm=20, dur=160), IDLE],
 'overhead': [IDLE, dict(body=(-3, 1), tilt=4, arm=-45, dur=210),
              dict(body=(9, 0), tilt=-3, arm=70, fx='arc', dur=80), dict(body=(10, 1), tilt=-4, arm=110, fx='arc2', dur=150),
              dict(body=(4, 0), tilt=-1, arm=25, dur=160), IDLE],
 'chop': [IDLE, dict(body=(-4, 1), tilt=5, arm=-40, dur=240),
          dict(body=(10, 1), tilt=-4, arm=40, fx='arc', dur=90), dict(body=(13, 3), tilt=-6, arm=62, fx='arc2', dur=180),
          dict(body=(5, 1), tilt=-2, arm=15, dur=170), IDLE],
 'thrust': [IDLE, dict(body=(-5, 0), tilt=3, push=-8, dur=220),
            dict(body=(11, 0), tilt=-3, push=16, fx='speed', dur=80), dict(body=(14, 0), tilt=-4, push=20, fx='speed2', dur=160),
            dict(body=(5, 0), tilt=-1, push=6, dur=160), IDLE],
 'punch': [IDLE, dict(body=(-3, 1), tilt=3, push=-4, dur=200),
           dict(body=(10, 0), tilt=-4, push=14, smear=True, fx='burst', dur=90), dict(body=(11, 0), tilt=-4, push=12, fx='ring', dur=150),
           dict(body=(4, 0), tilt=-1, push=3, dur=160), IDLE],
 'cast': [IDLE, dict(body=(-2, 0), tilt=3, arm=-35, fx='glow1', dur=220), dict(body=(-2, 0), tilt=3, arm=-40, fx='glow2', dur=200),
          dict(body=(5, 0), tilt=-3, arm=25, fx='shot0', dur=80), dict(body=(5, 0), tilt=-3, arm=25, fx='shot1', dur=80),
          dict(body=(3, 0), tilt=-1, arm=15, fx='shot2', dur=80), dict(body=(1, 0), arm=5, fx='shot3', dur=120), IDLE],
}
HIT = [IDLE, dict(body=(-5, 0), tilt=4, flash='white', fx='hitburst', dur=80), dict(body=(-8, 1), tilt=6, flash='red', dur=110),
       dict(body=(-5, 0), tilt=3, dur=120), dict(body=(-2, 0), tilt=1, dur=150), IDLE]

# class -> (loadout, stance, weapons [(hand, weapon, layer)], motion, attacking hands)
LOADOUTS = {
 'soldier': [('longsword', '1h', [('front', 'longsword', 'over')], 'slash', ['front']),
             ('sword_shield', '1h', [('back', 'longsword', 'under'), ('front', 'shield', 'over')], 'overhead', ['back']),
             ('greataxe', '2h', [('back', 'greataxe', 'over')], 'chop', ['back', 'front']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], 'thrust', ['back', 'front'])],
 'archer': [('bow', 'bow', [], 'shoot', []), ('dagger', '1h', [('front', 'dagger', 'over')], 'slash', ['front'])],
 'acolyte': [('mace_shield', '1h', [('back', 'mace', 'under'), ('front', 'shield', 'over')], 'overhead', ['back']),
             ('quarterstaff', '2h', [('back', 'quarterstaff', 'over')], 'chop', ['back', 'front']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], 'thrust', ['back', 'front'])],
 'mage': [('staff', '1h', [('front', 'staff', 'over')], 'cast', ['front'])],
 'brawler': [('unarmed', '1h', [], 'punch', ['front']), ('greataxe', '2h', [('back', 'greataxe', 'over')], 'chop', ['back', 'front']),
             ('longspear', 'reach', [('back', 'longspear', 'over')], 'thrust', ['back', 'front'])],
 'rogue': [('dual_daggers', '1h', [('front', 'dagger', 'over'), ('back', 'dagger', 'over')], 'slash', ['front'])],
}

# ---------------- rendering ---------------------------------------------------------------------------
def tilt_img(img, deg, center):
    if abs(deg) < 0.3: return img
    return np.asarray(Image.fromarray(img).rotate(deg, resample=Image.NEAREST, center=center))

def shadow(d, cx, by, a=60):
    d.ellipse([cx - 36, by - 5, cx + 36, by + 5], fill=(0, 0, 0, a))

def render_frame(ctx, f, anim):
    b, g, items, attackers = ctx['body'], ctx['grips'], ctx['items'], ctx['attackers']
    bx, by = f.get('body', (0, 0)); arm = f.get('arm', 0) if anim == 'attack' else 0; push = f.get('push', 0) if anim == 'attack' else 0
    char = np.zeros((CH_, CW_, 4), np.uint8); under = char.copy(); over = char.copy(); arms = char.copy()
    ox, oy = CELL + bx, TOP + by
    rest = ctx['rest'] if (arm or push) else b
    hands = {}                                                     # where each fist is this frame, and its weapon angle offset
    piv = ctx['pivot']
    for h in ('front', 'back'):
        if h not in g: continue
        p = np.array(g[h]['point'], float)
        if h in attackers and arm: p = rotp(p, piv, arm)
        if h in attackers and push:
            th = math.radians(ctx['push_dir']); p = p + push * np.array([math.cos(th), math.sin(th)])
        hands[h] = (p, arm if h in attackers else 0)
    # weapons
    for hand, wname, layer in items:
        p, da = hands[hand]
        if wname == 'shield':
            A.paste(over, A.SHIELD, ox + p[0] - A.SHIELD_FIST[0], oy + p[1] - A.SHIELD_FIST[1]); continue
        img, gp, L = A.WEAPON[wname](g[hand]['angle'] + da)
        behind = layer == 'under' or (attackers == ['back'] and hand == 'back' and (arm or push))
        A.paste(under if behind else over, img, ox + p[0] - gp[0], oy + p[1] - gp[1])
    far = attackers == ['back']                                     # the far arm swings behind the head and body
    # body (with the attacking arms cut out while they move), then the arms on top (or behind, for the far arm)
    if arm or push:
        part = ctx['arm_part']
        if arm:
            r, off = rot_part(part, piv, arm); A.paste(arms, r, ox + off[0], oy + off[1])
        else:
            th = math.radians(ctx['push_dir']); dv = push * np.array([math.cos(th), math.sin(th)])
            steps = np.linspace(0, 1, 5) if f.get('smear') else [1.0]
            for s in steps: A.paste(arms, part, ox + dv[0] * s, oy + dv[1] * s)    # smear = the arm stretching out
    if far and (arm or push):
        A.paste(char, under, 0, 0); A.paste(char, arms, 0, 0); A.paste(char, rest, ox, oy); A.paste(char, over, 0, 0)
    else:
        A.paste(char, under, 0, 0); A.paste(char, rest, ox, oy); A.paste(char, over, 0, 0)
        if arm or push: A.paste(char, arms, 0, 0)
    if not (arm or push):
                                                                    # idle: redraw fists over the handles
        fl = np.zeros_like(char)
        for hand, wname, layer in items:
            if wname == 'shield': continue
            m = A.fist(b, g[hand]['point'], max(4.5, g[hand]['fist_gap'] / 2)); blk = np.zeros_like(b); blk[m] = b[m]; A.paste(fl, blk, ox, oy)
        A.paste(char, fl, 0, 0)
    if f.get('flash'):
        col = np.array((255, 255, 255) if f['flash'] == 'white' else (235, 60, 50), float); k = 0.8 if f['flash'] == 'white' else 0.45
        m = char[..., 3] > 0; char[m, :3] = (char[m, :3] * (1 - k) + col * k).astype(np.uint8)
    feet = (ox + ctx['feet'][0], oy + ctx['feet'][1])
    char = tilt_img(char, f.get('tilt', 0), feet)
    frame = Image.new('RGBA', (CW_, CH_), (0, 0, 0, 0)); d = ImageDraw.Draw(frame, 'RGBA')
    shadow(d, feet[0], feet[1] + 1)
    fx = f.get('fx') if anim == 'attack' or f.get('fx') == 'hitburst' else None
    main = items[0] if items else None
    if fx in ('speed', 'speed2') and main:                          # speed lines behind the character
        p, _ = hands['front']; y = oy + p[1]
        for o in (-9, -4, 4, 9): d.line([(ox + p[0] - 110, y + o), (ox + p[0] - 30, y + o)], fill=(255, 255, 255, 150 if fx == 'speed' else 70))
    if fx in ('arc', 'arc2') and main:
        hand = attackers[0]; p, da = hands[hand]; L = A.WEAPON[main[1]](g[hand]['angle'] + da)[2]
        a1 = g[hand]['angle'] + da; span = 110 if fx == 'arc' else 60
        for k, (rr, al, w) in enumerate(((L * 0.98, 235, 4), (L * 0.85, 150, 3), (L * 0.7, 80, 2))):
            A.arc(d, (ox + p[0], oy + p[1]), rr, a1 - span, a1, col=(236, 246, 255) if fx == 'arc' else (200, 222, 244), w=w, alpha=al)
    frame.alpha_composite(Image.fromarray(char)); d = ImageDraw.Draw(frame, 'RGBA')
    if fx == 'speed' and main:
        p, _ = hands['front']; y = oy + p[1]
        if True:
            L = 120; tip = (ox + p[0] + L * math.cos(math.radians(g['front']['angle'])), y + L * math.sin(math.radians(g['front']['angle'])))
            A.burst(d, (tip[0] + 6, tip[1]), 10)
    if fx in ('burst', 'ring'):
        p, _ = hands['front']; c = (ox + p[0] + 10, oy + p[1])
        if fx == 'burst': A.burst(d, c, 14)
        else:
            for rr, col in ((10, (255, 255, 255, 200)), (16, (250, 216, 120, 160))): d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], outline=col, width=2)
    if fx and fx.startswith(('glow', 'shot')) and main:
        p, da = hands['front']; a = g['front']['angle'] + da; L = 54
        tip = (ox + p[0] + L * math.cos(math.radians(a)), oy + p[1] + L * math.sin(math.radians(a)))
        if fx.startswith('glow'): A.glow(d, tip, 5 if fx == 'glow1' else 9)
        else:
            k = int(fx[-1]); c = (tip[0] + 22 + k * 38, tip[1] + 8 + k * 5); A.glow(d, c, 8)
            d.line([(c[0] - 30, c[1]), (c[0] - 8, c[1])], fill=(200, 170, 255, 150), width=3)
    if fx == 'hitburst':
        A.burst(d, (ox + 70, oy + 60), 12)
    return np.asarray(frame)

SHOOT = [dict(fx='nock', dur=220), dict(body=(-1, 0), tilt=2, fx='nock', dur=260), dict(body=(-3, 0), tilt=1, fx='loose0', dur=70),
         dict(body=(-3, 0), fx='loose1', dur=70), dict(body=(-2, 0), fx='loose2', dur=70), dict(body=(-1, 0), fx='loose3', dur=90), dict(fx='nock', dur=220)]

def context(cls, sex, load, ramp):
    name, stance, items, motion, attackers = load
    key = f'{sex}_{stance}'; g = A.grips(cls, key); b = A.body(cls, key, ramp)
    ctx = dict(body=b, grips=g, items=items, attackers=attackers, motion=motion)
    ys, xs = np.where(b[..., 3] > 0); ctx['feet'] = (xs.mean(), ys.max())
    mask = np.zeros(b.shape[:2], bool); elbows = []
    for h in attackers:
        m, e = arm_part(b, g[h]['point'], max(4.5, g[h]['fist_gap'] / 2)); mask |= m; elbows.append(e)
    if attackers:
        part, rest = cut(b, mask); ctx['arm_part'], ctx['rest'] = part, rest
        ctx['pivot'] = np.mean(elbows, 0)
        ctx['push_dir'] = g['front']['angle'] if stance == 'reach' else 0.0
    return ctx

def render(cls, sex, load, ramp):
    ctx = context(cls, sex, load, ramp); motion = load[3]
    out = {}
    if motion == 'shoot':
        g = ctx['grips']; L = g['bow_rod']['bottom'] - g['bow_rod']['top']
        info = dict(length=L, bow=A.CW.bow(int(L), -90.0), arrow=A.CW.arrow(int(g['front']['point'][0] - g['back']['point'][0] + 14)), arrow_y=g['arrow']['y'])
        def bowframe(f):
            img = A.frame(cls, f'{sex}_bow', ramp, [], (f.get('body', (0, 0))[0], f.get('body', (0, 0))[1], 0, 0, f.get('fx')), [], 'attack', g, ctx['body'], info, 0)
            img = tilt_img(img, f.get('tilt', 0), (CELL + ctx['feet'][0], TOP + ctx['feet'][1]))
            fr = Image.new('RGBA', (CW_, CH_)); shadow(ImageDraw.Draw(fr, 'RGBA'), CELL + ctx['feet'][0], TOP + ctx['feet'][1] + 1); fr.alpha_composite(Image.fromarray(img)); return np.asarray(fr)
        out['attack'] = [(bowframe(f), f['dur']) for f in SHOOT]
        hit = []
        for f in HIT:
            img = A.frame(cls, f'{sex}_bow', ramp, [], (f.get('body', (0, 0))[0], f.get('body', (0, 0))[1], 0, 0, 'nock'), [], 'hit', g, ctx['body'], info, 0)
            if f.get('flash'):
                col = np.array((255, 255, 255) if f['flash'] == 'white' else (235, 60, 50), float); k = 0.8 if f['flash'] == 'white' else 0.45
                img = img.copy(); m = img[..., 3] > 0; img[m, :3] = (img[m, :3] * (1 - k) + col * k).astype(np.uint8)
            img = tilt_img(img, f.get('tilt', 0), (CELL + ctx['feet'][0], TOP + ctx['feet'][1]))
            fr = Image.new('RGBA', (CW_, CH_)); shadow(ImageDraw.Draw(fr, 'RGBA'), CELL + ctx['feet'][0], TOP + ctx['feet'][1] + 1); fr.alpha_composite(Image.fromarray(img))
            if f.get('fx') == 'hitburst': A.burst(ImageDraw.Draw(fr, 'RGBA'), (CELL + 70, TOP + 60), 12)
            hit.append((np.asarray(fr), f['dur']))
        out['hit'] = hit
        return out
    seq = MOTION[motion]
    if load[0] == 'dual_daggers':                                  # front slash, then back slash
        ctx2 = context(cls, sex, (load[0], load[1], load[2], motion, ['back']), ramp)
        out['attack'] = [(render_frame(ctx, f, 'attack'), f['dur']) for f in seq[:-1]] + [(render_frame(ctx2, f, 'attack'), f['dur']) for f in seq[1:]]
    else:
        out['attack'] = [(render_frame(ctx, f, 'attack'), f['dur']) for f in seq]
    out['hit'] = [(render_frame(ctx, f, 'hit'), f['dur']) for f in HIT]
    return out

def save_gif(path, rows):
    """rows: [(label, [(frame, dur)])] -> one GIF, rows stacked, frames in step (durations from row 0)."""
    n = max(len(r[1]) for r in rows); frames = []; durs = []
    for t in range(n):
        sheet = Image.new('RGBA', (CW_, (CH_ + 4) * len(rows)), (232, 226, 210, 255)); dd = ImageDraw.Draw(sheet)
        for i, (label, fr) in enumerate(rows):
            y0 = i * (CH_ + 4)
            for c in range(3):
                dd.rectangle([c * CELL, y0 + TOP + 128, (c + 1) * CELL - 1, y0 + CH_ - 2], fill=(212, 202, 178) if c == 1 else (222, 214, 194), outline=(170, 160, 140))
            sheet.alpha_composite(Image.fromarray(fr[min(t, len(fr) - 1)][0]), (0, y0)); dd.text((4, y0 + 4), label, fill=(60, 50, 40))
        frames.append(sheet.convert('P', palette=Image.ADAPTIVE, colors=255)); durs.append(max(r[1][min(t, len(r[1]) - 1)][1] for r in rows))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)

if __name__ == '__main__':
    os.makedirs('sheets', exist_ok=True); os.makedirs('gif', exist_ok=True)
    only = sys.argv[1:] or list(LOADOUTS)
    for cls in only:
        rows = {'attack': [], 'hit': []}
        for sex, ramp in zip('mf', A.RAMPS[cls]):
            for load in LOADOUTS[cls]:
                seqs = render(cls, sex, load, ramp)
                for an, fr in seqs.items():
                    Image.fromarray(np.hstack([f for f, _ in fr])).save(f'sheets/{cls}_{sex}_{load[0]}_{an}.png')
                    with open(f'sheets/{cls}_{sex}_{load[0]}_{an}.txt', 'w') as fh: fh.write(' '.join(str(dd) for _, dd in fr))
                    rows[an].append((f'{sex} {load[0]}', fr))
        for an in rows: save_gif(f'gif/{cls}_{an}.gif', rows[an])
        print(cls, 'done')
