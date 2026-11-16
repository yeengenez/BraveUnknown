class_name BattleScreen
extends Control
## Test battles: your party against a random group of monsters. The fight
## plays itself; you can step turn by turn, auto-play or skip to the result.
##
## Each turn is resolved by Combat at once, then played back as animation:
## the actor lights up, an arrow points at its target, the actor lunges or
## shoots, and the target flashes, shakes or dodges with a floating number.
## Cards show HP as it was *before* each blow until that blow lands.

signal go_to_party

const SURPRISE_OPTIONS := ["No surprise", "Party surprises", "Party ambushed"]
const SURPRISE_VALUES := [0, 1, -1]
## Animation time scale per speed setting (1.0 = full length).
const SPEEDS := {"1×": 1.0, "2×": 0.55, "4×": 0.3, "8×": 0.15}
const TURN_PAUSE := 0.35  ## gap between turns in auto-play, before scaling

var combat: Combat = null
var _encounter_name := ""
var _party_cells: Array = []  ## index = row * 3 + lane
var _enemy_cells: Array = []
var _log: RichTextLabel
var _order: RichTextLabel
var _banner: Label
var _round_label: Label
var _action: RichTextLabel
var _field_root: Control
var _fx: BattleFx
var _size_picker: OptionButton
var _surprise_picker: OptionButton
var _speed_picker: OptionButton
var _new_button: Button
var _step_button: Button
var _auto_button: Button
var _finish_button: Button
var _camp_button: Button

## What each card shows right now: uid -> [hp, dead]. Updated blow by blow.
var _shown := {}
## Highlights during playback: uid -> "active" | "target" | "ally_target".
var _marks := {}
## Which cell drew each unit last time, to slide units that changed slot.
var _last_cell := {}
var _busy := false
var _auto := false
var _skip_requested := false
var _battle_id := 0  ## bumps on every new/abandoned battle; stale animations stop


func _init() -> void:
	_field_root = UIKit.vbox(8)
	_field_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_field_root)
	var root := _field_root

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
	_step_button = UIKit.button("Next turn", "Play one unit's turn.")
	_step_button.pressed.connect(func() -> void: step_once())
	controls.add_child(_step_button)
	_auto_button = UIKit.button("Auto-play")
	_auto_button.toggle_mode = true
	_auto_button.toggled.connect(_on_auto_toggled)
	controls.add_child(_auto_button)
	_speed_picker = _picker(SPEEDS.keys(), 0)
	_speed_picker.tooltip_text = "Animation speed."
	controls.add_child(_speed_picker)
	_finish_button = UIKit.button("Skip to result", "Resolve the rest of the fight at once, without animation.")
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
	center.custom_minimum_size = Vector2(170, 0)
	center.alignment = BoxContainer.ALIGNMENT_CENTER
	field.add_child(center)
	_round_label = UIKit.label("", 16, UIKit.GOLD, true)
	_round_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	center.add_child(_round_label)
	_banner = UIKit.label("", 15, UIKit.TEXT, true)
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	center.add_child(_banner)
	_action = RichTextLabel.new()
	_action.bbcode_enabled = true
	_action.fit_content = true
	_action.scroll_active = false
	_action.custom_minimum_size = Vector2(170, 92)
	_action.add_theme_font_size_override("normal_font_size", 14)
	_action.add_theme_font_size_override("bold_font_size", 15)
	center.add_child(_action)
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

	# Effects draw over everything on this screen.
	_fx = BattleFx.new()
	_fx.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_fx)

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
			cell.card.mouse_default_cursor_shape = Control.CURSOR_ARROW
			grid.add_child(cell)
			cells[row * 3 + lane] = cell
	return box


func on_show() -> void:
	if combat == null:
		_log.clear()
		_log.append_text("[color=#9aa0a8]Pick an encounter size and press [b]New battle[/b]. Your party fights on its own, following each member's tactics profile. HP and spell slots carry over between fights until you make camp.[/color]\n")
	_sync_shown()
	_refresh(false)


