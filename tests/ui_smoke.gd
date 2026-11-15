extends Node
## Drives the real UI: hire, arrange, fight. Fails loudly on any broken step.
##
##   godot --headless --path . res://tests/ui_smoke.tscn
##   godot --path . res://tests/ui_smoke.tscn -- --shots=/some/folder   (saves PNGs)

var shots_dir := ""
var failures := 0


func _ready() -> void:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--shots="):
			shots_dir = arg.trim_prefix("--shots=")
	Dice.rng.seed = 7
	Game.new_game()
	var main: Control = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	add_child(main)
	await _frames(3)
	await _shot("1_guild")

	# Guild: hire four, refresh, hire more.
	var gold_before := Game.gold
	var first_cost: int = (Game.offers[0] as Unit).cost
	expect("hire succeeds", Game.hire(0), true)
	expect("gold is spent", Game.gold, gold_before - first_cost)
	expect("seat is empty after hiring", Game.offers[0] == null, true)
	Game.hire(1)
	Game.hire(2)
	var before_refresh := Game.gold
	var old_names: Array = []
	for offer: Unit in Game.offers:
		if offer != null:
			old_names.append(offer.unit_name)
	expect("refresh succeeds", Game.refresh_offers(), true)
	expect("refresh costs gold", Game.gold, before_refresh - GameData.REFRESH_COST)
	expect("refresh fills every seat", Game.offers.has(null), false)
	var index := 0
	while Game.roster.size() < 6 and index < Game.offers.size():
		Game.hire(index)
		index += 1
	Game.add_gold(2000)
	Game.refresh_offers()
	index = 0
	while Game.roster.size() < 6 and index < Game.offers.size():
		Game.hire(index)
		index += 1
	await _frames(3)
	await _shot("2_guild_hired")
	expect("roster has six", Game.roster.size(), 6)

	# Poor player cannot hire or refresh.
	var saved := Game.gold
	Game.gold = 5
	expect("cannot refresh without gold", Game.refresh_offers(), false)
	expect("cannot hire without gold", Game.hire(5), false)
	Game.gold = saved

	# Party
	main.call("show_screen", "Party")
	Game.auto_arrange()
	await _frames(3)
	expect("party has six", Game.party_size(), 6)
	var party_screen: PartyScreen = main.get("_screens")["Party"]
	party_screen.call("_select", Game.party_units()[0])
	await _frames(3)
	await _shot("3_party")
	var extra := RecruitGenerator.make()
	Game.roster.append(extra)
	expect("seventh member is refused", Game.place(extra, 8 if not Game.formation.has(8) else 7) and Game.party_size() > 6, false)
	Game.roster.erase(extra)

	# Battle
	main.call("show_screen", "Battle")
	var battle: BattleScreen = main.get("_screens")["Battle"]
	await _frames(2)
	battle.start_battle()
	await _frames(2)
	expect("battle started", battle.is_fighting(), true)
	for i in 6:
		battle.step_once()
	await _frames(3)
	await _shot("4_battle")
	battle.finish_now()
	await _frames(3)
	await _shot("5_battle_end")
	expect("battle finished", battle.combat.finished, true)
	expect("battle counted", Game.battles_fought, 1)
	print("outcome: %s after %d rounds, gold %d" % [battle.combat.outcome, battle.combat.round_num, Game.gold])

	# Attrition carries over, camp restores.
	Game.make_camp()
	var hurt := 0
	for unit: Unit in Game.roster:
		if unit.hp < unit.max_hp:
			hurt += 1
	expect("camp restores everyone", hurt, 0)

	# Several more fights through the UI, including surprise rounds.
	for round_index in 6:
		battle.get("_surprise_picker").select(round_index % 3)
		battle.get("_size_picker").select(round_index % 3)
		battle.start_battle()
		if battle.combat == null:
			Game.make_camp()
			continue
		battle.finish_now()
		Game.make_camp()
	await _frames(2)
	print("after 7 fights: roster %d, gold %d, won %d/%d" % [Game.roster.size(), Game.gold, Game.battles_won, Game.battles_fought])

	print("UI smoke test: %s" % ("FAILED (%d)" % failures if failures > 0 else "ok"))
	get_tree().quit(1 if failures > 0 else 0)


func expect(label: String, got: Variant, want: Variant) -> void:
	if got != want:
		failures += 1
		print("  FAIL %s: got %s, want %s" % [label, got, want])


func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	if shots_dir == "":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [shots_dir, shot_name])
