class_name GuildScreen
extends Control
## The adventurers' guild: six pre-rolled recruits for hire, a paid refresh,
## and your roster.

var _cards: GridContainer
var _refresh_button: Button
var _roster_title: Label
var _roster_list: VBoxContainer
var _hint: Label
var _queued := false


func _init() -> void:
	var columns := UIKit.hbox(12)
	columns.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(columns)

	# ---- left: offers
	var left := UIKit.vbox(8)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_stretch_ratio = 3.0
	columns.add_child(left)

	var header := UIKit.hbox(10)
	left.add_child(header)
	var titles := UIKit.vbox(0)
	titles.add_child(UIKit.label("Adventurers' Guild", 22, UIKit.TEXT, true))
	titles.add_child(UIKit.label("Recruits come pre-rolled (25-point buy). Better recruits cost more gold.", 13, UIKit.MUTED))
	header.add_child(titles)
	header.add_child(UIKit.spacer())
	_refresh_button = UIKit.button("")
	_refresh_button.pressed.connect(func() -> void: Game.refresh_offers())
	header.add_child(_refresh_button)

	_cards = GridContainer.new()
	_cards.columns = 3
	_cards.add_theme_constant_override("h_separation", 10)
	_cards.add_theme_constant_override("v_separation", 10)
	_cards.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(_cards)

	# ---- right: roster
	var right_panel := UIKit.panel(UIKit.PANEL_DARK)
	right_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_panel.size_flags_stretch_ratio = 1.25
	columns.add_child(right_panel)
	var right := UIKit.vbox(8)
	right_panel.add_child(right)
	_roster_title = UIKit.label("", 18, UIKit.TEXT, true)
	right.add_child(_roster_title)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	right.add_child(scroll)
	_roster_list = UIKit.vbox(6)
	_roster_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_roster_list)
	_hint = UIKit.wrapped("", 13, UIKit.MUTED)
	right.add_child(_hint)

	Game.changed.connect(refresh)


func on_show() -> void:
	refresh()


## Rebuilds are deferred so a button is never freed inside its own signal.
func refresh() -> void:
	if _queued or not is_inside_tree() or not visible:
		return
	_queued = true
	_rebuild.call_deferred()


func _rebuild() -> void:
	_queued = false
	_refresh_button.text = "  New faces  (%d g)  " % GameData.REFRESH_COST
	_refresh_button.disabled = not Game.can_refresh()
	_refresh_button.tooltip_text = "Pay %d gold to replace the whole list with new adventurers." % GameData.REFRESH_COST

	UIKit.clear(_cards)
	for index in Game.offers.size():
		_cards.add_child(_offer_card(index))

	_roster_title.text = "Your roster  (%d/%d)" % [Game.roster.size(), GameData.ROSTER_CAP]
	UIKit.clear(_roster_list)
	if Game.roster.is_empty():
		_roster_list.add_child(UIKit.wrapped("Nobody yet. Hire 4–6 adventurers to form a party.", 14, UIKit.MUTED))
	for unit: Unit in Game.roster:
		_roster_list.add_child(_roster_row(unit))
	_hint.text = "Next: open Party to place 4–6 members on the 3×3 formation grid, then Battle to test them."


