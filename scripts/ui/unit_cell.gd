class_name UnitCell
extends Control
## One slot of a 3x3 formation grid, used on the Party and Battle screens.
##
## The slot itself stays put inside its GridContainer; the visible "card" is a
## free child that can lunge, dodge, shake and flash without the container
## snapping it back.

signal pressed

const HIT_FLASH := Color(1.0, 0.35, 0.25)
const CRIT_FLASH := Color(1.0, 0.85, 0.35)

var unit: Unit = null
var card: Button
var _name: Label
var _sub: Label
var _bar: ProgressBar
var _hp: Label
var _flash: Panel
var _portrait: UnitPortrait
var _body: VBoxContainer
var _glow: Panel
var _move_tween: Tween
var _flash_tween: Tween
var _glow_tween: Tween
var _bar_tween: Tween

## Battle screen only: units with battle sprites (BattleSprites) stand on the tile as a figure
## instead of a card, and swap single frames (set_pose).
var allow_sprites := false
var _sprite_mode := false
var _sprite_root: Control
var _floor: Control
var _sprite: TextureRect
var _sprite_fx: TextureRect
var _frames: Dictionary = {}
var _frames_key := ""
var _pose := ""
var _pose_down := false
var _floor_color := Color(0, 0, 0, 0.35)
var _sprite_tween: Tween
const PLATE_H := 24.0


func _init() -> void:
	custom_minimum_size = Vector2(148, 84)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	card = Button.new()
	card.focus_mode = Control.FOCUS_NONE
	card.clip_contents = true
	card.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card.pressed.connect(func() -> void: pressed.emit())
	add_child(card)

	# Coloured outline that pulses when the unit acts (behind the card).
	_glow = Panel.new()
	_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_glow.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_glow.offset_left = -5
	_glow.offset_top = -5
	_glow.offset_right = 5
	_glow.offset_bottom = 5
	_glow.show_behind_parent = true
	_glow.modulate.a = 0.0
	card.add_child(_glow)

	_portrait = UnitPortrait.new()
	_portrait.corner = 4
	_portrait.crop = "face"
	card.add_child(_portrait)

	var body := VBoxContainer.new()
	_body = body
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_theme_constant_override("separation", 2)
	body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, 7)
	body.alignment = BoxContainer.ALIGNMENT_CENTER
	card.add_child(body)
	card.resized.connect(_layout)
	_name = UIKit.label("", 14, UIKit.TEXT, true)
	_sub = UIKit.label("", 12, UIKit.MUTED)
	_hp = UIKit.label("", 12, UIKit.TEXT)
	_bar = ProgressBar.new()
	_bar.show_percentage = false
	_bar.custom_minimum_size = Vector2(0, 7)
	for node: Control in [_name, _sub, _bar, _hp]:
		node.mouse_filter = Control.MOUSE_FILTER_IGNORE
		body.add_child(node)
	for text_label: Label in [_name, _sub, _hp]:
		text_label.clip_text = true
		text_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

	# Full-card colour wash for hits and heals (above the content).
	_flash = Panel.new()
	_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_flash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_flash.add_theme_stylebox_override("panel", UIKit.box(Color.WHITE, Color.WHITE, 0, 6, 0))
	_flash.modulate.a = 0.0
	card.add_child(_flash)

	# Sprite figure (battle): floor shadow, frame, effect layer. Drawn behind the name plate.
	_sprite_root = Control.new()
	_sprite_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sprite_root.visible = false
	card.add_child(_sprite_root)
	card.move_child(_sprite_root, _glow.get_index() + 1)
	_floor = Control.new()
	_floor.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_floor.draw.connect(_draw_floor)
	_sprite_root.add_child(_floor)
	_sprite = TextureRect.new()
	_sprite_fx = TextureRect.new()
	for rect: TextureRect in [_sprite, _sprite_fx]:
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_SCALE
		rect.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		_sprite_root.add_child(rect)
	show_unit(null)


## Portrait on the left, text to its right. In sprite mode: figure on the tile, plate at the bottom.
func _layout() -> void:
	if _sprite_mode:
		_portrait.visible = false
		_body.offset_left = 4.0
		_body.offset_right = -4.0
		_body.offset_top = card.size.y - PLATE_H
		_body.offset_bottom = -1.0
		_layout_sprite()
		return
	_body.offset_top = 7.0
	_body.offset_right = -7.0
	_body.offset_bottom = -7.0
	var side := clampf(card.size.y - 12.0, 0.0, 62.0)
	var has_portrait := unit != null and not unit.look.is_empty() and side >= 24.0
	_portrait.visible = has_portrait
	_portrait.position = Vector2(6, (card.size.y - side) / 2.0)
	_portrait.size = Vector2(side, side)
	_body.offset_left = (side + 12.0) if has_portrait else 7.0


