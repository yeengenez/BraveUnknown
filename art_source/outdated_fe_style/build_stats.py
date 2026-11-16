from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

wb = Workbook()
F = 'Arial'
TITLE = Font(name=F, size=14, bold=True)
SUB = Font(name=F, size=10, italic=True, color='555555')
HDR = Font(name=F, size=10, bold=True, color='FFFFFF')
HFILL = PatternFill('solid', fgColor='2F3E46')
GFILL = PatternFill('solid', fgColor='52796F')
INP = Font(name=F, size=10, color='0000FF')
LINK = Font(name=F, size=10, color='008000')
CALC = Font(name=F, size=10, color='000000')
YEL = PatternFill('solid', fgColor='FFF2CC')
DER = PatternFill('solid', fgColor='EEF3F1')
thin = Side(style='thin', color='C8D0CC')
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
CENTER = Alignment(horizontal='center', vertical='center')
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)
PCT_INT = '0"%"'

def header(ws, row, labels, start=1, fill=HFILL):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=start + i, value=l)
        c.font = HDR; c.fill = fill; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = BOX

def put(ws, r, c, v, font=INP, fmt=None, fill=None, align=CENTER):
    cell = ws.cell(row=r, column=c, value=v); cell.font = font; cell.border = BOX; cell.alignment = align
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    return cell

def widths(ws, w):
    for k, v in w.items(): ws.column_dimensions[k].width = v

# ---------------- Rules ----------------
ws = wb.active; ws.title = 'Rules'
ws['A1'] = 'Expedition: Brave Unknown — Combat Stat Sheet'; ws['A1'].font = TITLE
ws['A2'] = 'Balancing data for classes, enemies and gear. Edit blue cells; black cells are formulas.'; ws['A2'].font = SUB
header(ws, 4, ['Setting', 'Value', 'Used for'])
settings = [('Doubling threshold (AS gap)', 5, 'Attacker strikes twice when its AS is this much higher than the target'),
            ('Critical multiplier', 3, 'Crit damage = damage × this'),
            ('Effective multiplier', 2, 'Weapon Might × this against its effective monster type'),
            ('Max level', 20, 'Level cap for the Party sheet')]
for i, (a, b, c) in enumerate(settings):
    r = 5 + i
    put(ws, r, 1, a, CALC, align=LEFT); put(ws, r, 2, b, INP, fill=YEL); put(ws, r, 3, c, CALC, align=LEFT)
header(ws, 10, ['Value', 'Formula', 'Notes'])
formulas = [
    ('Stat at level', 'Base + Growth × (Level − 1), rounded', 'Expected (average) value; real level-ups roll each growth'),
    ('Total weight', 'Weapon Wt + Armor Wt + Off-hand Wt', ''),
    ('Attack Speed (AS)', 'max(0, Spd − max(0, Total weight − Con))', 'Sets turn order, doubling and Avoid'),
    ('Attack', 'Str (or Mag for magic and staves) + Might', 'Might × Effective multiplier vs effective type'),
    ('Damage', 'max(0, Attack − target Def, or Res for magic)', 'Armor Def/Res adds to the unit’s own'),
    ('Hit', 'Weapon Hit + Skl × 2 + Lck ÷ 2', ''),
    ('Avoid', 'AS × 2 + Lck', 'Terrain bonuses add here'),
    ('Displayed hit %', 'clamp(Hit − target Avoid, 0, 100)', ''),
    ('True hit % (2RN)', 'Average of two rolls 0–99 must be below displayed hit', 'High chances land more often, low chances less'),
    ('Crit %', 'clamp(Weapon Crit + Skl ÷ 2 − target Lck, 0, 100)', ''),
    ('Durability', 'Weapons −1 per strike; armor −1 per hit taken, −2 per crit', 'Broken armor gives no Def and no weight'),
]
for i, row in enumerate(formulas):
    for j, v in enumerate(row): put(ws, 11 + i, j + 1, v, CALC, align=LEFT)
