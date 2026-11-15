class_name Dice
extends RefCounted
## Shared random source so tests can seed every roll.

static var rng := RandomNumberGenerator.new()


static func d(sides: int) -> int:
	return rng.randi_range(1, sides)


static func roll(n: int, sides: int) -> int:
	var total := 0
	for i in n:
		total += rng.randi_range(1, sides)
	return total


static func chance(percent: int) -> bool:
	return rng.randi_range(1, 100) <= percent


static func pick(items: Array) -> Variant:
	return items[rng.randi_range(0, items.size() - 1)]


## Picks a key from {key: weight}.
static func pick_weighted(weights: Dictionary) -> Variant:
	var total := 0.0
	for key: Variant in weights:
		total += float(weights[key])
	var point := rng.randf() * total
	for key: Variant in weights:
		point -= float(weights[key])
		if point <= 0.0:
			return key
	return weights.keys().back()


static func shuffle(items: Array) -> void:
	for i in range(items.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var tmp: Variant = items[i]
		items[i] = items[j]
		items[j] = tmp
