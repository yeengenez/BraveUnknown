class_name MonsterPortrait
extends Control
## Draws a MONSTER bust portrait from a PortraitGen.monster() look. (Heroes use
## the pixel-art module in res://portraits/ via UnitPortrait.) Everything is
## drawn in a 100 x 100 space and scaled to the control, so the same look
## works as a 40 px battle icon or a 160 px character sheet.

var look: Dictionary = {}
var dimmed := false  ## greyed out (downed / dead)
var corner := 6
## How far the bust is zoomed in, and the point it centres on (100 x 100 space).
var zoom := 1.2
var focus := Vector2(50, 57)


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip_contents = true


func set_look(p_look: Dictionary, p_dimmed: bool = false) -> void:
	look = p_look
	dimmed = p_dimmed
	modulate = Color(0.55, 0.55, 0.58) if dimmed else Color.WHITE
	queue_redraw()


# ------------------------------------------------------------------ helpers
static func _ell(c: Vector2, rx: float, ry: float, n: int = 28) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in n:
		var a := TAU * i / n
		points.append(c + Vector2(cos(a) * rx, sin(a) * ry))
	return points


func _fill(points: PackedVector2Array, color: Color) -> void:
	if points.size() >= 3 and Geometry2D.triangulate_polygon(points).size() > 0:
		draw_colored_polygon(points, color)


func _ellipse(c: Vector2, rx: float, ry: float, color: Color) -> void:
	_fill(_ell(c, rx, ry), color)


func _line(points: Array, color: Color, width: float) -> void:
	draw_polyline(PackedVector2Array(points), color, width, true)


## Face outline: an ellipse whose lower half narrows into a jaw.
static func _head(cx: float, cy: float, rx: float, ry: float, jaw: float, n: int = 40) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in n:
		var a := TAU * i / n
		var s := sin(a)
		var x := cos(a) * rx
		var y := s * ry
		if s > 0.0:
			x *= lerpf(1.0, jaw, s)
			y *= 1.0 + 0.05 * s * s
		points.append(Vector2(cx + x, cy + y))
	return points


## The part of the face below y_from, pushed outward and stretched at the
## chin by `drop` (beards).
static func _lower_face(head: PackedVector2Array, cx: float, cy: float, ry: float, y_from: float, grow: float, drop: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for p: Vector2 in head:
		if p.y >= y_from:
			var depth := clampf((p.y - cy) / ry, 0.0, 1.2)
			points.append(Vector2(cx + (p.x - cx) * grow, p.y + drop * pow(depth, 3.0)))
	return points


## The cap of hair (or a helmet) across the top of the head down to a fringe.
static func _cap(cx: float, cy: float, rx: float, ry: float, fringe: Array, spiky: bool = false) -> PackedVector2Array:
	var points := PackedVector2Array()
	var n := 22
	for i in n + 1:
		var a := PI + PI * i / n
		var r := 1.0
		if spiky and i > 1 and i < n - 1:
			r = 1.16 if i % 2 == 0 else 1.0
		points.append(Vector2(cx + cos(a) * rx * r, cy + sin(a) * ry * r))
	for p: Vector2 in fringe:
		points.append(p)
	return points


# ------------------------------------------------------------------ draw
func _draw() -> void:
	var side := minf(size.x, size.y)
	draw_style_box(UIKit.box(Color("#111318"), Color("#111318"), 0, corner, 0), Rect2(Vector2.ZERO, size))
	if look.is_empty():
		return
	var s := side / 100.0
	var origin := (size - Vector2(side, side)) / 2.0 + Vector2(50, 50) * s - focus * s * zoom
	draw_set_transform(origin, 0.0, Vector2(s, s) * zoom)
	_backdrop()
	match String(look.get("kind", "human")):
		"skeleton":
			_body()
			_skeleton()
		"wolf":
			_wolf()
		"rat":
			_rat()
		"kobold":
			_body()
			_kobold()
		_:
			_humanoid()
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _backdrop() -> void:
	var accent: Color = look.get("accent", Color("#444444"))
	var top := accent.darkened(0.62)
	var bottom := accent.darkened(0.3)
	draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 100), Vector2(0, 100)]),
		PackedColorArray([top, top, bottom, bottom]))
	_ellipse(Vector2(50, 40), 40, 40, Color(accent.lightened(0.25), 0.16))


