class_name Combat
extends RefCounted
## Auto-battle engine. No UI code: call setup(), then step() until finished.
## Every step() resolves one unit's turn and appends BBCode lines to new_lines.
##
## Rules follow the design doc. Places where the doc is silent and the
## prototype had to pick something are marked "ASSUMPTION".

const MAX_ROUNDS := 60
const C_PARTY := "#8fc1ff"
const C_ENEMY := "#ff9d8a"
const C_GOOD := "#8fd68f"
const C_BAD := "#f08a78"
const C_DIM := "#9aa0a8"
const C_GOLD := "#e2b85a"

var party: Array = []
var enemies: Array = []
var all_units: Array = []
var order: Array = []  ## initiative order, fixed for the fight
var round_order: Array = []
var round_num := 0
var turn_idx := 0
var started := false
var round_open := false
var finished := false
var outcome := ""  ## victory | defeat | retreat | draw
var surprise := 0  ## 0 none, 1 party surprises the enemy, -1 party is ambushed
var retreat_threshold := 0  ## party flees when this many members are Downed (0 = never)

var new_lines: Array[String] = []
var active: Unit = null
var last_targets: Array = []
var _melee_this_round := {}  ## target uid -> Array of attacker uids
var counters := {"attacks": 0, "hits": 0, "crits": 0, "spells": 0, "spells_lost": 0}


func setup(p_party: Array, p_enemies: Array, p_surprise: int = 0, p_retreat: int = 0) -> void:
	party = p_party
	enemies = p_enemies
	surprise = p_surprise
	retreat_threshold = p_retreat
	all_units = party + enemies
	for unit: Unit in party:
		unit.side = 0
	for unit: Unit in enemies:
		unit.side = 1
	for unit: Unit in all_units:
		unit.has_acted = false
		unit.hit_since_last_turn = false
		unit.last_attacker = null
		unit.attack_buff = 0
		unit.initiative = 0
		unit.init_roll = 0


# ------------------------------------------------------------------ queries
func side_units(side: int) -> Array:
	return party if side == 0 else enemies


func standing(side: int) -> Array:
	var result: Array = []
	for unit: Unit in side_units(side):
		if unit.is_standing():
			result.append(unit)
	return result


func foes(unit: Unit) -> Array:
	return standing(1 - unit.side)


func allies(unit: Unit) -> Array:
	return side_units(unit.side)


func row_has_standing(side: int, row: int) -> bool:
	for unit: Unit in side_units(side):
		if unit.row == row and unit.is_standing():
			return true
	return false


func unit_at(side: int, row: int, lane: int, standing_only: bool = false) -> Unit:
	var fallback: Unit = null
	for unit: Unit in side_units(side):
		if unit.row == row and unit.lane == lane and not unit.dead:
			if unit.is_standing():
				return unit
			if not standing_only:
				fallback = unit
	return fallback


## A unit in a front row is engaged with the enemy front row.
func is_engaged(unit: Unit) -> bool:
	return unit.row == 0 and row_has_standing(1 - unit.side, 0)


func is_surprised(unit: Unit) -> bool:
	if surprise == 0 or unit.has_acted:
		return false
	var surprised_side := 1 if surprise == 1 else 0
	return unit.side == surprised_side


func are_adjacent(a: Unit, b: Unit) -> bool:
	return a.side == b.side and absi(a.row - b.row) + absi(a.lane - b.lane) == 1


## Which Defense an attack is rolled against. touch = rays and touch spells.
func defense_for(target: Unit, touch: bool) -> Array:
	var no_dodge := is_surprised(target)
	if touch:
		if no_dodge:
			return [10 + target.other_def, "Defense (Excl. Armor, surprised)"]
		return [target.defense_no_armor(), "Defense (Excl. Armor)"]
	if no_dodge:
		return [target.defense_no_dodge(), "Defense (Excl. Dodge)"]
	return [target.defense(), "Defense"]


## Can this unit swing a melee weapon from where it stands?
## Front row always; middle row only with a reach weapon.
func in_melee_position(unit: Unit) -> bool:
	return unit.row == 0 or (unit.row == 1 and unit.weapon["reach"])


