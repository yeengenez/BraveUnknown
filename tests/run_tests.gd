extends SceneTree
## Headless rule checks and balance simulation. No UI needed.
##
##   godot --headless --path . -s tests/run_tests.gd
##   godot --headless --path . -s tests/run_tests.gd -- --battles=1000
##
## (Open the project in the editor once first so Godot indexes the classes.)

var failures := 0
var checks := 0


func _init() -> void:
	var battles := 300
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--battles="):
			battles = int(arg.trim_prefix("--battles="))
	Dice.rng.seed = 20261115
	_test_doc_example()
	_test_point_buy()
	_test_formation_rules()
	_test_downed_and_death()
	_test_dual_wield_and_sprites()
	_simulate(battles)
	print("\n%d checks, %d failed" % [checks, failures])
	quit(1 if failures > 0 else 0)


func check(label: String, got: Variant, want: Variant) -> void:
	checks += 1
	if got != want:
		failures += 1
		print("  FAIL %s: got %s, want %s" % [label, got, want])


func _make(class_id: String, level: int, scores: Dictionary, weapon: String, armor: String, shield: String = "") -> Unit:
	var unit := Unit.new()
	unit.class_id = class_id
	unit.level = level
	for ability: String in scores:
		unit.abilities[ability] = scores[ability]
	unit.weapon_id = weapon
	unit.armor_id = armor
	unit.shield_id = shield
	unit.unit_name = class_id.capitalize()
	unit.recalc(true)
	return unit


## Doc "Worked example". The doc's Fighter also has two feats (+1 dodge
## Defense, +1 attack) and the feat list is not designed, so expected values
## here are the doc's numbers minus those feats.
func _test_doc_example() -> void:
	print("Worked example from the doc")
	var fighter := _make("soldier", 3, {"STR": 16, "DEX": 13, "CON": 14}, "longsword", "breastplate", "heavy_shield")
	check("Fighter HP", fighter.max_hp, 36)
	check("Fighter Defense (doc 20 incl. +1 feat)", fighter.defense(), 19)
	check("Fighter Defense excl. armor (doc 12 incl. +1 feat)", fighter.defense_no_armor(), 11)
	check("Fighter Defense excl. dodge", fighter.defense_no_dodge(), 18)
	check("Fighter longsword attack (doc +7 incl. +1 feat)", fighter.attack_bonus, 6)
	check("Fighter damage bonus", fighter.damage_bonus, 3)

	var wizard := _make("mage", 3, {"INT": 17, "DEX": 14, "CON": 12, "WIS": 12}, "dagger", "robes")
	check("Wizard HP", wizard.max_hp, 21)
	check("Wizard Defense", wizard.defense(), 12)
	check("Wizard Defense excl. armor", wizard.defense_no_armor(), 12)
	check("Wizard ray attack (BAB + DEX)", wizard.bab + wizard.dex_mod, 3)
	check("Wizard init", wizard.init_mod, 2)
	check("Wizard slots (2+1 bonus L1, 1+1 bonus L2)", wizard.slots_max, [3, 2])
	var combat := Combat.new()
	check("L1 auto-hit spell at CL3 is 2d4+2 (avg 7)", combat.spell_damage_dice("arcane_bolt", 3), [2, 4, 2])

	var orc := EncounterGenerator.make_monster("orc_raider")
	check("Orc HP", orc.max_hp, 13)
	check("Orc Defense", orc.defense(), 14)
	check("Orc Defense excl. armor", orc.defense_no_armor(), 10)
	check("Orc attack", orc.attack_bonus, 5)

	var two_hander := _make("soldier", 1, {"STR": 16}, "greatsword", "scale_mail")
	check("Two-handed damage = 1.5 x STR mod", two_hander.damage_bonus, 4)
	var heavy := _make("soldier", 1, {"DEX": 16}, "longsword", "splint_mail")
	check("Heavy armor caps DEX (max +0)", heavy.dodge_bonus, 0)
	check("Heavy armor initiative -2", heavy.init_mod, 1)
	var archer := _make("archer", 2, {"DEX": 16, "STR": 14}, "longbow", "leather")
	check("Bow attack uses DEX", archer.attack_bonus, 5)
	check("Bow adds no STR to damage", archer.damage_bonus, 0)
	var cleric := _make("cleric", 3, {"WIS": 16}, "longsword", "scale_mail", "light_shield")
	check("Cleric BAB 3/4", cleric.bab, 2)
	check("Divine casters ignore spell failure", cleric.spell_failure, 0)
	var armored_mage := _make("mage", 1, {"INT": 16}, "dagger", "chain_shirt")
	check("Arcane failure in chain shirt", armored_mage.spell_failure, 20)


