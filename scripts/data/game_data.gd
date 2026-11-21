class_name GameData
extends RefCounted
## All tuning tables in one place.
##
## Tables marked [DOC] are copied from the design doc
## "Expedition: Brave Unknown - Stats & Combat System (PF1e-style)".
## Tables marked [PLACEHOLDER] are NOT designed yet (classes, spells, monsters,
## prices). They exist only so the prototype can run; replace them freely.

# ---------------------------------------------------------------- abilities
const ABILITIES: Array[String] = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

## [DOC] Point buy at recruitment: scores start at 10, 25 points to spend.
const POINT_BUY_BUDGET := 25
const POINT_BUY_COST := {10: 0, 11: 1, 12: 2, 13: 3, 14: 5, 15: 7, 16: 10, 17: 13, 18: 17}

# ---------------------------------------------------------------- formation
## Row 0 = Front, 1 = Middle, 2 = Back. Lane 0 = Left, 1 = Center, 2 = Right.
const ROWS: Array[String] = ["Front", "Middle", "Back"]
const LANES: Array[String] = ["Left", "Center", "Right"]
const PARTY_MIN := 4
const PARTY_MAX := 6

# ---------------------------------------------------------------- weapons
## [DOC] Weapon table. threat = lowest d20 roll that threatens a critical.
## dtype (damage type: slash / pierce / blunt / claw / bite) only picks the
## strike animation for now. [PLACEHOLDER] The doc does not give damage types.
const WEAPONS := {
	"dagger": {"name": "Dagger", "hands": 1, "n": 1, "sides": 4, "threat": 19, "mult": 2, "weight": 1, "dtype": "pierce"},
	"longsword": {"name": "Longsword", "hands": 1, "n": 1, "sides": 8, "threat": 19, "mult": 2, "weight": 4, "dtype": "slash"},
	"battleaxe": {"name": "Battleaxe", "hands": 1, "n": 1, "sides": 8, "threat": 20, "mult": 3, "weight": 6, "dtype": "slash"},
	# [SHEET] from the user's weapon sheet ("Brave unknown Weapon sheet", PF1e baseline)
	"shortsword": {"name": "Short sword", "hands": 1, "n": 1, "sides": 6, "threat": 19, "mult": 2, "weight": 2, "light": true, "dtype": "pierce"},
	"greataxe": {"name": "Greataxe", "hands": 2, "n": 1, "sides": 12, "threat": 20, "mult": 3, "weight": 12, "dtype": "slash"},
	"rapier": {"name": "Rapier", "hands": 1, "n": 1, "sides": 6, "threat": 18, "mult": 2, "weight": 2, "finesse": true, "dtype": "pierce"},
	"spear": {"name": "Spear", "hands": 2, "n": 1, "sides": 8, "threat": 20, "mult": 3, "weight": 6, "brace": true, "dtype": "pierce"},
	"greatsword": {"name": "Greatsword", "hands": 2, "n": 2, "sides": 6, "threat": 19, "mult": 2, "weight": 8, "dtype": "slash"},
	"halberd": {"name": "Halberd", "hands": 2, "n": 1, "sides": 10, "threat": 20, "mult": 3, "weight": 12, "brace": true, "reach": true, "dtype": "slash"},
	"longbow": {"name": "Longbow", "hands": 2, "n": 1, "sides": 8, "threat": 20, "mult": 3, "weight": 3, "ranged": true, "no_str": true},
	"light_crossbow": {"name": "Light crossbow", "hands": 2, "n": 1, "sides": 8, "threat": 19, "mult": 2, "weight": 4, "ranged": true, "no_str": true},
}

# ---------------------------------------------------------------- armor
## [DOC] Armor category -> initiative modifier.
const ARMOR_CATEGORY_INIT := {"Cloth": 0, "Light": 0, "Medium": -1, "Heavy": -2}

