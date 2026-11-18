import unittest
from equipment_state import select_back_equipment


class ArcherEquipmentStateTests(unittest.TestCase):
    def test_arrows_persist_when_dagger_is_held(self):
        state = select_back_equipment("arrows", 24, held_weapon="dagger")
        self.assertEqual(state["quiver"].layer, "quiver_partial")
        self.assertFalse(state["bolt_case"].visible)

    def test_bolts_persist_when_dagger_is_held(self):
        state = select_back_equipment("bolts", 50, held_weapon="dagger")
        self.assertEqual(state["bolt_case"].layer, "boltcase_full")
        self.assertFalse(state["quiver"].visible)

    def test_zero_arrows_keeps_empty_quiver_if_equipped(self):
        state = select_back_equipment("arrows", 0, held_weapon="dagger")
        self.assertTrue(state["quiver"].visible)
        self.assertEqual(state["quiver"].layer, "quiver_empty")

    def test_zero_bolts_keeps_empty_case_if_equipped(self):
        state = select_back_equipment("bolts", 0, held_weapon="dagger")
        self.assertTrue(state["bolt_case"].visible)
        self.assertEqual(state["bolt_case"].layer, "boltcase_empty")

    def test_no_ammunition_item_hides_both(self):
        state = select_back_equipment(None, 0, held_weapon="dagger")
        self.assertFalse(state["quiver"].visible)
        self.assertFalse(state["bolt_case"].visible)

    def test_special_bundle_size(self):
        state = select_back_equipment("arrows", 10, bundle_size=10)
        self.assertEqual(state["quiver"].layer, "quiver_full")


if __name__ == "__main__":
    unittest.main()