# ------------------------------------------------------------------ people
func _humanoid() -> void:
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.5
	var cy := 45.0
	var rx: float = look["face_w"]
	var ry: float = look["face_h"]
	var jaw: float = look["jaw"]
	var skin: Color = look["skin"]
	var hair: Color = look["hair"]
	var gear: String = look.get("gear", "none")
	var style: String = look.get("hair_style", "crop")
	var head := _head(cx, cy, rx, ry, jaw)

	# -- behind the head
	if gear == "hood":
		var hood: Color = Color(look["accent"]).darkened(0.15)
		_fill(_ell(Vector2(cx, cy - 1), rx + 10.0, ry + 9.0), hood)
	elif gear == "coif":
		_fill(_ell(Vector2(cx, cy + 1), rx + 6.0, ry + 7.0), Color("#8d939b"))
	elif style in ["long", "braid", "stringy"] and gear != "helm":
		var back := PackedVector2Array([
			Vector2(cx - rx - 4, cy - 6), Vector2(cx + rx + 4, cy - 6),
			Vector2(cx + rx + 6, cy + 30), Vector2(cx, cy + 34), Vector2(cx - rx - 6, cy + 30)])
		_fill(back, hair.darkened(0.25))
	if style == "ponytail" and gear in ["none", "circlet"]:
		_fill(PackedVector2Array([Vector2(cx + rx - 4, cy - 14), Vector2(cx + rx + 7, cy - 8), Vector2(cx + rx + 9, cy + 26), Vector2(cx + rx + 2, cy + 30), Vector2(cx + rx - 1, cy)]), hair.darkened(0.2))
	if style == "bun" and gear in ["none", "circlet"]:
		_ellipse(Vector2(cx + 1, cy - ry - 3), 7.5, 6.5, hair.darkened(0.15))

	_body()

	# -- neck
	_fill(PackedVector2Array([Vector2(cx - 6.5, cy + ry - 8), Vector2(cx + 6.5, cy + ry - 8), Vector2(cx + 7.5, cy + ry + 9), Vector2(cx - 7.5, cy + ry + 9)]), skin.darkened(0.22))

	# -- ears
	var ears: String = look.get("ears", "normal")
	for sx: float in [-1.0, 1.0]:
		var ex := cx + sx * (rx - 0.5)
		match ears:
			"goblin":
				_fill(PackedVector2Array([Vector2(ex, cy - 4), Vector2(ex + sx * 17.0, cy - 12), Vector2(ex + sx * 2.0, cy + 6)]) if sx > 0 else PackedVector2Array([Vector2(ex, cy - 4), Vector2(ex + sx * 2.0, cy + 6), Vector2(ex + sx * 17.0, cy - 12)]), skin.darkened(0.08))
				_fill(PackedVector2Array([Vector2(ex + sx * 2.0, cy - 3), Vector2(ex + sx * 12.0, cy - 9), Vector2(ex + sx * 3.0, cy + 3)]) if sx > 0 else PackedVector2Array([Vector2(ex + sx * 2.0, cy - 3), Vector2(ex + sx * 3.0, cy + 3), Vector2(ex + sx * 12.0, cy - 9)]), skin.darkened(0.3))
			"pointed":
				_fill(PackedVector2Array([Vector2(ex, cy - 3), Vector2(ex + sx * 8.0, cy - 9), Vector2(ex + sx * 2.5, cy + 6)]) if sx > 0 else PackedVector2Array([Vector2(ex, cy - 3), Vector2(ex + sx * 2.5, cy + 6), Vector2(ex + sx * 8.0, cy - 9)]), skin.darkened(0.08))
			_:
				_ellipse(Vector2(ex + sx * 1.5, cy + 2), 3.4, 5.5, skin.darkened(0.08))
				_ellipse(Vector2(ex + sx * 1.6, cy + 2), 1.6, 3.2, skin.darkened(0.25))

	# -- face with simple light from the upper left
	_fill(head, skin.darkened(0.2))
	var lit := PackedVector2Array()
	for p: Vector2 in head:
		lit.append(Vector2(cx - 1.4, cy - 1.2) + (p - Vector2(cx, cy)) * 0.93)
	_fill(lit, skin)
	if look.get("blush", false):
		for sx: float in [-1.0, 1.0]:
			_ellipse(Vector2(cx + sx * (rx * 0.55), cy + ry * 0.32), 4.0, 2.4, Color(0.85, 0.35, 0.3, 0.16))

	# -- features
	_eyes(cx, cy, rx, ry)
	_nose(cx, cy, ry, skin)
	_age_lines(cx, cy, rx, ry, skin)

	# -- beard (under the mouth line so the mouth stays readable)
	var beard: String = look.get("beard", "none")
	var beard_color := hair.darkened(0.05)
	match beard:
		"stubble":
			_fill(_lower_face(head, cx, cy, ry, cy + ry * 0.28, 1.0, 0.0), Color(beard_color, 0.32))
		"short":
			_fill(_lower_face(head, cx, cy, ry, cy + ry * 0.3, 1.05, 3.5), beard_color)
		"full":
			_fill(_lower_face(head, cx, cy, ry, cy + ry * 0.24, 1.07, 11.0), beard_color)
		"goatee":
			_ellipse(Vector2(cx, cy + ry * 0.93), 4.5, 5.5, beard_color)
	_mouth(cx, cy, ry, skin)
	if beard in ["short", "full", "moustache", "goatee"]:
		var my := cy + ry * 0.6
		_fill(PackedVector2Array([Vector2(cx - 8, my + 2.2), Vector2(cx - 4, my - 2.2), Vector2(cx, my - 1.4), Vector2(cx + 4, my - 2.2), Vector2(cx + 8, my + 2.2), Vector2(cx + 3.5, my + 0.4), Vector2(cx, my + 0.8), Vector2(cx - 3.5, my + 0.4)]), beard_color.darkened(0.1))

	_scar(cx, cy, rx, ry)

	# -- hair and headgear in front
	if gear != "helm" and gear != "coif":
		_hair_front(cx, cy, rx, ry, hair, style, gear)
	_headgear(cx, cy, rx, ry, gear)