widths(ws, {'A': 30, 'B': 50, 'C': 62})
DBL, CRITM, EFFM, MAXLV = 'Rules!$B$5', 'Rules!$B$6', 'Rules!$B$7', 'Rules!$B$8'

# ---------------- Classes ----------------
ws = wb.create_sheet('Classes')
ws['A1'] = 'Classes'; ws['A1'].font = TITLE
ws['A2'] = 'Level 1 base stats and growth rates (chance per level-up). Con does not grow.'; ws['A2'].font = SUB
ws.merge_cells('G3:O3'); ws['G3'] = 'Base stats (Lv 1)'; ws.merge_cells('P3:W3'); ws['P3'] = 'Growth rates'
for c in ('G3', 'P3'): ws[c].font = HDR; ws[c].fill = GFILL; ws[c].alignment = CENTER
cols = ['Class', 'Role', 'Line', 'Weapons', 'Armor', 'Skill',
        'HP', 'Str', 'Mag', 'Skl', 'Spd', 'Lck', 'Def', 'Res', 'Con',
        'HP', 'Str', 'Mag', 'Skl', 'Spd', 'Lck', 'Def', 'Res']
header(ws, 4, cols)
classes = [
    ('Soldier', 'Early-game tank', 'Front', 'Sword, Axe, Spear + Shield', 'Medium', 'Shield Bash',
     24, 7, 0, 5, 5, 3, 6, 1, 9, .85, .50, 0, .40, .35, .30, .45, .15),
    ('Archer', 'Ranged damage', 'Mid / Back', 'Bow', 'Light', 'Power Shot',
     18, 6, 0, 8, 7, 4, 3, 2, 6, .65, .45, 0, .55, .50, .40, .20, .25),
    ('Cleric', 'Healer', 'Back', 'Staff', 'Cloth', 'Heal',
     16, 1, 6, 4, 6, 7, 1, 6, 5, .55, .10, .55, .35, .40, .55, .10, .50),
]
for i, row in enumerate(classes):
    r = 5 + i
    for j, v in enumerate(row):
        put(ws, r, j + 1, v, INP, fmt='0%' if j >= 15 else None, align=LEFT if j < 6 else CENTER)
widths(ws, {'A': 11, 'B': 17, 'C': 11, 'D': 26, 'E': 9, 'F': 13, **{chr(71 + k): 6 for k in range(17)}})
ws.freeze_panes = 'B5'

# ---------------- Weapons ----------------
ws = wb.create_sheet('Weapons')
ws['A1'] = 'Weapons'; ws['A1'].font = TITLE
ws['A2'] = 'Dmg: Phys uses Str vs Def, Mag uses Mag vs Res, Heal uses Mag + Might as healing. Durability is uses before breaking.'; ws['A2'].font = SUB
header(ws, 4, ['Weapon', 'Type', 'Dmg', 'Might', 'Hit', 'Crit', 'Wt', 'Durability', 'Range', 'Effective vs', 'Notes'])
weapons = [
    ('Iron Sword', 'Sword', 'Phys', 5, 90, 0, 5, 40, '1', '', 'Accurate, light'),
    ('Iron Axe', 'Axe', 'Phys', 8, 75, 0, 10, 45, '1', '', 'Heavy hitter, slows the wielder'),
    ('Iron Spear', 'Spear', 'Phys', 7, 80, 0, 8, 45, '1', '', 'Balanced'),
    ('Hand Axe', 'Axe', 'Phys', 7, 60, 0, 9, 20, '1–2', '', 'Can strike from the Back line'),
    ('Killing Edge', 'Sword', 'Phys', 9, 75, 30, 7, 20, '1', '', 'Rare; high crit, low durability'),
    ('Short Bow', 'Bow', 'Phys', 4, 95, 0, 3, 45, '2', 'Flying', 'Light and accurate'),
    ('Iron Bow', 'Bow', 'Phys', 6, 85, 0, 5, 40, '2', 'Flying', 'Standard bow'),
    ('Heal Staff', 'Staff', 'Heal', 10, 0, 0, 2, 15, '1–2', '', 'Heals Mag + Might; each heal uses 1'),
    ('Unarmed', 'None', 'Phys', 0, 70, 0, 0, 999, '1', '', 'Fallback when all weapons break'),
]
for i, row in enumerate(weapons):
    for j, v in enumerate(row): put(ws, 5 + i, j + 1, v, INP, align=LEFT if j in (0, 10) else CENTER)
