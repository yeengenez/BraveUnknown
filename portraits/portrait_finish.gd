class_name PortraitFinish
extends RefCounted
## Builds a finished hero portrait: stacks the layers and blends them into one painted image.
## GDScript port of art_source/new_art/portraits/finish.py compose() (branch art-source).
## Keep the two in step: if a pass changes there, change it here.
##
##   1 lines   eye, lash and mouth lines take the skin's darkest shade instead of fixed near-black
##   2 whites  eye whites (and teeth) become a warm off-white from the skin ramp; 1-px shadow under the upper lid
##   3 brows   darker hair shade on the lower edge of thick brows
##   4 hair    hair edge on skin uses the hair's own dark shade; hair casts a 1-2 px shadow onto the skin
##   5 neck    contact shadow on the skin just above the collar / scarf / armour
##   6 outline one outer silhouette outline (dark version of the fill colour); seams where the outfit meets
##             skin or hair use a dark shade of the outfit's own colour instead of black
##   7 grade   shared light: soft warm light from the upper left, shadows pulled toward one cool hue
##
## Building one takes tens of milliseconds, so finished portraits are cached per look.
## texture_async() builds on a worker thread so the UI never stalls; texture() builds right away.

const W := 200
const H := 200
const N := W * H
const LINE := Vector3(30, 22, 26)
const WHITE := Vector3(250, 248, 246)
const LUMA := Vector3(0.3, 0.59, 0.11)

## Layer tags (which layer is on top of each pixel).
enum { NONE, SKIN, BODY, EYES, IRIS, BROW, MOUTH, HAIR }
const ROLE_TAGS := {"skin": SKIN, "body": BODY, "eyes": EYES, "iris": IRIS, "brow": BROW, "mouth": MOUTH, "hair": HAIR}

static var _cache: Dictionary = {}
const CACHE_LIMIT := 300


## The finished portrait as a texture (with mipmaps for clean downscaling). Cached per look.
static func texture(a: HeroAppearance) -> ImageTexture:
	var key := a.key()
	if _cache.has(key):
		return _cache[key]
	var img := compose(a)
	img.generate_mipmaps()
	var tex := ImageTexture.create_from_image(img)
	if _cache.size() >= CACHE_LIMIT:
		_cache.erase(_cache.keys()[0])
	_cache[key] = tex
	return tex


static func clear_cache() -> void:
	_cache.clear()


static var _pending: Dictionary = {}  # look key -> callbacks waiting for that portrait


## Returns the cached texture at once, or null and builds it on a worker thread; `done` is
## then called with the texture on the main thread. Safe to call many times for one look.
static func texture_async(a: HeroAppearance, done: Callable) -> ImageTexture:
	var key := a.key()
	if _cache.has(key):
		return _cache[key]
	if _pending.has(key):
		(_pending[key] as Array).append(done)
		return null
	_pending[key] = [done]
	_warm(a)  # load parts and ramps here, so the worker only reads shared caches
	var look := HeroAppearance.from_dict(a.to_dict())
	WorkerThreadPool.add_task(func() -> void:
		var img := compose(look)
		img.generate_mipmaps()
		_finished.call_deferred(key, img))
	return null


static func _finished(key: String, img: Image) -> void:
	var tex := ImageTexture.create_from_image(img)
	if _cache.size() >= CACHE_LIMIT:
		_cache.erase(_cache.keys()[0])
	_cache[key] = tex
	for done: Callable in _pending.get(key, []):
		if done.is_valid():
			done.call(tex)
	_pending.erase(key)


## Fills the part and ramp caches for one look (main thread).
static func _warm(a: HeroAppearance) -> void:
	for layer: Array in a.layers():
		_part(layer[0])
		if layer[1] != "":
			_lut(layer[1], layer[2])
	PortraitLibrary.ramp_colors("skin", a.skin)


# ------------------------------------------------------------------ helpers
## Ramp (5 colours, 0-255) as Vector3s.
static func _ramp(group: String, ramp_name: String) -> Array:
	var out: Array = []
	for c: Color in PortraitLibrary.ramp_colors(group, ramp_name):
		out.append(Vector3(c.r8, c.g8, c.b8))
	return out


