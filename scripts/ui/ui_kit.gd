class_name UIKit
extends RefCounted
## Colors, theme and small widget helpers shared by every screen.

const BG := Color("#16181d")
const PANEL := Color("#22262e")
const PANEL_ALT := Color("#2b303a")
const PANEL_DARK := Color("#1b1e24")
const BORDER := Color("#3a404c")
const GOLD := Color("#e2b85a")
const TEXT := Color("#e8e4d8")
const MUTED := Color("#9aa0a8")
const GOOD := Color("#8fd68f")
const BAD := Color("#f08a78")
const ALLY := Color("#8fc1ff")
const ENEMY := Color("#ff9d8a")

static var _bold: Font = null


static func bold_font() -> Font:
	if _bold == null:
		var variation := FontVariation.new()
		variation.base_font = ThemeDB.fallback_font
		variation.variation_embolden = 0.7
		_bold = variation
	return _bold


static func box(bg: Color, border: Color = BORDER, border_width: int = 1, radius: int = 6, pad: int = 10) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(border_width)
	style.set_corner_radius_all(radius)
	style.set_content_margin_all(pad)
	return style


static func make_theme() -> Theme:
	var theme := Theme.new()
	theme.default_font_size = 15

	theme.set_color("font_color", "Label", TEXT)
	theme.set_color("default_color", "RichTextLabel", TEXT)
	theme.set_font("bold_font", "RichTextLabel", bold_font())
	theme.set_stylebox("panel", "PanelContainer", box(PANEL))

	for type: String in ["Button", "OptionButton"]:
		theme.set_stylebox("normal", type, box(PANEL_ALT, BORDER, 1, 5, 8))
		theme.set_stylebox("hover", type, box(Color("#353c49"), GOLD.darkened(0.3), 1, 5, 8))
		theme.set_stylebox("pressed", type, box(Color("#3c3320"), GOLD, 1, 5, 8))
		theme.set_stylebox("disabled", type, box(PANEL_DARK, Color("#2a2e36"), 1, 5, 8))
		theme.set_stylebox("focus", type, StyleBoxEmpty.new())
		theme.set_color("font_color", type, TEXT)
		theme.set_color("font_hover_color", type, Color.WHITE)
		theme.set_color("font_pressed_color", type, GOLD)
		theme.set_color("font_hover_pressed_color", type, GOLD)
		theme.set_color("font_disabled_color", type, Color("#5f6570"))

	theme.set_stylebox("background", "ProgressBar", box(Color("#101216"), Color("#101216"), 0, 3, 0))
	theme.set_stylebox("fill", "ProgressBar", box(GOOD.darkened(0.25), GOOD.darkened(0.25), 0, 3, 0))
	theme.set_stylebox("panel", "TooltipPanel", box(Color("#0f1115"), GOLD.darkened(0.4), 1, 4, 8))
	theme.set_color("font_color", "TooltipLabel", TEXT)
	theme.set_stylebox("normal", "LineEdit", box(PANEL_DARK, BORDER, 1, 4, 6))
	theme.set_stylebox("panel", "PopupMenu", box(PANEL_ALT, BORDER, 1, 4, 6))
	return theme


static func label(text: String, size: int = 15, color: Color = TEXT, bold: bool = false) -> Label:
	var node := Label.new()
	node.text = text
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", color)
	if bold:
		node.add_theme_font_override("font", bold_font())
	return node


static func wrapped(text: String, size: int = 13, color: Color = MUTED) -> Label:
	var node := label(text, size, color)
	node.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	node.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return node


static func button(text: String, tooltip: String = "") -> Button:
	var node := Button.new()
	node.text = text
	node.tooltip_text = tooltip
	node.focus_mode = Control.FOCUS_NONE
	return node


static func panel(bg: Color = PANEL, border: Color = BORDER, pad: int = 10) -> PanelContainer:
	var node := PanelContainer.new()
	node.add_theme_stylebox_override("panel", box(bg, border, 1, 6, pad))
	return node


static func vbox(separation: int = 6) -> VBoxContainer:
	var node := VBoxContainer.new()
	node.add_theme_constant_override("separation", separation)
	return node


static func hbox(separation: int = 8) -> HBoxContainer:
	var node := HBoxContainer.new()
	node.add_theme_constant_override("separation", separation)
	return node


static func spacer() -> Control:
	var node := Control.new()
	node.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return node


static func clear(node: Node) -> void:
	for child: Node in node.get_children():
		node.remove_child(child)
		child.queue_free()


## Full character sheet as plain text (tooltips and the detail panel).
static func sheet(unit: Unit) -> String:
	var lines: Array[String] = []
	lines.append("%s — %s" % [unit.unit_name, unit.title()])
	if not unit.is_monster:
		lines.append(unit.abilities_text())
	lines.append("HP %d/%d   Initiative %s" % [unit.hp, unit.max_hp, GameData.signed(unit.init_mod)])
	lines.append(unit.defense_text())
	lines.append(unit.weapon_text())
	if unit.offhand_text() != "":
		lines.append(unit.offhand_text())
	if unit.armor_text() != "":
		lines.append("Armor: " + unit.armor_text())
	if unit.caster_type != "":
		lines.append("%s caster — %s" % [unit.caster_type.capitalize(), unit.slots_text()])
		lines.append("Spells: " + unit.spells_text())
		if unit.spell_failure > 0:
			lines.append("Arcane spell failure %d%%" % unit.spell_failure)
	lines.append("Tactics: " + unit.tactic)
	return "\n".join(lines)
