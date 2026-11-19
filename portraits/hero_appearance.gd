class_name HeroAppearance
extends RefCounted
## What a hero looks like. Plain data: store to_dict() in your hero or save file.
## Only appearance lives here. Stats and class rules belong to the game's own hero data;
## hero_class just picks which outfit is drawn.
##
## New art (2026-11-19): every part is its own layer, so eyes, expression (brows + mouth)
## and hair combine freely. See library.json for the lists.

var body: String = "m"              ## "m" or "f"
var hero_class: String = "soldier"  ## outfit: soldier, archer, cleric (Acolyte), mage, warrior, rogue
var skin: String = "fair"           ## skin ramp
var expression: String = "neutral"  ## brows + mouth: neutral, smile, stern, grin, sleepy, worried
var eye_style: String = ""          ## eye shape, per body type (library.json "eyes")
var hair: String = ""               ## hairstyle, per body type (library.json "hair")
var hair_color: String = "brown"    ## hair ramp (also tints the brows)
var eyes: String = "brown"          ## eye colour ramp (tints the iris)

## Hair colors that turn up less often. Weight 1.0 is normal.
const HAIR_COLOR_WEIGHTS := {"teal": 0.3, "navy": 0.4, "rose": 0.3, "violet": 0.3, "platinum": 0.5}


## Rolls a random appearance. Pass a RandomNumberGenerator to control the randomness.
## Leave body or hero_class empty to roll them too.
static func roll(rng: RandomNumberGenerator = null, p_body: String = "", p_class: String = "") -> HeroAppearance:
	if rng == null:
		rng = RandomNumberGenerator.new()
		rng.randomize()
	var a := HeroAppearance.new()
	a.body = p_body if p_body != "" else _pick(rng, PortraitLibrary.body_types())
	a.hero_class = p_class if p_class != "" else _pick(rng, PortraitLibrary.classes())
	a.skin = _pick(rng, PortraitLibrary.ramp_names("skin"))
	a.expression = _pick(rng, PortraitLibrary.expressions())
	a.eye_style = _pick(rng, PortraitLibrary.eye_styles(a.body))
	a.hair = _pick(rng, PortraitLibrary.hairstyles(a.body))
	a.hair_color = _pick_weighted(rng, PortraitLibrary.ramp_names("hair"), HAIR_COLOR_WEIGHTS)
	a.eyes = _pick(rng, PortraitLibrary.ramp_names("eyes"))
	return a


static func _pick(rng: RandomNumberGenerator, options: Array) -> String:
	return options[rng.randi_range(0, options.size() - 1)]


static func _pick_weighted(rng: RandomNumberGenerator, options: Array, weights: Dictionary) -> String:
	var total := 0.0
	for o in options:
		total += float(weights.get(o, 1.0))
	var r := rng.randf() * total
	for o in options:
		r -= float(weights.get(o, 1.0))
		if r <= 0.0:
			return o
	return options[-1]


func to_dict() -> Dictionary:
	return {
		"body": body, "class": hero_class, "skin": skin, "expression": expression,
		"eye_style": eye_style, "hair": hair, "hair_color": hair_color, "eyes": eyes,
	}


## Reads to_dict() output. Values the current art does not have (for example a look saved
## with the Legacy art) fall back to the first option, so old data still draws.
static func from_dict(d: Dictionary) -> HeroAppearance:
	var a := HeroAppearance.new()
	a.body = _valid(d.get("body", a.body), PortraitLibrary.body_types())
	a.hero_class = _valid(d.get("class", a.hero_class), PortraitLibrary.classes())
	a.skin = _valid(d.get("skin", a.skin), PortraitLibrary.ramp_names("skin"))
	a.expression = _valid(d.get("expression", d.get("face", a.expression)), PortraitLibrary.expressions())
	a.eye_style = _valid(d.get("eye_style", ""), PortraitLibrary.eye_styles(a.body))
	a.hair = _valid(d.get("hair", ""), PortraitLibrary.hairstyles(a.body))
	a.hair_color = _valid(d.get("hair_color", a.hair_color), PortraitLibrary.ramp_names("hair"))
	a.eyes = _valid(d.get("eyes", a.eyes), PortraitLibrary.ramp_names("eyes"))
	return a


static func _valid(value: Variant, options: Array) -> String:
	return String(value) if options.has(String(value)) else String(options[0])


## Cache key: same key, same finished portrait.
func key() -> String:
	return "%s|%s|%s|%s|%s|%s|%s|%s" % [body, hero_class, skin, expression, eye_style, hair, hair_color, eyes]


## The layers to stack, back to front. Each entry is [part name, ramp group, ramp name, role];
## an empty ramp group means the part keeps its own colours. role names the layer for the
## finish passes (portrait_finish.gd).
func layers() -> Array:
	var b := "%s_body_%s" % [body, hero_class]
	var e := "%s_eyes_%s" % [body, eye_style]
	return [
		["%s_head_skin" % body, "skin", skin, "skin"],
		[b + "_skin", "skin", skin, "skin"],
		[b + "_fixed", "", "", "body"],
		[e + "_fixed", "", "", "eyes"],
		[e + "_iris", "eyes", eyes, "iris"],
		["%s_brows_%s" % [body, expression], "hair", hair_color, "brow"],
		["%s_mouth_%s" % [body, expression], "", "", "mouth"],
		["%s_hair_%s" % [body, hair], "hair", hair_color, "hair"],
	]
