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
| **Battle** | Pick an encounter size and a surprise setting, press **New battle**. The party fights on its own. Step turn by turn, auto-play (1×–8× speed), or skip to the result. Every roll is written to the log. |

### Combat presentation

Each turn plays back as animation before the next one starts:

- The acting unit glows and gets a gold outline, its target gets a red outline (green for an ally being healed), its line in the turn order lights up, and the centre caption reads *Actor ⟶ weapon/spell ⟶ Target · result*.
- Melee: the attacker winds up and lunges at the target, then returns.
- Ranged and spells fire a missile at the target: a fletched arrow (bows), a crossbow bolt, a sling stone, an ice shard (Frost Ray), violet orbs, one per bolt (Arcane Bolt), a fireball (Flame Wave and Searing Ray), a force spear (Force Lance) or a holy star (Holy Spark). Area spells send one missile to every target in the row or lane. Heals send a green orb to the ally; Blessing sends gold motes to everyone.
- Melee strikes match the weapon's damage type and always travel from the attacker's side to the far side (mirrored for enemies): **slash** is a crescent blade sweep, **pierce** a triangular stab mark shooting through, **blunt** an impact burst with shock waves rolling forward, **claw** three parallel rakes, **bite** two rows of teeth lunging in and snapping shut. Missile hits spray out of the far side of the target.
- Hit: red flash, knock-back shake, floating damage number. Critical: gold flash, harder knock-back, screen shake, "CRITICAL!". Miss: the target sidesteps and "MISS" floats up.
- HP on a card changes only when the blow lands. "DOWNED" / "SLAIN" pop up; units that change slot (side-steps, a row collapsing forward) slide over.

Animation code lives in `scripts/ui/battle_screen.gd` (sequencing), `unit_cell.gd` (card motion) and `battle_fx.gd` (arrows, projectiles, numbers). The engine reports each swing as a structured event (`Combat.take_events()`), so the rules never depend on the visuals.

You start with 1,000 g. Winning pays loot. HP and spell slots carry over between
fights until you make camp. Dead expeditioners leave the roster for good.
`+500 g` in the top bar is a test helper.

## Portraits

> **Legacy art (2026-11-18):** the portrait images were made from Canva art and are Legacy,
> reference only. They stay in the game until replacement art exists. See `portraits/LEGACY.md`.

Expeditioners use the **expedition-portraits** module (pixel-art anime bust
portraits assembled from layered parts and colour ramps), copied in as
`res://portraits/`. Each recruit rolls a `HeroAppearance` for its class
outfit when created; it is stored on the unit as `look`
(`HeroAppearance.to_dict()`), so it never changes unless you press
**New look** on the Party screen. A recruit's name matches the portrait's
body type.

`scripts/ui/unit_portrait.gd` shows a unit's portrait anywhere in the UI:
the full bust on Guild cards and the character sheet, a head-and-shoulders
crop on battle cards and roster rows (small sizes use smooth mipmapped
scaling; 180 px and up stay pixel-crisp).

Changes made to the module copy here: mipmaps turned on for the part
textures (for clean downscaling), and `portraits/robe_tint.gdshader` added.

Placeholders:
- **Mage** has no outfit in the module yet. Mages wear the cleric robe
  recoloured violet (`robe_tint.gdshader`); the gold cross still shows. Add
  `m_body_mage_*` / `f_body_mage_*` parts and list `mage` in
  `portraits/library.json`, and mages use them automatically.
- **Monsters** have no art in the module. They still use simple shapes drawn
  in code (`scripts/core/portrait_gen.gd` + `scripts/ui/monster_portrait.gd`).

## Where things are

```
scripts/data/game_data.gd        every table: weapons, armor, classes, spells, monsters, prices
scripts/core/unit.gd             one combatant and all derived stats
scripts/core/recruit_generator.gd  25-point-buy recruits
scripts/core/encounter_generator.gd  monster groups
scripts/core/portrait_gen.gd     placeholder monster portrait looks
portraits/                       expedition-portraits module (hero portraits)
scripts/core/combat.gd           the battle engine (no UI code)
scripts/core/tactics_ai.gd       the five tactics profiles
scripts/game_state.gd            autoload "Game": gold, guild offers, roster, formation
scripts/ui/                      the three screens + combat animation
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
- **Damage types** (slash / pierce / blunt / claw / bite) on weapons only pick the strike animation; they have no rules effect.
- **Monsters.** All stat blocks except Orc Raider (Goblin Brute with a club and Cave Ghoul with claws were added to show the blunt and claw strikes) (from the doc's worked example). Encounter budgets, themes, and the cap of two casters per encounter.
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