func _eyes(cx: float, cy: float, rx: float, ry: float) -> void:
	var gap: float = look["eye_gap"]
	var eye_color: Color = look["eyes"]
	var glow: bool = look.get("eye_glow", false)
	var monster := String(look.get("kind", "human")) != "human"
	var brow_tilt: float = look["brow_tilt"]
	var fem: bool = look.get("fem", false)
	var hair: Color = look["hair"]
	var ey := cy + 1.0
	for sx: float in [-1.0, 1.0]:
		var ex := cx + sx * gap
		if glow:
			_ellipse(Vector2(ex, ey), 4.2, 3.0, Color(eye_color, 0.3))
			_ellipse(Vector2(ex, ey), 2.6, 1.8, eye_color)
			_ellipse(Vector2(ex, ey), 1.0, 1.0, Color.WHITE)
		elif monster:
			_ellipse(Vector2(ex, ey), 3.4, 2.4, eye_color)
			_ellipse(Vector2(ex, ey), 0.8, 2.1, Color("#1a1210"))
		else:
			_ellipse(Vector2(ex, ey), 3.6, 2.2, Color("#f2ede4"))
			_ellipse(Vector2(ex + sx * 0.2, ey + 0.1), 1.9, 1.9, eye_color)
			_ellipse(Vector2(ex + sx * 0.2, ey + 0.1), 0.95, 0.95, Color("#140f0c"))
			_ellipse(Vector2(ex - 0.6, ey - 0.7), 0.5, 0.5, Color(1, 1, 1, 0.9))
		# upper lid
		_line([Vector2(ex - 3.9, ey + 0.3), Vector2(ex - 1.5, ey - 2.2), Vector2(ex + 1.5, ey - 2.2), Vector2(ex + 3.9, ey + 0.3)], Color("#3a2620"), 1.3 if fem else 0.9)
		if fem and not monster:
			_line([Vector2(ex + sx * 3.6, ey - 0.2), Vector2(ex + sx * 5.2, ey - 1.6)], Color("#3a2620"), 0.9)
		# brow: inner end lower when stern
		var inner := Vector2(ex - sx * 3.6, ey - 5.0 + brow_tilt * 0.9)
		var outer := Vector2(ex + sx * 4.4, ey - 5.6 - brow_tilt * 0.4)
		var brow_color := hair.darkened(0.25) if not monster else Color(look["skin"]).darkened(0.45)
		_line([inner, (inner + outer) / 2.0 + Vector2(0, -0.9), outer], brow_color, 1.6 if fem else 2.3)


func _nose(cx: float, cy: float, ry: float, skin: Color) -> void:
	var shade := skin.darkened(0.3)
	var ny := cy + ry * 0.42
	match int(look.get("nose", 0)):
		0:
			_line([Vector2(cx - 0.5, cy + 3), Vector2(cx - 2.2, ny), Vector2(cx + 1.2, ny + 0.8)], shade, 1.1)
		1:
			_line([Vector2(cx + 0.5, cy + 2), Vector2(cx + 2.0, ny - 1), Vector2(cx - 0.5, ny + 1)], shade, 1.2)
			_ellipse(Vector2(cx - 2.2, ny + 0.4), 1.0, 0.7, shade)
		_:
			_ellipse(Vector2(cx, ny), 3.6, 2.4, skin.darkened(0.12))
			_ellipse(Vector2(cx - 1.6, ny + 0.6), 0.9, 0.6, shade.darkened(0.2))
			_ellipse(Vector2(cx + 1.6, ny + 0.6), 0.9, 0.6, shade.darkened(0.2))


func _mouth(cx: float, cy: float, ry: float, skin: Color) -> void:
	var my := cy + ry * 0.62
	var curve: float = look["mouth_curve"]
	var width := 4.2 if look.get("fem", false) else 4.8
	var lip := Color("#9c4a48") if look.get("fem", false) else skin.darkened(0.42)
	var kind := String(look.get("mouth", "plain"))
	if kind != "plain":
		width = 6.5
	_line([Vector2(cx - width, my - curve * 0.5), Vector2(cx, my + curve * 0.35), Vector2(cx + width, my - curve * 0.5)], lip, 1.4)
	if look.get("fem", false):
		_ellipse(Vector2(cx, my + 1.6), 2.6, 1.0, Color(lip, 0.45))
	match kind:
		"fangs":
			for sx: float in [-1.0, 1.0]:
				_fill(PackedVector2Array([Vector2(cx + sx * 3.0, my), Vector2(cx + sx * 4.6, my), Vector2(cx + sx * 3.8, my + 3.2)]), Color("#f3eedc"))
		"tusks":
			for sx: float in [-1.0, 1.0]:
				_fill(PackedVector2Array([Vector2(cx + sx * 4.2, my + 1.5), Vector2(cx + sx * 6.6, my + 1.5), Vector2(cx + sx * 5.8, my - 5.5)]), Color("#efe6cf"))


