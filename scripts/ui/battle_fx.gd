class_name BattleFx
extends Control
## Overlay that draws combat effects above the battlefield:
## missiles (arrows, bolts, stones, spells), slashes, impact rings,
## sparkles and floating numbers. Every method takes global positions.

const FX_COLORS := {
	"slash": Color("#f4efe2"), "pierce": Color("#e6ecf5"), "blunt": Color("#f1d9a0"),
	"claw": Color("#ff9b8a"), "bite": Color("#f4efe2"), "arrow": Color("#f1d9a0"),
	"frost": Color("#8fd9ff"), "bolt": Color("#c59bff"), "fire": Color("#ff9a3c"),
	"force": Color("#b2a4ff"), "holy": Color("#ffe58a"), "heal": Color("#8fe39a"),
	"buff": Color("#e2b85a"),
}

var _items: Array = []
var _font: Font


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 50
	_font = UIKit.bold_font()


static func color_for(fx: String) -> Color:
	return FX_COLORS.get(fx, Color.WHITE)


func clear() -> void:
	_items.clear()
	for child: Node in get_children():
		child.queue_free()
	queue_redraw()


func _local(global_point: Vector2) -> Vector2:
	return get_global_transform().affine_inverse() * global_point


## Animates item[key] from a to b, redrawing as it goes; removes the item after.
func _run(item: Dictionary, key: String, a: float, b: float, duration: float, keep: bool = false) -> Tween:
	_items.append(item)
	item[key] = a
	var tween := create_tween()
	tween.tween_method(func(value: float) -> void:
		item[key] = value
		queue_redraw(), a, b, maxf(duration, 0.01))
	if not keep:
		tween.tween_callback(func() -> void:
			_items.erase(item)
			queue_redraw())
	return tween


# ------------------------------------------------------------------ effects
## Missile looks: speed in px/s, how high it arcs (fraction of distance), colour.
const MISSILES := {
	"arrow": {"speed": 1500.0, "arc": 0.13, "color": Color("#f1d9a0")},
	"xbolt": {"speed": 1900.0, "arc": 0.04, "color": Color("#d8dde6")},
	"stone": {"speed": 1300.0, "arc": 0.18, "color": Color("#b9b3a6")},
	"frost": {"speed": 1250.0, "arc": 0.02, "color": Color("#8fd9ff")},
	"arcane": {"speed": 1050.0, "arc": 0.06, "color": Color("#c59bff")},
	"fire": {"speed": 950.0, "arc": 0.08, "color": Color("#ff9a3c")},
	"force": {"speed": 2100.0, "arc": 0.0, "color": Color("#b2a4ff")},
	"holy": {"speed": 1150.0, "arc": 0.03, "color": Color("#ffe58a")},
	"heal": {"speed": 900.0, "arc": 0.10, "color": Color("#8fe39a")},
	"buff": {"speed": 900.0, "arc": 0.10, "color": Color("#e2b85a")},
}


## Missile for a ranged weapon, from its name.
static func weapon_missile(weapon_name: String) -> String:
	var lower := weapon_name.to_lower()
	if lower.contains("crossbow"):
		return "xbolt"
	if lower.contains("sling"):
		return "stone"
	return "arrow"


## Missile for a spell, from its effect colour key.
static func spell_missile(fx: String) -> String:
	match fx:
		"frost", "fire", "force", "holy", "heal", "buff":
			return fx
	return "arcane"


## Fires a missile from -> to. Await the returned tween to know when it lands.
func missile(from: Vector2, to: Vector2, style: String, time_scale: float, delay: float = 0.0) -> Tween:
	var spec: Dictionary = MISSILES.get(style, MISSILES["arcane"])
	var a := _local(from)
	var b := _local(to)
	var duration := clampf(a.distance_to(b) / float(spec["speed"]), 0.16, 0.6) * time_scale
	var item := {
		"kind": "missile", "style": style, "from": a, "to": b, "color": spec["color"],
		"arc": float(spec["arc"]), "t": 0.0, "seed": randf() * 10.0,
	}
	var tween := create_tween()
	if delay > 0.0:
		tween.tween_interval(delay)
	tween.tween_callback(func() -> void: _items.append(item))
	tween.tween_method(func(value: float) -> void:
		item["t"] = value
		queue_redraw(), 0.0, 1.0, maxf(duration, 0.01))
	tween.tween_callback(func() -> void:
		_items.erase(item)
		queue_redraw())
	return tween


