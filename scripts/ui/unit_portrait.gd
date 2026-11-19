class_name UnitPortrait
extends Control
## Shows a unit's portrait in a framed square.
##
## Expeditioners: the pixel-art portrait module in res://portraits/
## (HeroAppearance + HeroPortrait). unit.look holds HeroAppearance.to_dict().
## Monsters: MonsterPortrait (drawn in code) until monster art exists.
##
## crop = "bust" shows the whole 200x200 portrait; "face" zooms in on the head
## and shoulders, for small slots like battle cards.

## Head-and-shoulders region of the 200x200 portrait canvas (new art: skull top y=34, chin y~125).
const FACE_REGION := Rect2(36, 20, 128, 128)

var crop := "bust"
var corner := 6
var _unit: Unit = null
var _look: Dictionary = {}
var _dimmed := false
var _hero: HeroPortrait = null
var _monster: MonsterPortrait = null


func _init() -> void:
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(_layout)


func show_unit(unit: Unit, dimmed: bool = false) -> void:
	if unit == _unit and unit != null and unit.look == _look and dimmed == _dimmed:
		return
	_unit = unit
	_look = unit.look.duplicate() if unit != null else {}
	_dimmed = dimmed
	_rebuild()


func _draw() -> void:
	draw_style_box(UIKit.box(Color("#1b1e24"), Color("#2c313b"), 1, corner, 0), Rect2(Vector2.ZERO, size))


func _rebuild() -> void:
	for child: Node in get_children():
		remove_child(child)
		child.queue_free()
	_hero = null
	_monster = null
	if _unit == null or _look.is_empty():
		return
	if _unit.is_monster:
		_monster = MonsterPortrait.new()
		_monster.corner = corner
		_monster.set_look(_look, _dimmed)
		add_child(_monster)
	else:
		_hero = HeroPortrait.new()
		_hero.custom_minimum_size = Vector2.ZERO
		_hero.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_hero.appearance = HeroAppearance.from_dict(_look)
		_hero.modulate = Color(0.5, 0.5, 0.53) if _dimmed else Color.WHITE
		add_child(_hero)
	_layout()


func _layout() -> void:
	if _monster != null:
		_monster.position = Vector2.ZERO
		_monster.size = size
	if _hero == null:
		return
	var side := minf(size.x, size.y)
	var canvas := Vector2(PortraitLibrary.CANVAS)
	if crop == "face":
		var scale := side / FACE_REGION.size.x
		_hero.size = canvas * scale
		_hero.position = (size - Vector2(side, side)) / 2.0 - FACE_REGION.position * scale
	else:
		_hero.size = Vector2(side, side)
		_hero.position = (size - Vector2(side, side)) / 2.0
	# Big: crisp pixels. Small: smooth mipmapped downscale so faces stay readable.
	var on_screen := _hero.size.x
	var filter := CanvasItem.TEXTURE_FILTER_NEAREST if on_screen >= 180.0 else CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	for layer: Node in _hero.get_children():
		(layer as CanvasItem).texture_filter = filter