func is_fighting() -> bool:
	return combat != null and not combat.finished


func is_animating() -> bool:
	return _busy


## Drops the current fight without resolving it (used by New game).
func abandon_battle() -> void:
	_stop_auto()
	_battle_id += 1
	_busy = false
	_reset_visuals()
	combat = null
	Game.in_battle = false
	_log.clear()
	_action.clear()
	_sync_shown()
	_refresh(false)


# ------------------------------------------------------------------ actions
func start_battle() -> void:
	_stop_auto()
	_battle_id += 1
	_busy = false
	_skip_requested = false
	_reset_visuals()
	var members := Game.prepare_party_for_battle()
	var able := 0
	for unit: Unit in members:
		if unit.is_standing():
			able += 1
	_log.clear()
	_action.clear()
	if members.is_empty():
		combat = null
		Game.in_battle = false
		_log.append_text("[color=#f08a78]No party. Open Party and place 4–6 adventurers on the formation grid.[/color]\n")
		_sync_shown()
		_refresh(false)
		return
	if able == 0:
		combat = null
		Game.in_battle = false
		_log.append_text("[color=#f08a78]Nobody in the party can stand. Make camp to recover first.[/color]\n")
		_sync_shown()
		_refresh(false)
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
	combat.take_events()
	_flush()
	_sync_shown()
	_last_cell.clear()
	_refresh(false)
	_play_entrance()
	Game.changed.emit()


## Plays one unit's turn with animation. Await it to know when it is done.
func step_once() -> void:
	if not is_fighting() or _busy:
		return
	_busy = true
	_refresh_buttons()
	var id := _battle_id
	var time_scale := _time_scale()

	combat.step()
	_flush()
	var events := combat.take_events()
	if combat.finished:
		_on_finished(false)  # book loot and losses now; the banner waits for the animation

	# Row collapse and lane side-steps: slide cards to their new slots first.
	_marks.clear()
	if _refresh(true, time_scale):
		await _wait(0.34 * time_scale)
		if id != _battle_id:
			return

	for event: Dictionary in events:
		await _play_event(event, time_scale)
		if id != _battle_id:
			return

	_marks.clear()
	_sync_shown()
	_refresh(false)
	if combat.finished:
		_show_outcome()
	_busy = false
	_refresh_buttons()
	if _skip_requested:
		_skip_requested = false
		finish_now()


func finish_now() -> void:
	if not is_fighting():
		return
	_stop_auto()
	if _busy:
		_skip_requested = true  # finish once the current blow has landed
		return
	combat.run_to_end()
	combat.take_events()
	_flush()
	_reset_visuals()
	_marks.clear()
	_sync_shown()
	_refresh(false)
	_action.clear()
	_on_finished()


func _on_finished(show_now: bool = true) -> void:
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
	if show_now:
		_show_outcome()
	Game.changed.emit()


func _on_camp() -> void:
	Game.make_camp()
	_log.append_text("[color=#8fd68f]The party makes camp. HP and spell slots are restored.[/color]\n")
	_sync_shown()
	_refresh(false)
	for unit: Unit in Game.prepare_party_for_battle():
		var cell := _cell_of(unit)
		if cell != null:
			cell.flash(UIKit.GOOD, 0.5, 1.0)


func _on_auto_toggled(on: bool) -> void:
	_auto = on
	if on:
		_auto_loop()


func _auto_loop() -> void:
	var id := _battle_id
	while _auto and is_fighting() and id == _battle_id:
		if _busy:
			await get_tree().process_frame
			continue
		await step_once()
		if not _auto or id != _battle_id:
			break
		await _wait(TURN_PAUSE * _time_scale())
	_stop_auto()


func _stop_auto() -> void:
	_auto = false
	if _auto_button != null:
		_auto_button.set_pressed_no_signal(false)


func _time_scale() -> float:
	return float(SPEEDS[_speed_picker.get_item_text(_speed_picker.selected)])


