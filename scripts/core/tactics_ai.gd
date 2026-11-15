class_name TacticsAI
extends RefCounted
## Chooses Attack or Cast Spell and a target from the unit's tactics profile.
## The player never picks actions in combat; this is the whole "brain".
##
## Profiles (doc, "Tactics"):
##   Aggressive  attack or damage spell every turn        -> lowest-HP enemy in reach
##   Balanced    attack; heal allies below 25% HP         -> lowest Defense
##   Defensive   attack whoever threatens it or its ward  -> its attacker
##   Support     buff round 1, heal below 50%, cantrips   -> allies first, then biggest threat
##   Conserve    cantrips and weapons; slots for a Downed ally -> as Balanced
##
## Returns one of:
##   {"type": "attack", "target": Unit}
##   {"type": "cast", "spell": id, "target": Unit}            ray, bolt, heal
##   {"type": "cast", "spell": id, "index": int}              area (row or lane index)
##   {"type": "cast", "spell": id}                            buff
##   {"type": "shift", "lane": int}
##   {"type": "hold", "reason": String}


static func choose(combat: Combat, unit: Unit) -> Dictionary:
	var profile := unit.tactic

	if unit.caster_type != "":
		# 1. Support: buff on round 1.
		if profile == "Support" and combat.round_num == 1:
			var buff := _best_spell(unit, "buff")
			if buff != "" and unit.attack_buff == 0:
				return {"type": "cast", "spell": buff}

		# 2. Healing, by profile threshold.
		var heal_action := _choose_heal(combat, unit, profile)
		if not heal_action.is_empty():
			return heal_action

		# 3. Damage spells that cost a slot.
		if profile in ["Aggressive", "Balanced", "Defensive"]:
			var spell_action := _choose_damage_spell(combat, unit)
			if not spell_action.is_empty():
				return spell_action

	# 4. Weapon, if it has a target.
	var weapon_target := pick_target(combat, unit, combat.weapon_targets(unit))
	if weapon_target != null:
		return {"type": "attack", "target": weapon_target}

	# 5. Damage cantrip (free), e.g. a back-row caster with only a dagger.
	if unit.caster_type != "":
		var cantrip := _damage_cantrip(unit)
		if cantrip != "":
			var cantrip_target := pick_target(combat, unit, combat.foes(unit))
			if cantrip_target != null:
				return {"type": "cast", "spell": cantrip, "target": cantrip_target}

	# 6. Nothing in reach.
	var lane := combat.lane_shift_for(unit)
	if lane >= 0:
		return {"type": "shift", "lane": lane}
	if not unit.weapon["ranged"] and not combat.in_melee_position(unit):
		return {"type": "hold", "reason": "melee weapon cannot reach from the %s row" % GameData.ROWS[unit.row].to_lower()}
	return {"type": "hold", "reason": "no enemy in reach"}


# ------------------------------------------------------------------ targets
static func pick_target(combat: Combat, unit: Unit, candidates: Array) -> Unit:
	if candidates.is_empty():
		return null
	match unit.tactic:
		"Aggressive":
			return _lowest(candidates, func(u: Unit) -> float: return u.hp)
		"Defensive":
			# Whoever attacked it, then whoever attacked an adjacent ally (its ward).
			if unit.last_attacker != null and candidates.has(unit.last_attacker):
				return unit.last_attacker
			for ally: Unit in combat.allies(unit):
				if ally != unit and combat.are_adjacent(unit, ally) and ally.last_attacker != null and candidates.has(ally.last_attacker):
					return ally.last_attacker
		"Support":
			# The biggest threat: highest average damage, then highest attack bonus.
			return _lowest(candidates, func(u: Unit) -> float: return -(u.average_weapon_damage() * 100.0 + u.attack_bonus))
	# Balanced, Conserve and fall-through: lowest Defense, tie broken by lowest HP.
	return _lowest(candidates, func(u: Unit) -> float: return u.defense() * 1000.0 + u.hp)


static func _lowest(candidates: Array, score: Callable) -> Unit:
	var best: Unit = null
	var best_score := INF
	for candidate: Unit in candidates:
		var value: float = score.call(candidate)
		if value < best_score:
			best_score = value
			best = candidate
	return best