widths(ws, {'A': 14, 'B': 8, 'C': 7, 'D': 7, 'E': 6, 'F': 6, 'G': 5, 'H': 10, 'I': 7, 'J': 12, 'K': 36})
WROWS = f'$A$5:$A${4 + len(weapons)}'

# ---------------- Armor ----------------
ws = wb.create_sheet('Armor')
ws['A1'] = 'Armor & shields'; ws['A1'].font = TITLE
ws['A2'] = 'Def/Res add to the wearer. Durability drops per hit taken; broken pieces give nothing.'; ws['A2'].font = SUB
header(ws, 4, ['Item', 'Slot', 'Weight class', 'Def', 'Res', 'Wt', 'Durability', 'Notes'])
armor = [
    ('None', 'Body', '—', 0, 0, 0, 0, ''),
    ('Cleric Robe', 'Body', 'Cloth', 0, 1, 0, 15, 'Blessed thread'),
    ('Padded Vest', 'Body', 'Light', 0, 0, 1, 12, ''),
    ('Leather Coat', 'Body', 'Light', 1, 0, 1, 18, ''),
    ('Chainmail', 'Body', 'Medium', 3, 0, 4, 24, 'Soldier starting armor'),
    ('Full Plate', 'Body', 'Heavy', 7, 1, 8, 30, 'Near-immune to beasts, but AS often drops to 0'),
    ('No Shield', 'Off-hand', '—', 0, 0, 0, 0, ''),
    ('Wooden Buckler', 'Off-hand', 'Light', 1, 0, 1, 15, ''),
    ('Kite Shield', 'Off-hand', 'Medium', 2, 0, 3, 25, 'Soldier starting shield'),
]
for i, row in enumerate(armor):
    for j, v in enumerate(row): put(ws, 5 + i, j + 1, v, INP, align=LEFT if j in (0, 7) else CENTER)
widths(ws, {'A': 16, 'B': 10, 'C': 12, 'D': 6, 'E': 6, 'F': 5, 'G': 10, 'H': 44})
AROWS = f'$A$5:$A${4 + len(armor)}'

# ---------------- Enemies ----------------
ws = wb.create_sheet('Enemies')
ws['A1'] = 'Enemies'; ws['A1'].font = TITLE
ws['A2'] = 'Monster attacks are natural and never break. Derived columns (shaded) are formulas.'; ws['A2'].font = SUB
ecols = ['Enemy', 'Type', 'Line', 'Role', 'HP', 'Str', 'Mag', 'Skl', 'Spd', 'Lck', 'Def', 'Res',
         'Attack', 'Dmg', 'Might', 'Hit', 'Crit', 'Ability', 'Ability effect', 'AS', 'Attack pwr', 'Hit total', 'Avoid', 'Crit total']
