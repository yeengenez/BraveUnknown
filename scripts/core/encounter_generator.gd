class_name EncounterGenerator
extends RefCounted
## Builds monster groups. Monsters are individually weak; the threat budget
## buys numbers (design-decisions, 2026-11-15).


static func make_monster(monster_id: String) -> Unit:
	var data: Dictionary = GameData.MONSTERS[monster_id]
	var unit := Unit.new()
	unit.is_monster = true
	unit.side = 1
	unit.class_id = monster_id
	unit.class_label = data["name"]
	unit.unit_name = data["name"]
	unit.max_hp = int(data["hp"])
	unit.hp = unit.max_hp
	unit.armor_bonus = int(data["armor"])
	unit.dodge_bonus = int(data["dodge"])
	unit.init_mod = int(data["init"])
	unit.con_score = int(data["con"])
	unit.threat = float(data["threat"])
	unit.attack_bonus = int(data["attack"])
	unit.damage_bonus = int(data["dmg_bonus"])
	unit.default_row = int(data["row"])
	unit.tactic = data["tactic"]
	unit.weapon = GameData.fill_weapon(data["weapon"])
	unit.bab = int(data.get("bab", 0))
	unit.dex_mod = int(data.get("dex_mod", unit.dodge_bonus))
	unit.caster_type = data.get("caster", "")
	if unit.caster_type != "":
		unit.caster_level = int(data["caster_level"])
		unit.cast_mod = int(data["cast_mod"])
		unit.spells = (data["spells"] as Array).duplicate()
		unit.slots_max = (data["slots"] as Array).duplicate()
		unit.slots = unit.slots_max.duplicate()
	return unit


static func party_power(party: Array) -> float:
	var power := 0.0
	for unit: Unit in party:
		power += unit.level + 1
	return power


## The most threat a theme can field on a full grid.
static func theme_capacity(theme_name: String) -> float:
	var strongest := 0.0
	for monster_id: String in GameData.ENCOUNTER_THEMES[theme_name]:
		strongest = maxf(strongest, float(GameData.MONSTERS[monster_id]["threat"]))
	return strongest * GameData.ENCOUNTER_MAX_UNITS


## Returns {"theme": String, "units": Array[Unit]} with rows and lanes set.
static func generate(party: Array, size_name: String, forced_theme: String = "") -> Dictionary:
	var budget := party_power(party) * float(GameData.ENCOUNTER_SIZES[size_name])
	budget = maxf(budget, 2.0)
	var theme_name := forced_theme
	if theme_name == "":
		# Prefer themes that can actually spend the budget on a full grid.
		var fitting: Array = []
		for candidate: String in GameData.ENCOUNTER_THEMES:
			if theme_capacity(candidate) >= budget * 0.75:
				fitting.append(candidate)
		if fitting.is_empty():
			theme_name = GameData.ENCOUNTER_THEMES.keys()[0]
			for candidate: String in GameData.ENCOUNTER_THEMES:
				if theme_capacity(candidate) > theme_capacity(theme_name):
					theme_name = candidate
		else:
			theme_name = Dice.pick(fitting)
	var theme: Dictionary = GameData.ENCOUNTER_THEMES[theme_name]

	var ids: Array[String] = []
	var remaining := budget
	while ids.size() < GameData.ENCOUNTER_MAX_UNITS:
		var options := {}
		for monster_id: String in theme:
			if _is_caster(monster_id) and _count_casters(ids) >= GameData.ENCOUNTER_MAX_CASTERS:
				continue
			if float(GameData.MONSTERS[monster_id]["threat"]) <= remaining + 0.01:
				options[monster_id] = theme[monster_id]
		if options.is_empty():
			break
		var chosen: String = Dice.pick_weighted(options)
		ids.append(chosen)
		remaining -= float(GameData.MONSTERS[chosen]["threat"])

	# Grid is full but budget is left: trade weak monsters for stronger ones.
	var guard := 0
	while remaining >= 0.5 and guard < 40:
		guard += 1
		var slot := Dice.rng.randi_range(0, ids.size() - 1)
		var current := float(GameData.MONSTERS[ids[slot]]["threat"])
		var upgrades: Array[String] = []
		for monster_id: String in theme:
			var threat := float(GameData.MONSTERS[monster_id]["threat"])
			if _is_caster(monster_id) and _count_casters(ids) >= GameData.ENCOUNTER_MAX_CASTERS:
				continue
			if threat > current and threat - current <= remaining + 0.01:
				upgrades.append(monster_id)
		if upgrades.is_empty():
			continue
		var upgrade: String = Dice.pick(upgrades)
		remaining -= float(GameData.MONSTERS[upgrade]["threat"]) - current
		ids[slot] = upgrade

	if ids.is_empty():
		ids.append(theme.keys()[0])

	var units: Array = []
	for monster_id: String in ids:
		units.append(make_monster(monster_id))
	_letter_names(units)
	place_on_grid(units)
	return {"theme": theme_name, "units": units}


static func _is_caster(monster_id: String) -> bool:
	return String(GameData.MONSTERS[monster_id].get("caster", "")) != ""


static func _count_casters(ids: Array) -> int:
	var count := 0
	for monster_id: String in ids:
		if _is_caster(monster_id):
			count += 1
	return count


## "Goblin Cutter" x3 -> "Goblin Cutter A", "B", "C".
static func _letter_names(units: Array) -> void:
	var counts := {}
	for unit: Unit in units:
		counts[unit.class_label] = int(counts.get(unit.class_label, 0)) + 1
	var seen := {}
	for unit: Unit in units:
		if int(counts[unit.class_label]) > 1:
			var index := int(seen.get(unit.class_label, 0))
			seen[unit.class_label] = index + 1
			unit.unit_name = "%s %s" % [unit.class_label, char(65 + index)]


## Front-liners fill the front row first, shooters and casters the back row.
## Within a row: Center, then Left, then Right. Overflow spills to the next row.
static func place_on_grid(units: Array) -> void:
	var taken := {}
	var lane_order := [1, 0, 2]
	var sorted := units.duplicate()
	sorted.sort_custom(func(a: Unit, b: Unit) -> bool: return a.default_row < b.default_row)
	for unit: Unit in sorted:
		var row_order := [0, 1, 2]
		if unit.default_row == 2:
			row_order = [2, 1, 0]
		elif unit.default_row == 1:
			row_order = [1, 0, 2]
		var placed := false
		for row: int in row_order:
			for lane: int in lane_order:
				var key := row * 3 + lane
				if not taken.has(key):
					taken[key] = true
					unit.row = row
					unit.lane = lane
					placed = true
					break
			if placed:
				break
