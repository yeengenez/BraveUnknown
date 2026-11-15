# Expedition: Brave Unknown — guild + auto-battle prototype

Godot 4 project (GDScript, no plugins, no art assets). Tested on Godot 4.5 and 4.7.1.

## Run it

1. Install Godot 4.5 or newer (standard build, not .NET).
2. In the Project Manager choose **Import**, pick this folder's `project.godot`, then press **F5**.

## What you can do

| Screen | What it does |
| --- | --- |
| **Guild** | Six pre-rolled adventurers for hire. Hiring costs gold; **New faces** pays 30 g for a fresh list. Roster holds 12. |
| **Party** | Place 4–6 members on the 3×3 grid (select someone, click a slot; click an occupied slot to swap). Set each member's tactics profile and the party's retreat order. **Make camp** restores HP and spell slots. |
| **Battle** | Pick an encounter size and a surprise setting, press **New battle**. The party fights on its own. Step turn by turn, auto-play, or skip to the result. Every roll is written to the log. |

You start with 1,000 g. Winning pays loot. HP and spell slots carry over between
fights until you make camp. Dead expeditioners leave the roster for good.
`+500 g` in the top bar is a test helper.

## Where things are

```
scripts/data/game_data.gd        every table: weapons, armor, classes, spells, monsters, prices
scripts/core/unit.gd             one combatant and all derived stats
scripts/core/recruit_generator.gd  25-point-buy recruits
scripts/core/encounter_generator.gd  monster groups
scripts/core/combat.gd           the battle engine (no UI code)
scripts/core/tactics_ai.gd       the five tactics profiles
scripts/game_state.gd            autoload "Game": gold, guild offers, roster, formation
scripts/ui/                      the three screens
tests/run_tests.gd               rule checks + balance simulation
```

To rebalance, edit `game_data.gd` only. Tables copied from the design doc are
marked `[DOC]`; stand-ins are marked `[PLACEHOLDER]`.

## Rules implemented from the design doc

- d20 + bonus vs Defense; natural 20 always hits and threatens, natural 1 always misses.
- Three Defense values: Defense, Exclude Armor (rays), Exclude Dodge (surprised, until the unit acts).
- 25-point buy with the doc's cost table. HP = full Hit Die + CON mod per level.
- Attack: STR for melee, DEX for ranged and finesse; 1.5 × STR damage two-handed; no STR on bows and crossbows; crit threat, confirm and multiplier; iterative attacks at BAB +6/+11/+16.
- Formation: front/middle/back rows, lanes (own or adjacent only), reach from the middle row, engaged, −4 shooting into melee, +2 flanking, collapse at the start of the next round.
- Cast Spell: slots (cantrips free, bonus slots from casting ability), rays vs Defense (Exclude Armor), auto-hit spells, row/lane area spells, arcane spell failure from armor, concentration when engaged or hit since last turn (DC 15 + 2 × spell level).
- Initiative rolled once; armor category modifier (Medium −1, Heavy −2).
- Downed at 0 HP, dead at −CON score, healing in combat stands a Downed member back up.
- Tactics profiles: Aggressive, Balanced, Defensive, Support, Conserve. Party order: retreat threshold.

## Placeholders and assumptions

Not in the doc, invented so the prototype can run. Replace freely.

- **Classes.** Soldier (d10, full BAB), Archer (d8, full BAB), Cleric (d8, ¾ BAB, divine/WIS), Mage (d6, ½ BAB, arcane/INT), their gear and slot counts. `character_gen_pathfinder.py` was not available when this was built, so these may differ from it.
- **Spells.** Nine stand-in spells, one per spell shape the doc describes. Casters know every class spell they have slots for; the "prepare spells at camp" step is not built.
- **Monsters.** All stat blocks except Orc Raider (from the doc's worked example). Encounter budgets, themes, and the cap of two casters per encounter.
- **Economy.** Starting gold, recruit prices (by level: about 100 / 220 / 380 g), refresh price, loot.
- **Recruits** are level 1–3 and all use 25 points, so "better" means higher level. Scores stay 10–18 because the doc lists no refund for going below 10.
- **Feats** are left out (list not designed). The doc's worked-example Fighter has two feats, so this prototype's version of him is 1 lower on attack and Defense.
- **Melee targeting** is read per reachable lane: front-most occupied enemy row among the attacker's own and adjacent lanes. A reach weapon in the front row also reaches one row deeper; from the middle row it reaches the enemy front only.
- **Lane side-step.** A front-line melee unit with no enemy in its reachable lanes spends its turn moving one lane toward the nearest enemy. Without this, two survivors in opposite lanes can never reach each other.
- **Rays** take the −4 shooting-into-melee penalty.
- **Resist is TBD** in the doc, so area spells always deal full damage.
- **Surprise** is a dropdown on the Battle screen (Perception and Stealth do not exist yet). The surprising side acts first in round 1.
- **Defeat** leaves the party Downed, not dead, so you can camp and test again.
- Not built: Focus target order, Brace, XP and leveling, supplies, saving the game.

## Tests

Open the project in the editor once (so Godot indexes the classes), then:

```
godot --headless --path . -s tests/run_tests.gd -- --battles=500
godot --headless --path . res://tests/ui_smoke.tscn
```

The first checks the math against the doc's worked example and prints win
rate, rounds, HP lost, Downed and deaths per encounter size. The second drives
the real UI through hire → arrange → fight.
