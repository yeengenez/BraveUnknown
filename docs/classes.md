# Classes and weapons

Decided 2026-11-16. This is the design baseline; the prototype code does not use it yet (see "Not yet in the prototype" below). Rules use the Stats & Combat System doc (PF1e-style).

## Classes

Six base classes. **Cleric is renamed Acolyte.**

Armor ladder: cloth → light → medium → heavy. "Up to X" includes every category below X.

| Class | Hit Die | BAB | Armor | Shield | Weapons |
|---|---|---|---|---|---|
| Soldier | d10 | Full | Cloth to heavy | Yes | Simple, martial, reach. No bows or crossbows |
| Archer | d8 | Full | Cloth to light | No | Bow, crossbow, light simple weapons only |
| Acolyte | d8 | ¾ | Cloth | Yes | Simple, magic items (wand, staff) |
| Mage | d6 | ½ | Cloth | No | Light simple weapons only, magic items (wand, staff) |
| Brawler | d10 | Full | Cloth to medium | No | Simple, martial, unarmed. No bows or crossbows |
| Rogue | d8 | ¾ | Cloth to light | No | All one-handed weapons |

Light simple weapons (the Archer and Mage list): dagger, punching dagger, spiked gauntlet, light mace, sickle.

Classes branch into advanced classes later (for example an Acolyte branch that fights in melee). Not designed yet.

## General rules

- **Simple weapons:** every class can use them (Archer and Mage: light ones only).
- **Dual wield:** anyone holding two one-handed weapons can dual wield, including an Archer with two daggers. The secondary hit takes **−4 to hit and deals half damage**; the primary hit is unaffected. These are placeholder numbers to test; feats will reduce the penalties.
- **Secondary weapon:** every expeditioner can carry one, and it must be one-handed (light for Archer and Mage). An Archer out of ammunition switches to it.

## Class features

**Soldier.** Trained with every kind of gear: all armor, shields, martial and reach weapons.

**Archer.** Ranged attacker that needs ammunition.
- The player prepares ammunition and stores it in the wagon.
- An Archer carries one normal bundle (50 arrows, bolts or sling bullets) into combat and refills it from the wagon after the fight.
- Magic ammunition (beast-bane, fire, etc.) comes in bundles of 10. An Archer carries one magic bundle. If the wagon has no refill, the count carries over: 5 of 10 left means the next fight starts with 5.
- With no ammunition left, the Archer fights with the secondary weapon.

**Acolyte.** Divine power and healing. Has an attack cantrip and a healing cantrip of about 1d3 HP.

**Mage.** Arcane power. The normal attack is a cantrip (for example acid splash).

**Brawler.** Front-line damage dealer.
- Unarmed strike damage scales with level (table not set).
- Unarmed has its own exclusive weapon type (hand wraps, brass knuckles, cestus, gauntlet), so a Brawler can benefit from weapon bonuses.
- Unarmed weapons are a pair and attack like dual wield (same −4 and half damage on the secondary hit), so each one is on par with a one-handed martial weapon.

**Rogue.** Utility and stealth: unlocks chests and doors, disarms traps, scouts.
- **Stealth:** enemies cannot target the Rogue, unless the Rogue is the only target in its row.
- Starts automatically at the start of each fight and lasts 2 turns. After that the Rogue needs the **Stealth action**, which lasts 3 turns. Stealth is a Rogue-only action; Attack and Cast Spell stay the basic actions for everyone.
- Attacking does not break stealth. Area attacks still hit a stealthed Rogue.
- The benefit is safety, plus combos with some feats (feats not designed).

**Wands and staves.** To be designed. Rough idea: they improve spell damage or effects, and some have an inherent skill.

## Weapons

The working list lives in the Google Sheet "Brave unknown Weapon sheet". The CSV files in `docs/weapons/` are a copy taken on 2026-11-16:

| File | Contents |
|---|---|
| `weapons/one_handed.csv` | 25 light and one-handed melee weapons |
| `weapons/two_handed.csv` | 14 two-handed melee weapons, including reach weapons |
| `weapons/ranged.csv` | 9 bows, crossbows, sling and thrown weapons |
| `weapons/unarmed.csv` | 5 unarmed weapons (Brawler's exclusive type) |
| `weapons/ammunition.csv` | Normal and magic ammunition bundles |

- The list is a Pathfinder 1e baseline (Core Rulebook simple and martial weapons, Medium size). Final weapons will be defined later.
- Values were entered from memory of PF1e and not checked against the book.
- Unarmed weapons were raised to one-handed martial level; their numbers are placeholders.
- Halberd has Reach because the stats doc says so; the PF1e halberd has no reach.

## Still open

- Brawler unarmed scaling table, and whether bare fists (1d3) should start higher for Brawlers.
- Dual-wield numbers need testing.
- Advanced class list.
- Effects of magic ammunition, wands and staves.
- The stats doc still lists two actions; it needs the Rogue-only Stealth action, dual wield and the secondary weapon slot.

## Not yet in the prototype

`scripts/data/game_data.gd` still has the older placeholder classes: Soldier, Archer, Cleric and Mage, with their old gear rules. Brawler, Rogue, the Acolyte name, dual wield, stealth, ammunition and the weapon list above are not implemented.