func _test_point_buy() -> void:
	print("Point buy (25 points)")
	var bad := 0
	var by_class := {}
	for i in 3000:
		var recruit := RecruitGenerator.make()
		by_class[recruit.class_label] = int(by_class.get(recruit.class_label, 0)) + 1
		var spent := RecruitGenerator.points_spent(recruit.abilities)
		var in_range := true
		for ability: String in GameData.ABILITIES:
			var score: int = recruit.abilities[ability]
			if score < 10 or score > 18:
				in_range = false
		if spent != GameData.POINT_BUY_BUDGET or not in_range or recruit.max_hp < 1 or recruit.cost <= 0:
			bad += 1
	check("3000 recruits spend exactly 25 points, scores 10-18", bad, 0)
	print("  class mix: %s" % [by_class])


func _grid(unit: Unit, side: int, row: int, lane: int) -> Unit:
	unit.side = side
	unit.row = row
	unit.lane = lane
	return unit


func _test_formation_rules() -> void:
	print("Formation rules")
	var sword := _grid(_make("soldier", 1, {"STR": 16}, "longsword", "scale_mail"), 0, 0, 0)
	var halberd_mid := _grid(_make("soldier", 1, {"STR": 16}, "halberd", "scale_mail"), 0, 1, 1)
	var sword_mid := _grid(_make("soldier", 1, {"STR": 16}, "longsword", "scale_mail"), 0, 1, 2)
	var bow := _grid(_make("archer", 1, {"DEX": 16}, "longbow", "leather"), 0, 2, 1)
	var e_front_left := _grid(EncounterGenerator.make_monster("goblin_cutter"), 1, 0, 0)
	var e_front_right := _grid(EncounterGenerator.make_monster("goblin_cutter"), 1, 0, 2)
	var e_mid_center := _grid(EncounterGenerator.make_monster("goblin_cutter"), 1, 1, 1)
	var e_back := _grid(EncounterGenerator.make_monster("goblin_archer"), 1, 2, 1)
	var combat := Combat.new()
	combat.setup([sword, halberd_mid, sword_mid, bow], [e_front_left, e_front_right, e_mid_center, e_back])

	check("Left-lane sword cannot hit the right lane", combat.melee_targets(sword).has(e_front_right), false)
	check("Sword must take the front row", combat.melee_targets(sword), [e_front_left])
	check("Sword in the middle row cannot attack", combat.melee_targets(sword_mid).is_empty(), true)
	check("Halberd attacks from the middle row", combat.melee_targets(halberd_mid).size(), 2)
	check("Halberd from the middle does not reach the enemy middle", combat.melee_targets(halberd_mid).has(e_mid_center), false)
	check("Bow can target any row", combat.weapon_targets(bow).size(), 4)
	check("Front unit is engaged", combat.is_engaged(sword), true)
	check("Back unit is not engaged", combat.is_engaged(bow), false)

	halberd_mid.row = 0
	check("Halberd in front reaches the middle row", combat.melee_targets(halberd_mid).has(e_mid_center), true)
	halberd_mid.row = 1

	# Empty lane in front exposes the units behind it.
	e_front_left.hp = 0
	e_front_right.hp = 0
	check("Front row down: middle row can be hit", combat.melee_targets(sword), [e_mid_center])
	combat._collapse(1)
	check("Collapse moves the middle row to the front", e_mid_center.row, 0)
	check("Collapse moves the back row to the middle", e_back.row, 1)

	# Surprise: Defense (Exclude Dodge) until the unit acts.
	combat.surprise = 1
	var normal: int = e_mid_center.defense()
	check("Surprised enemy loses dodge", combat.defense_for(e_mid_center, false)[0], normal - e_mid_center.dodge_bonus)
	e_mid_center.has_acted = true
	check("...until it acts", combat.defense_for(e_mid_center, false)[0], normal)


func _test_downed_and_death() -> void:
	print("Downed and death")
	var soldier := _grid(_make("soldier", 1, {"CON": 14}, "longsword", "scale_mail"), 0, 0, 1)
	var combat := Combat.new()
	combat.setup([soldier], [_grid(EncounterGenerator.make_monster("giant_rat"), 1, 0, 1)])
	combat._apply_damage(soldier, soldier.hp + 3)
	check("At 0 or below: Downed", soldier.is_downed(), true)
	check("Downed is not dead", soldier.dead, false)
	combat._apply_heal(soldier, 10)
	check("Healed in combat: stands again", soldier.is_standing(), true)
	combat._apply_damage(soldier, soldier.hp + 14)
	check("At -CON score: dead", soldier.dead, true)