## Melee targets: own lane or an adjacent lane, and the front-most occupied
## enemy row among those lanes. A reach weapon used from the front row also
## reaches one row deeper.
## ASSUMPTION: "must target the front row" is read per reachable lanes, so an
## empty lane in front exposes the units behind it (doc, Positional rules).
func melee_targets(unit: Unit) -> Array:
	if not in_melee_position(unit):
		return []
	var in_reach: Array = []
	var nearest_row := 99
	for foe: Unit in foes(unit):
		if absi(foe.lane - unit.lane) <= 1:
			in_reach.append(foe)
			nearest_row = mini(nearest_row, foe.row)
	var depth := 1 if (unit.weapon["reach"] and unit.row == 0) else 0
	var result: Array = []
	for foe: Unit in in_reach:
		if foe.row <= nearest_row + depth:
			result.append(foe)
	return result


func weapon_targets(unit: Unit) -> Array:
	if unit.weapon["ranged"]:
		return foes(unit)  # ranged attacks can target any row
	return melee_targets(unit)


func area_targets(caster: Unit, shape: String, index: int) -> Array:
	var result: Array = []
	for foe: Unit in foes(caster):
		if (shape == "row" and foe.row == index) or (shape == "lane" and foe.lane == index):
			result.append(foe)
	return result


## ASSUMPTION: a front-line melee unit with nobody in reach spends its turn
## side-stepping one lane toward the nearest enemy. Returns -1 if it cannot.
func lane_shift_for(unit: Unit) -> int:
	if unit.weapon["ranged"] or not in_melee_position(unit):
		return -1
	var best_lane := -1
	var best_dist := 99
	for foe: Unit in foes(unit):
		var dist := absi(foe.lane - unit.lane)
		if dist < best_dist:
			best_dist = dist
			best_lane = foe.lane
	if best_lane < 0 or best_dist <= 1:
		return -1
	var new_lane := unit.lane + signi(best_lane - unit.lane)
	if unit_at(unit.side, unit.row, new_lane, true) != null:
		return -1
	return new_lane


# ------------------------------------------------------------------ logging
func tag(unit: Unit) -> String:
	return "[color=%s][b]%s[/b][/color]" % [C_PARTY if unit.side == 0 else C_ENEMY, unit.unit_name]


func say(line: String) -> void:
	new_lines.append(line)


func take_new_lines() -> Array[String]:
	var lines := new_lines
	new_lines = []
	return lines


# ------------------------------------------------------------------ flow
## Advances the fight by one unit's turn. Returns false once it is over.
func step() -> bool:
	if finished:
		return false
	if not started:
		_start()
		return true
	while not finished:
		if not round_open:
			_begin_round()
			if finished:
				break
		while turn_idx < round_order.size() and not (round_order[turn_idx] as Unit).is_standing():
			turn_idx += 1
		if turn_idx >= round_order.size():
			_end_round()
			continue
		var unit: Unit = round_order[turn_idx]
		turn_idx += 1
		_take_turn(unit)
		break
	return not finished


func run_to_end() -> void:
	while step():
		pass


func _start() -> void:
	started = true
	if surprise == 1:
		say("[color=%s]Surprise! The party's scout spots the enemy first. Enemies use Defense (Excl. Dodge) until they act.[/color]" % C_GOLD)
	elif surprise == -1:
		say("[color=%s]Ambush! The party is caught off guard and uses Defense (Excl. Dodge) until each member acts.[/color]" % C_GOLD)
	# Initiative: d20 + DEX mod, rolled once; order holds for the whole fight.
	for unit: Unit in all_units:
		unit.init_roll = Dice.d(20)
		unit.initiative = unit.init_roll + unit.init_mod
	order = []
	for unit: Unit in all_units:
		if not unit.dead:  # a member who starts Downed can still be healed and act
			order.append(unit)
	Dice.shuffle(order)  # random tie-break
	order.sort_custom(func(a: Unit, b: Unit) -> bool:
		if a.initiative != b.initiative:
			return a.initiative > b.initiative
		return a.init_mod > b.init_mod)
	var parts: Array[String] = []
	for unit: Unit in order:
		parts.append("%s %d" % [tag(unit), unit.initiative])
	say("[b]Initiative:[/b] " + ", ".join(parts))
	_check_end()


func _begin_round() -> void:
	round_num += 1
	if round_num > MAX_ROUNDS:
		_finish("draw", "Neither side can finish the other. The fight breaks off.")
		return
	round_open = true
	turn_idx = 0
	_melee_this_round.clear()
	say("")
	say("[color=%s][b]— Round %d —[/b][/color]" % [C_GOLD, round_num])
	_collapse(0)
	_collapse(1)
	round_order = order.duplicate()
	if round_num == 1 and surprise != 0:
		# The surprising side acts first; initiative order is kept inside each side.
		var first_side := 0 if surprise == 1 else 1
		var first: Array = []
		var second: Array = []
		for unit: Unit in round_order:
			if unit.side == first_side:
				first.append(unit)
			else:
				second.append(unit)
		round_order = first + second


