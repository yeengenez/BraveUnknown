extends SceneTree
## Builds portraits with PortraitFinish and saves them, for comparison with the art
## pipeline's finish.py. Also reports build time.
##   godot --headless --path . -s tests/portrait_finish_check.gd -- --out=/tmp/pcmp --count=12

func _init() -> void:
	var out := "user://portrait_check"
	var count := 12
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			out = arg.trim_prefix("--out=")
		elif arg.begins_with("--count="):
			count = int(arg.trim_prefix("--count="))
	DirAccess.make_dir_recursive_absolute(out)
	var rng := RandomNumberGenerator.new()
	rng.seed = 19
	var looks: Array = []
	var total_ms := 0.0
	for i in count:
		var a := HeroAppearance.roll(rng, "m" if i % 2 == 0 else "f", PortraitLibrary.classes()[i % 6])
		var t0 := Time.get_ticks_usec()
		var img := PortraitFinish.compose(a)
		var ms := (Time.get_ticks_usec() - t0) / 1000.0
		total_ms += ms
		img.save_png("%s/gd_%02d.png" % [out, i])
		var d := a.to_dict()
		d["file"] = "gd_%02d.png" % i
		looks.append(d)
	var f := FileAccess.open(out + "/looks.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(looks))
	f.close()
	print("built %d portraits, %.1f ms each on average" % [count, total_ms / count])
	quit()