func _age_lines(cx: float, cy: float, rx: float, ry: float, skin: Color) -> void:
	var age: float = look.get("age", 0.0)
	if age < 0.65 or String(look.get("kind", "human")) != "human":
		return
	var line_color := Color(skin.darkened(0.35), clampf((age - 0.65) * 3.0, 0.3, 0.8))
	var gap: float = look["eye_gap"]
	for sx: float in [-1.0, 1.0]:
		_line([Vector2(cx + sx * (gap - 2.5), cy + 4.2), Vector2(cx + sx * (gap + 2.5), cy + 3.6)], line_color, 0.7)
		_line([Vector2(cx + sx * 3.5, cy + ry * 0.45), Vector2(cx + sx * 6.0, cy + ry * 0.68)], line_color, 0.7)
	if age > 0.8:
		_line([Vector2(cx - 6, cy - 12), Vector2(cx + 6, cy - 12.5)], line_color, 0.7)


func _scar(cx: float, cy: float, rx: float, ry: float) -> void:
	var scar: int = look.get("scar", -1)
	if scar < 0:
		return
	var gap: float = look["eye_gap"]
	var sx := -1.0 if scar % 2 == 0 else 1.0
	var a: Vector2
	var b: Vector2
	if scar < 5:  # across an eye
		a = Vector2(cx + sx * (gap - 3.0), cy - 8.0)
		b = Vector2(cx + sx * (gap + 2.0), cy + 8.0)
	else:  # cheek
		a = Vector2(cx + sx * (rx * 0.35), cy + ry * 0.2)
		b = Vector2(cx + sx * (rx * 0.75), cy + ry * 0.5)
	var color := Color(0.75, 0.38, 0.36, 0.85)
	_line([a, b], color, 1.3)
	for k in 3:
		var m := a.lerp(b, 0.25 + k * 0.25)
		var across := (b - a).normalized().orthogonal() * 1.6
		_line([m - across, m + across], Color(color, 0.6), 0.6)


func _hair_front(cx: float, cy: float, rx: float, ry: float, hair: Color, style: String, gear: String) -> void:
	var hood := gear == "hood" or gear == "hat"
	var fringe: Array = []
	var spiky := false
	var hx := rx + 1.6
	var hy := ry + 1.4
	var top := cy - 1.5
	match style:
		"bald":
			for sx: float in [-1.0, 1.0]:
				_fill(PackedVector2Array([Vector2(cx + sx * (rx + 0.5), cy - 6), Vector2(cx + sx * (rx - 3), cy - 9), Vector2(cx + sx * (rx - 2.5), cy + 1), Vector2(cx + sx * (rx + 0.8), cy + 3)]), hair)
			return
		"tuft":
			for k in 3:
				var x := cx - 4.0 + k * 4.0
				_fill(PackedVector2Array([Vector2(x - 2.5, cy - ry + 1), Vector2(x + 2.5, cy - ry + 1), Vector2(x + (k - 1) * 3.0, cy - ry - 7)]), hair)
			return
		"stringy":
			for k in 7:
				var x := cx - rx + 2.0 + k * (rx * 2.0 - 4.0) / 6.0
				_line([Vector2(x, cy - ry + 3), Vector2(x + (x - cx) * 0.15, cy - 6), Vector2(x + (x - cx) * 0.25, cy + 10 + (k % 3) * 4)], hair, 1.2)
			return
		"crop":
			fringe = [Vector2(cx + rx + 0.5, cy - 5), Vector2(cx + rx * 0.5, cy - 12), Vector2(cx, cy - 13.5), Vector2(cx - rx * 0.5, cy - 12), Vector2(cx - rx - 0.5, cy - 5)]
		"receding":
			fringe = [Vector2(cx + rx + 0.5, cy - 6), Vector2(cx + rx * 0.55, cy - 15), Vector2(cx + 2, cy - 17.5), Vector2(cx, cy - 15.5), Vector2(cx - 2, cy - 17.5), Vector2(cx - rx * 0.55, cy - 15), Vector2(cx - rx - 0.5, cy - 6)]
		"swept":
			fringe = [Vector2(cx + rx + 0.8, cy - 2), Vector2(cx + rx * 0.4, cy - 8), Vector2(cx - rx * 0.2, cy - 12.5), Vector2(cx - rx * 0.7, cy - 14), Vector2(cx - rx - 0.8, cy - 7)]
		"spiky":
			spiky = true
			fringe = [Vector2(cx + rx + 0.5, cy - 6), Vector2(cx + rx * 0.6, cy - 11), Vector2(cx + rx * 0.3, cy - 9), Vector2(cx, cy - 13), Vector2(cx - rx * 0.3, cy - 9), Vector2(cx - rx * 0.6, cy - 11), Vector2(cx - rx - 0.5, cy - 6)]
		"topknot":
			fringe = [Vector2(cx + rx + 0.5, cy - 7), Vector2(cx, cy - 14), Vector2(cx - rx - 0.5, cy - 7)]
		_:  # long, braid, bun, ponytail: centre parting
			fringe = [Vector2(cx + rx + 1.2, cy + 4), Vector2(cx + rx * 0.7, cy - 9), Vector2(cx + 1.5, cy - 15), Vector2(cx - 1.5, cy - 15), Vector2(cx - rx * 0.7, cy - 9), Vector2(cx - rx - 1.2, cy + 4)]
	if hood:
		# Under a hood or hat only the fringe shows.
		fringe = [Vector2(cx + rx * 0.8, cy - 8), Vector2(cx, cy - 12.5), Vector2(cx - rx * 0.8, cy - 8)]
		var under := PackedVector2Array([Vector2(cx - rx * 0.85, cy - 14), Vector2(cx + rx * 0.85, cy - 14)])
		under.append_array(PackedVector2Array(fringe))
		_fill(under, hair)
		return
	_fill(_cap(cx, top, hx, hy, fringe, spiky), hair)
	_line([Vector2(cx - rx * 0.5, cy - ry + 3), Vector2(cx - rx * 0.1, cy - ry + 1.2)], Color(hair.lightened(0.35), 0.6), 1.2)
	if style in ["long", "braid"]:
		for sx: float in [-1.0, 1.0]:
			_fill(PackedVector2Array([Vector2(cx + sx * (rx + 1.2), cy + 3), Vector2(cx + sx * (rx - 1.8), cy + 4), Vector2(cx + sx * (rx - 1.0), cy + 22), Vector2(cx + sx * (rx + 3.0), cy + 26)]) if sx < 0 else PackedVector2Array([Vector2(cx + sx * (rx + 1.2), cy + 3), Vector2(cx + sx * (rx + 3.0), cy + 26), Vector2(cx + sx * (rx - 1.0), cy + 22), Vector2(cx + sx * (rx - 1.8), cy + 4)]), hair)
	if style == "braid":
		for k in 4:
			_ellipse(Vector2(cx - rx - 2.0, cy + 26 + k * 4.5), 2.6, 2.4, hair.darkened(0.1 * (k % 2)))
	if style == "topknot":
		_ellipse(Vector2(cx, cy - ry - 4), 5.0, 4.2, hair)
		_ellipse(Vector2(cx, cy - ry + 0.5), 3.0, 1.4, hair.darkened(0.3))