func _end_round() -> void:
	# End of round: ongoing effects would tick here (bleed, burn, durations).
	# None exist yet; collapse is handled when the next round opens.
	round_open = false


## When a front row is emptied, every unit behind it steps forward one row at
## the start of the next round, keeping its lane. Downed bodies in the old
## front row end up behind the line.
func _collapse(side: int) -> void:
	if standing(side).is_empty():
		return
	var steps := 0
	while steps < 2 and not row_has_standing(side, 0):
		for unit: Unit in side_units(side):
			unit.row = (unit.row + 2) % 3
		steps += 1
	if steps > 0:
		var who := "The party's" if side == 0 else "The enemy's"
		say("[color=%s]%s front row is empty: everyone behind it steps forward.[/color]" % [C_DIM, who])


func _take_turn(unit: Unit) -> void:
	active = unit
	last_targets = []
	var action: Dictionary = TacticsAI.choose(self, unit)
	match String(action["type"]):
		"attack":
			_do_attack_action(unit, action["target"])
		"cast":
			_do_cast(unit, action)
		"shift":
			var new_lane := int(action["lane"])
			var body := unit_at(unit.side, unit.row, new_lane)
			if body != null:
				body.lane = unit.lane  # a Downed ally lying there is stepped around
			unit.lane = new_lane
			say("%s — nobody in reach; side-steps to the %s lane." % [tag(unit), GameData.LANES[unit.lane]])
		_:
			say("%s — holds position (%s)." % [tag(unit), action.get("reason", "no target")])
	unit.has_acted = true
	unit.hit_since_last_turn = false
	_check_end()


func _check_end() -> void:
	if finished:
		return
	if standing(1).is_empty():
		_finish("victory", "All enemies are down.")
	elif standing(0).is_empty():
		_finish("defeat", "The whole party is down.")
	elif retreat_threshold > 0:
		var down := 0
		for unit: Unit in party:
			if not unit.is_standing():
				down += 1
		if down >= retreat_threshold:
			_finish("retreat", "%d member(s) down: the party retreats, as ordered." % down)


func _finish(result: String, text: String) -> void:
	finished = true
	outcome = result
	active = null
	last_targets = []
	for unit: Unit in all_units:
		unit.last_attacker = null  # drop cross-references so units can be freed
	var color := C_GOOD if result == "victory" else (C_BAD if result == "defeat" else C_GOLD)
	say("")
	say("[color=%s][b]%s[/b] %s[/color]" % [color, result.capitalize() + ".", text])


# ------------------------------------------------------------------ Attack
func _do_attack_action(unit: Unit, first_target: Unit) -> void:
	# Iterative attacks: BAB +6 / +11 / +16 give extra attacks at -5 each.
	var attacks := 1
	for threshold: int in [6, 11, 16]:
		if unit.bab >= threshold:
			attacks += 1
	var target := first_target
	for i in attacks:
		if target == null or not target.is_standing():
			target = TacticsAI.pick_target(self, unit, weapon_targets(unit))  # each attack can pick a new target
		if target == null:
			break
		_attack_roll(unit, target, -5 * i)
		if finished:
			break