func _wait(seconds: float) -> void:
	await get_tree().create_timer(maxf(seconds, 0.0)).timeout


# ------------------------------------------------------------------ playback
func _play_event(event: Dictionary, time_scale: float) -> void:
	var actor: Unit = event["actor"]
	var actor_cell := _cell_of(actor)
	var impacts: Array = event["impacts"]
	var type: String = event["type"]
	var fx: String = event["fx"]
	var color := BattleFx.color_for(fx)
	var id := _battle_id

	# 1. Spotlight: who acts, on whom.
	_marks.clear()
	_marks[actor.uid] = "active"
	for impact: Dictionary in impacts:
		var target: Unit = impact["target"]
		if target != actor:
			_marks[target.uid] = "ally_target" if target.side == actor.side else "target"
	_refresh(false)
	_show_action(event)
	_highlight_order(actor)
	if actor_cell == null:
		return

	match type:
		"hold":
			actor_cell.glow(UIKit.MUTED, time_scale)
			_fx.float_text(actor_cell.card_center(), "HOLD", UIKit.MUTED, 15, 0.7 * time_scale, 26.0)
			await _wait(0.45 * time_scale)
			return
		"move":
			actor_cell.glow(UIKit.ALLY if actor.side == 0 else UIKit.ENEMY, time_scale)
			_fx.float_text(actor_cell.card_center(), "SIDE-STEP", UIKit.TEXT, 15, 0.7 * time_scale, 26.0)
			await _wait(0.45 * time_scale)
			return
		"fizzle":
			actor_cell.glow(color, time_scale)
			await _wait(0.25 * time_scale)
			actor_cell.flash(UIKit.MUTED, 0.6, time_scale)
			_fx.float_text(actor_cell.card_center(), "FIZZLE", UIKit.MUTED, 18, 0.8 * time_scale, 30.0)
			await _wait(0.55 * time_scale)
			return

	var targets: Array = []
	for impact: Dictionary in impacts:
		var cell := _cell_of(impact["target"])
		targets.append(cell)
	var aim := actor_cell.card_center()
	if not targets.is_empty() and targets[0] != null:
		aim = (targets[0] as UnitCell).card_center()

	# 2. Wind-up: the actor glows in its action colour.
	actor_cell.glow(color if type == "spell" else UIKit.GOLD, time_scale)
	await _wait(0.2 * time_scale)
	if id != _battle_id:
		return

	# 3. Delivery: a lunge for melee, a missile for everything else.
	var kind := ""
	if type == "spell":
		kind = String(GameData.SPELLS[event["spell"]]["kind"])
	var from := actor_cell.card_center()
	if type == "attack" and not event["ranged"]:
		var land := actor_cell.lunge(aim, time_scale)
		await _wait(land)
	elif type == "attack":
		actor_cell.recoil(aim, time_scale)
		await _fx.missile(from, aim, BattleFx.weapon_missile(String(event["label"])), time_scale).finished
	elif kind == "bolt":
		# One missile per bolt, fired in a quick burst.
		actor_cell.recoil(aim, time_scale)
		var count := int(event.get("count", 1))
		var last: Tween = null
		for i in count:
			var spread := Vector2(0, (i - (count - 1) / 2.0) * 14.0)
			last = _fx.missile(from + spread, aim, BattleFx.spell_missile(fx), time_scale, 0.08 * i * time_scale)
		await last.finished
	elif kind in ["ray", "area"]:
		actor_cell.recoil(aim, time_scale)
		var last: Tween = null
		for i in targets.size():
			var cell: UnitCell = targets[i]
			if cell != null:
				last = _fx.missile(from, cell.card_center(), BattleFx.spell_missile(fx), time_scale, 0.05 * i * time_scale)
		if last != null:
			await last.finished
	else:  # heal, buff: a mote flies to each ally (self-targeted ones just glow)
		var last: Tween = null
		for i in targets.size():
			var cell: UnitCell = targets[i]
			if cell != null and cell != actor_cell:
				last = _fx.missile(from, cell.card_center(), BattleFx.spell_missile(fx), time_scale, 0.04 * i * time_scale)
		if last != null:
			await last.finished
		else:
			await _wait(0.25 * time_scale)
	if id != _battle_id:
		return

	# 4. Impact on every target at once.
	var any_crit := false
	var any_down := false
	for i in impacts.size():
		var impact: Dictionary = impacts[i]
		var cell: UnitCell = targets[i]
		if cell == null:
			continue
		var target: Unit = impact["target"]
		var center := cell.card_center()
		match String(impact["result"]):
			"miss":
				if type == "attack" and not event["ranged"]:
					_fx.strike(center, from, fx, false, true, 0.42 * time_scale)
				cell.dodge(from, time_scale)
				_fx.float_text(center, "MISS", UIKit.MUTED, 20, 0.75 * time_scale, 30.0)
			"hit", "crit":
				var crit: bool = impact["result"] == "crit"
				any_crit = any_crit or crit
				if type == "attack" and not event["ranged"]:
					_fx.strike(center, from, fx, crit, false, 0.46 * time_scale)
				else:
					_fx.splash(center, from, UIKit.GOLD if crit else color, crit, 0.36 * time_scale)
				cell.take_hit(from, crit, time_scale)
				if crit:
					_fx.float_text(center + Vector2(0, -26), "CRITICAL!", UIKit.GOLD, 17, 0.95 * time_scale, 40.0)
					_fx.float_text(center, "-%d" % int(impact["amount"]), UIKit.GOLD, 34, 1.0 * time_scale, 52.0)
				else:
					_fx.float_text(center, "-%d" % int(impact["amount"]), Color("#ff6b5a"), 26, 0.85 * time_scale)
			"heal":
				cell.flash(UIKit.GOOD, 0.7, time_scale)
				_fx.sparkle(center, UIKit.GOOD, 0.8 * time_scale)
				_fx.float_text(center, "+%d" % int(impact["amount"]), UIKit.GOOD, 26, 0.85 * time_scale)
				if impact["revived"]:
					_fx.float_text(center + Vector2(0, 24), "BACK UP!", UIKit.GOOD, 15, 1.0 * time_scale, 36.0)
			"buff":
				cell.flash(UIKit.GOLD, 0.45, time_scale)
				_fx.sparkle(center, UIKit.GOLD, 0.7 * time_scale)
				_fx.float_text(center, "+%d ATK" % int(impact["amount"]), UIKit.GOLD, 16, 0.8 * time_scale, 30.0)
		# Now the card may show the new HP.
		if impact["result"] != "miss":
			_shown[target.uid] = [int(impact["hp_after"]), 1 if impact["dead_after"] else 0]
		if impact["dead"]:
			any_down = true
			_fx.float_text(center + Vector2(0, 26), "SLAIN", UIKit.BAD, 20, 1.1 * time_scale, 20.0)
		elif impact["downed"]:
			any_down = true
			_fx.float_text(center + Vector2(0, 26), "DOWNED", UIKit.BAD, 18, 1.1 * time_scale, 20.0)
		_draw_cell(cell, target, true)

	if any_crit:
		_screen_shake(9.0, time_scale)
	elif any_down:
		_screen_shake(4.0, time_scale)

	# 5. Recover.
	if type == "attack" and not event["ranged"]:
		await _wait(0.08 * time_scale)
		if id != _battle_id:
			return
		actor_cell.return_home(time_scale)
	await _wait((0.5 if any_crit or any_down else 0.38) * time_scale)


