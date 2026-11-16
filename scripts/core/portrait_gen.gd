class_name PortraitGen
extends RefCounted
## Looks for MONSTER portraits only (drawn by MonsterPortrait).
## Expeditioners use the pixel-art portrait module in res://portraits/
## (HeroAppearance / HeroPortrait); see UnitPortrait.


## Fixed looks for monsters, one per kind, with a little per-unit variation.
static func monster(monster_id: String, seed: int) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	var base := {
		"seed": seed, "fem": false, "class_id": "", "accent": Color("#7a3030"), "material": "Light",
		"face_w": rng.randf_range(16.0, 18.0), "face_h": rng.randf_range(20.0, 22.5), "jaw": rng.randf_range(0.8, 0.95),
		"brow_tilt": rng.randf_range(1.2, 2.6), "mouth_curve": rng.randf_range(-1.6, 0.2), "eye_gap": 7.6,
		"nose": 2, "age": 0.3, "scar": rng.randi_range(0, 9) if rng.randf() < 0.3 else -1, "blush": false,
		"gear": "none", "lean": rng.randf_range(-2.0, 2.0), "beard": "none", "hair_style": "bald",
		"hair": Color("#1d1a19"), "eyes": Color("#e8c23a"), "ears": "normal", "mouth": "plain",
		"eye_glow": false,
	}
	var green := Color("#6f9a45").lerp(Color("#56803a"), rng.randf())
	match monster_id:
		"goblin_cutter", "goblin_archer", "goblin_hexer", "goblin_brute":
			base.merge({"kind": "humanoid", "skin": green, "ears": "goblin", "mouth": "fangs", "face_w": rng.randf_range(15.0, 16.5),
				"face_h": rng.randf_range(18.0, 20.0), "jaw": 0.7, "eye_gap": 8.2, "hair_style": "tuft", "material": "Light",
				"accent": Color("#7a5a2a")}, true)
			if monster_id == "goblin_hexer":
				base.merge({"gear": "hood", "accent": Color("#4d3470"), "material": "Cloth", "eye_glow": true, "eyes": Color("#c59bff")}, true)
			elif monster_id == "goblin_archer":
				base.merge({"gear": "hood", "accent": Color("#5a4630")}, true)
			elif monster_id == "goblin_brute":
				base.merge({"face_w": 18.5, "jaw": 1.02, "material": "Medium", "mouth": "tusks", "accent": Color("#6a3a2a")}, true)
		"orc_raider":
			base.merge({"kind": "humanoid", "skin": Color("#7d8f5c").lerp(Color("#6a7d52"), rng.randf()), "ears": "pointed",
				"mouth": "tusks", "face_w": 19.0, "jaw": 1.05, "hair_style": "topknot", "material": "Medium",
				"accent": Color("#7a2a2a"), "eyes": Color("#d8462c")}, true)
		"kobold_slinger":
			base.merge({"kind": "kobold", "skin": Color("#b0643a").lerp(Color("#8c4c2c"), rng.randf()), "eyes": Color("#f0d24a"),
				"accent": Color("#5a4630")}, true)
		"skeleton":
			base.merge({"kind": "skeleton", "skin": Color("#e2dccb"), "eyes": Color("#5fd0ff"), "accent": Color("#3a3a44"), "material": "Medium"}, true)
		"cave_ghoul":
			base.merge({"kind": "humanoid", "skin": Color("#8f9aa3").lerp(Color("#7a8790"), rng.randf()), "ears": "pointed",
				"mouth": "fangs", "jaw": 0.72, "face_w": 15.5, "face_h": 23.0, "hair_style": "stringy", "hair": Color("#2c2d33"),
				"eyes": Color("#f2f2e6"), "eye_glow": true, "material": "Cloth", "accent": Color("#3c3a40")}, true)
		"wolf":
			base.merge({"kind": "wolf", "skin": Color("#77787c").lerp(Color("#5d5a55"), rng.randf()), "eyes": Color("#e7b43c"),
				"accent": Color("#2f3a2c")}, true)
		"giant_rat":
			base.merge({"kind": "rat", "skin": Color("#6e5a4a").lerp(Color("#5a4a3e"), rng.randf()), "eyes": Color("#d8302a"),
				"accent": Color("#3a2e26")}, true)
		_:
			base.merge({"kind": "humanoid", "skin": green}, true)
	return base
