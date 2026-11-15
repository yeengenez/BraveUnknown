class_name PartyScreen
extends Control
## Party formation: pick 4-6 roster members, stand them on the 3x3 grid and
## give each a tactics profile. This is everything the player controls in a
## fight; the expeditioners act on their own once it starts.

signal go_to_battle

var _selected: Unit = null
var _queued := false
var _roster_list: VBoxContainer
var _cells: Array = []  ## index = slot (row * 3 + lane)
var _status: Label
var _detail: VBoxContainer
var _remove_button: Button
var _camp_button: Button
var _battle_button: Button
var _retreat: SpinBox


func _init() -> void:
	var columns := UIKit.hbox(12)
	columns.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(columns)

	# ---- roster
	var roster_panel := UIKit.panel(UIKit.PANEL_DARK)
	roster_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	roster_panel.size_flags_stretch_ratio = 1.0
	columns.add_child(roster_panel)
	var roster_box := UIKit.vbox(8)
	roster_panel.add_child(roster_box)
	roster_box.add_child(UIKit.label("Roster", 18, UIKit.TEXT, true))
	roster_box.add_child(UIKit.wrapped("Select an adventurer, then click a slot on the grid.", 12))
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	roster_box.add_child(scroll)
	_roster_list = UIKit.vbox(5)
	_roster_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_roster_list)

	# ---- formation
	var middle := UIKit.vbox(8)
	middle.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	middle.size_flags_stretch_ratio = 1.7
	columns.add_child(middle)
	middle.add_child(UIKit.label("Formation", 22, UIKit.TEXT, true))
	middle.add_child(UIKit.wrapped("3 rows × 3 lanes. Melee can only hit the front row and its own or an adjacent lane; the back row is safe until the rows ahead fall. Reach weapons fight from the middle row.", 12))

	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 6)
	grid.add_theme_constant_override("v_separation", 6)
	middle.add_child(grid)
	_cells.resize(9)
	grid.add_child(Control.new())
	# Columns run Back, Middle, Front so the party faces right, as in battle.
	for row: int in [2, 1, 0]:
		var head := UIKit.label(GameData.ROWS[row] + (" → enemy" if row == 0 else ""), 13, UIKit.GOLD)
		head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		grid.add_child(head)
	for lane in 3:
		grid.add_child(UIKit.label(GameData.LANES[lane], 13, UIKit.MUTED))
		for row: int in [2, 1, 0]:
			var cell := UnitCell.new()
			cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var slot := row * 3 + lane
			cell.pressed.connect(_on_cell_pressed.bind(slot))
			grid.add_child(cell)
			_cells[slot] = cell

	_status = UIKit.label("", 14, UIKit.TEXT)
	middle.add_child(_status)

	var tools := UIKit.hbox(8)
	middle.add_child(tools)
	var auto := UIKit.button("Auto-arrange", "Fill the party (up to 6) and stand everyone in the row their gear suits.")
	auto.pressed.connect(func() -> void: Game.auto_arrange())
	tools.add_child(auto)
	_remove_button = UIKit.button("Remove from party")
	_remove_button.pressed.connect(_on_remove)
	tools.add_child(_remove_button)
	var clear := UIKit.button("Clear")
	clear.pressed.connect(func() -> void: Game.clear_party())
	tools.add_child(clear)

	var orders := UIKit.panel(UIKit.PANEL_DARK, UIKit.BORDER, 8)
	middle.add_child(orders)
	var orders_row := UIKit.hbox(8)
	orders.add_child(orders_row)
	orders_row.add_child(UIKit.label("Party order — retreat when", 13))
	_retreat = SpinBox.new()
	_retreat.min_value = 0
	_retreat.max_value = GameData.PARTY_MAX
	_retreat.value_changed.connect(func(value: float) -> void: Game.retreat_threshold = int(value))
	orders_row.add_child(_retreat)
	orders_row.add_child(UIKit.label("members are down  (0 = never)", 13))

	var filler := Control.new()
	filler.size_flags_vertical = Control.SIZE_EXPAND_FILL
	middle.add_child(filler)

	var actions := UIKit.hbox(8)
	middle.add_child(actions)
	_camp_button = UIKit.button("Make camp", "Rest: everyone recovers full HP and all spell slots. Free in this prototype.")
	_camp_button.pressed.connect(func() -> void: Game.make_camp())
	actions.add_child(_camp_button)
	actions.add_child(UIKit.spacer())
	_battle_button = UIKit.button("   To battle  →   ")
	_battle_button.pressed.connect(func() -> void: go_to_battle.emit())
	actions.add_child(_battle_button)

	# ---- detail
	var detail_panel := UIKit.panel(UIKit.PANEL_DARK)
	detail_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	detail_panel.size_flags_stretch_ratio = 1.25
	columns.add_child(detail_panel)
	_detail = UIKit.vbox(6)
	detail_panel.add_child(_detail)

	Game.changed.connect(refresh)


func on_show() -> void:
	refresh()


func refresh() -> void:
	if _queued or not is_inside_tree() or not visible:
		return
	_queued = true
	_rebuild.call_deferred()