## Value map value (0-255, may be fractional) -> RGB along the ramp. Same maths as finish.py ramp_rgb().
static func _ramp_rgb(ramp: Array, v: float) -> Vector3:
	var last := ramp.size() - 1
	var t := clampf(v, 0.0, 255.0) / 255.0 * last
	var lo := clampi(int(floor(t)), 0, last - 1)
	var f := t - lo
	return (ramp[lo] as Vector3) * (1.0 - f) + (ramp[lo + 1] as Vector3) * f


static func _hex(c: Color) -> Vector3:
	return Vector3(c.r8, c.g8, c.b8)


## Pixel colour of a layer is within tol of c (and the layer has a pixel there).
static func _is_col(data: PackedByteArray, i: int, c: Vector3, tol: int) -> bool:
	var o := i * 4
	if data.is_empty() or data[o + 3] == 0:
		return false
	return absi(data[o] - int(c.x)) <= tol and absi(data[o + 1] - int(c.y)) <= tol and absi(data[o + 2] - int(c.z)) <= tol


## 4-neighbour dilation (the pixel itself or one of its 4 neighbours is set), inside a work area.
static func _dilate(m: PackedByteArray, bx0: int = 0, by0: int = 0, bx1: int = W, by1: int = H) -> PackedByteArray:
	var out := PackedByteArray()
	out.resize(N)
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			if m[i] != 0 or (x > 0 and m[i - 1] != 0) or (x < W - 1 and m[i + 1] != 0) \
					or (y > 0 and m[i - W] != 0) or (y < H - 1 and m[i + W] != 0):
				out[i] = 1
	return out


## Index of the nearest pixel set in `src` (Euclidean), searching outward from (x, y).
static func _nearest(src: PackedByteArray, x: int, y: int) -> int:
	var best := -1
	var best_d2 := 1 << 30
	for r in range(1, W):
		for yy in range(maxi(0, y - r), mini(H, y + r + 1)):
			var on_edge_row := absi(yy - y) == r
			var xx := maxi(0, x - r)
			var x_end := mini(W, x + r + 1)
			while xx < x_end:
				if src[yy * W + xx] != 0:
					var d2 := (xx - x) * (xx - x) + (yy - y) * (yy - y)
					if d2 < best_d2:
						best_d2 = d2
						best = yy * W + xx
				# inside rows only the two ends of the ring are new
				if on_edge_row or xx == x + r:
					xx += 1
				else:
					xx = x + r if x + r < x_end else x_end
		# everything in ring r + 1 is at least r + 1 away
		if best >= 0 and best_d2 < (r + 1) * (r + 1):
			return best
	return best


## Is any of the 4 neighbours (or the pixel) set? Bounds-checked.
static func _near(m: PackedByteArray, i: int, x: int, y: int) -> bool:
	return m[i] != 0 or (x > 0 and m[i - 1] != 0) or (x < W - 1 and m[i + 1] != 0) \
			or (y > 0 and m[i - W] != 0) or (y < H - 1 and m[i + W] != 0)


# ------------------------------------------------------------------ compose
## Per-part cache: [raw RGBA bytes, indices of opaque pixels].
static var _parts: Dictionary = {}
## Per-ramp cache: 256 colours for integer values (exact same maths as _ramp_rgb).
static var _luts: Dictionary = {}


static func _part(part_name: String) -> Array:
	if _parts.has(part_name):
		return _parts[part_name]
	var entry: Array = []
	var img := PortraitLibrary.part_image(part_name)
	if img != null:
		var data := img.get_data()
		var idx := PackedInt32Array()
		for i in N:
			if data[i * 4 + 3] > 127:
				idx.append(i)
		entry = [data, idx]
	_parts[part_name] = entry
	return entry


static func _lut(group: String, ramp_name: String) -> PackedVector3Array:
	var key := group + "/" + ramp_name
	if _luts.has(key):
		return _luts[key]
	var ramp := _ramp(group, ramp_name)
	var lut := PackedVector3Array()
	lut.resize(256)
	for v in 256:
		lut[v] = _ramp_rgb(ramp, float(v))
	_luts[key] = lut
	return lut