func _attack_roll(unit: Unit, target: Unit, penalty: int) -> void:
	var weapon: Dictionary = unit.weapon
	var is_ranged: bool = weapon["ranged"]
	var bonus := unit.attack_bonus + unit.attack_buff + penalty
	var notes: Array[String] = []
	if penalty != 0:
		notes.append("iterative %d" % penalty)
	if unit.attack_buff != 0:
		notes.append("blessed %s" % GameData.signed(unit.attack_buff))
	if is_ranged:
		if is_engaged(target):
			bonus -= 4  # shooting into melee
			notes.append("−4 into melee")
	else:
		var earlier: Array = _melee_this_round.get(target.uid, [])
		for attacker_uid: int in earlier:
			if attacker_uid != unit.uid:
				bonus += 2  # flanking: second ally to melee the same target this round
				notes.append("+2 flanking")
				break
		if not earlier.has(unit.uid):
			earlier.append(unit.uid)
		_melee_this_round[target.uid] = earlier

	var defense: Array = defense_for(target, false)
	var def_value: int = defense[0]
	var roll := Dice.d(20)
	var total := roll + bonus
	target.last_attacker = unit
	last_targets = [target]
	counters["attacks"] += 1

	var note_text := "" if notes.is_empty() else " [color=%s](%s)[/color]" % [C_DIM, ", ".join(notes)]
	var head := "%s — Attack → %s with %s.%s Roll %d %s = %d vs %s %d." % [
		tag(unit), tag(target), String(weapon["name"]).to_lower(), note_text,
		roll, _signed_term(bonus), total, defense[1], def_value,
	]

	# Natural 1 always misses; natural 20 always hits and threatens.
	var hit := roll == 20 or (roll != 1 and total >= def_value)
	if not hit:
		say("%s [color=%s]Miss%s.[/color]" % [head, C_DIM, " (natural 1)" if roll == 1 else ""])
		return
	counters["hits"] += 1

	var multiplier := 1
	var crit_text := ""
	if roll >= int(weapon["threat"]):
		var confirm_roll := Dice.d(20)
		var confirm_total := confirm_roll + bonus
		var confirmed := confirm_roll == 20 or (confirm_roll != 1 and confirm_total >= def_value)
		if confirmed:
			multiplier = int(weapon["mult"])
			counters["crits"] += 1
			crit_text = " Threat! Confirm %d %s = %d: [color=%s]critical ×%d[/color]." % [confirm_roll, _signed_term(bonus), confirm_total, C_GOLD, multiplier]
		else:
			crit_text = " Threat! Confirm %d %s = %d fails, so a normal hit." % [confirm_roll, _signed_term(bonus), confirm_total]

	# A critical multiplies weapon damage (dice + modifier). Bonus dice would not multiply.
	var damage := 0
	var rolled := 0
	for i in multiplier:
		rolled += Dice.roll(int(weapon["n"]), int(weapon["sides"]))
	damage = maxi(1, rolled + unit.damage_bonus * multiplier)
	var math := "%d damage" % damage
	if unit.damage_bonus != 0:
		math = "%d %s = %d damage" % [rolled, _signed_term(unit.damage_bonus * multiplier), damage]
	say("%s%s [color=%s]Hit[/color]: %s. %s" % [head, crit_text, C_GOOD, math, _apply_damage(target, damage)])


func _signed_term(value: int) -> String:
	return ("+ %d" % value) if value >= 0 else ("− %d" % absi(value))


## Returns the "Name: 13 → 6 HP" text.
func _apply_damage(target: Unit, amount: int) -> String:
	var before := target.hp
	target.hp -= amount
	target.hit_since_last_turn = true
	var text := "%s: %d → %d HP" % [target.unit_name, before, target.hp]
	if target.hp <= 0:
		# Downed at 0 or below; dead at -CON score.
		if target.hp <= -target.con_score:
			target.dead = true
			text += ", [color=%s][b]dead[/b][/color]" % C_BAD
		elif before > 0:
			text += ", [color=%s]Downed[/color]" % C_BAD
	return text + "."


func _apply_heal(target: Unit, amount: int) -> String:
	var before := target.hp
	target.hp = mini(target.max_hp, target.hp + amount)
	var text := "%s: %d → %d HP" % [target.unit_name, before, target.hp]
	if before <= 0 and target.hp > 0:
		text += ", [color=%s]back on their feet[/color]" % C_GOOD
	return text + "."


# ------------------------------------------------------------------ Cast Spell
func spell_damage_dice(spell_id: String, caster_level: int) -> Array:
	var spell: Dictionary = GameData.SPELLS[spell_id]
	match spell_id:
		"arcane_bolt":
			var bolts := clampi((caster_level + 1) / 2, 1, 5)
			return [bolts, 4, bolts]
		"flame_wave":
			return [clampi(caster_level, 1, 5), 4, 0]
	return [int(spell.get("n", 1)), int(spell.get("sides", 4)), int(spell.get("bonus", 0))]