func _screen_shake(strength: float, time_scale: float) -> void:
	var tween := create_tween()
	for i in 6:
		var offset := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * strength * (1.0 - i / 6.0)
		tween.tween_property(_field_root, "position", offset, 0.035 * maxf(time_scale, 0.5))
	tween.tween_property(_field_root, "position", Vector2.ZERO, 0.05)


## Enemies slide in from the right edge when a battle starts.
func _play_entrance() -> void:
	var time_scale := _time_scale()
	for slot in 9:
		var cell: UnitCell = _enemy_cells[slot]
		if cell.unit != null:
			cell.slide_from(cell.card.global_position + Vector2(260 + (2 - slot / 3) * 20, 0), time_scale * (1.0 + (slot / 3) * 0.15))


## The centre caption: "Wolf A ⟶ Bite ⟶ Jorund · HIT 7".
func _show_action(event: Dictionary) -> void:
	var actor: Unit = event["actor"]
	var impacts: Array = event["impacts"]
	var who := "[b][color=%s]%s[/color][/b]" % [_side_hex(actor), actor.unit_name]
	var text := "[center]%s\n" % who
	match String(event["type"]):
		"hold":
			text += "[color=#9aa0a8]holds position[/color]"
		"move":
			text += "[color=#9aa0a8]side-steps to the %s lane[/color]" % GameData.LANES[actor.lane].to_lower()
		"fizzle":
			text += "[color=#f08a78]%s — spell lost[/color]" % event["label"]
		_:
			text += "[color=#e2b85a]⟶ %s ⟶[/color]\n" % event["label"]
			if impacts.size() == 1:
				var impact: Dictionary = impacts[0]
				var target: Unit = impact["target"]
				text += "[b][color=%s]%s[/color][/b]\n%s" % [_side_hex(target), target.unit_name, _result_text(impact)]
			else:
				text += "[color=#9aa0a8]%d targets[/color]" % impacts.size()
	_action.clear()
	_action.append_text(text + "[/center]")


