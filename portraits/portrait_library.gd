class_name PortraitLibrary
extends RefCounted
## Loads the portrait parts list and the color ramps, and caches textures.
## Everything here is static: call PortraitLibrary.part("m_hair_messy") etc.

const DIR := "res://portraits/"
const PARTS_DIR := DIR + "parts/"
const CANVAS := Vector2i(200, 200)

static var _lib: Dictionary = {}
static var _palettes: Dictionary = {}
static var _ramp_textures: Dictionary = {}
static var _images: Dictionary = {}


static func _ensure_loaded() -> void:
	if not _lib.is_empty():
		return
	_lib = _read_json(DIR + "library.json")
	_palettes = _read_json(DIR + "palettes.json")
	_palettes.erase("_note")


static func _read_json(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("PortraitLibrary: could not read %s" % path)
		return {}
	return data


## "m" and "f".
static func body_types() -> Array:
	_ensure_loaded()
	return _lib["body_types"]


## Class outfits: soldier, archer, cleric (Acolyte), mage, warrior, rogue.
static func classes() -> Array:
	_ensure_loaded()
	return _lib["bodies"]


## Expressions (each one is a brows layer + a mouth layer).
static func expressions() -> Array:
	_ensure_loaded()
	return _lib["expressions"]


## Older name for expressions().
static func faces() -> Array:
	return expressions()


## Eye shapes available for one body type.
static func eye_styles(body: String) -> Array:
	_ensure_loaded()
	return _lib["eyes"][body]


## Hairstyles available for one body type.
static func hairstyles(body: String) -> Array:
	_ensure_loaded()
	return _lib["hair"][body]


## No detail layers (scars) in the current art.
static func details() -> Array:
	_ensure_loaded()
	return _lib.get("details", [])


## A ramp as a 256-entry colour table (index = value-map value), for CPU tinting. Cached.
static var _ramp_tables: Dictionary = {}
static func ramp_table(group: String, ramp_name: String) -> PackedColorArray:
	var key := group + "/" + ramp_name
	if _ramp_tables.has(key):
		return _ramp_tables[key]
	var colors := ramp_colors(group, ramp_name)
	var last := colors.size() - 1
	var table := PackedColorArray()
	table.resize(256)
	for v in 256:
		var t := v / 255.0 * last
		var i := mini(int(t), last - 1)
		table[v] = colors[i].lerp(colors[i + 1], t - i)
	_ramp_tables[key] = table
	return table


## Ramp names for a group: "skin", "hair" or "eyes".
static func ramp_names(group: String) -> Array:
	_ensure_loaded()
	return _palettes[group].keys()


## The ramp colors, dark to light.
static func ramp_colors(group: String, ramp_name: String) -> PackedColorArray:
	_ensure_loaded()
	var colors := PackedColorArray()
	for hex in _palettes[group][ramp_name]:
		colors.append(Color.html(hex))
	return colors


## A 256-pixel gradient texture for the ramp shader. Cached.
static func ramp_texture(group: String, ramp_name: String) -> GradientTexture1D:
	var key := group + "/" + ramp_name
	if _ramp_textures.has(key):
		return _ramp_textures[key]
	var colors := ramp_colors(group, ramp_name)
	var gradient := Gradient.new()
	var offsets := PackedFloat32Array()
	for i in colors.size():
		offsets.append(float(i) / float(colors.size() - 1))
	gradient.offsets = offsets
	gradient.colors = colors
	var tex := GradientTexture1D.new()
	tex.gradient = gradient
	tex.width = 256
	_ramp_textures[key] = tex
	return tex


static func has_part(part_name: String) -> bool:
	return ResourceLoader.exists(PARTS_DIR + part_name + ".png")


## The texture for one part, e.g. "f_body_cleric_fixed".
static func part(part_name: String) -> Texture2D:
	return load(PARTS_DIR + part_name + ".png") as Texture2D


## One part as an RGBA8 Image (decoded once, then cached), or null if the part does not exist.
static func part_image(part_name: String) -> Image:
	if _images.has(part_name):
		return _images[part_name]
	var img: Image = null
	if has_part(part_name):
		img = part(part_name).get_image()
		if img.is_compressed():
			img.decompress()
		img.convert(Image.FORMAT_RGBA8)
	_images[part_name] = img
	return img
