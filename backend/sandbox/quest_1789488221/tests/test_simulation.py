"""Unit test suite for Mount Sumbing Expedition Simulator."""

import unittest
from sumbing_sim.models import Climber, Item, GearCategory, Weather
from sumbing_sim.data import create_standard_gear_kit, get_garung_route
from sumbing_sim.engine import ExpeditionSimulator, ExpeditionStatus


class TestExpeditionSimulator(unittest.TestCase):

    def test_gear_validation(self):
        """Verify that missing critical gear flags readiness warnings and score drop."""
        climber = Climber(name="Novice", max_carry_weight_kg=15.0)
        # Climber has only snacks and water
        climber.add_item(Item("Water", GearCategory.HYDRATION, 1.0, hydration_bonus=50))
        climber.add_item(Item("Snack", GearCategory.NUTRITION, 0.5, nutrition_value=30))

        sim = ExpeditionSimulator(climber)
        readiness = sim.validate_gear_readiness()

        self.assertFalse(readiness.is_ready)
        self.assertLess(readiness.score, 50.0)
        self.assertIn(GearCategory.SHELTER, readiness.missing_categories)
        self.assertIn(GearCategory.APPAREL, readiness.missing_categories)
        self.assertTrue(len(readiness.warnings) > 0)

    def test_weight_capacity_overflow(self):
        """Ensure carrying beyond max capacity penalizes stamina consumption."""
        # Normal climber
        c_normal = Climber(name="Normal", max_carry_weight_kg=20.0)
        for item in create_standard_gear_kit():
            c_normal.add_item(item)
        sim_normal = ExpeditionSimulator(c_normal)
        sim_normal.trek(pace="normal")
        stamina_after_normal = c_normal.stamina

        # Overweight climber carrying 50kg of heavy stones
        c_heavy = Climber(name="Heavy", max_carry_weight_kg=15.0)
        for item in create_standard_gear_kit():
            c_heavy.add_item(item)
        c_heavy.add_item(Item("Batu Candi", GearCategory.MISC, weight_kg=35.0))
        sim_heavy = ExpeditionSimulator(c_heavy)
        sim_heavy.trek(pace="normal")
        stamina_after_heavy = c_heavy.stamina

        self.assertGreater(c_heavy.current_carry_weight, c_heavy.max_carry_weight_kg)
        self.assertLess(stamina_after_heavy, stamina_after_normal)

    def test_checkpoint_progression(self):
        """Ascending step-by-step updates climber altitude and pos correctly."""
        climber = Climber(name="Ranger")
        for item in create_standard_gear_kit():
            climber.add_item(item)

        sim = ExpeditionSimulator(climber)
        self.assertEqual(sim.current_checkpoint.name, "Basecamp Garung")
        self.assertEqual(sim.current_checkpoint.elevation_masl, 1400)

        success = sim.trek(pace="normal")
        self.assertTrue(success)
        self.assertEqual(sim.current_checkpoint.name, "Pos 1 Malim")
        self.assertEqual(sim.current_checkpoint.elevation_masl, 1800)

        sim.trek(pace="normal")
        self.assertEqual(sim.current_checkpoint.name, "Pos 2 Godean")
        self.assertEqual(sim.current_checkpoint.elevation_masl, 2250)

    def test_survival_hazards(self):
        """Verify extreme weather without warmth gear triggers hypothermia or exhaustion."""
        ill_prepared = Climber(name="Unprepared", body_temp=36.8, stamina=100.0)
        # No jacket, no tent, no sleeping bag
        sim = ExpeditionSimulator(ill_prepared)
        sim.current_checkpoint_idx = 4  # Pasar Watu (2850m masl)
        sim.set_weather(Weather.STORM)
        sim.hour_of_day = 22.0  # Night storm

        # Trekking under storm at high altitude without warm clothing
        sim.trek(pace="slow")

        # Body temp must drop below 35.0 or result in defeat
        self.assertTrue(
            sim.climber.body_temp < 35.0 or sim.status in [ExpeditionStatus.HYPOTHERMIA_DEFEAT, ExpeditionStatus.EXHAUSTION_DEFEAT]
        )

    def test_summit_success(self):
        """A well-prepared climber navigating through all checkpoints reaches Puncak Sejati with SUCCESS_SUMMIT."""
        climber = Climber(name="Pendaki Tangguh", max_carry_weight_kg=22.0)
        for item in create_standard_gear_kit():
            climber.add_item(item)

        sim = ExpeditionSimulator(climber)
        # Route has 7 checkpoints (indices 0 through 6)
        sim.trek(pace="normal")  # Pos 1 Malim
        sim.trek(pace="normal")  # Pos 2 Godean
        sim.trek(pace="normal")  # Pos 3 Pestan
        sim.trek(pace="slow")    # Pasar Watu
        sim.trek(pace="slow")    # Watu Kotak

        # Rest & camp at Watu Kotak
        sim.consume("Ransum Makanan Tinggi Kalori")
        sim.camp(hours=6.0)

        # Final summit attack
        res = sim.summit_attack()
        self.assertTrue(res)
        self.assertEqual(sim.current_checkpoint.name, "Puncak Sejati")
        self.assertEqual(sim.current_checkpoint.elevation_masl, 3371)
        self.assertEqual(sim.status, ExpeditionStatus.SUCCESS_SUMMIT)


if __name__ == "__main__":
    unittest.main()