## [DOC] Armor table. max_dex = -1 means no cap. asf = arcane spell failure %.
const ARMOR := {
	"robes": {"name": "Robes", "category": "Cloth", "bonus": 0, "max_dex": -1, "asf": 0, "weight": 4},
	"padded_cloth": {"name": "Padded cloth", "category": "Cloth", "bonus": 1, "max_dex": 8, "asf": 0, "weight": 10},
	"leather": {"name": "Leather", "category": "Light", "bonus": 2, "max_dex": 6, "asf": 10, "weight": 15},
	"studded_leather": {"name": "Studded leather", "category": "Light", "bonus": 3, "max_dex": 5, "asf": 15, "weight": 20},
	"chain_shirt": {"name": "Chain shirt", "category": "Light", "bonus": 4, "max_dex": 4, "asf": 20, "weight": 25},
	"hide": {"name": "Hide", "category": "Medium", "bonus": 4, "max_dex": 4, "asf": 20, "weight": 25},
	"scale_mail": {"name": "Scale mail", "category": "Medium", "bonus": 5, "max_dex": 3, "asf": 25, "weight": 30},
	"breastplate": {"name": "Breastplate", "category": "Medium", "bonus": 6, "max_dex": 3, "asf": 25, "weight": 30},
	"splint_mail": {"name": "Splint mail", "category": "Heavy", "bonus": 7, "max_dex": 0, "asf": 40, "weight": 45},
	"half_plate": {"name": "Half-plate", "category": "Heavy", "bonus": 8, "max_dex": 0, "asf": 40, "weight": 50},
	"full_plate": {"name": "Full plate", "category": "Heavy", "bonus": 9, "max_dex": 1, "asf": 35, "weight": 50},
}

## [DOC] Shields.
const SHIELDS := {
	"light_shield": {"name": "Light shield", "bonus": 1, "asf": 5, "weight": 6},
	"heavy_shield": {"name": "Heavy shield", "bonus": 2, "asf": 15, "weight": 15},
}

# ---------------------------------------------------------------- classes
## [PLACEHOLDER] The class system is not designed. Hit Die, BAB, gear and
## spell lists below are stand-ins. "bab": full = level, three_quarter =
## level * 3/4, half = level / 2 (rounded down).
##
## Each loadout: weapon, optional shield, armor options, the row the unit
## prefers, and the order in which point-buy favours abilities.
const CLASSES := {
	"soldier": {
		"name": "Soldier", "hit_die": 10, "bab": "full", "caster": "", "cast_ability": "",
		"spells": [],
		# The five loadouts that have battle sprites (2026-11-21). "id" = sprite loadout in
		# res://sprites/battle/soldier.json; "offhand" = second weapon (dual wield).
		"loadouts": [
			{"id": "sword_shield", "weapon": "longsword", "shield": "heavy_shield", "armor": ["scale_mail", "breastplate", "splint_mail"], "row": 0, "focus": ["STR", "CON", "DEX"]},
			{"id": "dual_shortswords", "weapon": "shortsword", "offhand": "shortsword", "shield": "", "armor": ["chain_shirt", "scale_mail", "breastplate"], "row": 0, "focus": ["STR", "DEX", "CON"]},
			{"id": "spear", "weapon": "spear", "shield": "", "armor": ["hide", "scale_mail", "breastplate"], "row": 0, "focus": ["STR", "CON", "DEX"]},
			{"id": "greatsword", "weapon": "greatsword", "shield": "", "armor": ["scale_mail", "breastplate", "half_plate"], "row": 0, "focus": ["STR", "CON", "DEX"]},
			{"id": "greataxe", "weapon": "greataxe", "shield": "", "armor": ["hide", "scale_mail", "breastplate"], "row": 0, "focus": ["STR", "CON", "DEX"]},
		],
	},
	"archer": {
		"name": "Archer", "hit_die": 8, "bab": "full", "caster": "", "cast_ability": "",
		"spells": [],
		"loadouts": [
			{"weapon": "longbow", "shield": "", "armor": ["leather", "studded_leather", "chain_shirt"], "row": 2, "focus": ["DEX", "CON", "WIS"]},
			{"weapon": "longbow", "shield": "", "armor": ["leather", "studded_leather"], "row": 2, "focus": ["DEX", "CON", "STR"]},
			{"weapon": "light_crossbow", "shield": "", "armor": ["leather", "studded_leather", "chain_shirt"], "row": 2, "focus": ["DEX", "CON", "WIS"]},
		],
	},
	"cleric": {
		"name": "Cleric", "hit_die": 8, "bab": "three_quarter", "caster": "divine", "cast_ability": "WIS",
		"spells": ["holy_spark", "mend_wounds", "blessing", "greater_mend"],
		"loadouts": [
			{"weapon": "longsword", "shield": "light_shield", "armor": ["hide", "scale_mail"], "row": 0, "focus": ["WIS", "STR", "CON"]},
			{"weapon": "battleaxe", "shield": "heavy_shield", "armor": ["chain_shirt", "scale_mail"], "row": 0, "focus": ["WIS", "CON", "STR"]},
			{"weapon": "spear", "shield": "", "armor": ["chain_shirt", "hide"], "row": 1, "focus": ["WIS", "CON", "STR"]},
		],
	},
	"mage": {
		"name": "Mage", "hit_die": 6, "bab": "half", "caster": "arcane", "cast_ability": "INT",
		"spells": ["frost_ray", "arcane_bolt", "flame_wave", "searing_ray", "force_lance"],
		"loadouts": [
			{"weapon": "dagger", "shield": "", "armor": ["robes", "padded_cloth"], "row": 2, "focus": ["INT", "DEX", "CON"]},
			{"weapon": "dagger", "shield": "", "armor": ["robes"], "row": 2, "focus": ["INT", "CON", "DEX"]},
		],
	},
}