func _missile_pos(item: Dictionary, t: float) -> Vector2:
	var a: Vector2 = item["from"]
	var b: Vector2 = item["to"]
	var lift := sin(clampf(t, 0.0, 1.0) * PI) * minf(a.distance_to(b) * float(item["arc"]), 60.0)
	return a.lerp(b, clampf(t, 0.0, 1.0)) + Vector2(0, -lift)


## Melee strike across the target, travelling away from `from`.
## dtype: slash | pierce | blunt | claw | bite. miss draws a faint whiff.
func strike(at: Vector2, from: Vector2, dtype: String, heavy: bool, miss: bool, duration: float) -> void:
	var u := (at - from).normalized()
	if u == Vector2.ZERO:
		u = Vector2.RIGHT
	var up := Vector2(u.y, -u.x)
	if up.y > 0.0:
		up = -up  # keep "up" pointing up the screen whichever way the blow goes
	var seeds: Array = []
	for i in 8:
		seeds.append(Vector2(randf_range(-1.0, 1.0), randf_range(0.6, 1.0)))
	_run({"kind": "strike", "dtype": dtype, "at": _local(at), "u": u, "up": up, "heavy": heavy,
		"miss": miss, "seeds": seeds, "color": color_for(dtype)}, "t", 0.0, 1.0, duration)


## Spray of streaks bursting out of the far side of a target (missile hits).
func splash(at: Vector2, from: Vector2, color: Color, heavy: bool, duration: float) -> void:
	var u := (at - from).normalized()
	if u == Vector2.ZERO:
		u = Vector2.RIGHT
	var rays: Array = []
	for i in (11 if heavy else 7):
		rays.append({"angle": randf_range(-0.6, 0.6), "length": randf_range(0.55, 1.0)})
	_run({"kind": "splash", "at": _local(at), "u": u, "color": color, "heavy": heavy, "rays": rays}, "t", 0.0, 1.0, duration)


## Rising specks (heals, buffs).
func sparkle(at: Vector2, color: Color, duration: float) -> void:
	var seeds: Array = []
	for i in 9:
		seeds.append(Vector2(randf_range(-55, 55), randf_range(-10, 30)))
	_run({"kind": "sparkle", "at": _local(at), "color": color, "seeds": seeds}, "t", 0.0, 1.0, duration)