func _headgear(cx: float, cy: float, rx: float, ry: float, gear: String) -> void:
	var accent: Color = look["accent"]
	match gear:
		"helm":
			var steel := Color("#a3acb6")
			_fill(_cap(cx, cy - 6.0, rx + 2.6, ry - 1.8, []), steel)
			_fill(PackedVector2Array([Vector2(cx - rx - 3, cy - 10), Vector2(cx + rx + 3, cy - 10), Vector2(cx + rx + 3, cy - 5), Vector2(cx - rx - 3, cy - 5)]), steel.darkened(0.25))
			_fill(PackedVector2Array([Vector2(cx - 1.8, cy - 9), Vector2(cx + 1.8, cy - 9), Vector2(cx + 1.4, cy + 7), Vector2(cx - 1.4, cy + 7)]), steel.darkened(0.12))
			_line([Vector2(cx - rx * 0.6, cy - ry + 1), Vector2(cx - rx * 0.1, cy - ry - 1.5)], Color(1, 1, 1, 0.55), 1.6)
			for sx: float in [-1.0, 1.0]:
				_ellipse(Vector2(cx + sx * (rx - 1.0), cy - 7.5), 0.9, 0.9, steel.darkened(0.45))
		"coif":
			var mail := Color("#8d939b")
			_fill(_cap(cx, cy - 1.0, rx + 2.4, ry + 2.0, [Vector2(cx + rx + 2.4, cy + 6), Vector2(cx + rx - 0.5, cy - 9), Vector2(cx, cy - 12), Vector2(cx - rx + 0.5, cy - 9), Vector2(cx - rx - 2.4, cy + 6)]), mail)
			for k in 4:
				_line([Vector2(cx - rx + 1, cy - 13 - k * 3.5), Vector2(cx + rx - 1, cy - 13 - k * 3.5)], Color(mail.darkened(0.3), 0.6), 0.6)
			_line([Vector2(cx - rx + 0.5, cy - 9.5), Vector2(cx, cy - 12.5), Vector2(cx + rx - 0.5, cy - 9.5)], Color("#d9b44a"), 1.4)
		"circlet":
			var gold := Color("#d9b44a")
			_line([Vector2(cx - rx - 0.5, cy - 8), Vector2(cx, cy - 11.5), Vector2(cx + rx + 0.5, cy - 8)], gold, 1.6)
			_ellipse(Vector2(cx, cy - 11.5), 1.8, 1.8, Color("#5fb0e8"))
		"hood":
			var cloth := accent.darkened(0.05)
			var rim := PackedVector2Array()
			var n := 26
			for i in n + 1:
				var a := PI * 0.82 + PI * 1.36 * i / n
				rim.append(Vector2(cx + cos(a) * (rx + 4.0), cy + 1 + sin(a) * (ry + 3.0)))
			draw_polyline(rim, cloth, 7.0, true)
			draw_polyline(rim, Color(0, 0, 0, 0.25), 2.0, true)
			_fill(PackedVector2Array([Vector2(cx - rx - 7.5, cy + 12), Vector2(cx - rx - 1.5, cy + 16), Vector2(cx - 5, cy + ry + 12), Vector2(cx - rx - 6, cy + ry + 14)]), cloth)
			_fill(PackedVector2Array([Vector2(cx + rx + 7.5, cy + 12), Vector2(cx + rx + 6, cy + ry + 14), Vector2(cx + 5, cy + ry + 12), Vector2(cx + rx + 1.5, cy + 16)]), cloth)
		"hat":
			var hat := accent.darkened(0.2)
			var lean: float = look.get("lean", 0.0)
			_fill(PackedVector2Array([Vector2(cx - 17, cy - 14), Vector2(cx + 17, cy - 14), Vector2(cx + 8 + lean, cy - 36), Vector2(cx + 17 + lean * 2.0, cy - 46), Vector2(cx - 2 + lean, cy - 38)]), hat)
			_fill(_ell(Vector2(cx, cy - 13), 30.0, 6.5), hat.darkened(0.25))
			_fill(PackedVector2Array([Vector2(cx - 16.5, cy - 19), Vector2(cx + 16.5, cy - 19), Vector2(cx + 17, cy - 14.5), Vector2(cx - 17, cy - 14.5)]), Color("#d9b44a"))
			_star(Vector2(cx + 1 + lean * 0.5, cy - 27), 3.6, Color("#e9d27a"))


