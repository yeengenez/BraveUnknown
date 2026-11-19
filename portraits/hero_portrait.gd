class_name HeroPortrait
extends Control
## Shows a hero portrait. The layers are stacked and blended once by PortraitFinish
## (port of the art pipeline's finish step) and the finished image is cached per look.
## Add it to any UI, give it a size, and set `appearance`.
##
##   var portrait := HeroPortrait.new()
##   portrait.custom_minimum_size = Vector2(200, 200)
##   portrait.appearance = HeroAppearance.roll()

var appearance: HeroAppearance:
	set(value):
		appearance = value
		_rebuild()

## Drawn behind the hero. Transparent leaves the background to the parent.
@export var background := Color(0, 0, 0, 0):
	set(value):
		background = value
		queue_redraw()

var _rect: TextureRect


func _init() -> void:
	custom_minimum_size = Vector2(PortraitLibrary.CANVAS)
	clip_contents = true
	_rect = TextureRect.new()
	_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_rect)


func _draw() -> void:
	if background.a > 0.0:
		draw_rect(Rect2(Vector2.ZERO, size), background)


func _rebuild() -> void:
	if appearance == null:
		_rect.texture = null
		return
	var key := appearance.key()
	_rect.texture = PortraitFinish.texture_async(appearance, _on_built.bind(key))


func _on_built(tex: ImageTexture, key: String) -> void:
	if appearance != null and appearance.key() == key:
		_rect.texture = tex


## True once the portrait is on screen (not still being built).
func is_ready() -> bool:
	return _rect.texture != null


## The finished portrait as an Image (for saving as a PNG, etc.).
static func bake(p_appearance: HeroAppearance) -> Image:
	return PortraitFinish.compose(p_appearance)
