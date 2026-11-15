extends Control
## Root of the prototype: top bar (gold, navigation) and the three screens.

const SCREENS := ["Guild", "Party", "Battle"]

var _gold_label: Label
var _info_label: Label
var _nav := {}
var _screens := {}
var _current := ""


func _ready() -> void:
	theme = UIKit.make_theme()

	var background := ColorRect.new()
	background.color = UIKit.BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 12)
	add_child(margin)

	var root := UIKit.vbox(10)
	margin.add_child(root)
	root.add_child(_build_top_bar())

	var content := Control.new()
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(content)

	_screens["Guild"] = GuildScreen.new()
	_screens["Party"] = PartyScreen.new()
	_screens["Battle"] = BattleScreen.new()
	for screen_name: String in SCREENS:
		var screen: Control = _screens[screen_name]
		screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		screen.visible = false
		content.add_child(screen)
	(_screens["Party"] as PartyScreen).go_to_battle.connect(show_screen.bind("Battle"))
	(_screens["Battle"] as BattleScreen).go_to_party.connect(show_screen.bind("Party"))

	Game.changed.connect(_refresh_top_bar)
	_refresh_top_bar()
	show_screen("Guild")


func _build_top_bar() -> Control:
	var bar := UIKit.panel(UIKit.PANEL_DARK, UIKit.BORDER, 8)
	var row := UIKit.hbox(10)
	bar.add_child(row)
	row.add_child(UIKit.label("EXPEDITION: BRAVE UNKNOWN", 18, UIKit.GOLD, true))
	row.add_child(UIKit.label("prototype", 12, UIKit.MUTED))
	var gap := Control.new()
	gap.custom_minimum_size = Vector2(16, 0)
	row.add_child(gap)
	for screen_name: String in SCREENS:
		var nav_button := UIKit.button("  %s  " % screen_name)
		nav_button.toggle_mode = true
		nav_button.pressed.connect(show_screen.bind(screen_name))
		row.add_child(nav_button)
		_nav[screen_name] = nav_button
	row.add_child(UIKit.spacer())
	_info_label = UIKit.label("", 13, UIKit.MUTED)
	row.add_child(_info_label)
	_gold_label = UIKit.label("", 18, UIKit.GOLD, true)
	row.add_child(_gold_label)
	var debug := UIKit.button("+500 g", "Test helper: adds 500 gold.")
	debug.pressed.connect(Game.add_gold.bind(500))
	row.add_child(debug)
	var restart := UIKit.button("New game", "Start over: 1,000 gold, empty roster.")
	restart.pressed.connect(_on_new_game)
	row.add_child(restart)
	return bar


func _on_new_game() -> void:
	(_screens["Battle"] as BattleScreen).abandon_battle()
	Game.new_game()
	show_screen("Guild")


func _refresh_top_bar() -> void:
	_gold_label.text = "%d g" % Game.gold
	_info_label.text = "Roster %d/%d   ·   Party %d/%d   ·   Won %d of %d   " % [
		Game.roster.size(), GameData.ROSTER_CAP, Game.party_size(), GameData.PARTY_MAX,
		Game.battles_won, Game.battles_fought,
	]


func show_screen(screen_name: String) -> void:
	_current = screen_name
	for other: String in SCREENS:
		(_screens[other] as Control).visible = other == screen_name
		(_nav[other] as Button).set_pressed_no_signal(other == screen_name)
	(_screens[screen_name] as Control).call("on_show")
