extends SceneTree
##   godot --path . -s tests/portrait_check.gd -- out.png
## Bakes every outfit for both body types and checks each layer loaded.
func _init() -> void:
	await process_frame
	var out := OS.get_cmdline_user_args()[0]
	var fails := 0
	var rng := RandomNumberGenerator.new(); rng.seed = 3
	var sheet := Image.create(200 * PortraitLibrary.classes().size(), 400, false, Image.FORMAT_RGBA8)
	var row := 0
	for body in ["m", "f"]:
		var col := 0
		for cls in PortraitLibrary.classes():
			var look := HeroAppearance.roll(rng, body, cls)
			for layer in look.layers():
				if not PortraitLibrary.has_part(layer[0]): fails += 1; print("MISSING ", layer[0])
			var img: Image = HeroPortrait.bake(look)
			if img == null or img.get_used_rect().size.x < 100: fails += 1; print("FAIL ", body, " ", cls)
			else: sheet.blit_rect(img, Rect2i(Vector2i.ZERO, img.get_size()), Vector2i(col * 200, row * 200))
			col += 1
		row += 1
	sheet.save_png(out)
	print("classes ", PortraitLibrary.classes(), " failures ", fails)
	quit(fails)
