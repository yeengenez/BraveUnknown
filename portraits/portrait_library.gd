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


## Class outfits: soldier, archer, cleric.
static func classes() -> Array:
	_ensure_loaded()
	return _lib["bodies"]


static func faces() -> Array:
	_ensure_loaded()
	return _lib["faces"]


## Hairstyles available for one body type.
static func hairstyles(body: String) -> Array:
	_ensure_loaded()
	return _lib["hair"][body]


static func details() -> Array:
	_ensure_loaded()
	return _lib["details"]


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
