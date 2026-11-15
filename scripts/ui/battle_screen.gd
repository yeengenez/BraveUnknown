class_name BattleScreen
extends Control
## Test battles: your party against a random group of monsters. The fight
## plays itself; you can step turn by turn, auto-play or skip to the result.

signal go_to_party

const SURPRISE_OPTIONS := ["No surprise", "Party surprises", "Party ambushed"]
const SURPRISE_VALUES := [0, 1, -1]
const SPEEDS := {"1×": 0.9, "2×": 0.45, "4×": 0.2, "8×": 0.08}

var combat: Combat = null
var _encounter_name := ""
var _party_cells: Array = []  ## index = row * 3 + lane
var _enemy_cells: Array = []
var _log: RichTextLabel
var _order: RichTextLabel
var _banner: Label
var _round_label: Label
var _size_picker: OptionButton
var _surprise_picker: OptionButton
var _speed_picker: OptionButton
var _new_button: Button
var _step_button: Button
var _auto_button: Button
var _finish_button: Button
var _camp_button: Button
var _timer: Timer


func _init() -> void:
	var root := UIKit.vbox(8)
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)

	# ---- controls
	var controls := UIKit.hbox(8)
	root.add_child(controls)
	controls.add_child(UIKit.label("Enemies", 13, UIKit.MUTED))
	_size_picker = _picker(GameData.ENCOUNTER_SIZES.keys(), 1)
	_size_picker.tooltip_text = "How much monster threat the encounter gets, relative to your party."
	controls.add_child(_size_picker)
	_surprise_picker = _picker(SURPRISE_OPTIONS, 0)
	_surprise_picker.tooltip_text = "The surprised side uses Defense (Exclude Dodge) until each unit acts; the other side acts first."
	controls.add_child(_surprise_picker)
	_new_button = UIKit.button("New battle", "Roll a new group of monsters and start the fight.")
	_new_button.pressed.connect(start_battle)
	controls.add_child(_new_button)
	controls.add_child(VSeparator.new())
	_step_button = UIKit.button("Next turn", "Resolve one unit's turn.")
	_step_button.pressed.connect(step_once)
	controls.add_child(_step_button)
	_auto_button = UIKit.button("Auto-play")
	_auto_button.toggle_mode = true
	_auto_button.toggled.connect(_on_auto_toggled)
	controls.add_child(_auto_button)
	_speed_picker = _picker(SPEEDS.keys(), 1)
	_speed_picker.item_selected.connect(func(_index: int) -> void: _apply_speed())
	controls.add_child(_speed_picker)
	_finish_button = UIKit.button("Skip to result", "Resolve the rest of the fight at once.")
	_finish_button.pressed.connect(finish_now)
	controls.add_child(_finish_button)
	controls.add_child(UIKit.spacer())
	_camp_button = UIKit.button("Make camp", "Rest: full HP and spell slots. Only between fights.")
	_camp_button.pressed.connect(_on_camp)
	controls.add_child(_camp_button)

	# ---- battlefield
	var field := UIKit.hbox(10)
	root.add_child(field)
	field.add_child(_build_grid("YOUR PARTY", UIKit.ALLY, [2, 1, 0], _party_cells))
	var center := UIKit.vbox(6)
	center.custom_minimum_size = Vector2(150, 0)
	center.alignment = BoxContainer.ALIGNMENT_CENTER
	field.add_child(center)
	_round_label = UIKit.label("", 16, UIKit.GOLD, true)
	_round_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	center.add_child(_round_label)
	_banner = UIKit.label("", 15, UIKit.TEXT, true)
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	center.add_child(_banner)
	field.add_child(_build_grid("ENEMIES", UIKit.ENEMY, [0, 1, 2], _enemy_cells))

	# ---- log + turn order
	var bottom := UIKit.hbox(10)
	bottom.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(bottom)
	var log_panel := UIKit.panel(UIKit.PANEL_DARK)
	log_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bottom.add_child(log_panel)
	_log = RichTextLabel.new()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.selection_enabled = true
	_log.add_theme_font_size_override("normal_font_size", 14)
	_log.add_theme_font_size_override("bold_font_size", 14)
	_log.add_theme_constant_override("line_separation", 4)
	log_panel.add_child(_log)
	var order_panel := UIKit.panel(UIKit.PANEL_DARK)
	order_panel.custom_minimum_size = Vector2(250, 0)
	bottom.add_child(order_panel)
	_order = RichTextLabel.new()
	_order.bbcode_enabled = true
	_order.add_theme_font_size_override("normal_font_size", 13)
	_order.add_theme_font_size_override("bold_font_size", 13)
	order_panel.add_child(_order)

	_timer = Timer.new()
	_timer.one_shot = false
	_timer.timeout.connect(step_once)
	add_child(_timer)
	Game.changed.connect(_refresh_buttons)


