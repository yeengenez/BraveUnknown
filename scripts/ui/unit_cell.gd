class_name UnitCell
extends Button
## One slot of a 3x3 formation grid. Used on the Party and Battle screens.

var unit: Unit = null
var _name: Label
var _sub: Label
var _bar: ProgressBar
var _hp: Label


func _init() -> void:
	custom_minimum_size = Vector2(148, 84)
	focus_mode = Control.FOCUS_NONE
	clip_contents = true
	var body := VBoxContainer.new()
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_theme_constant_override("separation", 2)
	body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, 7)
	body.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(body)
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
	show_unit(null)


## highlight: "" | "selected" | "active" | "target"
func show_unit(p_unit: Unit, highlight: String = "", empty_text: String = "") -> void:
	unit = p_unit
	var bg := UIKit.PANEL_ALT
	var border := UIKit.BORDER
	var width := 1
	if unit == null:
		_name.text = ""
		_sub.text = empty_text
		_hp.text = ""
		_bar.visible = false
		_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		tooltip_text = ""
		bg = UIKit.PANEL_DARK
		border = Color("#2a2e36")
	else:
		_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		_name.text = unit.unit_name
		_sub.text = unit.title()
		_bar.visible = true
		_bar.max_value = unit.max_hp
		_bar.value = maxi(unit.hp, 0)
		var status := unit.status_text()
		_hp.text = "HP %d/%d%s" % [unit.hp, unit.max_hp, ("  ·  " + status) if status != "" else ""]
		var side_color := UIKit.ENEMY if unit.side == 1 else UIKit.ALLY
		_name.add_theme_color_override("font_color", side_color if unit.is_standing() else UIKit.MUTED)
		_hp.add_theme_color_override("font_color", UIKit.TEXT if unit.is_standing() else UIKit.BAD)
		var fraction := unit.hp_fraction()
		var fill := UIKit.GOOD.darkened(0.25) if fraction > 0.5 else (UIKit.GOLD.darkened(0.15) if fraction > 0.25 else UIKit.BAD.darkened(0.15))
		_bar.add_theme_stylebox_override("fill", UIKit.box(fill, fill, 0, 3, 0))
		tooltip_text = UIKit.sheet(unit)
		if not unit.is_standing():
			bg = UIKit.PANEL_DARK
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
	var normal := UIKit.box(bg, border, width, 6, 6)
	var hover := UIKit.box(bg.lightened(0.06), border if highlight != "" else UIKit.GOLD.darkened(0.35), width, 6, 6)
	add_theme_stylebox_override("normal", normal)
	add_theme_stylebox_override("hover", hover)
	add_theme_stylebox_override("pressed", hover)
	add_theme_stylebox_override("disabled", normal)