## highlight: "" | "selected" | "active" | "target"
## hp / dead override what is drawn, so the battle screen can hold back a
## result until the blow lands. hp = -9999 means "use the unit's real values".
func show_unit(p_unit: Unit, highlight: String = "", empty_text: String = "", hp: int = -9999, dead: int = -1, animate_bar: bool = false) -> void:
	var changed := p_unit != unit
	unit = p_unit
	_set_sprite_mode(allow_sprites and unit != null and BattleSprites.has_sprites(unit), changed)
	_layout()
	var bg := UIKit.PANEL_ALT
	var border := UIKit.BORDER
	var width := 1
	if unit == null:
		_name.text = ""
		_sub.text = empty_text
		_hp.text = ""
		_bar.visible = false
		_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		card.tooltip_text = ""
		bg = UIKit.PANEL_DARK
		border = Color("#2a2e36")
	else:
		var shown_hp := unit.hp if hp == -9999 else hp
		var is_dead := unit.dead if dead < 0 else dead == 1
		var standing := shown_hp > 0 and not is_dead
		var status := "Dead" if is_dead else ("Downed" if shown_hp <= 0 else "")
		_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		_name.text = unit.unit_name
		_sub.text = unit.title()
		_bar.visible = true
		_bar.max_value = unit.max_hp
		var bar_value := float(maxi(shown_hp, 0))
		if _bar_tween != null:
			_bar_tween.kill()
		if animate_bar and absf(_bar.value - bar_value) > 0.01:
			_bar_tween = create_tween()
			_bar_tween.tween_property(_bar, "value", bar_value, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		else:
			_bar.value = bar_value
		_hp.text = "HP %d/%d%s" % [shown_hp, unit.max_hp, ("  ·  " + status) if status != "" else ""]
		var side_color := UIKit.ENEMY if unit.side == 1 else UIKit.ALLY
		_name.add_theme_color_override("font_color", side_color if standing else UIKit.MUTED)
		_hp.add_theme_color_override("font_color", UIKit.TEXT if standing else UIKit.BAD)
		var fraction := clampf(float(shown_hp) / float(unit.max_hp), 0.0, 1.0)
		var fill := UIKit.GOOD.darkened(0.25) if fraction > 0.5 else (UIKit.GOLD.darkened(0.15) if fraction > 0.25 else UIKit.BAD.darkened(0.15))
		_bar.add_theme_stylebox_override("fill", UIKit.box(fill, fill, 0, 3, 0))
		card.tooltip_text = UIKit.sheet(unit)
		if not standing:
			bg = UIKit.PANEL_DARK
		card.modulate = Color(1, 1, 1, 0.55) if is_dead else Color.WHITE
		_portrait.show_unit(unit, not standing)
		if _sprite_mode:
			_name.text = "%s  %d/%d%s" % [unit.unit_name, shown_hp, unit.max_hp, ("  · " + status) if status != "" else ""]
			_name.add_theme_color_override("font_color", side_color if standing else UIKit.BAD)
			_sprite.modulate = Color(0.55, 0.55, 0.6) if not standing else Color.WHITE
			if changed or _pose == "" or (not standing) != _pose_down:
				set_pose("stand" if standing else "hit")  # downed / dead: recoil frame, greyed
			_pose_down = not standing
	match highlight:
		"selected":
			border = UIKit.GOLD
			width = 2
		"active":
			border = UIKit.GOLD
			width = 3
			bg = Color("#3a3323")
		"target":
			border = UIKit.BAD
			width = 3
			bg = Color("#3a2826")
		"ally_target":
			border = UIKit.GOOD
			width = 3
			bg = Color("#24352a")
	if _sprite_mode:
		var plate := StyleBoxEmpty.new()
		for state: String in ["normal", "hover", "pressed", "disabled"]:
			card.add_theme_stylebox_override(state, plate)
		_floor_color = {"active": Color(UIKit.GOLD, 0.75), "target": Color(UIKit.BAD, 0.75),
			"ally_target": Color(UIKit.GOOD, 0.7), "selected": Color(UIKit.GOLD, 0.6)}.get(highlight, Color(0, 0, 0, 0.35))
		_floor.queue_redraw()
		return
	var normal := UIKit.box(bg, border, width, 6, 6)
	var hover := UIKit.box(bg.lightened(0.06), border if highlight != "" else UIKit.GOLD.darkened(0.35), width, 6, 6)
	card.add_theme_stylebox_override("normal", normal)
	card.add_theme_stylebox_override("hover", hover)
	card.add_theme_stylebox_override("pressed", hover)
	card.add_theme_stylebox_override("disabled", normal)


func card_center() -> Vector2:
	if _sprite_mode and _sprite.size.x > 0.0:
		# middle of the figure's torso
		var s := _sprite.size.y / BattleSprites.canvas(unit.class_id).y
		var feet := BattleSprites.feet(unit.class_id)
		return _sprite.get_global_rect().position + Vector2(feet.x, feet.y - 95.0) * s
	return card.get_global_rect().get_center()


# ------------------------------------------------------------------ sprite mode
func has_sprite() -> bool:
	return _sprite_mode


func _set_sprite_mode(on: bool, changed: bool) -> void:
	if on != _sprite_mode:
		_sprite_mode = on
		_sprite_root.visible = on
		_sub.visible = not on
		_hp.visible = not on
		_glow.visible = not on
		_flash.visible = not on
		card.clip_contents = not on
		_name.add_theme_font_size_override("font_size", 12 if on else 14)
		_bar.custom_minimum_size = Vector2(0, 5 if on else 7)
		_pose = ""
	if on:
		var key := "%d|%s" % [unit.uid, JSON.stringify(unit.look)]
		if key != _frames_key:
			_frames = BattleSprites.frames_for(unit)
			_frames_key = key
			_pose = ""


## Swap to one frame (stand, ready, attack, hit, slash_left, slash_right, finish). Missing frames
## fall back to stand.
func set_pose(state: String) -> void:
	if not _sprite_mode:
		return
	if not _frames.has(state):
		state = "stand"
	_pose = state
	var frame: Array = _frames.get(state, [null, null])
	_sprite.texture = frame[0]
	_sprite_fx.texture = frame[1]
	_sprite_fx.visible = frame[1] != null


func pose() -> String:
	return _pose


func _layout_sprite() -> void:
	if unit == null:
		return
	var canvas := BattleSprites.canvas(unit.class_id)
	var feet := BattleSprites.feet(unit.class_id)
	var ground := card.size.y - PLATE_H + 2.0
	var s := (ground - 2.0) / 196.0  # stand figure: ~190 px from the helmet top to the feet
	var size_px := canvas * s
	var pos := Vector2(card.size.x * 0.5 - feet.x * s, ground - feet.y * s)
	for rect: TextureRect in [_sprite, _sprite_fx]:
		rect.position = pos
		rect.size = size_px
	_floor.position = Vector2.ZERO
	_floor.size = card.size
	_floor.set_meta("feet", Vector2(card.size.x * 0.5, ground))
	_floor.set_meta("scale", s)
	_floor.queue_redraw()


func _draw_floor() -> void:
	if not _sprite_mode or not _floor.has_meta("feet"):
		return
	var at: Vector2 = _floor.get_meta("feet")
	var s: float = _floor.get_meta("scale")
	var points := PackedVector2Array()
	for i in 28:
		var a := TAU * i / 28.0
		points.append(at + Vector2(cos(a) * 62.0 * s, sin(a) * 13.0 * s))
	_floor.draw_colored_polygon(points, _floor_color)


# ------------------------------------------------------------------ motion
func _new_move_tween() -> Tween:
	if _move_tween != null:
		_move_tween.kill()
	card.z_index = 10
	_move_tween = create_tween()
	return _move_tween


func _settle() -> void:
	card.z_index = 0


## Stops every animation and puts the card back in its slot.
func reset_motion() -> void:
	for tween: Tween in [_move_tween, _flash_tween, _glow_tween]:
		if tween != null:
			tween.kill()
	card.position = Vector2.ZERO
	card.rotation = 0.0
	card.scale = Vector2.ONE
	card.z_index = 0
	_flash.modulate.a = 0.0
	_glow.modulate.a = 0.0
	if _sprite_tween != null:
		_sprite_tween.kill()
	_sprite.self_modulate = Color.WHITE


## Melee: pull back, then dash toward `toward` (global position).
## Returns the time until the blow lands.
func lunge(toward: Vector2, time_scale: float) -> float:
	var dir := (toward - card_center())
	var reach := clampf(dir.length() - 70.0, 24.0, 110.0)
	dir = dir.normalized()
	var wind := 0.10 * time_scale
	var dash := 0.11 * time_scale
	card.pivot_offset = card.size / 2.0
	var tween := _new_move_tween()
	tween.tween_property(card, "position", -dir * 10.0, wind).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tween.tween_property(card, "position", dir * reach, dash).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	return wind + dash


## Return to the slot after a lunge or recoil.
func return_home(time_scale: float) -> void:
	var tween := _new_move_tween()
	tween.tween_property(card, "position", Vector2.ZERO, 0.22 * time_scale).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_callback(_settle)


## Ranged and spells: a short kick backward away from `toward`.
func recoil(toward: Vector2, time_scale: float) -> void:
	var dir := (toward - card_center()).normalized()
	var tween := _new_move_tween()
	tween.tween_property(card, "position", -dir * 9.0, 0.06 * time_scale).set_ease(Tween.EASE_OUT)
	tween.tween_property(card, "position", Vector2.ZERO, 0.18 * time_scale).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_callback(_settle)


## Struck: knocked back away from `from` and shaken. Crits hit harder.
func take_hit(from: Vector2, heavy: bool, time_scale: float) -> void:
	var dir := (card_center() - from).normalized()
	var push := 20.0 if heavy else 11.0
	var shake := 7.0 if heavy else 4.0
	var tween := _new_move_tween()
	tween.tween_property(card, "position", dir * push, 0.05 * time_scale).set_ease(Tween.EASE_OUT)
	for i in 4:
		var side := Vector2(dir.y, -dir.x) * shake * (1.0 if i % 2 == 0 else -1.0) * (1.0 - i * 0.2)
		tween.tween_property(card, "position", dir * push * 0.5 + side, 0.04 * time_scale)
	tween.tween_property(card, "position", Vector2.ZERO, 0.16 * time_scale).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_callback(_settle)
	flash(CRIT_FLASH if heavy else HIT_FLASH, 0.85, time_scale)


## Missed: side-steps out of the way and back.
func dodge(from: Vector2, time_scale: float) -> void:
	var dir := (card_center() - from).normalized()
	var side := Vector2(-dir.y, dir.x)
	if absf(side.y) < 0.3:
		side = Vector2(0, -1)
	var tween := _new_move_tween()
	tween.tween_property(card, "position", side * 16.0 + dir * 6.0, 0.08 * time_scale).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tween.tween_interval(0.08 * time_scale)
	tween.tween_property(card, "position", Vector2.ZERO, 0.16 * time_scale).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_callback(_settle)


## Slides in from another slot (formation moves, row collapse).
func slide_from(global_from: Vector2, time_scale: float) -> void:
	card.global_position = global_from
	var tween := _new_move_tween()
	tween.tween_property(card, "position", Vector2.ZERO, 0.32 * time_scale).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	tween.tween_callback(_settle)


## A colour wash over the whole card that fades out.
func flash(color: Color, strength: float, time_scale: float) -> void:
	if _sprite_mode:
		if _sprite_tween != null:
			_sprite_tween.kill()
		_sprite.self_modulate = Color(1, 1, 1).lerp(color * 2.2, clampf(strength, 0.0, 1.0))
		_sprite_tween = create_tween()
		_sprite_tween.tween_property(_sprite, "self_modulate", Color.WHITE, 0.38 * time_scale).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		return
	if _flash_tween != null:
		_flash_tween.kill()
	_flash.self_modulate = color
	_flash.modulate.a = strength
	_flash_tween = create_tween()
	_flash_tween.tween_property(_flash, "modulate:a", 0.0, 0.38 * time_scale).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


## The acting unit's outline pulses in its action colour.
func glow(color: Color, time_scale: float) -> void:
	if _sprite_mode:
		_floor_color = Color(color, 0.85)
		_floor.queue_redraw()
		return
	if _glow_tween != null:
		_glow_tween.kill()
	_glow.add_theme_stylebox_override("panel", UIKit.box(Color(color, 0.0), color, 3, 9, 0))
	_glow.modulate.a = 1.0
	_glow_tween = create_tween()
	_glow_tween.tween_property(_glow, "modulate:a", 0.0, 0.55 * time_scale).set_delay(0.15 * time_scale)
