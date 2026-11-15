extends Node
## Autoload "Game": gold, the guild's offers, your roster and the party formation.

signal changed

var gold := 0
var offers: Array = []  ## Unit or null (null = already hired from that seat)
var roster: Array = []
var formation := {}  ## slot (row * 3 + lane) -> Unit
var retreat_threshold := 0
var battles_won := 0
var battles_fought := 0
var in_battle := false  ## a fight is in progress on the Battle screen


func _ready() -> void:
	Dice.rng.randomize()
	new_game()


func new_game() -> void:
	gold = GameData.START_GOLD
	roster = []
	formation = {}
	retreat_threshold = 0
	battles_won = 0
	battles_fought = 0
	in_battle = false
	_roll_offers()
	changed.emit()


# ------------------------------------------------------------------ guild
func _roll_offers() -> void:
	var taken: Array = []
	for unit: Unit in roster:
		taken.append(unit.unit_name)
	offers = []
	for i in GameData.OFFER_COUNT:
		var recruit := RecruitGenerator.make(taken)
		taken.append(recruit.unit_name)
		offers.append(recruit)


func can_refresh() -> bool:
	return gold >= GameData.REFRESH_COST


## Pays gold for a fresh list of adventurers.
func refresh_offers() -> bool:
	if not can_refresh():
		return false
	gold -= GameData.REFRESH_COST
	_roll_offers()
	changed.emit()
	return true


func can_hire(index: int) -> bool:
	if index < 0 or index >= offers.size() or offers[index] == null:
		return false
	return gold >= (offers[index] as Unit).cost and roster.size() < GameData.ROSTER_CAP


func hire(index: int) -> bool:
	if not can_hire(index):
		return false
	var recruit: Unit = offers[index]
	gold -= recruit.cost
	offers[index] = null
	roster.append(recruit)
	changed.emit()
	return true


func dismiss(unit: Unit) -> void:
	unplace(unit)
	roster.erase(unit)
	changed.emit()


func add_gold(amount: int) -> void:
	gold += amount
	changed.emit()


# ------------------------------------------------------------------ party
func slot_of(unit: Unit) -> int:
	for slot: int in formation:
		if formation[slot] == unit:
			return slot
	return -1


func party_units() -> Array:
	var result: Array = []
	var slots := formation.keys()
	slots.sort()
	for slot: int in slots:
		result.append(formation[slot])
	return result


func party_size() -> int:
	return formation.size()


## Puts a unit on a slot. Swaps if both units are already placed.
func place(unit: Unit, slot: int) -> bool:
	var old_slot := slot_of(unit)
	var occupant: Unit = formation.get(slot, null)
	if occupant == unit:
		return true
	if old_slot < 0 and occupant == null and formation.size() >= GameData.PARTY_MAX:
		return false  # party is full
	if old_slot >= 0:
		formation.erase(old_slot)
	if occupant != null:
		formation.erase(slot)
		if old_slot >= 0:
			formation[old_slot] = occupant
	formation[slot] = unit
	changed.emit()
	return true


func unplace(unit: Unit) -> void:
	var slot := slot_of(unit)
	if slot >= 0:
		formation.erase(slot)
		changed.emit()


func clear_party() -> void:
	formation = {}
	changed.emit()


## Fills the party (up to 6) and stands everyone in the row their gear suits.
func auto_arrange() -> void:
	var members := party_units()
	for unit: Unit in roster:
		if members.size() >= GameData.PARTY_MAX:
			break
		if not members.has(unit) and not unit.dead:
			members.append(unit)
	formation = {}
	members.sort_custom(func(a: Unit, b: Unit) -> bool:
		if a.default_row != b.default_row:
			return a.default_row < b.default_row
		return a.max_hp > b.max_hp)
	var lane_order := [1, 0, 2]
	for unit: Unit in members:
		var rows := [0, 1, 2]
		if unit.default_row == 1:
			rows = [1, 0, 2]
		elif unit.default_row == 2:
			rows = [2, 1, 0]
		var placed := false
		for row: int in rows:
			for lane: int in lane_order:
				if not formation.has(row * 3 + lane):
					formation[row * 3 + lane] = unit
					placed = true
					break
			if placed:
				break
	# A line needs someone holding it: if nobody stands in front, the sturdiest steps up.
	var front_empty := true
	for lane in 3:
		if formation.has(lane):
			front_empty = false
	if front_empty and not members.is_empty():
		var sturdy: Unit = members[0]
		for unit: Unit in members:
			if unit.max_hp > sturdy.max_hp:
				sturdy = unit
		formation.erase(slot_of(sturdy))
		formation[1] = sturdy
	changed.emit()


## Camp: HP and spell slots return. (Free in the prototype; supplies come later.)
func make_camp() -> void:
	for unit: Unit in roster:
		unit.rest()
	changed.emit()


## Dead expeditioners stay dead: remove them from roster and formation.
func bury_dead() -> Array:
	var lost: Array = []
	for unit: Unit in roster.duplicate():
		if unit.dead:
			lost.append(unit)
			unplace(unit)
			roster.erase(unit)
	if not lost.is_empty():
		changed.emit()
	return lost


## Copies formation slots onto the units before a fight.
func prepare_party_for_battle() -> Array:
	var members: Array = []
	for slot: int in formation:
		var unit: Unit = formation[slot]
		unit.side = 0
		unit.row = slot / 3
		unit.lane = slot % 3
		members.append(unit)
	return members