func _result_text(impact: Dictionary) -> String:
	match String(impact["result"]):
		"miss":
			return "[color=#9aa0a8]MISS[/color]"
		"crit":
			return "[color=#e2b85a][b]CRITICAL %d[/b][/color]" % int(impact["amount"])
		"heal":
			return "[color=#8fd68f]+%d HP[/color]" % int(impact["amount"])
		"buff":
			return "[color=#e2b85a]+%d attack[/color]" % int(impact["amount"])
	var extra := ""
	if impact["dead"]:
		extra = " · slain"
	elif impact["downed"]:
		extra = " · downed"
	return "[color=#f08a78]HIT %d%s[/color]" % [int(impact["amount"]), extra]


func _side_hex(unit: Unit) -> String:
	return "#8fc1ff" if unit.side == 0 else "#ff9d8a"


func _show_outcome() -> void:
	_action.clear()
	var colors := {"victory": "#8fd68f", "defeat": "#f08a78", "retreat": "#e2b85a", "draw": "#e2b85a"}
	_action.append_text("[center][font_size=26][b][color=%s]%s[/color][/b][/font_size][/center]" % [colors.get(combat.outcome, "#e8e4d8"), combat.outcome.to_upper()])


# ------------------------------------------------------------------ drawing
func _flush() -> void:
	if combat == null:
		return
	for line: String in combat.take_new_lines():
		_log.append_text(line + "\n")


## Copies real HP into what the cards show (between turns, after camp).
func _sync_shown() -> void:
	_shown.clear()
	var units: Array = combat.all_units if combat != null else Game.prepare_party_for_battle()
	for unit: Unit in units:
		_shown[unit.uid] = [unit.hp, 1 if unit.dead else 0]


func _reset_visuals() -> void:
	_fx.clear()
	_field_root.position = Vector2.ZERO
	for cell: UnitCell in _party_cells + _enemy_cells:
		cell.reset_motion()
	_marks.clear()


func _refresh_buttons() -> void:
	var fighting := is_fighting()
	_step_button.disabled = not fighting or _busy
	_auto_button.disabled = not fighting
	_finish_button.disabled = not fighting
	_camp_button.disabled = fighting
	_new_button.tooltip_text = "Abandon this fight and roll a new group of monsters." if fighting else "Roll a new group of monsters and start the fight."