func _picker(items: Array, selected: int) -> OptionButton:
	var picker := OptionButton.new()
	picker.focus_mode = Control.FOCUS_NONE
	for item: String in items:
		picker.add_item(item)
	picker.select(selected)
	return picker


## rows = the order rows appear left to right, so both front rows meet in the middle.
func _build_grid(title: String, color: Color, rows: Array, cells: Array) -> Control:
	var box := UIKit.vbox(4)
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var caption := UIKit.label(title, 13, color, true)
	caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(caption)
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 5)
	grid.add_theme_constant_override("v_separation", 5)
	box.add_child(grid)
	cells.resize(9)
	for row: int in rows:
		var head := UIKit.label(GameData.ROWS[row], 12, UIKit.MUTED)
		head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		grid.add_child(head)
	for lane in 3:
		for row: int in rows:
			var cell := UnitCell.new()
			cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			cell.custom_minimum_size = Vector2(120, 78)
			cell.mouse_default_cursor_shape = Control.CURSOR_ARROW
			grid.add_child(cell)
			cells[row * 3 + lane] = cell
	return box


func on_show() -> void:
	if combat == null:
		_log.clear()
		_log.append_text("[color=#9aa0a8]Pick an encounter size and press [b]New battle[/b]. Your party fights on its own, following each member's tactics profile. HP and spell slots carry over between fights until you make camp.[/color]\n")
	_refresh()


func is_fighting() -> bool:
	return combat != null and not combat.finished


## Drops the current fight without resolving it (used by New game).
func abandon_battle() -> void:
	_stop_auto()
	combat = null
	Game.in_battle = false
	_log.clear()
	_refresh()


# ------------------------------------------------------------------ actions
func start_battle() -> void:
	_stop_auto()
	var members := Game.prepare_party_for_battle()
	var able := 0
	for unit: Unit in members:
		if unit.is_standing():
			able += 1
	_log.clear()
	if members.is_empty():
		combat = null
		_log.append_text("[color=#f08a78]No party. Open Party and place 4–6 adventurers on the formation grid.[/color]\n")
		_refresh()
		return
	if able == 0:
		combat = null
		_log.append_text("[color=#f08a78]Nobody in the party can stand. Make camp to recover first.[/color]\n")
		_refresh()
		return

	var size_name: String = _size_picker.get_item_text(_size_picker.selected)
	var encounter: Dictionary = EncounterGenerator.generate(members, size_name)
	_encounter_name = encounter["theme"]
	var foes: Array = encounter["units"]
	combat = Combat.new()
	combat.setup(members, foes, SURPRISE_VALUES[_surprise_picker.selected], Game.retreat_threshold)
	Game.in_battle = true
	_log.append_text("[b]%s[/b] [color=#9aa0a8]— %s, %d enemies against your %d.[/color]\n" % [_encounter_name, size_name.to_lower(), foes.size(), members.size()])
	combat.step()  # surprise + initiative
	_flush()
	_refresh()
	Game.changed.emit()


func step_once() -> void:
	if not is_fighting():
		_stop_auto()
		return
	combat.step()
	_flush()
	if combat.finished:
		_on_finished()
	_refresh()


func finish_now() -> void:
	if not is_fighting():
		return
	_stop_auto()
	combat.run_to_end()
	_flush()
	_on_finished()
	_refresh()


