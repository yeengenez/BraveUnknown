"""Archer back-equipment state selection.

The selected container follows equipped ammunition, not the weapon currently in hand.
This helper is independent of Godot UI code so the art pipeline can validate the rule.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BackEquipmentState:
    layer: Optional[str]
    visible: bool
    state: Optional[str]


def _container_state(equipped: bool, count: int, bundle_size: int, prefix: str) -> BackEquipmentState:
    if not equipped:
        return BackEquipmentState(None, False, None)
    if count <= 0:
        state = "empty"
    elif count >= bundle_size:
        state = "full"
    else:
        state = "partial"
    return BackEquipmentState(f"{prefix}_{state}", True, state)


def select_back_equipment(
    ammunition_type: Optional[str],
    ammunition_count: int,
    *,
    bundle_size: int = 50,
    held_weapon: Optional[str] = None,
) -> dict:
    """Return quiver/bolt-case states for the equipped ammunition.

    held_weapon is intentionally ignored: swapping to a dagger must not hide a
    quiver or bolt case while the corresponding ammunition remains equipped.
    """
    if bundle_size <= 0:
        raise ValueError("bundle_size must be positive")
    count = max(0, int(ammunition_count))
    ammo = (ammunition_type or "").lower()
    return {
        "quiver": _container_state(ammo == "arrows", count, bundle_size, "quiver"),
        "bolt_case": _container_state(ammo == "bolts", count, bundle_size, "boltcase"),
    }
