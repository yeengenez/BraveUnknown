class_name BattleSprites
extends RefCounted
## Battle sprites exported from the art pipeline (art_source/new_art/battle/export_game.py, branch
## art-source) into res://sprites/battle/<class>/ with a manifest <class>.json.
##
## Each frame is 399x270 with the feet at manifest "feet". Hero-specific pixels are marked:
##   alpha 254 = skin (value in R) -> tinted with the hero's portrait skin ramp
##   alpha 253 = hair (value in R) -> the hair piece under the helmet, tinted with the hero's hair
##               ramp, shown only for long portrait hairstyles (manifest "hair_long")
## Slash frames of the dual stance have a separate effect layer (<frame>_fx.png).
##
## States per stance (user rule: swap single frames, no in-between animation):
##   shield / two-handed / spear: stand, ready, attack, hit
##   dual:                        stand, ready, slash_left (off hand), slash_right (main hand), finish, hit

const ROOT := "res://sprites/battle/"

static var _manifests: Dictionary = {}
static var _bases: Dictionary = {}     # file -> [PackedByteArray data, PackedInt32Array keyed pixel indices]
static var _frames: Dictionary = {}    # file|skin|hair|long -> ImageTexture
static var _fx: Dictionary = {}        # fx file -> Texture2D


static func manifest(cls: String) -> Dictionary:
	if not _manifests.has(cls):
		var m := {}
		var path := ROOT + cls + ".json"
		if FileAccess.file_exists(path):
			m = JSON.parse_string(FileAccess.get_file_as_string(path))
		_manifests[cls] = m
	return _manifests[cls]


## The frame list for a unit, or [] if it has no battle sprites.
static func states_for(unit: Unit) -> Array:
	if unit == null or unit.is_monster or unit.loadout_id == "" or unit.look.is_empty():
		return []
	var m := manifest(unit.class_id)
	if m.is_empty() or not (m["loadouts"] as Dictionary).has(unit.loadout_id):
		return []
	var sexes: Dictionary = m["loadouts"][unit.loadout_id]["sexes"]
	return sexes.get(String(unit.look.get("body", "m")), [])


static func has_sprites(unit: Unit) -> bool:
	return not states_for(unit).is_empty()


static func stance(unit: Unit) -> String:
	var m := manifest(unit.class_id)
	return String(m["loadouts"][unit.loadout_id]["stance"]) if has_sprites(unit) else ""


static func canvas(cls: String) -> Vector2:
	var m := manifest(cls)
	return Vector2(m["canvas"][0], m["canvas"][1]) if not m.is_empty() else Vector2(399, 270)


static func feet(cls: String) -> Vector2:
	var m := manifest(cls)
	return Vector2(m["feet"][0], m["feet"][1]) if not m.is_empty() else Vector2(199, 250)


## {state: [texture, fx texture or null]} for one unit, coloured for its look.
static func frames_for(unit: Unit) -> Dictionary:
	var out := {}
	var m := manifest(unit.class_id)
	var skin := String(unit.look.get("skin", "fair"))
	var hair_color := String(unit.look.get("hair_color", "brown"))
	var body := String(unit.look.get("body", "m"))
	var long := (m.get("hair_long", {}).get(body, []) as Array).has(String(unit.look.get("hair", "")))
	var dir := ROOT + unit.class_id + "/"
	for entry: Dictionary in states_for(unit):
		var fx_tex: Texture2D = null
		if entry.get("fx") != null:
			fx_tex = _fx_texture(dir + String(entry["fx"]))
		out[entry["state"]] = [_frame(dir + String(entry["file"]), skin, hair_color, long), fx_tex]
	return out


static func _fx_texture(path: String) -> Texture2D:
	if not _fx.has(path):
		_fx[path] = load(path)
	return _fx[path]


static func _base(path: String) -> Array:
	if _bases.has(path):
		return _bases[path]
	var img: Image = (load(path) as Texture2D).get_image()
	if img.is_compressed():
		img.decompress()
	img.convert(Image.FORMAT_RGBA8)
	var data := img.get_data()
	var keyed := PackedInt32Array()
	for i in data.size() / 4:
		var a := data[i * 4 + 3]
		if a == 254 or a == 253:
			keyed.append(i)
	var entry := [data, keyed, img.get_width(), img.get_height()]
	_bases[path] = entry
	return entry


static func _frame(path: String, skin: String, hair_color: String, long: bool) -> ImageTexture:
	var key := "%s|%s|%s|%s" % [path, skin, hair_color, long]
	if _frames.has(key):
		return _frames[key]
	var base := _base(path)
	var data: PackedByteArray = (base[0] as PackedByteArray).duplicate()
	var skin_lut := PortraitLibrary.ramp_table("skin", skin)
	var hair_lut := PortraitLibrary.ramp_table("hair", hair_color)
	for i: int in base[1]:
		var o := i * 4
		var hair := data[o + 3] == 253
		if hair and not long:
			data[o + 3] = 0
			continue
		var c: Color = (hair_lut if hair else skin_lut)[data[o]]
		data[o] = c.r8
		data[o + 1] = c.g8
		data[o + 2] = c.b8
		data[o + 3] = 255
	var img := Image.create_from_data(base[2], base[3], false, Image.FORMAT_RGBA8, data)
	img.generate_mipmaps()
	var tex := ImageTexture.create_from_image(img)
	_frames[key] = tex
	return tex