## [PLACEHOLDER] How often each class shows up at the guild.
const CLASS_WEIGHTS := {"soldier": 40, "archer": 22, "cleric": 20, "mage": 18}

# ---------------------------------------------------------------- spells
## [PLACEHOLDER] No spell list exists in the doc. These cover each spell
## shape the doc describes: ray (attack roll vs Defense (Exclude Armor)),
## auto-hit damage, area (one row or one lane), heal and buff.
## Resist is TBD in the doc, so area spells deal full damage with no roll.
##
## kind: ray | bolt | area | heal | buff
const SPELLS := {
	# arcane
	"frost_ray": {"name": "Frost Ray", "level": 0, "kind": "ray", "n": 1, "sides": 3},
	"arcane_bolt": {"name": "Arcane Bolt", "level": 1, "kind": "bolt"},  # 1d4+1 per bolt, 1 bolt per 2 CL (max 5)
	"flame_wave": {"name": "Flame Wave", "level": 1, "kind": "area", "shape": "row", "sides": 4},  # 1d4 per CL (max 5d4)
	"searing_ray": {"name": "Searing Ray", "level": 2, "kind": "ray", "n": 4, "sides": 6},
	"force_lance": {"name": "Force Lance", "level": 2, "kind": "area", "shape": "lane", "n": 3, "sides": 6},
	# divine
	"holy_spark": {"name": "Holy Spark", "level": 0, "kind": "ray", "n": 1, "sides": 3},
	"mend_wounds": {"name": "Mend Wounds", "level": 1, "kind": "heal", "n": 1, "sides": 8, "cl_cap": 5},
	"blessing": {"name": "Blessing", "level": 1, "kind": "buff", "attack": 1},  # allies +1 attack for the fight
	"greater_mend": {"name": "Greater Mend", "level": 2, "kind": "heal", "n": 2, "sides": 8, "cl_cap": 10},
}

## [DOC baseline + PLACEHOLDER] Slots per day for a full caster by class level.
## Doc: L1 = 1 first-level slot, 2nd-level spells unlock at L3. Counts beyond
## that are stand-ins until classes are designed. Index 0 = 1st-level slots.
const CASTER_SLOTS := {
	1: [1],
	2: [2],
	3: [2, 1],
}

# ---------------------------------------------------------------- tactics
## [DOC] Tactics profiles.
const TACTICS: Array[String] = ["Aggressive", "Balanced", "Defensive", "Support", "Conserve"]
const TACTIC_INFO := {
	"Aggressive": "Attack or damage spell every turn. Targets the lowest-HP enemy it can reach.",
	"Balanced": "Attack; heal allies below 25% HP. Targets the enemy with the lowest Defense.",
	"Defensive": "Attacks whoever attacked it or an adjacent ally.",
	"Support": "Buff on round 1, heal below 50% HP, otherwise cantrips. Then the biggest threat.",
	"Conserve": "Cantrips and weapons only; slots kept for a Downed ally. Targets as Balanced.",
}

# ---------------------------------------------------------------- dual wield
## [DOC: design notes, class design 2026-11-16; placeholder numbers] Anyone holding two one-handed
## weapons attacks with both. The secondary (off-hand) hit has -4 attack and deals half damage;
## the primary hit is unaffected.
const OFFHAND_ATTACK_PENALTY := -4
const OFFHAND_DAMAGE_FACTOR := 0.5