func _offer_card(index: int) -> Control:
	var recruit: Unit = Game.offers[index]
	var card := UIKit.panel(UIKit.PANEL if recruit != null else UIKit.PANEL_DARK)
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.size_flags_vertical = Control.SIZE_EXPAND_FILL
	card.custom_minimum_size = Vector2(230, 250)
	var body := UIKit.vbox(4)
	card.add_child(body)
	if recruit == null:
		var gone := UIKit.label("Hired", 16, UIKit.MUTED, true)
		gone.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		gone.size_flags_vertical = Control.SIZE_EXPAND_FILL
		gone.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		body.add_child(gone)
		var note := UIKit.wrapped("This seat stays empty until the list is refreshed.", 12, UIKit.MUTED)
		note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		body.add_child(note)
		return card

	var top := UIKit.hbox(10)
	body.add_child(top)
	var face := UnitPortrait.new()
	face.custom_minimum_size = Vector2(96, 96)
	face.show_unit(recruit)
	top.add_child(face)
	var heading := UIKit.vbox(1)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(heading)
	var name_label := UIKit.label(recruit.unit_name, 16, UIKit.TEXT, true)
	name_label.clip_text = true
	name_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	heading.add_child(name_label)
	heading.add_child(UIKit.label(recruit.title(), 14, UIKit.ALLY))
	heading.add_child(UIKit.label("%d g" % recruit.cost, 17, UIKit.GOLD, true))
	heading.add_child(UIKit.label("HP %d · Def %d · Init %s" % [recruit.max_hp, recruit.defense(), GameData.signed(recruit.init_mod)], 12, UIKit.MUTED))

	var scores := GridContainer.new()
	scores.columns = 6
	scores.add_theme_constant_override("h_separation", 4)
	for ability: String in GameData.ABILITIES:
		var score: int = recruit.abilities[ability]
		var chip := UIKit.panel(UIKit.PANEL_DARK, Color("#2a2e36"), 3)
		chip.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var chip_body := UIKit.vbox(0)
		chip.add_child(chip_body)
		var ability_label := UIKit.label(ability, 10, UIKit.MUTED)
		ability_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		var score_label := UIKit.label(str(score), 15, UIKit.GOLD if score >= 16 else UIKit.TEXT, score >= 14)
		score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		chip_body.add_child(ability_label)
		chip_body.add_child(score_label)
		chip.tooltip_text = "%s %d (modifier %s)" % [ability, score, GameData.signed(Unit.ability_mod(score))]
		scores.add_child(chip)
	body.add_child(scores)

	body.add_child(UIKit.wrapped(recruit.weapon_text(), 13, UIKit.TEXT))
	body.add_child(UIKit.wrapped("Armor: " + recruit.armor_text(), 13, UIKit.MUTED))
	if recruit.caster_type != "":
		body.add_child(UIKit.wrapped("%s · %s" % [recruit.caster_type.capitalize(), recruit.slots_text()], 13, UIKit.MUTED))

	var filler := Control.new()
	filler.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(filler)

	var hire := UIKit.button("Hire")
	hire.disabled = not Game.can_hire(index)
	if Game.roster.size() >= GameData.ROSTER_CAP:
		hire.text = "Roster full"
	elif Game.gold < recruit.cost:
		hire.text = "Not enough gold"
	hire.pressed.connect(func() -> void: Game.hire(index))
	body.add_child(hire)
	card.tooltip_text = UIKit.sheet(recruit)
	return card


func _roster_row(unit: Unit) -> Control:
	var row_panel := UIKit.panel(UIKit.PANEL, UIKit.BORDER, 6)
	var row := UIKit.hbox(8)
	row_panel.add_child(row)
	var face := UnitPortrait.new()
	face.custom_minimum_size = Vector2(44, 44)
	face.corner = 4
	face.crop = "face"
	face.show_unit(unit)
	row.add_child(face)
	var text := UIKit.vbox(0)
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(text)
	var name_label := UIKit.label(unit.unit_name, 15, UIKit.TEXT, true)
	name_label.clip_text = true
	text.add_child(name_label)
	var slot := Game.slot_of(unit)
	var where := "not in party" if slot < 0 else "%s · %s" % [GameData.ROWS[slot / 3], GameData.LANES[slot % 3]]
	text.add_child(UIKit.label("%s   HP %d/%d   %s" % [unit.title(), unit.hp, unit.max_hp, where], 12, UIKit.MUTED))
	var dismiss := UIKit.button("Dismiss", "Remove from the roster. No refund.")
	dismiss.pressed.connect(func() -> void: Game.dismiss(unit))
	row.add_child(dismiss)
	row_panel.tooltip_text = UIKit.sheet(unit)
	return row_panel
