# Expedition: Brave Unknown — Design Decisions

## Source of truth for stats and combat
The Claude doc **"Expedition: Brave Unknown — Stats & Combat System (PF1e-style)"** (https://claude.ai/artifact/7YZqGvkNTh9J2xbVdvaPJU) is the authority. Read it before any stat, combat or character work. Do not fill gaps from standard Pathfinder rules: where the doc says TBD, keep it TBD or mark the assumption as a placeholder.

Key points from that doc that are easy to get wrong:
- No saving throws (excluded; "Resist (TBD)" spots only). No CMB/CMD. No races.
- "Defense", not AC. Three versions: Defense, Defense (Exclude Armor), Defense (Exclude Dodge).
- Ability scores by **25-point buy** (PF1e standard costs). Tavern recruits come pre-rolled. (Changed from 20 on 2026-11-15.)
- HP: **full Hit Die + CON mod at every level**. Never rolled, never averaged. (Changed on 2026-11-15.)
- Formation 3×3 grid, **two basic actions: Attack and Cast Spell** (plus the Rogue-only Stealth action, decided 2026-11-16, not yet in the doc), tactics profiles.
- **Brace is not a basic action** (removed 2026-11-15). It will be a feat choice, designed with the feat list.
- Class roles, gear, Hit Die and BAB are set (see "Class design" below; **not yet written into the stats doc**). Spell slots per class and feature numbers are still not designed.

## Class design (2026-11-16, user direction)
Six classes. **Cleric is renamed Acolyte.** This section is the baseline.

Armor ladder: **cloth → light → medium → heavy**. "Up to X" includes every category below X.

| Class | Hit Die | BAB | Armor | Shield | Weapons |
|---|---|---|---|---|---|
| Soldier | d10 | Full | Cloth to heavy | Yes | Simple, martial, reach. **No bows or crossbows** |
| Archer | d8 | Full | Cloth to light | — | Bow, crossbow, **light simple weapons only** |
| Acolyte | d8 | ¾ | Cloth | Yes | Simple, magic items (wand, staff) |
| Mage | d6 | ½ | Cloth | — | **Light simple weapons only**, magic items (wand, staff) |
| Brawler | d10 | Full | Cloth to medium | — | Simple, martial, unarmed. **No bows or crossbows** |
| Rogue | d8 | ¾ | Cloth to light | — | All one-handed weapons |

Archer and Mage melee weapons limited to **light** weapons on 2026-11-16 (user: "wear only light weapon", read as weapons, not armor). Read as light **simple** weapons, since both classes were simple-only before; light martial (short sword, kukri) not confirmed. In PF1e sizes, club and shortspear (both in the user's original Archer list) are one-handed, not light, so they are now excluded unless the user re-sizes them.

General rules decided:
- **Simple weapons can be used by every class** (Archer and Mage: light ones only).
- **Dual wield is open to anyone** holding two one-handed weapons (an Archer with two daggers is valid). **Secondary hit: −4 attack and half damage.** Placeholder numbers for testing; feats will ease the penalties. Read as: the primary hit is unaffected.
- **Secondary weapon slot**: every expeditioner can carry a secondary weapon, and it must be **one-handed** (for Archer and Mage, light). Used e.g. when an Archer runs out of ammunition.
- **Class advancement exists**: classes branch into advanced classes later (e.g. an Acolyte branch that fights in melee). Not designed.

Class features:
- **Archer — ammunition.** The player prepares ammunition and stores it in the **wagon**. An Archer carries **one normal bundle (50)** into combat and refills it from the wagon after the fight. **Bolts and sling bullets use the same bundle rules as arrows.** Magic-tier ammunition (beast-bane, fire, etc.) comes in bundles of **10** (changed from 10–20 on 2026-11-16) and the Archer can carry **one** such bundle. If the wagon has no refill, the count carries over (5/10 beast-bane left means the next fight starts with 5). With no ammunition left, the Archer switches to the **secondary weapon** and holds ground.
- **Mage:** normal attack is a cantrip (e.g. acid splash).
- **Acolyte:** has an attack cantrip, and a **healing cantrip of about 1d3 HP**.
- **Brawler:** unarmed strike damage scales (table not set). Unarmed has its **own exclusive weapon type** (hand wraps, knuckles, cestus, gauntlet) so it can benefit from weapon bonuses. Unarmed weapons are a **pair that attacks like dual wield** (same −4 / half damage on the secondary hit), so **each is on par with a one-handed martial weapon** (decided 2026-11-16). This is what separates Brawler from Soldier.
- **Rogue:** unlocks chests and doors, disarms traps, scouts. **Stealth:** enemies cannot target the Rogue unless the Rogue is the only target in the row. Starts **automatically at the start of the fight and lasts 2 turns**; after that it needs a **Stealth action** and lasts **3 turns**. Attacking does **not** break it. **Area attacks still hit** a stealthed Rogue. Benefit is safety, plus combos with some feats (feats not designed). **The Stealth action is Rogue-exclusive**: Attack and Cast Spell stay the basic actions for everyone.
- **Wands and staves:** to be designed later. Rough idea: they improve spell damage or effect; some have an inherent skill.

Still open:
- Brawler unarmed scaling table; advanced class list; dual-wield numbers need testing.
- Whether Brawlers' bare fists (1d3) should start higher so they are not forced to buy unarmed gear.

Knock-on effects:
- The stats doc still says there are two actions; it needs a line for the Rogue-only Stealth action, plus dual wield and the secondary weapon slot, when classes are written into it.
- "Cleric" still appears in the prototype code, `character_gen_pathfinder.py` and portrait part names (`body_cleric`). Rename when those are next touched. (Kept as `cleric` on 2026-11-17 when the new outfits were added, to avoid breaking the prototype.)
- The prototype has no Brawler or Rogue class yet, although their portraits and sprite bodies now exist.

## Weapon sheet (2026-11-16)
Google Sheet **"Brave unknown Weapon sheet"**: https://docs.google.com/spreadsheets/d/1cMPrVnVlqgxuxLEweszsmELcD8rQGhkrTE9TT8A-h6E — the user's working list of weapons, based on Pathfinder 1e. **The user will define the final weapons there later; treat current rows as a PF1e baseline, not final.** Read it before any weapon work.

- Tabs: `1-handed` (25 weapons), `2-handed` (14), `Ranged` (9), `Unarmed` (5), `Ammunition` (5).
- Contents: PF1e Core Rulebook simple and martial weapons at Medium size. **No exotic weapons.** Left out: shield bash, armor spikes, net, blowgun.
- Columns: Weapon, Category (Simple / Martial / Unarmed), Size (Light / One-handed / Two-handed / Pair), Hands, Damage, Crit, Damage type (Slash / Pierce / Blunt), Weight, Cost, Property (rules that exist in the stats doc: Reach, Brace, Thrown, Finesse, Ranged; plus Paired), "PF1e special (no rule yet)" (trip, disarm, double, monk, nonlethal — the game has no CMB), Source, Notes.
- Light simple weapons (the Archer and Mage list): dagger, punching dagger, spiked gauntlet, light mace, sickle.
- `Unarmed` tab (Brawler's exclusive type), raised to one-handed martial level on 2026-11-16, placeholders: bare unarmed strike 1d3 (unchanged); hand wraps 1d8 20/×2 (like flail); brass knuckles 1d8 19–20/×2 (like longsword); cestus 1d6 18–20/×2 (like scimitar); gauntlet 1d8 20/×3 (like warhammer). Brass knuckles and cestus profiles were swapped at the user's request (2026-11-16). All Size "Pair", Property "Paired (attacks as dual wield)".
- `Ammunition` tab: arrows, bolts and sling bullets all 50 per bundle (cost and weight derived from PF1e packs; a sling-bullet bundle weighs 25 lb). Beast-bane and fire arrows 10 per bundle, effect not set.
- Values were entered from memory of PF1e and **not checked against the book**.
- **Halberd** has Reach in the sheet because the stats doc says so; the PF1e halberd has no reach.

## Monster design direction (2026-11-15)
- Monsters are deliberately **under-leveled and individually weak**. Challenge comes from **numbers and attrition** across an expedition, not from single strong enemies.
- High party HP (full Hit Die) is intended to support this: the party wins most fights but wears down HP and spell slots between camps.

## Character generator
`character_gen_pathfinder.py` follows the doc. Class chassis (gear, slots per level) predate the 2026-11-16 class design and need updating. Cleric is now Acolyte.

## Godot prototype (2026-11-15)
Godot 4 project `expedition-brave-unknown` (GDScript, UI built in code, tested on 4.5 and 4.7.1). GitHub: `yeengenez/BraveUnknown` (public). Three screens: **Guild** (six pre-rolled recruits, hire for gold, paid refresh), **Party** (3×3 formation, tactics per member, retreat order, make camp), **Battle** (auto-battle vs random monster group, step / auto-play / skip, full roll log). All tuning tables live in `scripts/data/game_data.gd`, tagged `[DOC]` or `[PLACEHOLDER]`. `tests/run_tests.gd` checks the math against the doc's worked example and runs a balance simulation.

Placeholders the prototype invented (not design decisions; replace when the real systems exist):
- Classes: Soldier d10 full BAB, Archer d8 full BAB, Cleric d8 ¾ BAB divine/WIS, Mage d6 ½ BAB arcane/INT. (These Hit Die and BAB values were confirmed by the user on 2026-11-16.) No Brawler or Rogue. Gear rules predate the 2026-11-16 class design.
- Nine stand-in spells (ray, auto-hit, row/lane area, heal, buff). No spell preparation step.
- All monsters except Orc Raider; encounter budgets; max two casters per encounter. Goblin Brute (club) and Cave Ghoul (claws) were added 2026-11-16 to show blunt and claw strikes.
- Weapon damage types (slash / pierce / blunt / claw / bite) only choose the strike animation; no rules effect.
- Economy: 1,000 starting gold, recruits about 100 / 220 / 380 g at level 1 / 2 / 3, refresh 30 g, loot 12 g per threat point.
- Recruits are level 1–3, all 25 points, scores 10–18 (no buying below 10).
- No feats, XP, leveling, supplies, Focus target order, Brace or save game.

Rule readings the prototype had to choose (open questions for the combat doc):
- Melee targeting is per reachable lane: front-most occupied enemy row among own + adjacent lanes. Reach from the front row hits one row deeper; reach from the middle row hits the enemy front only.
- A front-line melee unit with nobody in its reachable lanes side-steps one lane as its turn (otherwise opposite-lane survivors stalemate).
- Rays take the −4 shooting-into-melee penalty.
- Surprise: the surprising side acts first in round 1.
- Armor category initiative modifiers are applied (Medium −1, Heavy −2). The doc's worked-example Fighter shows Init +1 in a breastplate, which that rule would make +0.

Findings from simulation (500 fights per setup, placeholder numbers):
- Level 1 parties win about 96–99% of small and medium fights while losing 15–30% of total HP, which matches the attrition goal.
- Only three melee enemies can attack at once (front row is three wide), so extra melee monsters wait in the middle row until the whole front row falls. Hordes arrive as waves, not as a swarm.
- Several enemy casters with auto-hit spells kill a level-1 back-liner in one round, hence the cap of two.

## Combat presentation (2026-11-16, user direction)
- Each turn plays back as animation: actor glows, melee lunges, ranged/spells fire a **missile** (arrow, crossbow bolt, sling stone, ice shard, arcane orbs, fireball, force spear, holy star; heals/buffs send motes). **No pointer arrow** between attacker and target.
- Melee shows a **hit mark by damage type**: slash (crescent), pierce (triangular stab mark), blunt (impact burst and shock waves), claw (three rakes), bite (closing jaws). **Pierce and blunt show only the hit mark, never the weapon.**
- **Every effect travels from the attacker's side to the far side** (left→right for the party, mirrored for enemies). No circular impact rings; missile hits spray out of the far side.
- HP on a card changes only when the blow lands; floating numbers, MISS/CRITICAL/DOWNED/SLAIN text, screen shake on crits.

## LEGACY ART: everything made with Canva (user decision, 2026-11-18)
**All assets generated in Canva, and anything cut, edited or composed from a Canva image, are Legacy: use them for reference only** (style, proportions, colours, poses, grip positions). Do not build new game content from them and do not extend them with more Canva generations. New production art replaces them. Register: `art_source/LEGACY.md` and `art_source/legacy_assets.json` (branch `art-source`).
- **Legacy:** hero portrait parts (`portraits/parts/`) and their source images; every battle sprite body, grip body, stand/attack/hit pose, sprite sheet and GIF in `art_source/battle_sprites/`; the style reference and first layer test; the longsword and kite shield cut from the first test image; the enemy sprites (wolf, boar, goblin).
- **Portraits stay in the game until replaced** (the user chose "Legacy too", not removal). Keep the `HeroAppearance` contract and the ramp-tinting system for the replacement art.
- **Canva battle sprites are not put into the game.** (A trial export into the prototype was started and discarded on 2026-11-18.)
- **Not Legacy:** all scripts and data formats (pipelines, grip measurement and grip JSON, compose, `palettes.json`, `library.json`, `HeroAppearance`); weapons drawn in code (great axe, longspear, dagger, mace, quarterstaff, mage staff, bow, arrow); the user's own reference art in `art_source/old_battle_sprites/`.
- **Archer handoff from ChatGPT (2026-11-18,** `art_source/battle_sprites/archer/`**):** docs only, no images. README, `archer_asset_manifest.json`, `equipment_state.py` + test (6/6 pass). Its rules match this doc (light simple melee, bow/crossbow, no reach or 2h melee, 1h in the right hand, bow release without an arrow, bundles 50 / 10). New rules it adds, **not yet confirmed by the user:** quiver and bolt case shown by the equipped ammunition, not the held weapon (`quiver_full/partial/empty`, `boltcase_*`); crossbow poses stand/ready/aim/release/hit. It proposes a **compact 4.0–4.5-head style**, which conflicts with the confirmed ~6–7-head style below; it says a "compact pixel-art reference pack" exists, but that pack is not on GitHub. Gaps: the manifest calls the bow pose `release` while files use `attack`; the state helper handles one ammo type at a time (the Archer may carry a normal and a special bundle) and shows "partial" after the first shot from a full 50.

## New art (2026-11-18, replaces Legacy)
- **Portrait base heads** (`art_source/new_art/portraits/`): male and female bald, faceless heads from ChatGPT, accepted by the user ("this is new head for portrait"). Cut out and saved as 200×200 **skin value maps** `m_head_skin.png` / `f_head_skin.png` in the legacy convention (outline as the darkest skin values, mid skin ~204, skull top y=20, chin y~111, centred x~99, one scale for both so the female head is slightly smaller). Not yet in the game: faces (eyes, brows, mouth per expression) and hair must be drawn for these heads.
- ChatGPT's earlier head layers (step 1/2, corrupted files and wrong head angle) were deleted at the user's request.
- Hairstyles requested from ChatGPT: 12 per sex on a sheet, grayscale hair on a flat green mannequin head (first 8 male / 7 female keep the game's existing names).

## Hero portraits (2026-11-15) — art is LEGACY (Canva), still in the game until replaced
Art style chosen: **pixel-art anime bust portraits** ("style A"), 200×200. Portraits are assembled at runtime from layered parts, not generated by AI in-game. **This module (code, `HeroAppearance`, ramp tinting) is THE portrait system; do not build a different portrait generator** (a code-drawn one was made by mistake on 2026-11-16 and replaced at the user's request). Its current part images are Legacy (Canva, see above) and will be swapped for new art.

- Layers, back to front: body (class outfit) fixed + skin, face skin + fixed + iris, optional scar, hair. Skin, iris and hair are grayscale value maps tinted by color ramps (`palettes.json`: 5 skin, 10 hair, 6 eye ramps).
- **Male and female sets are fully separate**: own base head, bodies, five expressions, scar and hairstyles. Male hair (8): messy, side part, spiky, crew cut, slicked, shaggy, ponytail, long. Female hair (7): long, ponytail, bob, braids, wavy, pixie, bun.
- **Outfits exist for all six classes** (Mage, Brawler and Rogue added 2026-11-17, awaiting user review). Part ids: `soldier`, `archer`, `cleric` (= Acolyte), `mage`, `brawler`, `rogue`.
  - Mage: deep violet robe, silver trim, high collar, crescent clasp.
  - Brawler: crimson sleeveless tunic, studded leather vest, black sash, bare arms. Its arms and chest are on the skin layer (`BARE_SKIN` in `build_library.py`), so they follow the skin colour.
  - Rogue: charcoal leather armor, plum short cape (hood down) and scarf, chest strap with a dagger. The female Rogue's low neckline is also on the skin layer (fixed 2026-11-18 after the user spotted it staying one colour).
- Art direction set by the user: male Soldier has a bulkier frame than the female; female Cleric keeps the original wide hooded mantle with a **single centered cross** (never two crosses on the chest); female Archer has a slightly fuller chest.
- Appearance is separate from stats. `hero_class` in the appearance record only selects the outfit.
- Godot 4 module `expedition-portraits` (tested on 4.5): `portraits/` folder with `PortraitLibrary`, `HeroAppearance` (random roll, `to_dict`/`from_dict`) and `HeroPortrait` (Control using a ramp shader; `bake()` returns an Image).
- **Wired into the prototype 2026-11-16** as `res://portraits/`: recruits roll a `HeroAppearance` for their class outfit, stored on the unit as `look`; the name follows the body type; "New look" re-rolls. `scripts/ui/unit_portrait.gd` shows the full bust (Guild cards, character sheet) or a head-and-shoulders crop (battle cards, roster rows). Changes to the module copy: part textures import with mipmaps; `portraits/robe_tint.gdshader` added. `tests/portrait_check.gd` bakes every outfit for both body types (added 2026-11-17).
- Roll appearances from the game's shared RNG. Seeding a fresh RandomNumberGenerator per recruit from it gave strongly correlated looks (most recruits same hairstyle and colour).
- Mages wear their own robe since 2026-11-17. The recoloured-cleric-robe fallback (`robe_tint.gdshader`) stays in the code for any future class without an outfit. **Monsters** still use simple code-drawn portraits; no monster art in the module.
- Known limits: one head shape per gender; portraits always show hoods down and no helmet; eyebrows follow the skin ramp, not hair color.
- Source images and the build scripts are saved on GitHub in `art_source/portrait_pipeline/` (branch `art-source`, see below).

## Battle sprites (2026-11-16) — LEGACY (Canva), reference only
Full-body battle sprites that match the portraits (same `HeroAppearance`), assembled from layers like the portraits. **Current bodies: the grip bodies (see "Grip bodies, skin layer and animations").**

Confirmed by the user (Soldier test):
- **Art style:** the first full-body design (taller, natural anime proportions, ~6–7 heads), not the chunkier big-head version. Facing right (party is on the left). Canva source of the style: MAHbDbX73BU.
- **Bodies are drawn without weapons**, with empty gripping fists. Weapons and shields are **separate layers**, placed at per-body hand anchor points; the body's own fist is drawn over the handle.
- **Three stances per body** (every class gets all it needs):
  - **One-handed:** back fist raised, front fist forward. Weapon alone → front hand. Weapon + shield → shield on the front arm, weapon in the back hand.
  - **Two-handed:** both fists together, forward (greatsword; future 2H axes/hammers).
  - **Reach:** hands spread along the shaft, front fist forward, back fist at the rear hip (spear, glaive, halberd).
  - Archers: their two-handed stance is a **bow/crossbow shooting pose** (front arm out holding the grip, back hand drawn back).
- **Female bodies must be clearly feminine** at sprite size: smaller frame, narrow shoulders, curved waist and hips, visible chest under the armor, slimmer limbs, smaller pauldrons. Same armor style as the male.
- Confirmed Soldier bodies (Canva media ids): male 1H MAHbDda6aMk, 2H MAHbDT2gx3c, reach MAHbDaj44KI; female 1H MAHbDWuOiaE, 2H MAHbDfkRYn0, reach MAHbDfxJVE8. They differ slightly in scale; normalize to one head size when cutting layers.
- Lessons from the first attempt: cutting a weapon back out of an AI edit of the body leaves artifacts (ghost outlines, broken poles). Prefer drawing each weapon on its own at matching scale and placing it by its grip point.

Bodies for the other classes (2026-11-17, **awaiting user review**), made as outfit edits of the Soldier body with the same stance and sex, with the same outfits as the portraits. Stances chosen from the class weapon lists:

| Class | Stances | Reason |
|---|---|---|
| Archer | 1h, bow | Light secondary weapon; bow/crossbow pose |
| Acolyte | 1h, 2h, reach | Quarterstaff (2h) and spears (reach) are simple weapons; shield on 1h |
| Mage | 1h | Light weapons only; staff or wand in the front hand |
| Brawler | 1h, 2h, reach | Simple and martial; unarmed pair uses 1h |
| Rogue | 1h | One-handed only; dual wield uses 1h |

**Acolyte can use the longspear** (simple, reach), confirmed by the user 2026-11-17, so the Acolyte keeps its reach bodies. Long-shafted weapons: Soldier and Brawler (all), Acolyte (longspear, spear). Archer, Mage and Rogue have none.

Assumptions to confirm with the user: no Acolyte crossbow pose; the Mage holds a staff in the 1h pose; dual wield and unarmed reuse the 1h pose. Canva ids are listed in `art_source/battle_sprites/README.md`. Known flaws: the male Acolyte reach body has a warmer head colour; the female Acolyte reach body seems to have lost the cross.

## Grip bodies, skin layer and animations (2026-11-18) — images LEGACY (Canva), scripts reusable
User: "make sure their hand can grip weapon properly"; then "create sprite for all class including attack and get hit animation with all grip correction". Soldier grips approved ("grip look perfect"); the weapons themselves still look a bit weird and will be fixed later (user).
- **Grip bodies (all classes, 26):** each confirmed body edited in Canva so the fists grip a flat **magenta guide rod** (1h: front rod up-forward, raised back rod straight up; 2h: one rod through both stacked fists; reach: one pole at hip height; Archer bow pose: vertical bow rod in the front fist + horizontal arrow line to the drawing hand). Code fits the rod on both sides of each fist → each hand's **grip point, angle, fist size** (no guessed anchors). Magenta removed, refilled from the original body. These replace the earlier `<class>/bodies/`.
- **Skin layer:** sprites split into fixed colours + a skin brightness map, coloured at runtime by the hero's **portrait skin ramp** (same 5 tones), so head and body match each other and the portrait. Skin = head, bare hands at the grips (Acolyte, Mage, Rogue, Brawler), Brawler arms and chest, female Rogue neckline. Fixes the user-reported Brawler head/body mismatch. The portraits' female Rogue neckline was also put on the skin layer (same day).
- **Class weapons drawn in code** (never Canva): dagger, mace, quarterstaff, mage staff (violet orb), bow, arrow; plus the earlier longsword + kite shield (cut from the first test image), great axe, longspear.
- **Animations v2 (superseded 2026-11-18):** the user found v1 (only the weapon swinging about a frozen fist) laughable and asked for the approach of the first reference animations, with **attack and get-hit as separate animations**. Now the attacking forearm + fist are cut out and swung about the elbow with the weapon locked in the fist; thrusts and punches push the arms forward; the far arm swings behind the head and body; body leans back, tilts into the strike and lunges; ground shadow; per-frame timing with a hold on impact. Loadouts: Soldier longsword / sword+shield / great axe / longspear; Archer bow / dagger; Acolyte mace+shield / quarterstaff / longspear; Mage staff (cast + orb); Brawler unarmed punch / great axe / longspear; Rogue dual daggers. Hit = white flash + impact burst, red flash and knockback, recover. Frames 399×270 (three squares, body in the middle).
- **Battle animation = three single-frame sprites (current, 2026-11-18).** User: "I want standing animation, attacking animation, get hit animation. Each of them is one frame, just swap between those three sprite." Rule from the user: **do not switch to an alternative approach without asking.**
  - stand = the grip body; attack and hit = Canva redraws of every grip body, one per stance (1h, 2h, reach, bow) for each class and sex (52 images), with the same magenta guide rods in the fists. Attack: 1h lunge with front-hand thrust and back-hand overhead strike; 2h heavy forward chop; reach full spear thrust; bow release (open draw hand thrown back). Hit: still facing right, body recoiling back, wincing, fists still gripping.
  - Weapons are drawn in code at each pose's measured grip (Canva never draws weapons). Feet aligned to the stand sprite; reach attacks scaled ×1.25; Mage hit staff drawn behind the body.
  - **Revision (user feedback, same day):** one-handed weapons are **always in the right hand** in stand, attack and hit (the first poses switched hands). The 1h attack follows the user's two reference images (Viking / Roman sword-and-shield strike): deep lunge, weapon arm extended forward over a shield braced in front of the chest. Guide rods: magenta = right hand, cyan = left hand. **Archer bow: stand (relaxed, bow lowered) → nock (full draw with arrow) → release → hit.**
  - Files: `art_source/battle_sprites/poses/` (`sprites/<class>_<sex>_<loadout>_<stand|attack|hit>.png`, 399×270, `review.png`, `process_pose.py`, `compose.py`).
- Files: `art_source/battle_sprites/grip_bodies/` (raw, bodies, grips, layers, scripts) and `art_source/battle_sprites/animation/` (`anim2.py` current, `anim.py` v1 helpers, `class_weapons.py`, `sheets/`, `gif/<class>_attack.gif` and `_hit.gif`).
- Canva: the connector uses the team **Benchamarachuthit Chanthaburi** (2026-11-18). Old-team media is not visible there; bodies were re-imported from the public GitHub repo. Ids in `grip_bodies/grip_canva_ids.json`.
- Known flaws: male Acolyte reach body warm head tint (colour now fixed by the skin layer); female Acolyte reach body has no cross; weapon art still placeholder (user: fix later).

## Weapon layers (2026-11-17, test)
**Rule (user, 2026-11-17): NEVER use Canva to generate weapons.** Existing images may be reused.

Current test set (`art_source/weapons/`, preview `previews/weapon_merge_test2.png`):
- **Longsword and kite shield (fleur-de-lis):** cut from the first layer test image (longsword + shield), which the user picked. Handle replaced with a clean leather grip.
- **Great axe:** painted in code (lit at 4x, palette sampled from the bodies, tinted outline) and drawn directly at the held angle. The first code-drawn axe and shield (flat colours, black outline) were rejected as not matching the art style.
- **Longspear:** pixel art drawn in code.

Holds (user said the first front-sword and spear grips looked weird):
- **Front-hand one-handed weapon:** steep (about −66°) like the rapier in the first test image, guard just above the fist. The body's front fist is a forward punch, so a handle can only pass through it near-vertically.
- **Sword + shield:** sword raised in the back hand behind the head, guard on top of the fist; shield on the front arm.
- **Two-handed and reach weapons are drawn behind the body**, aimed from the back fist through the front fist, so the arms and fists wrap over the shaft (drawn in front, the shaft looked like it pierced the forearm).
- **Long (reach) weapons may draw across more than one formation square** (user direction). The sprite canvas is three squares wide with the body in the middle one.

Aseprite (user has it on their PC): `build_weapons.lua` builds `weapons.aseprite` (one layer per weapon, slices with grip pivots) and `merge_examples.aseprite` (layers squares / weapon_back / body / weapon_front / fists). Files on the PC: `Documents\BraveUnknownArt\weapons`; the user runs it from Aseprite's File > Scripts menu (computer use could not find Aseprite).

## Where the files are (saved 2026-11-16, updated 2026-11-17)
All art working files are on GitHub, repo `yeengenez/BraveUnknown`, **branch `art-source`** (not merged into `main` yet), folder `art_source/` (Godot ignores it via `.gdignore`). The game's `portraits/` module on that branch also has the new outfits.
- `weapons/` — weapon pixel art, fist anchors, merge script, Aseprite script.
- `battle_sprites/` — bodies for every class in `<class>/bodies/<m|f>_<stance>.png`, review sheet `all_class_bodies_sheet.png`, Soldier weapon previews, style reference, first layer test and scripts.
- `portrait_pipeline/` — portrait source images, `build_library.py`, `compose.py`, palettes, review sheets.
- `old_battle_sprites/` — the user's reference art and the earlier animated sprites ("battle sprites v2").
- `enemies/` — wolf, boar, goblin sprites (Canva originals included).
- `outdated_fe_style/` — FE-style stat sheet, battle simulator and status-screen mockups.
Each folder has a README. Generated images are also in the user's Canva account.

## OUTDATED
- Fire Emblem: The Sacred Stones-style stats (HP/Str/Mag/Skl/Spd/Lck/Def/Res with growth rates). Replaced. Reference only: `character_gen_fe_OUTDATED.py` and `art_source/outdated_fe_style/`. (Note: `docs/GDD.md` on GitHub still describes FE-style combat.)