# ---------------------------------------------------------------- guild
## The very first Guild list of a new game (user, 2026-11-21): one Soldier per battle-sprite
## loadout, then random recruits for the remaining seats.
const FIRST_GUILD_SOLDIERS: Array[String] = ["sword_shield", "dual_shortswords", "spear", "greatsword", "greataxe"]
## [PLACEHOLDER] Economy numbers.
const START_GOLD := 1000
const REFRESH_COST := 30
const OFFER_COUNT := 6
const ROSTER_CAP := 12
const RECRUIT_BASE_COST := {1: 100, 2: 220, 3: 380}
const RECRUIT_LEVEL_WEIGHTS := {1: 60, 2: 28, 3: 12}
const GOLD_PER_THREAT := 12

# ---------------------------------------------------------------- monsters
## [PLACEHOLDER] except Orc Raider, which is the doc's worked-example stat
## block. Direction from design-decisions: monsters are under-leveled and
## individually weak; the challenge is numbers and attrition.
##
## armor / dodge feed the three Defense values:
##   Defense = 10 + armor + dodge, Exclude Armor = 10 + dodge,
##   Exclude Dodge = 10 + armor.
const MONSTERS := {
	"giant_rat": {
		"name": "Giant Rat", "hp": 4, "armor": 0, "dodge": 2, "init": 2, "con": 10, "threat": 1.0,
		"attack": 1, "dmg_bonus": 0, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Bite", "n": 1, "sides": 3, "threat": 20, "mult": 2, "dtype": "bite"},
	},
	"goblin_cutter": {
		"name": "Goblin Cutter", "hp": 5, "armor": 1, "dodge": 2, "init": 2, "con": 10, "threat": 1.0,
		"attack": 1, "dmg_bonus": 0, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Rusty blade", "n": 1, "sides": 4, "threat": 19, "mult": 2, "dtype": "slash"},
	},
	"kobold_slinger": {
		"name": "Kobold Slinger", "hp": 4, "armor": 1, "dodge": 1, "init": 1, "con": 9, "threat": 1.0,
		"attack": 1, "dmg_bonus": 0, "row": 2, "tactic": "Balanced",
		"weapon": {"name": "Sling", "n": 1, "sides": 3, "threat": 20, "mult": 2, "ranged": true},
	},
	"goblin_archer": {
		"name": "Goblin Archer", "hp": 5, "armor": 1, "dodge": 2, "init": 2, "con": 10, "threat": 1.5,
		"attack": 2, "dmg_bonus": 0, "row": 2, "tactic": "Aggressive",
		"weapon": {"name": "Shortbow", "n": 1, "sides": 4, "threat": 20, "mult": 3, "ranged": true},
	},
	"skeleton": {
		"name": "Skeleton", "hp": 6, "armor": 2, "dodge": 1, "init": 1, "con": 10, "threat": 1.5,
		"attack": 1, "dmg_bonus": 1, "row": 0, "tactic": "Balanced",
		"weapon": {"name": "Notched sword", "n": 1, "sides": 6, "threat": 19, "mult": 2, "dtype": "slash"},
	},
	"goblin_hexer": {
		"name": "Goblin Hexer", "hp": 5, "armor": 0, "dodge": 2, "init": 2, "con": 10, "threat": 2.0,
		"attack": 0, "dmg_bonus": 0, "row": 2, "tactic": "Aggressive",
		"weapon": {"name": "Bone knife", "n": 1, "sides": 3, "threat": 20, "mult": 2, "dtype": "pierce"},
		"caster": "arcane", "caster_level": 1, "cast_mod": 2, "bab": 0, "dex_mod": 2,
		"spells": ["frost_ray", "arcane_bolt"], "slots": [1],
	},
	"wolf": {
		"name": "Wolf", "hp": 11, "armor": 1, "dodge": 2, "init": 2, "con": 13, "threat": 2.0,
		"attack": 2, "dmg_bonus": 1, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Bite", "n": 1, "sides": 6, "threat": 20, "mult": 2, "dtype": "bite"},
	},
	"goblin_brute": {
		"name": "Goblin Brute", "hp": 9, "armor": 2, "dodge": 1, "init": 1, "con": 12, "threat": 1.5,
		"attack": 2, "dmg_bonus": 1, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Club", "n": 1, "sides": 6, "threat": 20, "mult": 2, "dtype": "blunt"},
	},
	"cave_ghoul": {
		"name": "Cave Ghoul", "hp": 8, "armor": 1, "dodge": 2, "init": 2, "con": 10, "threat": 1.5,
		"attack": 2, "dmg_bonus": 0, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Claws", "n": 1, "sides": 4, "threat": 20, "mult": 2, "dtype": "claw"},
	},
	"orc_raider": {  # [DOC] worked example: HP 13, Defense 14 / 10, Greataxe +5, 1d12+4 x3, Init +0
		"name": "Orc Raider", "hp": 13, "armor": 4, "dodge": 0, "init": 0, "con": 12, "threat": 4.0,
		"attack": 5, "dmg_bonus": 4, "row": 0, "tactic": "Aggressive",
		"weapon": {"name": "Greataxe", "n": 1, "sides": 12, "threat": 20, "mult": 3, "dtype": "slash"},
	},
}

