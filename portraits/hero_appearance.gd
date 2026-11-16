class_name HeroAppearance
extends RefCounted
## What a hero looks like. Plain data: store to_dict() in your hero or save file.
## Only appearance lives here. Stats and class rules belong to the game's own hero data;
## hero_class just picks which outfit is drawn.

var body: String = "m"            ## "m" or "f"
var hero_class: String = "soldier" ## soldier, archer or cleric (the outfit)
var skin: String = "fair"
var face: String = "neutral"
var hair: String = "messy"         ## "" means bald
var hair_color: String = "brown"
var eyes: String = "brown"
var details: Array = []            ## e.g. ["scar"]

## Chance that a rolled hero has a scar.
const SCAR_CHANCE := 0.15
## Hair colors that turn up less often. Weight 1.0 is normal.
const HAIR_COLOR_WEIGHTS := {"teal": 0.3, "navy": 0.4, "rose": 0.3, "violet": 0.3, "platinum": 0.5}


## Rolls a random appearance. Pass a seeded RandomNumberGenerator to get repeatable heroes.
## Leave body or hero_class empty to roll them too.
static func roll(rng: RandomNumberGenerator = null, p_body: String = "", p_class: String = "") -> HeroAppearance:
	if rng == null:
		rng = RandomNumberGenerator.new()
		rng.randomize()
	var a := HeroAppearance.new()
	a.body = p_body if p_body != "" else _pick(rng, PortraitLibrary.body_types())
	a.hero_class = p_class if p_class != "" else _pick(rng, PortraitLibrary.classes())
	a.skin = _pick(rng, PortraitLibrary.ramp_names("skin"))
	a.face = _pick(rng, PortraitLibrary.faces())
	a.hair = _pick(rng, PortraitLibrary.hairstyles(a.body))
	a.hair_color = _pick_weighted(rng, PortraitLibrary.ramp_names("hair"), HAIR_COLOR_WEIGHTS)
	a.eyes = _pick(rng, PortraitLibrary.ramp_names("eyes"))
	a.details = ["scar"] if rng.randf() < SCAR_CHANCE else []
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
		"body": body, "class": hero_class, "skin": skin, "face": face,
		"hair": hair, "hair_color": hair_color, "eyes": eyes, "details": details.duplicate(),
	}


static func from_dict(d: Dictionary) -> HeroAppearance:
	var a := HeroAppearance.new()
	a.body = d.get("body", a.body)
	a.hero_class = d.get("class", a.hero_class)
	a.skin = d.get("skin", a.skin)
	a.face = d.get("face", a.face)
	a.hair = d.get("hair", a.hair)
	a.hair_color = d.get("hair_color", a.hair_color)
	a.eyes = d.get("eyes", a.eyes)
	a.details = Array(d.get("details", [])).duplicate()
	return a


## The layers to draw, back to front. Each entry is [part name, ramp group, ramp name];
## an empty ramp group means the part is drawn as it is.
func layers() -> Array:
	var b := "%s_body_%s" % [body, hero_class]
	var f := "%s_face_%s" % [body, face]
	var out: Array = [
		[b + "_fixed", "", ""],
		[b + "_skin", "skin", skin],
		[f + "_skin", "skin", skin],
		[f + "_fixed", "", ""],
		[f + "_iris", "eyes", eyes],
	]
	for d in details:
		out.append(["%s_detail_%s" % [body, d], "skin", skin])
	if hair != "":
		out.append(["%s_hair_%s" % [body, hair], "hair", hair_color])
	return out