func _star(c: Vector2, r: float, color: Color) -> void:
	var points := PackedVector2Array()
	for i in 10:
		var a := -PI / 2.0 + i * PI / 5.0
		points.append(c + Vector2(cos(a), sin(a)) * (r if i % 2 == 0 else r * 0.45))
	_fill(points, color)


## Shoulders and clothing, by armor category (Cloth / Light / Medium / Heavy).
func _body() -> void:
	var accent: Color = look["accent"]
	var material: String = look.get("material", "Light")
	var class_id: String = look.get("class_id", "")
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.3
	var shoulders := PackedVector2Array([
		Vector2(2, 100), Vector2(4, 90), Vector2(13, 80), Vector2(30, 73.5), Vector2(cx - 8, 71),
		Vector2(cx + 8, 71), Vector2(70, 73.5), Vector2(87, 80), Vector2(96, 90), Vector2(98, 100)])
	match material:
		"Cloth":
			var robe := Color("#e6dfcd") if class_id == "cleric" else accent.darkened(0.15)
			_fill(shoulders, robe)
			_fill(PackedVector2Array([Vector2(cx - 9, 71), Vector2(cx + 9, 71), Vector2(cx, 88)]), robe.darkened(0.35))
			var trim := Color("#d9b44a")
			_line([Vector2(cx - 11, 71), Vector2(cx, 90), Vector2(cx + 11, 71)], trim, 1.8)
			if class_id == "cleric":
				_ellipse(Vector2(cx, 94), 4.0, 4.0, trim)
				_ellipse(Vector2(cx, 94), 2.0, 2.0, robe)
			elif class_id == "mage":
				_ellipse(Vector2(cx, 91), 2.6, 2.6, Color("#5fd0ff"))
		"Light":
			var leather := Color("#7a5232")
			_fill(shoulders, leather)
			_fill(PackedVector2Array([Vector2(cx - 9, 71), Vector2(cx + 9, 71), Vector2(cx + 4, 80), Vector2(cx - 4, 80)]), leather.darkened(0.3))
			# cloak over the shoulders in the class colour
			_fill(PackedVector2Array([Vector2(2, 100), Vector2(4, 90), Vector2(13, 80), Vector2(28, 74), Vector2(24, 86), Vector2(18, 100)]), accent.darkened(0.1))
			_fill(PackedVector2Array([Vector2(98, 100), Vector2(82, 100), Vector2(76, 86), Vector2(72, 74), Vector2(87, 80), Vector2(96, 90)]), accent.darkened(0.1))
			_line([Vector2(30, 74), Vector2(70, 100)], Color("#4a3020"), 3.0)  # strap
		"Medium":
			var mail := Color("#8b929a")
			_fill(shoulders, mail)
			for row in 4:
				var y := 78.0 + row * 6.0
				for k in 14:
					var x := 6.0 + k * 7.0 + (3.5 if row % 2 == 1 else 0.0)
					draw_arc(Vector2(x, y), 3.2, 0.2, PI - 0.2, 6, Color(mail.darkened(0.35), 0.7), 0.8, true)
			_fill(PackedVector2Array([Vector2(cx - 8, 76), Vector2(cx + 8, 76), Vector2(cx + 9, 100), Vector2(cx - 9, 100)]), accent)
			_line([Vector2(cx - 8, 76), Vector2(cx + 8, 76)], accent.lightened(0.3), 1.2)
		"Heavy":
			var steel := Color("#b4bcc6")
			_fill(shoulders, steel.darkened(0.12))
			_fill(PackedVector2Array([Vector2(cx - 13, 74), Vector2(cx + 13, 74), Vector2(cx + 15, 100), Vector2(cx - 15, 100)]), steel)
			_line([Vector2(cx, 76), Vector2(cx, 100)], steel.darkened(0.3), 1.2)
			for sx: float in [-1.0, 1.0]:
				_ellipse(Vector2(cx + sx * 34.0, 84), 15.0, 9.0, steel.darkened(0.05))
				_line([Vector2(cx + sx * 22.0, 80), Vector2(cx + sx * 46.0, 82)], Color(1, 1, 1, 0.5), 1.4)
				_ellipse(Vector2(cx + sx * 34.0, 84), 1.2, 1.2, steel.darkened(0.45))
			_fill(PackedVector2Array([Vector2(cx - 10, 70), Vector2(cx + 10, 70), Vector2(cx + 12, 76), Vector2(cx - 12, 76)]), steel.darkened(0.25))
			_fill(PackedVector2Array([Vector2(cx - 5, 80), Vector2(cx + 5, 80), Vector2(cx + 5, 100), Vector2(cx - 5, 100)]), accent)