## Floating text that pops, rises and fades ("-7", "MISS", "CRITICAL!").
func float_text(at: Vector2, text: String, color: Color, size: int, duration: float, rise: float = 46.0) -> void:
	var label := Label.new()
	label.text = text
	label.add_theme_font_override("font", _font)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.05, 0.05, 0.07))
	label.add_theme_constant_override("outline_size", maxi(4, size / 4))
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)
	label.size = label.get_minimum_size()
	label.pivot_offset = label.size / 2.0
	var start := _local(at) - label.size / 2.0
	label.position = start
	label.scale = Vector2(0.4, 0.4)
	var tween := create_tween()
	tween.tween_property(label, "scale", Vector2(1.25, 1.25), duration * 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(label, "scale", Vector2.ONE, duration * 0.1)
	tween.parallel().tween_property(label, "position:y", start.y - rise, duration * 0.88).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(label, "modulate:a", 0.0, duration * 0.35).set_delay(duration * 0.55)
	tween.tween_callback(label.queue_free)


# ------------------------------------------------------------------ drawing
func _draw() -> void:
	for item: Dictionary in _items:
		var color: Color = item["color"]
		match String(item["kind"]):
			"missile":
				_draw_missile(item, color)
			"strike":
				_draw_strike(item, color)
			"splash":
				_draw_splash(item, color)
			"sparkle":
				var t: float = item.get("t", 0.0)
				for seed: Vector2 in item["seeds"]:
					var p: Vector2 = item["at"] + seed + Vector2(0, -60.0 * t)
					draw_circle(p, 3.5 * (1.0 - t) + 0.5, Color(color, 1.0 - t))


func _draw_missile(item: Dictionary, color: Color) -> void:
	var t: float = item["t"]
	var pos := _missile_pos(item, t)
	var ahead := _missile_pos(item, t + 0.03)
	var dir := (ahead - pos).normalized() if ahead != pos else (Vector2(item["to"]) - Vector2(item["from"])).normalized()
	var normal := Vector2(-dir.y, dir.x)
	var seed: float = item["seed"]
	match String(item["style"]):
		"arrow":
			# Faint motion streak, wooden shaft, steel head, coloured fletching.
			draw_line(pos - dir * 70.0, pos - dir * 20.0, Color(1, 1, 1, 0.12), 3.0, true)
			var tail := pos - dir * 36.0
			draw_line(tail, pos, Color("#8a6236"), 3.0, true)
			draw_colored_polygon(PackedVector2Array([pos + dir * 11.0, pos + normal * 5.5, pos - normal * 5.5]), Color("#e6e9ee"))
			for side: float in [1.0, -1.0]:
				draw_line(tail + dir * 9.0, tail - dir * 1.0 + normal * 6.0 * side, Color("#e8e4d8"), 2.5, true)
		"xbolt":
			draw_line(pos - dir * 60.0, pos - dir * 16.0, Color(1, 1, 1, 0.14), 4.0, true)
			var tail := pos - dir * 24.0
			draw_line(tail, pos, Color("#5d4630"), 4.5, true)
			draw_colored_polygon(PackedVector2Array([pos + dir * 13.0, pos - dir * 2.0 + normal * 7.0, pos - dir * 2.0 - normal * 7.0]), Color("#cfd5de"))
			draw_line(tail, tail + normal * 5.0, Color("#b0383a"), 3.0, true)
			draw_line(tail, tail - normal * 5.0, Color("#b0383a"), 3.0, true)
		"stone":
			draw_line(pos - dir * 30.0, pos, Color(1, 1, 1, 0.12), 6.0, true)
			draw_circle(pos, 7.0, Color("#3c3a36"))
			draw_circle(pos, 5.5, Color("#9c968a"))
			draw_circle(pos + Vector2(-1.5, -1.5), 2.0, Color("#d6d0c4"))
		"frost":
			# Ice shard with a trail of glittering flakes.
			for i in 6:
				var flake := pos - dir * (14.0 + i * 11.0) + normal * sin(seed + i * 1.7 + t * 20.0) * 6.0
				var r := 4.0 - i * 0.5
				draw_colored_polygon(PackedVector2Array([flake + dir * r, flake + normal * r * 0.6, flake - dir * r, flake - normal * r * 0.6]), Color(color, 0.8 - i * 0.12))
			draw_circle(pos, 14.0, Color(color, 0.22))
			draw_colored_polygon(PackedVector2Array([pos + dir * 20.0, pos + normal * 7.0, pos - dir * 14.0, pos - normal * 7.0]), color)
			draw_colored_polygon(PackedVector2Array([pos + dir * 14.0, pos + normal * 3.0, pos - dir * 6.0, pos - normal * 3.0]), Color(1, 1, 1, 0.9))
		"arcane":
			# Spinning violet orb with orbiting sparks.
			for i in 6:
				draw_circle(pos - dir * (i * 9.0), 10.0 - i * 1.4, Color(color, 0.45 - i * 0.07))
			draw_circle(pos, 17.0, Color(color, 0.22))
			draw_circle(pos, 9.0, color)
			draw_circle(pos, 4.5, Color(1, 1, 1, 0.95))
			for i in 3:
				var angle := seed + t * 18.0 + i * TAU / 3.0
				draw_circle(pos + Vector2(cos(angle), sin(angle)) * 15.0, 2.5, Color(1, 1, 1, 0.85))
		"fire":
			# Fireball: flickering tail going from yellow to dark red.
			for i in range(9, 0, -1):
				var flicker := sin(seed + i * 2.3 + t * 40.0) * 4.0
				var p := pos - dir * (i * 8.0) + normal * flicker
				var heat := Color("#ffd23c").lerp(Color("#b8261a"), i / 9.0)
				draw_circle(p, 12.0 - i * 1.0, Color(heat, 0.75 - i * 0.07))
			draw_circle(pos, 20.0, Color(color, 0.25))
			draw_circle(pos, 13.0, color)
			draw_circle(pos, 8.0, Color("#ffd23c"))
			draw_circle(pos, 4.0, Color("#fff6d0"))
		"force":
			# Long spear of force.
			draw_line(pos - dir * 80.0, pos, Color(color, 0.25), 14.0, true)
			draw_line(pos - dir * 64.0, pos, color, 5.0, true)
			draw_line(pos - dir * 50.0, pos, Color(1, 1, 1, 0.9), 1.8, true)
			draw_colored_polygon(PackedVector2Array([pos + dir * 16.0, pos + normal * 8.0, pos - normal * 8.0]), Color(1, 1, 1, 0.95))
		"holy":
			# Turning four-point star.
			for i in 4:
				draw_circle(pos - dir * (i * 11.0), 6.0 - i * 1.2, Color(color, 0.5 - i * 0.1))
			draw_circle(pos, 18.0, Color(color, 0.25))
			var spin := seed + t * 10.0
			var points := PackedVector2Array()
			for i in 8:
				var radius := 15.0 if i % 2 == 0 else 5.0
				var angle := spin + i * TAU / 8.0
				points.append(pos + Vector2(cos(angle), sin(angle)) * radius)
			draw_colored_polygon(points, color)
			draw_circle(pos, 3.5, Color(1, 1, 1, 0.95))
		"heal":
			for i in 5:
				draw_circle(pos - dir * (i * 9.0) + normal * sin(seed + i + t * 16.0) * 5.0, 5.0 - i * 0.8, Color(color, 0.6 - i * 0.1))
			draw_circle(pos, 15.0, Color(color, 0.25))
			draw_circle(pos, 9.0, color)
			draw_rect(Rect2(pos - Vector2(5.5, 1.8), Vector2(11, 3.6)), Color.WHITE)
			draw_rect(Rect2(pos - Vector2(1.8, 5.5), Vector2(3.6, 11)), Color.WHITE)
		_:  # buff mote
			for i in 4:
				draw_circle(pos - dir * (i * 8.0), 4.0 - i * 0.8, Color(color, 0.6 - i * 0.12))
			draw_circle(pos, 12.0, Color(color, 0.25))
			draw_colored_polygon(PackedVector2Array([pos + Vector2(0, -8), pos + Vector2(6, 0), pos + Vector2(0, 8), pos + Vector2(-6, 0)]), color)


# ------------------------------------------------------------------ strikes
static func _ease_out(x: float) -> float:
	x = clampf(x, 0.0, 1.0)
	return 1.0 - (1.0 - x) * (1.0 - x)


static func _ease_in(x: float) -> float:
	x = clampf(x, 0.0, 1.0)
	return x * x


static func _bezier(a: Vector2, b: Vector2, c: Vector2, s: float) -> Vector2:
	return a.lerp(b, s).lerp(b.lerp(c, s), s)


## A blade-shaped ribbon along a curve between s0 and s1: pointed at both
## ends, widest in the middle, with a soft coloured glow around a bright core.
func _draw_sweep(a: Vector2, b: Vector2, c: Vector2, s0: float, s1: float, width: float, color: Color, alpha: float) -> void:
	if s1 - s0 <= 0.001 or alpha <= 0.01:
		return
	var steps := 16
	var centers: Array[Vector2] = []
	for i in steps + 1:
		centers.append(_bezier(a, b, c, lerpf(s0, s1, float(i) / steps)))
	for layer: Array in [[2.4, Color(color, 0.35 * alpha)], [1.0, Color(1, 1, 1, alpha)]]:
		var scale: float = layer[0]
		var left := PackedVector2Array()
		var right := PackedVector2Array()
		for i in steps + 1:
			var k := float(i) / steps
			var along := (centers[mini(i + 1, steps)] - centers[maxi(i - 1, 0)]).normalized()
			var side := Vector2(-along.y, along.x)
			var half := width * scale * 0.5 * sin(k * PI) + 0.01
			left.append(centers[i] + side * half)
			right.append(centers[i] - side * half)
		right.reverse()
		var outline := left + right
		if Geometry2D.triangulate_polygon(outline).size() > 0:
			draw_colored_polygon(outline, layer[1])


func _draw_strike(item: Dictionary, color: Color) -> void:
	var t: float = item["t"]
	var at: Vector2 = item["at"]
	var u: Vector2 = item["u"]
	var up: Vector2 = item["up"]
	var heavy: bool = item["heavy"]
	var alpha := 0.35 if item["miss"] else 1.0
	match String(item["dtype"]):
		"slash":
			# Crescent cut from the near-high side to the far-low side.
			var arcs := 2 if heavy else 1
			for n in arcs:
				var lt := clampf((t - n * 0.12) / (1.0 - n * 0.12), 0.0, 1.0)
				var shift := -up * 16.0 * n
				var a := at - u * 64.0 + up * 36.0 + shift
				var b := at + u * 14.0 + up * 22.0 + shift
				var c := at + u * 62.0 - up * 34.0 + shift
				var head := _ease_out(lt / 0.5)
				var tail := clampf(head - 0.55 + maxf(lt - 0.5, 0.0) * 2.2, 0.0, 1.0)
				_draw_sweep(a, b, c, tail, head, 9.0 if heavy else 6.5, color, alpha * (1.0 - maxf(lt - 0.75, 0.0) * 4.0))
		"pierce":
			# Hit mark only: a triangular stab streak shoots from the near side
			# through the target (wide at the entry, pointed at the far side).
			var head := _ease_out(t / 0.3)
			var tail := _ease_in((t - 0.3) / 0.5)
			var entry := at - u * 62.0
			var tip := entry + u * lerpf(10.0, 128.0, head)
			var base := entry + u * lerpf(0.0, 112.0, tail)
			var half := (11.0 if heavy else 8.0) * (1.0 - tail)
			if tip.distance_to(base) > 2.0 and half > 0.3:
				var fade := alpha * (1.0 - _ease_in((t - 0.6) / 0.4))
				draw_colored_polygon(PackedVector2Array([tip + u * 6.0, base + up * (half + 5.0), base - up * (half + 5.0)]), Color(color, 0.35 * fade))
				draw_colored_polygon(PackedVector2Array([tip, base + up * half, base - up * half]), Color(1, 1, 1, fade))
			# Sparks thrown forward out of the far side.
			if t > 0.22 and not item["miss"]:
				var st := clampf((t - 0.22) / 0.5, 0.0, 1.0)
				for i in 4:
					var seed: Vector2 = item["seeds"][i]
					var dir := u.rotated(seed.x * 0.5)
					var p0 := at + u * 48.0 + dir * 36.0 * st
					draw_line(p0, p0 + dir * 14.0 * seed.y * (1.0 - st), Color(1, 1, 1, 1.0 - st), 2.0, true)
		"blunt":
			# Hit mark only: a flattened impact burst on the near side, then
			# shock fronts and debris roll forward through the target.
			var heading := u.angle()
			var origin := at - u * 46.0
			var burst := clampf(t / 0.22, 0.0, 1.0)
			if burst < 1.0:
				var flare := 1.0 - burst
				var width := lerpf(10.0, 30.0, _ease_out(burst))
				draw_arc(origin, width, heading - 1.25, heading + 1.25, 16, Color(1, 1, 1, alpha * flare), 7.0 * flare + 2.0, true)
				draw_arc(origin, width + 8.0, heading - 1.25, heading + 1.25, 16, Color(color, 0.4 * alpha * flare), 10.0 * flare + 2.0, true)
			for i in (4 if heavy else 3):
				var wt := clampf((t - 0.06 - i * 0.09) / 0.6, 0.0, 1.0)
				if wt <= 0.0 or wt >= 1.0:
					continue
				var radius := lerpf(18.0, 120.0 if heavy else 100.0, _ease_out(wt))
				var span := lerpf(1.1, 0.75, wt)
				draw_arc(origin, radius, heading - span, heading + span, 20, Color(color, (1.0 - wt) * alpha), 6.0 * (1.0 - wt) + 1.0, true)
			if not item["miss"]:
				var dt := clampf((t - 0.15) / 0.65, 0.0, 1.0)
				if dt > 0.0:
					for i in 6:
						var seed: Vector2 = item["seeds"][i]
						var dir := u.rotated(seed.x * 0.9)
						var p := at - u * 10.0 + dir * 80.0 * seed.y * dt + Vector2(0, 50.0 * dt * dt)
						draw_circle(p, 3.0 * (1.0 - dt) + 0.5, Color(color, 1.0 - dt))
		"claw":
			# Three (four on a crit) parallel rakes, near-high to far-low, one after another.
			var rake := (u * 1.0 - up * 0.75).normalized()
			var across := Vector2(-rake.y, rake.x)
			var count := 4 if heavy else 3
			for i in count:
				var lt := clampf((t - i * 0.07) / 0.7, 0.0, 1.0)
				var offset := across * (i - (count - 1) / 2.0) * 15.0
				var a := at - rake * 58.0 + offset
				var c := at + rake * 58.0 + offset
				var b := (a + c) / 2.0 + up * 10.0
				var head := _ease_out(lt / 0.45)
				var tail := clampf(head - 0.7 + maxf(lt - 0.45, 0.0) * 2.0, 0.0, 1.0)
				_draw_sweep(a, b, c, tail, head, 4.0, color, alpha * (1.0 - maxf(lt - 0.7, 0.0) * 3.3))
		"bite":
			# Two rows of teeth lunge in from the near side and snap shut.
			var close := _ease_in(t / 0.28)
			var x := lerpf(-56.0, 6.0, _ease_out(t / 0.28))
			var gap := lerpf(34.0, 3.0, close)
			var fade := alpha * (1.0 - _ease_in((t - 0.55) / 0.45))
			var center := at + u * x
			for jaw: float in [1.0, -1.0]:
				var line := center + up * gap * jaw
				draw_line(line - u * 34.0, line + u * 34.0, Color("#7a2a2a", fade), 5.0, true)
				for i in 5:
					var along := (i - 2.0) * 13.0 + (0.0 if jaw > 0 else 6.5)
					var root := line + u * along
					var tooth := PackedVector2Array([root - u * 5.5, root + u * 5.5, root - up * jaw * 15.0])
					draw_colored_polygon(tooth, Color(color, fade))
			if t > 0.28 and not item["miss"]:
				var dt := clampf((t - 0.28) / 0.6, 0.0, 1.0)
				for i in 6:
					var seed: Vector2 = item["seeds"][i]
					var dir := u.rotated(seed.x * 0.7)
					var p := center + dir * 64.0 * seed.y * dt + Vector2(0, 40.0 * dt * dt)
					draw_circle(p, 3.5 * (1.0 - dt) + 0.5, Color(0.85, 0.12, 0.12, 1.0 - dt))


func _draw_splash(item: Dictionary, color: Color) -> void:
	var t: float = item["t"]
	var at: Vector2 = item["at"]
	var u: Vector2 = item["u"]
	var reach := 80.0 if item["heavy"] else 58.0
	for ray: Dictionary in item["rays"]:
		var dir := u.rotated(float(ray["angle"]))
		var far := reach * float(ray["length"]) * _ease_out(t)
		var near := maxf(far - 26.0, 0.0) + 16.0 * t
		draw_line(at + dir * near, at + dir * far, Color(color, 0.9 * (1.0 - t)), 3.0 * (1.0 - t) + 1.0, true)