## Redraws both grids. With slide on, units that changed slot glide over.
## Returns true if anything slid.
func _refresh(slide: bool, time_scale: float = 1.0) -> bool:
	_refresh_buttons()
	var party_units: Array = combat.party if combat != null else Game.prepare_party_for_battle()
	var enemy_units: Array = combat.enemies if combat != null else []
	var moved := _draw_side(_party_cells, party_units, slide, time_scale)
	moved = _draw_side(_enemy_cells, enemy_units, slide, time_scale) or moved

	if combat == null:
		_round_label.text = "VS"
		_banner.text = ""
		_order.clear()
		return moved
	_round_label.text = "Round %d" % maxi(combat.round_num, 1)
	if combat.finished:
		var colors := {"victory": UIKit.GOOD, "defeat": UIKit.BAD, "retreat": UIKit.GOLD, "draw": UIKit.GOLD}
		_banner.text = combat.outcome.to_upper()
		_banner.add_theme_color_override("font_color", colors.get(combat.outcome, UIKit.TEXT))
	else:
		_banner.text = _encounter_name
		_banner.add_theme_color_override("font_color", UIKit.MUTED)
	_highlight_order(combat.active)
	return moved


func _shown_hp(unit: Unit) -> int:
	return int(_shown.get(unit.uid, [unit.hp, 0])[0])


func _shown_dead(unit: Unit) -> bool:
	return int(_shown.get(unit.uid, [unit.hp, 1 if unit.dead else 0])[1]) == 1


func _draw_cell(cell: UnitCell, unit: Unit, animate_bar: bool = false) -> void:
	if unit == null:
		cell.show_unit(null)
		return
	cell.show_unit(unit, _marks.get(unit.uid, ""), "", _shown_hp(unit), 1 if _shown_dead(unit) else 0, animate_bar)


func _draw_side(cells: Array, units: Array, slide: bool, time_scale: float) -> bool:
	var by_slot := {}
	for unit: Unit in units:
		var slot := unit.row * 3 + unit.lane
		var current: Unit = by_slot.get(slot, null)
		# If a body and a standing unit share a slot, show the one still standing.
		var standing := _shown_hp(unit) > 0 and not _shown_dead(unit)
		var current_standing := current != null and _shown_hp(current) > 0 and not _shown_dead(current)
		if current == null or (standing and not current_standing) or (_shown_dead(current) and not _shown_dead(unit)):
			by_slot[slot] = unit
	var moved := false
	for slot in 9:
		var unit: Unit = by_slot.get(slot, null)
		var cell: UnitCell = cells[slot]
		_draw_cell(cell, unit)
		if unit == null:
			continue
		var previous: UnitCell = _last_cell.get(unit.uid, null)
		if slide and previous != null and previous != cell and is_instance_valid(previous):
			cell.slide_from(previous.global_position, time_scale)
			moved = true
		_last_cell[unit.uid] = cell
	return moved


func _cell_of(unit: Unit) -> UnitCell:
	for cell: UnitCell in _party_cells + _enemy_cells:
		if cell.unit == unit:
			return cell
	return null


func _highlight_order(current: Unit) -> void:
	_order.clear()
	if combat == null:
		return
	_order.append_text("[b]Turn order[/b]\n")
	for unit: Unit in combat.order:
		var color := _side_hex(unit)
		var standing := _shown_hp(unit) > 0 and not _shown_dead(unit)
		var line := ""
		if not standing:
			line = "    [color=#5f6570][s]%s[/s]  %s[/color]" % [unit.unit_name, "dead" if _shown_dead(unit) else "downed"]
		elif unit == current:
			line = "[bgcolor=#3a3323][color=#e2b85a]▶ [/color][b][color=%s]%s[/color][/b] [color=#9aa0a8]%d[/color][/bgcolor]" % [color, unit.unit_name, unit.initiative]
		else:
			line = "    [color=%s]%s[/color] [color=#9aa0a8]%d[/color]" % [color, unit.unit_name, unit.initiative]
		_order.append_text(line + "\n")
