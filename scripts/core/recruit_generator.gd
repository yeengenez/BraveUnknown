class_name RecruitGenerator
extends RefCounted
## Rolls the pre-made adventurers offered at the guild.
##
## Abilities: 25-point buy with the doc's cost table, weighted toward what the
## recruit's loadout needs. Scores stay in 10-18 because the doc lists no
## refund for going below 10.

const DEFAULT_TACTIC := {"soldier": "Balanced", "archer": "Aggressive", "cleric": "Support", "mage": "Balanced"}


static func step_cost(score: int) -> int:
	return int(GameData.POINT_BUY_COST[score + 1]) - int(GameData.POINT_BUY_COST[score])


static func points_spent(scores: Dictionary) -> int:
	var total := 0
	for ability: String in GameData.ABILITIES:
		total += int(GameData.POINT_BUY_COST[int(scores[ability])])
	return total


## Spends exactly POINT_BUY_BUDGET points. focus = abilities in priority order.
static func roll_abilities(focus: Array) -> Dictionary:
	for attempt in 200:
		var scores := {}
		var weights := {}
		for ability: String in GameData.ABILITIES:
			scores[ability] = 10
			weights[ability] = 1.0
		# A recruit is at least competent at their job.
		scores[focus[0]] = 15
		weights[focus[0]] = 6.0
		if focus.size() > 1:
			scores[focus[1]] = 12
			weights[focus[1]] = 4.0
		if focus.size() > 2:
			weights[focus[2]] = 2.5
		var points := GameData.POINT_BUY_BUDGET - points_spent(scores)
		while points > 0:
			var options := {}
			for ability: String in GameData.ABILITIES:
				var score: int = scores[ability]
				if score < 18 and step_cost(score) <= points:
					options[ability] = weights[ability]
			if options.is_empty():
				break
			var chosen: String = Dice.pick_weighted(options)
			points -= step_cost(int(scores[chosen]))
			scores[chosen] = int(scores[chosen]) + 1
		if points == 0:
			return scores
	# Practically unreachable; a legal 25-point spread as a fallback.
	var fallback := {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
	fallback[focus[0]] = 18
	fallback[focus[1] if focus.size() > 1 else "CON"] = 14
	fallback[focus[2] if focus.size() > 2 else "DEX"] = 13
	return fallback


static func random_name(taken: Array, fem: bool = false) -> String:
	var firsts: Array[String] = GameData.FIRST_NAMES_F if fem else GameData.FIRST_NAMES_M
	for attempt in 40:
		var candidate := "%s %s" % [Dice.pick(firsts), Dice.pick(GameData.BYNAMES)]
		if not taken.has(candidate):
			return candidate
	return "%s %s" % [Dice.pick(firsts), Dice.pick(GameData.BYNAMES)]


## A random portrait from the portrait module (res://portraits/), stored as
## HeroAppearance.to_dict(). body: "m", "f" or "" for random.
## Every class now has its own outfit. A class without one would borrow the
## cleric robe, recoloured; see UnitPortrait._apply_tint().
static func roll_look(class_id: String, body: String = "") -> Dictionary:
	var outfit := class_id if PortraitLibrary.classes().has(class_id) else "cleric"
	# Roll straight from the shared generator: re-seeding a fresh generator per
	# recruit gave correlated looks (most recruits got the same hairstyle).
	var look := HeroAppearance.roll(Dice.rng, body, outfit).to_dict()
	if outfit != class_id:
		look["tint"] = class_id
	return look


static func make(taken_names: Array = [], forced_class: String = "", forced_level: int = 0) -> Unit:
	var unit := Unit.new()
	unit.class_id = forced_class if forced_class != "" else String(Dice.pick_weighted(GameData.CLASS_WEIGHTS))
	unit.level = forced_level if forced_level > 0 else int(Dice.pick_weighted(GameData.RECRUIT_LEVEL_WEIGHTS))
	var cls: Dictionary = GameData.CLASSES[unit.class_id]
	var loadout: Dictionary = Dice.pick(cls["loadouts"])
	unit.weapon_id = loadout["weapon"]
	unit.shield_id = loadout["shield"]
	unit.armor_id = Dice.pick(loadout["armor"])
	unit.default_row = int(loadout["row"])
	unit.abilities = roll_abilities(loadout["focus"])
	unit.tactic = DEFAULT_TACTIC.get(unit.class_id, "Balanced")
	unit.look = roll_look(unit.class_id)
	unit.unit_name = random_name(taken_names, unit.look["body"] == "f")
	unit.recalc(true)
	# Better recruits cost more gold: price follows level, with some haggle room.
	var base: int = GameData.RECRUIT_BASE_COST[unit.level]
	unit.cost = int(round(base * Dice.rng.randf_range(0.9, 1.15) / 5.0)) * 5
	return unit