## Returns the 200x200 portrait. finish = false gives the plain stacked layers.
static func compose(a: HeroAppearance, finish: bool = true) -> Image:
	var rgb := PackedVector3Array()
	rgb.resize(N)
	var alpha := PackedByteArray()
	alpha.resize(N)
	var top := PackedByteArray()
	top.resize(N)
	var sv := PackedFloat32Array()
	sv.resize(N)
	var bv := PackedFloat32Array()
	bv.resize(N)
	var hv := PackedFloat32Array()
	hv.resize(N)
	var layer_data := {}  # role -> PackedByteArray (last layer with that role)
	var box: Rect2i  # bounding box of everything drawn
	var x0 := W
	var y0 := H
	var x1 := -1
	var y1 := -1

	for layer: Array in a.layers():
		var entry := _part(layer[0])
		if entry.is_empty():
			continue
		var data: PackedByteArray = entry[0]
		var idx: PackedInt32Array = entry[1]
		var role: String = layer[3]
		var tag: int = ROLE_TAGS[role]
		if role != "skin":
			layer_data[role] = data
		var tinted: bool = layer[1] != ""
		var lut: PackedVector3Array = _lut(layer[1], layer[2]) if tinted else PackedVector3Array()
		for i in idx:
			var o := i * 4
			var v := data[o]
			rgb[i] = lut[v] if tinted else Vector3(v, data[o + 1], data[o + 2])
			alpha[i] = 1
			top[i] = tag
			if tag == SKIN:
				sv[i] = v
			elif tag == BROW:
				bv[i] = v
			elif tag == HAIR:
				hv[i] = v
		if not idx.is_empty():
			x0 = mini(x0, _min_x(idx))
			x1 = maxi(x1, _max_x(idx))
			y0 = mini(y0, idx[0] / W)
			y1 = maxi(y1, idx[idx.size() - 1] / W)

	if x1 < 0:
		return Image.create_empty(W, H, false, Image.FORMAT_RGBA8)
	box = Rect2i(x0, y0, x1 - x0 + 1, y1 - y0 + 1)
	if finish:
		_finish(rgb, alpha, top, sv, bv, hv, _ramp("skin", a.skin), _ramp("hair", a.hair_color), layer_data, box)

	var out := PackedByteArray()
	out.resize(N * 4)
	for y in range(box.position.y, box.end.y):
		for x in range(box.position.x, box.end.x):
			var i := y * W + x
			if alpha[i] == 0:
				continue
			var c: Vector3 = rgb[i]
			var o := i * 4
			out[o] = int(clampf(c.x, 0.0, 255.0))
			out[o + 1] = int(clampf(c.y, 0.0, 255.0))
			out[o + 2] = int(clampf(c.z, 0.0, 255.0))
			out[o + 3] = 255
	return Image.create_from_data(W, H, false, Image.FORMAT_RGBA8, out)


static func _min_x(idx: PackedInt32Array) -> int:
	var m := W
	for i in idx:
		m = mini(m, i % W)
	return m


static func _max_x(idx: PackedInt32Array) -> int:
	var m := -1
	for i in idx:
		m = maxi(m, i % W)
	return m