func _test_dual_wield_and_sprites() -> void:
	print("Dual wield, first Guild list, battle sprites")
	var dual := RecruitGenerator.make([], "soldier", 1, "dual_shortswords")
	check("Dual loadout has an off-hand short sword", dual.offhand_id, "shortsword")
	check("Short sword from the weapon sheet: 1d6 19-20", [int(dual.weapon["sides"]), int(dual.weapon["threat"])], [6, 19])
	var greataxe := RecruitGenerator.make([], "soldier", 1, "greataxe")
	check("Greataxe from the weapon sheet: 1d12 x3", [int(greataxe.weapon["sides"]), int(greataxe.weapon["mult"])], [12, 3])
	# Two swings per Attack action: off-hand first at -4, then the main hand.
	var target := _grid(EncounterGenerator.make_monster("orc_raider"), 1, 0, 1)
	target.max_hp = 999
	target.hp = 999
	_grid(dual, 0, 0, 1)
	var combat := Combat.new()
	combat.setup([dual], [target])
	combat._do_attack_action(dual, target)
	var events := combat.take_events()
	var hands: Array = []
	for e: Dictionary in events:
		hands.append(e.get("hand", ""))
	check("Dual wielder attacks off-hand then main hand", hands, ["off", "main"])
	var lines := "\n".join(combat.take_new_lines())
	check("Off-hand roll shows the -4", lines.contains("off-hand -4"), true)
	# First Guild list of a new game
	var state: Node = load("res://scripts/game_state.gd").new()
	state.new_game()
	var ids: Array = []
	for i in 5:
		ids.append((state.offers[i] as Unit).loadout_id)
	check("First Guild list: the five Soldier loadouts", ids, ["sword_shield", "dual_shortswords", "spear", "greatsword", "greataxe"])
	state.free()
	# Every Soldier loadout has a full set of frames for both body types
	var missing := 0
	for load_id: String in GameData.FIRST_GUILD_SOLDIERS:
		for body: String in ["m", "f"]:
			var u := RecruitGenerator.make([], "soldier", 1, load_id)
			u.look["body"] = body
			var frames := BattleSprites.frames_for(u)
			var need := ["stand", "ready", "slash_left", "slash_right", "finish", "hit"] if load_id == "dual_shortswords" else ["stand", "ready", "attack", "hit"]
			for st: String in need:
				if not frames.has(st) or frames[st][0] == null:
					missing += 1
	check("Soldier battle sprites: no missing frames", missing, 0)


# ------------------------------------------------------------------ balance
func _random_party(size: int, level: int) -> Array:
	# One of each role first, then random picks: what a sensible player hires.
	var classes := ["soldier", "soldier", "cleric", "archer", "mage", "soldier"]
	var members: Array = []
	for i in size:
		members.append(RecruitGenerator.make([], classes[i], level))
	return members


func _place_party(members: Array) -> void:
	var taken := {}
	for unit: Unit in members:
		var rows := [0, 1, 2]
		if unit.default_row == 1:
			rows = [1, 0, 2]
		elif unit.default_row == 2:
			rows = [2, 1, 0]
		var placed := false
		for row: int in rows:
			for lane: int in [1, 0, 2]:
				if not taken.has(row * 3 + lane):
					taken[row * 3 + lane] = true
					_grid(unit, 0, row, lane)
					placed = true
					break
			if placed:
				break


func _simulate(battles: int) -> void:
	print("\nBalance simulation: %d fresh-party battles per row" % battles)
	print("  %-9s %-5s %-6s | %6s %6s %6s %6s | %6s %7s %7s %6s" % ["size", "party", "level", "win%", "lose%", "draw%", "rounds", "foes", "HP lost", "downed", "dead"])
	for size_name: String in GameData.ENCOUNTER_SIZES:
		for party_size: int in [4, 6]:
			for level: int in [1, 3]:
				var wins := 0
				var losses := 0
				var draws := 0
				var rounds := 0
				var foes := 0
				var hp_lost := 0.0
				var downed := 0
				var dead := 0
				for i in battles:
					var members := _random_party(party_size, level)
					_place_party(members)
					var encounter: Dictionary = EncounterGenerator.generate(members, size_name)
					var combat := Combat.new()
					combat.setup(members, encounter["units"])
					combat.run_to_end()
					combat.take_new_lines()
					rounds += combat.round_num
					foes += (encounter["units"] as Array).size()
					match combat.outcome:
						"victory":
							wins += 1
						"defeat":
							losses += 1
						_:
							draws += 1
					var total := 0.0
					var left := 0.0
					for unit: Unit in members:
						total += unit.max_hp
						left += maxi(unit.hp, 0)
						if unit.dead:
							dead += 1
						elif unit.is_downed():
							downed += 1
					hp_lost += 1.0 - left / total
				var n := float(battles)
				print("  %-9s %-5d %-6d | %5.1f%% %5.1f%% %5.1f%% %6.1f | %6.1f %6.1f%% %7.2f %6.2f" % [
					size_name, party_size, level, 100 * wins / n, 100 * losses / n, 100 * draws / n,
					rounds / n, foes / n, 100 * hp_lost / n, downed / n, dead / n,
				])
				check("%s/%d/L%d produces no stalemates" % [size_name, party_size, level], draws, 0)