# ------------------------------------------------------------------ spells
static func _castable(unit: Unit, kind: String, slot_spells_only: bool = false) -> Array:
	var result: Array = []
	for spell_id: String in unit.spells:
		var spell: Dictionary = GameData.SPELLS[spell_id]
		var level: int = spell["level"]
		if spell["kind"] != kind:
			continue
		if slot_spells_only and level == 0:
			continue
		if unit.slots_left(level) > 0:
			result.append(spell_id)
	return result


## Highest-level castable spell of a kind, or "".
static func _best_spell(unit: Unit, kind: String) -> String:
	var best := ""
	var best_level := -1
	for spell_id: String in _castable(unit, kind):
		var level: int = GameData.SPELLS[spell_id]["level"]
		if level > best_level:
			best_level = level
			best = spell_id
	return best


static func _damage_cantrip(unit: Unit) -> String:
	for spell_id: String in unit.spells:
		var spell: Dictionary = GameData.SPELLS[spell_id]
		if int(spell["level"]) == 0 and spell["kind"] in ["ray", "bolt"]:
			return spell_id
	return ""


static func _choose_heal(combat: Combat, unit: Unit, profile: String) -> Dictionary:
	var threshold := -1.0
	match profile:
		"Balanced":
			threshold = 0.25
		"Support":
			threshold = 0.5
		"Conserve":
			threshold = 0.0  # emergencies only: an ally is Downed
	if threshold < 0.0:
		return {}
	var heals := _castable(unit, "heal")
	if heals.is_empty():
		return {}
	var patient: Unit = null
	var worst := INF
	for ally: Unit in combat.allies(unit):
		if ally.dead:
			continue
		var fraction := float(ally.hp) / float(ally.max_hp)
		var needs := ally.hp <= 0 if threshold == 0.0 else fraction < threshold
		if needs and fraction < worst:
			worst = fraction
			patient = ally
	if patient == null:
		return {}
	# Smallest heal that is enough, otherwise the biggest one available.
	var missing := patient.max_hp - patient.hp
	var chosen := ""
	var chosen_level := 99
	for spell_id: String in heals:
		var spell: Dictionary = GameData.SPELLS[spell_id]
		var average := int(spell["n"]) * (int(spell["sides"]) + 1) / 2.0 + mini(unit.caster_level, int(spell["cl_cap"]))
		if average >= missing and int(spell["level"]) < chosen_level:
			chosen = spell_id
			chosen_level = int(spell["level"])
	if chosen == "":
		chosen = _best_spell(unit, "heal")
	return {"type": "cast", "spell": chosen, "target": patient}


## Picks the slot spell with the best expected damage this turn.
static func _choose_damage_spell(combat: Combat, unit: Unit) -> Dictionary:
	var foes := combat.foes(unit)
	if foes.is_empty():
		return {}
	var best := {}
	var best_value := 0.0
	var single_target := pick_target(combat, unit, foes)
	for kind: String in ["ray", "bolt", "area"]:
		for spell_id: String in _castable(unit, kind, true):
			var spell: Dictionary = GameData.SPELLS[spell_id]
			var dice: Array = combat.spell_damage_dice(spell_id, unit.caster_level)
			var average := int(dice[0]) * (int(dice[1]) + 1) / 2.0 + int(dice[2])
			# Higher slots are scarcer: they must be clearly better to be chosen.
			var thrift := 1.0 + 0.25 * (int(spell["level"]) - 1)
			match kind:
				"bolt":
					# Do not count damage beyond what the target has left.
					var value := minf(average, single_target.hp + 2.0) / thrift
					if value > best_value:
						best_value = value
						best = {"type": "cast", "spell": spell_id, "target": single_target}
				"ray":
					var bonus := unit.bab + unit.dex_mod + unit.attack_buff - (4 if combat.is_engaged(single_target) else 0)
					var need: int = combat.defense_for(single_target, true)[0] - bonus
					var hit_chance := clampf((21 - need) / 20.0, 0.05, 0.95)
					var value := minf(average, single_target.hp + 2.0) * hit_chance / thrift
					if value > best_value:
						best_value = value
						best = {"type": "cast", "spell": spell_id, "target": single_target}
				"area":
					var shape: String = spell["shape"]
					for index in 3:
						var value := 0.0
						for target: Unit in combat.area_targets(unit, shape, index):
							value += minf(average, target.hp + 2.0)
						value /= thrift
						if value > best_value:
							best_value = value
							best = {"type": "cast", "spell": spell_id, "index": index}
	return best