## [PLACEHOLDER] Encounter themes: which monsters appear together, with weights.
const ENCOUNTER_THEMES := {
	"Vermin swarm": {"giant_rat": 6, "kobold_slinger": 2},
	"Goblin warband": {"goblin_cutter": 5, "goblin_brute": 2, "goblin_archer": 2, "goblin_hexer": 1, "wolf": 1},
	"Restless dead": {"skeleton": 5, "cave_ghoul": 3, "giant_rat": 2},
	"Kobold ambushers": {"kobold_slinger": 4, "goblin_cutter": 2, "giant_rat": 2},
	"Orc raid": {"orc_raider": 2, "goblin_cutter": 4, "goblin_brute": 1, "goblin_archer": 2, "wolf": 1},
}

## [PLACEHOLDER] Encounter size = party power x multiplier, spent on monster
## threat. Party power = sum of (level + 1) over the party.
const ENCOUNTER_SIZES := {
	"Skirmish": 0.9,
	"Pack": 1.4,
	"Horde": 2.0,
}
const ENCOUNTER_MAX_UNITS := 9
const ENCOUNTER_MAX_CASTERS := 2  ## auto-hit spells from many casters delete a level-1 back-liner

# ---------------------------------------------------------------- names
## Given names, split so a recruit's name fits their portrait.
const FIRST_NAMES_M: Array[String] = [
	"Aldric", "Brann", "Dorian", "Faramond", "Hadrian", "Jorund", "Leofric", "Osric",
	"Quillon", "Sigurd", "Ulric", "Wystan", "Anselm", "Corwin", "Edric", "Garrick",
	"Ivo", "Lucan", "Njal", "Perrin", "Roderic", "Tobias", "Varek", "Wilmot", "Yorick",
]
const FIRST_NAMES_F: Array[String] = [
	"Cedany", "Elowen", "Gisela", "Isolde", "Katrin", "Maelis", "Nerys", "Petra",
	"Rowena", "Tamsin", "Vesna", "Ysolt", "Brigid", "Dagny", "Freya", "Hilde",
	"Jocosa", "Kestrel", "Mirabel", "Odette", "Saskia", "Una", "Zelda", "Aveline",
]
const BYNAMES: Array[String] = [
	"of Harrowmere", "the Quiet", "Blackthorn", "Ashdown", "the Younger", "Stonehand",
	"of the Fens", "Greycloak", "Halloway", "the Lucky", "Ironwood", "of Dunmoor",
	"Fairweather", "the Stubborn", "Marrowick", "Thornbury", "of Saltreach", "Longstride",
	"Underhill", "the Patient", "Wolfsbane", "Coldwater", "of Brackenridge", "Oakenshaw",
]


# ---------------------------------------------------------------- helpers
static func weapon(id: String) -> Dictionary:
	return fill_weapon(WEAPONS[id])


## Adds the optional flags so every weapon dictionary has the same keys.
static func fill_weapon(src: Dictionary) -> Dictionary:
	var w: Dictionary = src.duplicate()
	for key: String in ["ranged", "reach", "finesse", "brace", "no_str"]:
		if not w.has(key):
			w[key] = false
	if not w.has("hands"):
		w["hands"] = 1
	if not w.has("dtype"):
		w["dtype"] = "slash"
	return w


static func crit_text(w: Dictionary) -> String:
	var threat: int = w["threat"]
	var range_text := "20" if threat >= 20 else "%d–20" % threat
	return "%s/×%d" % [range_text, int(w["mult"])]


static func dice_text(n: int, sides: int, bonus: int = 0) -> String:
	var text := "%dd%d" % [n, sides]
	if bonus > 0:
		text += "+%d" % bonus
	elif bonus < 0:
		text += "−%d" % absi(bonus)
	return text


static func signed(value: int) -> String:
	return ("+%d" % value) if value >= 0 else ("−%d" % absi(value))