func _rebuild() -> void:
	_queued = false
	if _selected != null and not Game.roster.has(_selected):
		_selected = null

	UIKit.clear(_roster_list)
	if Game.roster.is_empty():
		_roster_list.add_child(UIKit.wrapped("Your roster is empty. Hire adventurers at the Guild first.", 14))
	for unit: Unit in Game.roster:
		_roster_list.add_child(_roster_button(unit))

	for slot in 9:
		var occupant: Unit = Game.formation.get(slot, null)
		var cell: UnitCell = _cells[slot]
		cell.show_unit(occupant, "selected" if occupant != null and occupant == _selected else "", "empty")

	var count := Game.party_size()
	var front := 0
	for lane in 3:
		if Game.formation.has(lane):
			front += 1
	if count == 0:
		_status.text = "Party: 0 / %d. Place %d–%d members." % [GameData.PARTY_MAX, GameData.PARTY_MIN, GameData.PARTY_MAX]
		_status.add_theme_color_override("font_color", UIKit.MUTED)
	elif count < GameData.PARTY_MIN:
		_status.text = "Party: %d / %d. The design calls for %d–%d (you can still test a smaller one)." % [count, GameData.PARTY_MAX, GameData.PARTY_MIN, GameData.PARTY_MAX]
		_status.add_theme_color_override("font_color", UIKit.GOLD)
	elif front == 0:
		_status.text = "Party: %d / %d. Nobody in the front row: the next row will step forward at round 1." % [count, GameData.PARTY_MAX]
		_status.add_theme_color_override("font_color", UIKit.GOLD)
	else:
		_status.text = "Party: %d / %d. Ready." % [count, GameData.PARTY_MAX]
		_status.add_theme_color_override("font_color", UIKit.GOOD)

	_remove_button.disabled = _selected == null or Game.slot_of(_selected) < 0
	_battle_button.disabled = count == 0
	_camp_button.disabled = Game.in_battle
	_camp_button.tooltip_text = "Finish the current battle first." if Game.in_battle else "Rest: everyone recovers full HP and all spell slots. Free in this prototype."
	_retreat.set_value_no_signal(Game.retreat_threshold)
	_rebuild_detail()


func _roster_button(unit: Unit) -> Button:
	var slot := Game.slot_of(unit)
	var where := "—" if slot < 0 else "%s · %s" % [GameData.ROWS[slot / 3], GameData.LANES[slot % 3]]
	var entry := UIKit.button("%s\n%s   HP %d/%d   %s" % [unit.unit_name, unit.title(), unit.hp, unit.max_hp, where])
	entry.alignment = HORIZONTAL_ALIGNMENT_LEFT
	entry.toggle_mode = true
	entry.set_pressed_no_signal(unit == _selected)
	entry.clip_text = true
	entry.add_theme_font_size_override("font_size", 13)
	if slot >= 0:
		entry.add_theme_color_override("font_color", UIKit.ALLY)
	entry.tooltip_text = UIKit.sheet(unit)
	entry.pressed.connect(_select.bind(unit))
	return entry


func _select(unit: Unit) -> void:
	_selected = null if _selected == unit else unit
	refresh()


func _on_cell_pressed(slot: int) -> void:
	var occupant: Unit = Game.formation.get(slot, null)
	if _selected == null:
		if occupant != null:
			_select(occupant)
		return
	if occupant == _selected:
		_select(occupant)  # click again to deselect
		return
	if not Game.place(_selected, slot):
		_status.text = "The party is full (%d). Remove someone first, or click an occupied slot to replace them." % GameData.PARTY_MAX
		_status.add_theme_color_override("font_color", UIKit.BAD)


func _on_remove() -> void:
	if _selected != null:
		Game.unplace(_selected)


func _rebuild_detail() -> void:
	UIKit.clear(_detail)
	if _selected == null:
		_detail.add_child(UIKit.label("Adventurer", 18, UIKit.TEXT, true))
		_detail.add_child(UIKit.wrapped("Select someone to see their sheet and set their tactics.", 13))
		return
	var unit := _selected
	_detail.add_child(UIKit.label(unit.unit_name, 18, UIKit.TEXT, true))
	_detail.add_child(UIKit.label(unit.title(), 14, UIKit.ALLY))

	var scores := GridContainer.new()
	scores.columns = 3
	scores.add_theme_constant_override("h_separation", 14)
	for ability: String in GameData.ABILITIES:
		var score: int = unit.abilities[ability]
		scores.add_child(UIKit.label("%s %d (%s)" % [ability, score, GameData.signed(Unit.ability_mod(score))], 13, UIKit.GOLD if score >= 16 else UIKit.TEXT))
	_detail.add_child(scores)

	_detail.add_child(UIKit.label("HP %d / %d      Initiative %s      BAB +%d" % [unit.hp, unit.max_hp, GameData.signed(unit.init_mod), unit.bab], 13))
	_detail.add_child(UIKit.wrapped(unit.defense_text(), 13, UIKit.TEXT))
	_detail.add_child(UIKit.wrapped("Weapon: " + unit.weapon_text(), 13, UIKit.TEXT))
	_detail.add_child(UIKit.wrapped("Armor: " + unit.armor_text(), 13, UIKit.TEXT))
	if unit.caster_type != "":
		var failure := "" if unit.spell_failure == 0 else "   ·   spell failure %d%%" % unit.spell_failure
		_detail.add_child(UIKit.wrapped("%s caster (%s)   ·   %s%s" % [unit.caster_type.capitalize(), unit.cast_ability, unit.slots_text(), failure], 13, UIKit.TEXT))
		_detail.add_child(UIKit.wrapped("Spells: " + unit.spells_text(), 13))
	_detail.add_child(UIKit.label("Feats: TBD (feat list not designed)", 12, UIKit.MUTED))

	_detail.add_child(HSeparator.new())
	_detail.add_child(UIKit.label("Tactics", 15, UIKit.TEXT, true))
	var picker := OptionButton.new()
	picker.focus_mode = Control.FOCUS_NONE
	for tactic: String in GameData.TACTICS:
		picker.add_item(tactic)
	picker.select(GameData.TACTICS.find(unit.tactic))
	picker.item_selected.connect(func(index: int) -> void:
		unit.tactic = GameData.TACTICS[index]
		refresh())
	_detail.add_child(picker)
	_detail.add_child(UIKit.wrapped(GameData.TACTIC_INFO[unit.tactic], 13))