# ------------------------------------------------------------------ monsters
func _skeleton() -> void:
	var bone: Color = look["skin"]
	var glow: Color = look["eyes"]
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.4
	_fill(PackedVector2Array([Vector2(cx - 5, 60), Vector2(cx + 5, 60), Vector2(cx + 5, 75), Vector2(cx - 5, 75)]), bone.darkened(0.35))  # spine
	_ellipse(Vector2(cx, 38), 18.0, 18.0, bone.darkened(0.15))
	_ellipse(Vector2(cx - 1.2, 37), 16.5, 16.5, bone)
	_fill(PackedVector2Array([Vector2(cx - 13, 44), Vector2(cx + 13, 44), Vector2(cx + 10, 58), Vector2(cx - 10, 58)]), bone)
	_fill(PackedVector2Array([Vector2(cx - 10, 58), Vector2(cx + 10, 58), Vector2(cx + 8, 66), Vector2(cx - 8, 66)]), bone.darkened(0.12))  # jaw
	for sx: float in [-1.0, 1.0]:
		_ellipse(Vector2(cx + sx * 7.0, 42), 5.0, 5.5, Color("#1a1716"))
		_ellipse(Vector2(cx + sx * 7.0, 42.5), 2.6, 2.6, Color(glow, 0.35))
		_ellipse(Vector2(cx + sx * 7.0, 42.5), 1.2, 1.2, glow)
	_fill(PackedVector2Array([Vector2(cx, 47), Vector2(cx + 2.5, 53), Vector2(cx - 2.5, 53)]), Color("#1a1716"))
	_fill(PackedVector2Array([Vector2(cx - 8, 57), Vector2(cx + 8, 57), Vector2(cx + 8, 61), Vector2(cx - 8, 61)]), Color("#2a2523"))
	for k in 7:
		var x := cx - 7.0 + k * 2.33
		_fill(PackedVector2Array([Vector2(x - 0.9, 57), Vector2(x + 0.9, 57), Vector2(x + 0.9, 60.5), Vector2(x - 0.9, 60.5)]), bone)
	_line([Vector2(cx - 10, 30), Vector2(cx - 4, 35), Vector2(cx - 6, 40)], Color(bone.darkened(0.4), 0.8), 0.8)  # crack


func _kobold() -> void:
	var skin: Color = look["skin"]
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.4
	for sx: float in [-1.0, 1.0]:  # horns
		_fill(PackedVector2Array([Vector2(cx + sx * 8, 30), Vector2(cx + sx * 13, 28), Vector2(cx + sx * 22, 14)]) if sx > 0 else PackedVector2Array([Vector2(cx + sx * 8, 30), Vector2(cx + sx * 22, 14), Vector2(cx + sx * 13, 28)]), Color("#d8cfb4"))
	_fill(PackedVector2Array([Vector2(cx - 6, 58), Vector2(cx + 6, 58), Vector2(cx + 7, 76), Vector2(cx - 7, 76)]), skin.darkened(0.25))
	_ellipse(Vector2(cx, 40), 15.0, 13.0, skin.darkened(0.15))
	_ellipse(Vector2(cx - 1, 39), 13.5, 11.5, skin)
	_ellipse(Vector2(cx, 54), 9.5, 9.0, skin.darkened(0.08))  # snout
	_ellipse(Vector2(cx, 56), 7.5, 6.0, skin.lightened(0.12))
	for sx: float in [-1.0, 1.0]:
		_ellipse(Vector2(cx + sx * 2.4, 52), 0.9, 0.6, Color("#2a1810"))
		_ellipse(Vector2(cx + sx * 7.5, 39), 3.4, 2.6, look["eyes"])
		_ellipse(Vector2(cx + sx * 7.5, 39), 0.7, 2.3, Color("#1a1210"))
		_line([Vector2(cx + sx * 3.5, 34.5), Vector2(cx + sx * 11, 33)], skin.darkened(0.45), 1.8)
	_line([Vector2(cx - 6, 60), Vector2(cx, 61.5), Vector2(cx + 6, 60)], skin.darkened(0.5), 1.2)
	_fill(PackedVector2Array([Vector2(cx - 3.5, 60.5), Vector2(cx - 2.2, 60.8), Vector2(cx - 2.8, 63)]), Color("#f3eedc"))
	for k in 4:
		draw_arc(Vector2(cx - 6 + k * 4, 29), 2.0, 0.2, PI - 0.2, 5, Color(skin.darkened(0.35), 0.8), 0.8, true)