## Is mask m set at (x + dx, y + dy)? Out of the canvas counts as not set.
static func _on(m: PackedByteArray, x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < W and y < H and m[y * W + x] != 0


static func _finish(rgb: PackedVector3Array, alpha: PackedByteArray, top: PackedByteArray, sv: PackedFloat32Array,
		bv: PackedFloat32Array, hv: PackedFloat32Array, S: Array, Hr: Array, layer_data: Dictionary, box: Rect2i) -> void:
	var efix: PackedByteArray = layer_data.get("eyes", PackedByteArray())
	var mouth: PackedByteArray = layer_data.get("mouth", PackedByteArray())
	# Work area: the drawn box plus a margin for the shifted / dilated masks.
	var bx0 := maxi(box.position.x - 2, 0)
	var by0 := maxi(box.position.y - 2, 0)
	var bx1 := mini(box.end.x + 2, W)
	var by1 := mini(box.end.y + 2, H)
	var skin_m := PackedByteArray()
	skin_m.resize(N)
	var hair_m := PackedByteArray()
	hair_m.resize(N)
	var body_m := PackedByteArray()
	body_m.resize(N)
	var brow_m := PackedByteArray()
	brow_m.resize(N)
	var eline := PackedByteArray()  # efix pixel is a dark line (any layer on top)
	eline.resize(N)
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			var t := top[i]
			skin_m[i] = 1 if t == SKIN else 0
			hair_m[i] = 1 if t == HAIR else 0
			body_m[i] = 1 if t == BODY else 0
			brow_m[i] = 1 if t == BROW else 0
			if not efix.is_empty() and efix[i * 4 + 3] != 0:
				eline[i] = 1 if _is_col(efix, i, LINE, 12) else 0

	var line_c := _ramp_rgb(S, 14.0)
	var white_c := Vector3(247, 244, 240) * 0.78 + (S[4] as Vector3) * 0.22
	var lid_c := white_c * 0.55 + (S[3] as Vector3) * 0.45
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			match top[i]:
				EYES:
					# 1 lines -> darkest skin shade; 2 whites -> warm off-white, shadow under the upper lid
					if eline[i] != 0:
						rgb[i] = line_c
					elif _is_col(efix, i, WHITE, 6):
						rgb[i] = lid_c if _on(eline, x, y - 1) else white_c
				MOUTH:
					if _is_col(mouth, i, LINE, 12):
						rgb[i] = line_c
					elif _is_col(mouth, i, WHITE, 6):
						rgb[i] = white_c
				BROW:
					# 3 brows: lower edge one hair shade darker where the brow is 2+ px thick
					if not _on(brow_m, x, y + 1) and _on(brow_m, x, y - 1):
						rgb[i] = _ramp_rgb(Hr, bv[i] * 0.55)
				HAIR:
					# 4 hair on skin: edge in the hair's own dark shade
					if _near(skin_m, i, x, y):
						rgb[i] = _ramp_rgb(Hr, maxf(hv[i], 40.0))
				SKIN:
					# 4 cast + contact shadow from hair; 5 contact shadow above the outfit
					var cast := _on(hair_m, x - 1, y - 1) or _on(hair_m, x - 1, y - 2) or _on(hair_m, x - 2, y - 2)
					var collar1 := _near(body_m, i, x, y) or _on(body_m, x, y + 1)
					var dark := 0.0
					if _on(body_m, x, y + 2) and not collar1:
						dark = 22.0
					if collar1:
						dark = 40.0
					if cast:
						dark = maxf(dark, 34.0)
					if _near(hair_m, i, x, y):
						dark = maxf(dark, 44.0)
					if dark > 0.0 and sv[i] > 60.0:
						rgb[i] = _ramp_rgb(S, maxf(sv[i] - dark, 45.0))

	# 6 outline: outfit seams against skin / hair -> dark outfit colour; outer silhouette -> dark fill colour
	var lum := PackedFloat32Array()
	lum.resize(N)
	var body_fill := PackedByteArray()
	body_fill.resize(N)
	var skin_or_hair := PackedByteArray()
	skin_or_hair.resize(N)
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			if alpha[i] == 0:
				continue
			lum[i] = (rgb[i] as Vector3).dot(LUMA)
			body_fill[i] = 1 if body_m[i] != 0 and lum[i] > 70.0 else 0
			skin_or_hair[i] = 1 if skin_m[i] != 0 or hair_m[i] != 0 else 0
	var seams: Array = []
	var outer: Array = []
	var fill := PackedByteArray()
	fill.resize(N)
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			if alpha[i] == 0:
				continue
			if body_m[i] != 0 and lum[i] <= 70.0 and _near(skin_or_hair, i, x, y):
				seams.append(Vector2i(x, y))
			var edge := x == 0 or y == 0 or x == W - 1 or y == H - 1 \
					or alpha[i - 1] == 0 or alpha[i + 1] == 0 or alpha[i - W] == 0 or alpha[i + W] == 0
			if edge:
				outer.append(Vector2i(x, y))
			elif lum[i] > 70.0:
				fill[i] = 1
	for p: Vector2i in seams:
		var j := _nearest(body_fill, p.x, p.y)
		if j >= 0:
			rgb[p.y * W + p.x] = (rgb[j] as Vector3) * 0.42
	var outline_tint := Vector3(18, 13, 24) * 0.6
	for p: Vector2i in outer:
		var j := _nearest(fill, p.x, p.y)
		if j >= 0:
			rgb[p.y * W + p.x] = (rgb[j] as Vector3) * 0.24 + outline_tint

	# 7 grade: warm light from the upper left, shadows toward one cool hue
	var cool := Vector3(58, 48, 92)
	var warm := Vector3(255, 238, 212)
	for y in range(by0, by1):
		for x in range(bx0, bx1):
			var i := y * W + x
			if alpha[i] == 0:
				continue
			var c: Vector3 = rgb[i]
			var l := c.dot(LUMA) / 255.0
			c *= 1.04 - 0.08 * (x + y) / 300.0
			c += (cool - c) * ((1.0 - l) * (1.0 - l) * 0.10)
			c += (warm - c) * (l * l * 0.07)
			rgb[i] = c
