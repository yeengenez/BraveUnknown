class_name Unit
extends RefCounted
## One combatant: an expeditioner or a monster.
##
## Expeditioners derive everything from abilities + level + class + gear in
## recalc(). Monsters get their numbers set directly by MonsterFactory.

static var _next_uid := 1

# ---- identity
var uid := 0
var unit_name := ""
var is_monster := false
var class_id := ""
var class_label := ""
var level := 1
var abilities := {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
var tactic := "Balanced"
var cost := 0
var threat := 0.0
var default_row := 0

## Portrait. Expeditioners: HeroAppearance.to_dict() from the portrait module
## (res://portraits/). Monsters: PortraitGen.monster(). Drawn by UnitPortrait.
var look: Dictionary = {}

# ---- gear
var weapon_id := ""
var armor_id := ""
var shield_id := ""
var weapon: Dictionary = {}

# ---- derived stats
var max_hp := 1
var hp := 1
var bab := 0
var str_mod := 0
var dex_mod := 0
var armor_bonus := 0  ## armor + shield
var dodge_bonus := 0  ## DEX mod after the armor's Max DEX cap (+ dodge feats later)
var other_def := 0
var attack_bonus := 0
var damage_bonus := 0
var init_mod := 0
var spell_failure := 0
var con_score := 10

# ---- casting
var caster_type := ""  ## "", "arcane" or "divine"
var cast_ability := ""
var caster_level := 0
var cast_mod := 0
var spells: Array = []
var slots_max: Array = []  ## index 0 = 1st-level slots
var slots: Array = []

# ---- combat state (reset by Combat.setup)
var side := 0  ## 0 = party, 1 = enemies
var row := 0
var lane := 0
var initiative := 0
var init_roll := 0
var has_acted := false
var hit_since_last_turn := false
var last_attacker: Unit = null
var attack_buff := 0
var dead := false


func _init() -> void:
	uid = _next_uid
	_next_uid += 1


## New random face, same class and gear.
func reroll_look() -> void:
	if is_monster:
		look = PortraitGen.monster(class_id, Dice.rng.randi())
	else:
		look = RecruitGenerator.roll_look(class_id, String(look.get("body", "")))


static func ability_mod(score: int) -> int:
	return floori((score - 10) / 2.0)


func mod(ability: String) -> int:
	return ability_mod(int(abilities[ability]))


## Rebuilds every derived stat of an expeditioner. Keeps current damage.
func recalc(full_heal: bool = false) -> void:
	if is_monster:
		return
	var cls: Dictionary = GameData.CLASSES[class_id]
	class_label = cls["name"]
	str_mod = mod("STR")
	dex_mod = mod("DEX")
	con_score = int(abilities["CON"])

	# HP: full Hit Die + CON mod at every level. Never rolled, never averaged.
	var missing := max_hp - hp
	max_hp = level * (int(cls["hit_die"]) + mod("CON"))
	hp = max_hp if full_heal else max_hp - missing

	match String(cls["bab"]):
		"full":
			bab = level
		"three_quarter":
			bab = level * 3 / 4
		_:
			bab = level / 2

	# Defense parts
	var armor: Dictionary = GameData.ARMOR[armor_id]
	armor_bonus = int(armor["bonus"])
	spell_failure = int(armor["asf"])
	if shield_id != "":
		var shield: Dictionary = GameData.SHIELDS[shield_id]
		armor_bonus += int(shield["bonus"])
		spell_failure += int(shield["asf"])
	var max_dex := int(armor["max_dex"])
	dodge_bonus = dex_mod if max_dex < 0 else mini(dex_mod, max_dex)
	init_mod = dex_mod + int(GameData.ARMOR_CATEGORY_INIT[armor["category"]])

	# Attack and damage
	weapon = GameData.weapon(weapon_id)
	var uses_dex: bool = weapon["ranged"] or weapon["finesse"]
	attack_bonus = bab + (dex_mod if uses_dex else str_mod)
	if weapon["ranged"]:
		damage_bonus = 0  # bows: no STR unless composite; crossbows: no STR
	elif int(weapon["hands"]) == 2:
		damage_bonus = floori(str_mod * 1.5)
	else:
		damage_bonus = str_mod

	# Casting
	caster_type = cls["caster"]
	cast_ability = cls["cast_ability"]
	if caster_type == "":
		spell_failure = 0
		caster_level = 0
		cast_mod = 0
		spells = []
		slots_max = []
		slots = []
		return
	if caster_type == "divine":
		spell_failure = 0  # divine casters ignore armor spell failure
	caster_level = level
	cast_mod = mod(cast_ability)
	var base: Array = GameData.CASTER_SLOTS.get(mini(level, 3), [1])
	var new_max: Array = []
	for i in base.size():
		var spell_level := i + 1
		var bonus := 0
		if cast_mod >= spell_level:  # PF1e bonus slots from a high casting ability
			bonus = 1 + (cast_mod - spell_level) / 4
		new_max.append(int(base[i]) + bonus)
	var refill := full_heal or slots.size() != new_max.size()
	slots_max = new_max
	if refill:
		slots = slots_max.duplicate()
	spells = []
	for spell_id: String in cls["spells"]:
		if int(GameData.SPELLS[spell_id]["level"]) <= slots_max.size():
			spells.append(spell_id)


# ---- Defense: three versions, as in the doc
func defense() -> int:
	return 10 + armor_bonus + dodge_bonus + other_def


func defense_no_armor() -> int:
	return 10 + dodge_bonus + other_def


func defense_no_dodge() -> int:
	return 10 + armor_bonus + other_def


# ---- state
func is_standing() -> bool:
	return hp > 0 and not dead


func is_downed() -> bool:
	return hp <= 0 and not dead


func hp_fraction() -> float:
	return clampf(float(hp) / float(max_hp), 0.0, 1.0)


func status_text() -> String:
	if dead:
		return "Dead"
	if hp <= 0:
		return "Downed"
	return ""


func slots_left(spell_level: int) -> int:
	if spell_level <= 0:
		return 999  # cantrips are free
	if spell_level > slots.size():
		return 0
	return int(slots[spell_level - 1])


func spend_slot(spell_level: int) -> void:
	if spell_level >= 1 and spell_level <= slots.size():
		slots[spell_level - 1] = int(slots[spell_level - 1]) - 1


func has_any_slot() -> bool:
	for count: int in slots:
		if count > 0:
			return true
	return false


## Camp rest: HP and spell slots come back.
func rest() -> void:
	if dead:
		return
	hp = max_hp
	slots = slots_max.duplicate()


func average_weapon_damage() -> float:
	return int(weapon["n"]) * (int(weapon["sides"]) + 1) / 2.0 + damage_bonus


# ---- text for the UI
func title() -> String:
	if is_monster:
		return class_label
	return "L%d %s" % [level, class_label]


func abilities_text() -> String:
	var parts: Array[String] = []
	for ability: String in GameData.ABILITIES:
		parts.append("%s %d" % [ability, int(abilities[ability])])
	return "  ".join(parts)


func weapon_text() -> String:
	var kind := "ranged" if weapon["ranged"] else ("reach" if weapon["reach"] else "melee")
	return "%s %s (%s, %s, %s)" % [
		weapon["name"], GameData.signed(attack_bonus),
		GameData.dice_text(int(weapon["n"]), int(weapon["sides"]), damage_bonus),
		GameData.crit_text(weapon), kind,
	]


func armor_text() -> String:
	if is_monster:
		return ""
	var text: String = GameData.ARMOR[armor_id]["name"]
	if shield_id != "":
		text += " + " + String(GameData.SHIELDS[shield_id]["name"]).to_lower()
	return text


func defense_text() -> String:
	return "Defense %d  (excl. armor %d · excl. dodge %d)" % [defense(), defense_no_armor(), defense_no_dodge()]


func slots_text() -> String:
	if caster_type == "":
		return ""
	var parts: Array[String] = []
	for i in slots_max.size():
		parts.append("L%d %d/%d" % [i + 1, int(slots[i]), int(slots_max[i])])
	return "Slots: " + ", ".join(parts)


func spells_text() -> String:
	if spells.is_empty():
		return ""
	var names: Array[String] = []
	for spell_id: String in spells:
		var spell: Dictionary = GameData.SPELLS[spell_id]
		names.append("%s (%s)" % [spell["name"], "cantrip" if int(spell["level"]) == 0 else "L%d" % int(spell["level"])])
	return ", ".join(names)