func _wolf() -> void:
	var fur: Color = look["skin"]
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.4
	# ruff and shoulders
	_fill(PackedVector2Array([Vector2(0, 100), Vector2(4, 84), Vector2(18, 70), Vector2(34, 64), Vector2(66, 64), Vector2(82, 70), Vector2(96, 84), Vector2(100, 100)]), fur.darkened(0.25))
	for sx: float in [-1.0, 1.0]:  # ears
		_fill(PackedVector2Array([Vector2(cx + sx * 6, 30), Vector2(cx + sx * 16, 30), Vector2(cx + sx * 15, 10)]) if sx > 0 else PackedVector2Array([Vector2(cx + sx * 6, 30), Vector2(cx + sx * 15, 10), Vector2(cx + sx * 16, 30)]), fur.darkened(0.15))
		_fill(PackedVector2Array([Vector2(cx + sx * 9, 28), Vector2(cx + sx * 14, 28), Vector2(cx + sx * 13.5, 17)]) if sx > 0 else PackedVector2Array([Vector2(cx + sx * 9, 28), Vector2(cx + sx * 13.5, 17), Vector2(cx + sx * 14, 28)]), Color("#3a2c2a"))
	_fill(PackedVector2Array([Vector2(cx - 20, 34), Vector2(cx - 14, 26), Vector2(cx, 23), Vector2(cx + 14, 26), Vector2(cx + 20, 34), Vector2(cx + 24, 52), Vector2(cx + 14, 62), Vector2(cx, 70), Vector2(cx - 14, 62), Vector2(cx - 24, 52)]), fur)
	for sx: float in [-1.0, 1.0]:  # cheek tufts
		_fill(PackedVector2Array([Vector2(cx + sx * 22, 46), Vector2(cx + sx * 29, 56), Vector2(cx + sx * 18, 58)]) if sx > 0 else PackedVector2Array([Vector2(cx + sx * 22, 46), Vector2(cx + sx * 18, 58), Vector2(cx + sx * 29, 56)]), fur.lightened(0.1))
	_fill(PackedVector2Array([Vector2(cx - 8, 46), Vector2(cx + 8, 46), Vector2(cx + 9, 62), Vector2(cx, 70), Vector2(cx - 9, 62)]), fur.lightened(0.35))  # muzzle
	_ellipse(Vector2(cx, 56), 4.0, 2.8, Color("#151313"))
	_line([Vector2(cx, 59), Vector2(cx, 63), Vector2(cx - 4, 65)], Color("#151313"), 1.0)
	_line([Vector2(cx, 63), Vector2(cx + 4, 65)], Color("#151313"), 1.0)
	for sx: float in [-1.0, 1.0]:
		_fill(PackedVector2Array([Vector2(cx + sx * 4, 42), Vector2(cx + sx * 12, 38), Vector2(cx + sx * 11, 43)]) if sx > 0 else PackedVector2Array([Vector2(cx + sx * 4, 42), Vector2(cx + sx * 11, 43), Vector2(cx + sx * 12, 38)]), look["eyes"])
		_ellipse(Vector2(cx + sx * 8.5, 41), 0.9, 1.2, Color("#151313"))
		_line([Vector2(cx + sx * 3, 38), Vector2(cx + sx * 12, 35)], fur.darkened(0.45), 1.6)


func _rat() -> void:
	var fur: Color = look["skin"]
	var lean: float = look.get("lean", 0.0)
	var cx := 50.0 + lean * 0.4
	_fill(PackedVector2Array([Vector2(0, 100), Vector2(6, 82), Vector2(24, 70), Vector2(76, 70), Vector2(94, 82), Vector2(100, 100)]), fur.darkened(0.2))
	for sx: float in [-1.0, 1.0]:
		_ellipse(Vector2(cx + sx * 17, 30), 9.5, 9.0, fur.darkened(0.1))
		_ellipse(Vector2(cx + sx * 17, 31), 6.0, 5.5, Color("#c98b86"))
	_fill(PackedVector2Array([Vector2(cx - 17, 36), Vector2(cx - 10, 28), Vector2(cx, 26), Vector2(cx + 10, 28), Vector2(cx + 17, 36), Vector2(cx + 15, 50), Vector2(cx + 6, 62), Vector2(cx, 66), Vector2(cx - 6, 62), Vector2(cx - 15, 50)]), fur)
	_ellipse(Vector2(cx, 57), 6.5, 6.0, fur.lightened(0.15))
	_ellipse(Vector2(cx, 63), 2.6, 2.0, Color("#d58a8a"))
	_fill(PackedVector2Array([Vector2(cx - 2, 66), Vector2(cx + 2, 66), Vector2(cx + 2, 71), Vector2(cx - 2, 71)]), Color("#efe2b8"))
	_line([Vector2(cx, 66), Vector2(cx, 71)], Color("#8a7a5a"), 0.5)
	for sx: float in [-1.0, 1.0]:
		_ellipse(Vector2(cx + sx * 7, 42), 2.6, 2.6, Color("#151313"))
		_ellipse(Vector2(cx + sx * 7, 42), 1.5, 1.5, look["eyes"])
		for k in 3:
			_line([Vector2(cx + sx * 5, 61 + k), Vector2(cx + sx * 20, 57 + k * 4)], Color(1, 1, 1, 0.45), 0.5)