header(ws, 4, ecols[:19]); header(ws, 4, ecols[19:], start=20, fill=GFILL)
enemies = [
    ('Goblin', 'Humanoid', 'Front', 'Weak skirmisher', 18, 6, 0, 5, 6, 3, 2, 0, 'Rusty Blade', 'Phys', 4, 70, 5, 'Gang Up', '+10 Hit against a target already hit this round'),
    ('Wolf', 'Beast', 'Front', 'Fast striker', 20, 7, 0, 5, 10, 3, 3, 0, 'Fangs', 'Phys', 5, 75, 5, 'Pack Hunter', '+10 Hit while another Wolf is alive'),
    ('Boar', 'Beast', 'Front', 'Bruiser', 28, 9, 0, 3, 4, 1, 5, 0, 'Tusks', 'Phys', 6, 70, 10, 'Charge', 'First attack each battle gets +5 Might'),
    ('Harpy', 'Flying', 'Mid', 'Backline diver', 18, 8, 0, 8, 12, 5, 3, 3, 'Talons', 'Phys', 4, 80, 10, 'Dive', 'Ignores cover and always targets the Back line'),
    ('Stone Tortoise', 'Armored', 'Front', 'Wall', 32, 11, 0, 4, 2, 0, 6, 1, 'Crushing Bite', 'Phys', 6, 65, 0, 'Shell', '+6 Def until it has been hit 4 times'),
    ('Gloomcap', 'Plant', 'Back', 'Ranged caster', 18, 0, 8, 6, 4, 2, 3, 6, 'Spore Burst', 'Mag', 4, 70, 0, 'Spores', 'Ranged; aims at the weakest uncovered target'),
]
for i, row in enumerate(enemies):
    r = 5 + i
    for j, v in enumerate(row): put(ws, r, j + 1, v, INP, align=LEFT if j in (0, 3, 12, 17, 18) else CENTER)
    put(ws, r, 20, f'=I{r}', CALC, fill=DER)
    put(ws, r, 21, f'=IF(N{r}="Mag",G{r},F{r})+O{r}', CALC, fill=DER)
    put(ws, r, 22, f'=P{r}+H{r}*2+INT(J{r}/2)', CALC, fill=DER)
    put(ws, r, 23, f'=T{r}*2+J{r}', CALC, fill=DER)
    put(ws, r, 24, f'=Q{r}+INT(H{r}/2)', CALC, fill=DER)
widths(ws, {'A': 15, 'B': 10, 'C': 7, 'D': 15, **{chr(69 + k): 5.5 for k in range(8)}, 'M': 14, 'N': 6, 'O': 6, 'P': 5, 'Q': 5,
            'R': 12, 'S': 44, 'T': 6, 'U': 8, 'V': 7, 'W': 7, 'X': 7})
ws.freeze_panes = 'B5'
EN = len(enemies)

# ---------------- Party ----------------
ws = wb.create_sheet('Party')
ws['A1'] = 'Party loadout'; ws['A1'].font = TITLE
ws['A2'] = 'Pick class, level and gear in the yellow cells; stats and combat numbers update. Stats are expected values at that level.'; ws['A2'].font = SUB
pcols = ['Unit', 'Class', 'Level', 'Weapon', 'Armor', 'Off-hand',
         'HP', 'Str', 'Mag', 'Skl', 'Spd', 'Lck', 'Def', 'Res', 'Con',
         'Total Wt', 'AS', 'Attack / Heal', 'Def total', 'Res total', 'Hit', 'Avoid', 'Crit', 'Dmg', 'Might', 'Effective vs', 'Power stat']
header(ws, 4, pcols[:6]); header(ws, 4, pcols[6:15], start=7); header(ws, 4, pcols[15:], start=16, fill=GFILL)
party = [('Garrick', 'Soldier', 1, 'Iron Sword', 'Chainmail', 'Kite Shield'),
         ('Lyse', 'Archer', 1, 'Iron Bow', 'Leather Coat', 'No Shield'),
         ('Mira', 'Cleric', 1, 'Heal Staff', 'Cleric Robe', 'No Shield')]