func _on_finished() -> void:
	_stop_auto()
	Game.in_battle = false
	Game.battles_fought += 1
	if combat.outcome == "victory":
		Game.battles_won += 1
		var threat := 0.0
		for unit: Unit in combat.enemies:
			threat += unit.threat
		var reward := int(round(threat * GameData.GOLD_PER_THREAT))
		Game.gold += reward
		_log.append_text("[color=#e2b85a]Loot: +%d gold.[/color]\n" % reward)
	var downed: Array[String] = []
	for unit: Unit in combat.party:
		if unit.is_downed():
			downed.append(unit.unit_name)
	if not downed.is_empty():
		_log.append_text("[color=#9aa0a8]Stabilized after the fight: %s. They stay Downed until the party makes camp.[/color]\n" % ", ".join(downed))
	var lost: Array = Game.bury_dead()
	for unit: Unit in lost:
		_log.append_text("[color=#f08a78]%s is dead and leaves the roster. Dead expeditioners stay dead.[/color]\n" % unit.unit_name)
	Game.changed.emit()


func _on_camp() -> void:
	Game.make_camp()
	_log.append_text("[color=#8fd68f]The party makes camp. HP and spell slots are restored.[/color]\n")
	_refresh()


func _on_auto_toggled(on: bool) -> void:
	if on and is_fighting():
		_apply_speed()
		_timer.start()
	else:
		_stop_auto()


func _apply_speed() -> void:
	_timer.wait_time = float(SPEEDS[_speed_picker.get_item_text(_speed_picker.selected)])


func _stop_auto() -> void:
	_timer.stop()
	_auto_button.set_pressed_no_signal(false)


# ------------------------------------------------------------------ drawing
func _flush() -> void:
	if combat == null:
		return
	for line: String in combat.take_new_lines():
		_log.append_text(line + "\n")


func _refresh_buttons() -> void:
	var fighting := is_fighting()
	_step_button.disabled = not fighting
	_auto_button.disabled = not fighting
	_finish_button.disabled = not fighting
	_camp_button.disabled = fighting
	_new_button.tooltip_text = "Abandon this fight and roll a new group of monsters." if fighting else "Roll a new group of monsters and start the fight."


func _refresh() -> void:
	_refresh_buttons()
	var party_units: Array = combat.party if combat != null else Game.prepare_party_for_battle()
	var enemy_units: Array = combat.enemies if combat != null else []
	_draw_side(_party_cells, party_units)
	_draw_side(_enemy_cells, enemy_units)

	if combat == null:
		_round_label.text = "VS"
		_banner.text = ""
		_order.clear()
		return
	_round_label.text = "Round %d" % maxi(combat.round_num, 1)
	if combat.finished:
		var colors := {"victory": UIKit.GOOD, "defeat": UIKit.BAD, "retreat": UIKit.GOLD, "draw": UIKit.GOLD}
		_banner.text = combat.outcome.to_upper()
		_banner.add_theme_color_override("font_color", colors.get(combat.outcome, UIKit.TEXT))
	else:
		_banner.text = _encounter_name
		_banner.add_theme_color_override("font_color", UIKit.MUTED)
	_draw_order()


func _draw_side(cells: Array, units: Array) -> void:
	var by_slot := {}
	for unit: Unit in units:
		var slot := unit.row * 3 + unit.lane
		var current: Unit = by_slot.get(slot, null)
		# If a body and a standing unit share a slot, show the one still standing.
		if current == null or (unit.is_standing() and not current.is_standing()) or (current.dead and not unit.dead):
			by_slot[slot] = unit
	for slot in 9:
		var unit: Unit = by_slot.get(slot, null)
		var highlight := ""
		if combat != null and unit != null:
			if unit == combat.active:
				highlight = "active"
			elif combat.last_targets.has(unit):
				highlight = "target"
		(cells[slot] as UnitCell).show_unit(unit, highlight)


func _draw_order() -> void:
	_order.clear()
	_order.append_text("[b]Turn order[/b]\n")
	for unit: Unit in combat.order:
		var color := "#8fc1ff" if unit.side == 0 else "#ff9d8a"
		var marker := "▶ " if unit == combat.active else "    "
		var line := "%s[color=%s]%s[/color] [color=#9aa0a8]%d[/color]" % [marker, color, unit.unit_name, unit.initiative]
		if not unit.is_standing():
			line = "    [color=#5f6570][s]%s[/s]  %s[/color]" % [unit.unit_name, unit.status_text().to_lower()]
		_order.append_text(line + "\n")