func _do_cast(unit: Unit, action: Dictionary) -> void:
	var spell_id: String = action["spell"]
	var spell: Dictionary = GameData.SPELLS[spell_id]
	var level: int = spell["level"]
	var kind: String = spell["kind"]
	counters["spells"] += 1
	unit.spend_slot(level)  # cantrips are free
	var slot_text := "cantrip" if level == 0 else "L%d slot" % level
	var head := "%s — Cast Spell: %s [color=%s](%s)[/color]." % [tag(unit), spell["name"], C_DIM, slot_text]

	# Arcane casters in armor roll the armor's spell failure % first.
	if unit.caster_type == "arcane" and unit.spell_failure > 0:
		var failure_roll := Dice.d(100)
		if failure_roll <= unit.spell_failure:
			counters["spells_lost"] += 1
			say("%s Armor spell failure %d%%: rolled %d. [color=%s]The spell fizzles.[/color]" % [head, unit.spell_failure, failure_roll, C_BAD])
			return

	# Casting while engaged, or after being hit since the last turn: concentration.
	var engaged := is_engaged(unit)
	if engaged or unit.hit_since_last_turn:
		var dc := 15 + 2 * level
		var roll := Dice.d(20)
		var total := roll + unit.caster_level + unit.cast_mod
		var why := "engaged" if engaged else "hit since last turn"
		if total < dc:
			counters["spells_lost"] += 1
			say("%s Concentration (%s) %d %s = %d vs DC %d. [color=%s]The spell is lost.[/color]" % [head, why, roll, _signed_term(unit.caster_level + unit.cast_mod), total, dc, C_BAD])
			return
		head += " Concentration (%s) %d %s = %d vs DC %d: holds." % [why, roll, _signed_term(unit.caster_level + unit.cast_mod), total, dc]

	match kind:
		"ray":
			_cast_ray(unit, spell_id, action["target"], head)
		"bolt":
			var target: Unit = action["target"]
			var dice: Array = spell_damage_dice(spell_id, unit.caster_level)
			var damage := Dice.roll(dice[0], dice[1]) + int(dice[2])
			last_targets = [target]
			target.last_attacker = unit
			say("%s Auto-hit on %s: %d damage [color=%s](%s)[/color]. %s" % [head, tag(target), damage, C_DIM, GameData.dice_text(dice[0], dice[1], dice[2]), _apply_damage(target, damage)])
		"area":
			var shape: String = spell["shape"]
			var index: int = action["index"]
			var targets: Array = area_targets(unit, shape, index)
			var dice: Array = spell_damage_dice(spell_id, unit.caster_level)
			var where := "%s %s" % [GameData.ROWS[index].to_lower() if shape == "row" else GameData.LANES[index].to_lower(), shape]
			var lines: Array[String] = []
			last_targets = targets
			for target: Unit in targets:
				var damage := Dice.roll(dice[0], dice[1]) + int(dice[2])
				target.last_attacker = unit
				lines.append("%d → %s" % [damage, _apply_damage(target, damage)])
			# Resist is TBD in the doc: area damage is not reduced.
			say("%s Hits the enemy %s (%s each): %s" % [head, where, GameData.dice_text(dice[0], dice[1], dice[2]), " ".join(lines)])
		"heal":
			var target: Unit = action["target"]
			var amount := Dice.roll(int(spell["n"]), int(spell["sides"])) + mini(unit.caster_level, int(spell["cl_cap"]))
			last_targets = [target]
			say("%s Heals %s for %d. %s" % [head, tag(target), amount, _apply_heal(target, amount)])
		"buff":
			var bonus: int = spell["attack"]
			for ally: Unit in allies(unit):
				if ally.is_standing():
					ally.attack_buff = maxi(ally.attack_buff, bonus)
			last_targets = standing(unit.side)
			say("%s All allies gain %s attack for this fight." % [head, GameData.signed(bonus)])


## Attack spells: d20 + BAB + DEX mod vs the target's Defense (Exclude Armor).
## ASSUMPTION: a ray is a ranged attack, so it takes -4 into melee as well.
func _cast_ray(unit: Unit, spell_id: String, target: Unit, head: String) -> void:
	var bonus := unit.bab + unit.dex_mod + unit.attack_buff
	var note := ""
	if is_engaged(target):
		bonus -= 4
		note = " [color=%s](−4 into melee)[/color]" % C_DIM
	var defense: Array = defense_for(target, true)
	var def_value: int = defense[0]
	var roll := Dice.d(20)
	var total := roll + bonus
	target.last_attacker = unit
	last_targets = [target]
	var text := "%s Ray at %s.%s Roll %d %s = %d vs %s %d." % [head, tag(target), note, roll, _signed_term(bonus), total, defense[1], def_value]
	var hit := roll == 20 or (roll != 1 and total >= def_value)
	if not hit:
		say("%s [color=%s]Miss.[/color]" % [text, C_DIM])
		return
	var dice: Array = spell_damage_dice(spell_id, unit.caster_level)
	var damage := maxi(1, Dice.roll(dice[0], dice[1]) + int(dice[2]))
	say("%s [color=%s]Hit[/color]: %d damage [color=%s](%s)[/color]. %s" % [text, C_GOOD, damage, C_DIM, GameData.dice_text(dice[0], dice[1], dice[2]), _apply_damage(target, damage)])