def cls(col, r): return f'INDEX(Classes!${col}$5:${col}$7,MATCH($B{r},Classes!$A$5:$A$7,0))'
def wpn(col, r): return f'INDEX(Weapons!${col}$5:${col}${4 + len(weapons)},MATCH($D{r},Weapons!{WROWS},0))'
def arm(col, r, key='E'): return f'INDEX(Armor!${col}$5:${col}${4 + len(armor)},MATCH(${key}{r},Armor!{AROWS},0))'
base_cols = {'G': ('G', 'P'), 'H': ('H', 'Q'), 'I': ('I', 'R'), 'J': ('J', 'S'), 'K': ('K', 'T'), 'L': ('L', 'U'), 'M': ('M', 'V'), 'N': ('N', 'W')}
for i, row in enumerate(party):
    r = 5 + i
    put(ws, r, 1, row[0], INP, align=LEFT)
    for j in range(1, 6): put(ws, r, j + 1, row[j], INP, fill=YEL)
    for pc, (bc, gc) in base_cols.items():
        c = ws[f'{pc}{r}']; c.value = f'={cls(bc, r)}+ROUND({cls(gc, r)}*($C{r}-1),0)'; c.font = LINK; c.border = BOX; c.alignment = CENTER
    c = ws[f'O{r}']; c.value = f'={cls("O", r)}'; c.font = LINK; c.border = BOX; c.alignment = CENTER
    f = {
        'P': f'={wpn("G", r)}+{arm("F", r)}+{arm("F", r, "F")}',
        'Q': f'=MAX(0,K{r}-MAX(0,P{r}-O{r}))',
        'X': f'={wpn("C", r)}', 'Y': f'={wpn("D", r)}', 'Z': f'=IF({wpn("J", r)}="","—",{wpn("J", r)})',
        'AA': f'=IF(X{r}="Phys",H{r},I{r})',
        'R': f'=AA{r}+Y{r}',
        'S': f'=M{r}+{arm("D", r)}+{arm("D", r, "F")}',
        'T': f'=N{r}+{arm("E", r)}+{arm("E", r, "F")}',
        'U': f'=IF(X{r}="Heal","—",{wpn("E", r)}+J{r}*2+INT(L{r}/2))',
        'V': f'=Q{r}*2+L{r}',
        'W': f'=IF(X{r}="Heal","—",{wpn("F", r)}+INT(J{r}/2))',
    }
    for k, v in f.items():
        c = ws[f'{k}{r}']; c.value = v; c.font = CALC; c.border = BOX; c.alignment = CENTER; c.fill = DER
ws['C4'].comment = Comment('Level 1 to the max level set on the Rules sheet.', 'Stat sheet')
dv_cls = DataValidation(type='list', formula1='=Classes!$A$5:$A$7', allow_blank=False); ws.add_data_validation(dv_cls); dv_cls.add('B5:B7')
dv_lv = DataValidation(type='whole', operator='between', formula1='1', formula2=f'={MAXLV}'); ws.add_data_validation(dv_lv); dv_lv.add('C5:C7')
dv_w = DataValidation(type='list', formula1=f'=Weapons!{WROWS}'); ws.add_data_validation(dv_w); dv_w.add('D5:D7')
dv_a = DataValidation(type='list', formula1='=Armor!$A$5:$A$10'); ws.add_data_validation(dv_a); dv_a.add('E5:E7')
dv_o = DataValidation(type='list', formula1='=Armor!$A$11:$A$13'); ws.add_data_validation(dv_o); dv_o.add('F5:F7')
ws['A9'] = 'Legend: yellow cells with blue text are inputs (dropdowns). Green text pulls from another sheet. Shaded cells are formulas.'; ws['A9'].font = SUB
widths(ws, {'A': 10, 'B': 10, 'C': 7, 'D': 13, 'E': 13, 'F': 13, **{chr(71 + k): 5.5 for k in range(9)},
            'P': 8, 'Q': 6, 'R': 9, 'S': 8, 'T': 8, 'U': 6, 'V': 7, 'W': 6, 'X': 6, 'Y': 7, 'Z': 11, 'AA': 8})
ws.freeze_panes = 'B5'

