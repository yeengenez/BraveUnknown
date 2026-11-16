class_name HeroPortrait
extends Control
## Draws a hero portrait by stacking the part layers and tinting them with a shader.
## Add it to any UI, give it a size, and set `appearance`.
##
##   var portrait := HeroPortrait.new()
##   portrait.custom_minimum_size = Vector2(200, 200)
##   portrait.appearance = HeroAppearance.roll()

const RAMP_SHADER := preload("res://portraits/ramp_map.gdshader")

var appearance: HeroAppearance:
	set(value):
		appearance = value
		_rebuild()

## Drawn behind the hero. Transparent leaves the background to the parent.
@export var background := Color(0, 0, 0, 0):
	set(value):
		background = value
		queue_redraw()


func _init() -> void:
	custom_minimum_size = Vector2(PortraitLibrary.CANVAS)
	clip_contents = true


func _draw() -> void:
	if background.a > 0.0:
		draw_rect(Rect2(Vector2.ZERO, size), background)


func _rebuild() -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()
	if appearance == null:
		return
	for layer in appearance.layers():
		var part_name: String = layer[0]
		if not PortraitLibrary.has_part(part_name):
			push_warning("HeroPortrait: missing part %s" % part_name)
			continue
		var rect := TextureRect.new()
		rect.texture = PortraitLibrary.part(part_name)
		rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		if layer[1] != "":
			var mat := ShaderMaterial.new()
			mat.shader = RAMP_SHADER
			mat.set_shader_parameter("ramp", PortraitLibrary.ramp_texture(layer[1], layer[2]))
			rect.material = mat
		add_child(rect)


## Builds the finished portrait as an Image on the CPU (no rendering needed).
## Use it to cache a hero's portrait as one texture, or to save it as a PNG.
static func bake(p_appearance: HeroAppearance) -> Image:
	var canvas := PortraitLibrary.CANVAS
	var out := Image.create(canvas.x, canvas.y, false, Image.FORMAT_RGBA8)
	for layer in p_appearance.layers():
		var part_name: String = layer[0]
		if not PortraitLibrary.has_part(part_name):
			continue
		var img := PortraitLibrary.part(part_name).get_image()
		if img.is_compressed():
			img.decompress()
		img.convert(Image.FORMAT_RGBA8)
		if layer[1] != "":
			_tint(img, PortraitLibrary.ramp_colors(layer[1], layer[2]))
		out.blend_rect(img, Rect2i(Vector2i.ZERO, canvas), Vector2i.ZERO)
	return out


static func _tint(img: Image, ramp: PackedColorArray) -> void:
	var last := ramp.size() - 1
	for y in img.get_height():
		for x in img.get_width():
			var c := img.get_pixel(x, y)
			if c.a == 0.0:
				continue
			var v := c.r * last
			var i := mini(int(v), last - 1)
			var tinted := ramp[i].lerp(ramp[i + 1], v - i)
			tinted.a = c.a
			img.set_pixel(x, y, tinted)