# ---------------- Matchups ----------------
ws = wb.create_sheet('Matchups')
ws['A1'] = 'Matchups'; ws['A1'].font = TITLE
ws['A2'] = 'One action each way, from the Party loadout against each enemy. Expected damage = damage × true hit × strikes (crits not included).'; ws['A2'].font = SUB
ws.merge_cells('C3:I3'); ws['C3'] = 'Your unit attacks'; ws.merge_cells('J3:O3'); ws['J3'] = 'Enemy attacks your unit'
for c in ('C3', 'J3'): ws[c].font = HDR; ws[c].fill = GFILL; ws[c].alignment = CENTER
header(ws, 4, ['Unit', 'Enemy', 'Damage', 'Hit %', 'True hit', 'Crit %', 'Doubles?', 'Exp. dmg / action', 'Actions to defeat',
               'Damage', 'Hit %', 'True hit', 'Doubles?', 'Exp. dmg / action', 'Actions to defeat you'])
def truehit(ref): return f'=IF(ISNUMBER({ref}),IF(2*{ref}<=100,2*{ref}*(2*{ref}+1)/2,10000-(199-2*{ref})*(200-2*{ref})/2)/10000,"—")'
r = 5
for p in range(len(party)):
    pr = 5 + p
    for e in range(EN):
        er = 5 + e
        P_, E_ = f'Party!', f'Enemies!'
        heal = f'{P_}$X${pr}="Heal"'
        cells = {
            1: f'={P_}$A${pr}&" ("&{P_}$B${pr}&")"',
            2: f'={E_}$A${er}',
            3: f'=IF({heal},"—",MAX(0,{P_}$AA${pr}+{P_}$Y${pr}*IF({P_}$Z${pr}={E_}$B${er},{EFFM},1)-IF({P_}$X${pr}="Mag",{E_}$L${er},{E_}$K${er})))',
            4: f'=IF({heal},"—",MAX(0,MIN(100,{P_}$U${pr}-{E_}$W${er})))',
            5: truehit(f'D{r}'),
            6: f'=IF({heal},"—",MAX(0,MIN(100,{P_}$W${pr}-{E_}$J${er})))',
            7: f'=IF({heal},"—",IF({P_}$Q${pr}-{E_}$T${er}>={DBL},"Yes","No"))',
            8: f'=IF(ISNUMBER(C{r}),C{r}*E{r}*IF(G{r}="Yes",2,1),"—")',
            9: f'=IF(ISNUMBER(H{r}),IF(H{r}>0,ROUNDUP({E_}$E${er}/H{r},0),"Can\'t hurt"),"—")',
            10: f'=MAX(0,{E_}$U${er}-IF({E_}$N${er}="Mag",{P_}$T${pr},{P_}$S${pr}))',
            11: f'=MAX(0,MIN(100,{E_}$V${er}-{P_}$V${pr}))',
            12: truehit(f'K{r}'),
            13: f'=IF({E_}$T${er}-{P_}$Q${pr}>={DBL},"Yes","No")',
            14: f'=J{r}*L{r}*IF(M{r}="Yes",2,1)',
            15: f'=IF(N{r}>0,ROUNDUP({P_}$G${pr}/N{r},0),"Can\'t hurt")',
        }
        for c, v in cells.items():
            fmt = PCT_INT if c in (4, 6, 11) else '0.0%' if c in (5, 12) else '0.0' if c in (8, 14) else None
            cell = put(ws, r, c, v, LINK if c in (1, 2) else CALC, fmt=fmt, align=LEFT if c in (1, 2) else CENTER)
            if p % 2 == 0: cell.fill = DER
        r += 1
widths(ws, {'A': 18, 'B': 15, 'C': 8, 'D': 7, 'E': 9, 'F': 7, 'G': 9, 'H': 10, 'I': 10, 'J': 8, 'K': 7, 'L': 9, 'M': 9, 'N': 10, 'O': 11})
ws.freeze_panes = 'C5'

wb.move_sheet('Party', offset=-4)
wb.save('/home/claude/stats/Expedition_Stat_Sheet.xlsx')
print('saved')
