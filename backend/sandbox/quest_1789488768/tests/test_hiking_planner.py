"""Unit tests verifying expedition planning, gear filtering, calculators, and safety validation."""

import unittest
from hiking_planner.models import (
    Difficulty,
    WeatherCondition,
    ExperienceLevel,
    GearCategory,
    GearItem,
    MountainTrail,
    HikerProfile,
    ExpeditionPlan,
)
from hiking_planner.gear_recommender import recommend_gear, DEFAULT_GEAR_CATALOG
from hiking_planner.calculator import calculate_hydration, calculate_calories
from hiking_planner.planner import ExpeditionPlanner


class TestHikingPlanner(unittest.TestCase):

    def setUp(self) -> None:
        self.trail_easy = MountainTrail(
            name="Meadow Loop",
            elevation_meters=450.0,
            elevation_gain=50.0,
            distance_km=6.0,
            estimated_hours=2.0,
            default_weather=WeatherCondition.SUNNY,
            difficulty=Difficulty.EASY,
        )

        self.trail_alpine = MountainTrail(
            name="Matterhorn High Pass",
            elevation_meters=3800.0,
            elevation_gain=1400.0,
            distance_km=22.0,
            estimated_hours=9.0,
            default_weather=WeatherCondition.FREEZING,
            difficulty=Difficulty.EXTREME,
        )

        self.trail_multiday = MountainTrail(
            name="Trans-Range Traverse",
            elevation_meters=2800.0,
            elevation_gain=2600.0,
            distance_km=52.0,
            estimated_hours=26.0,
            default_weather=WeatherCondition.STORMY,
            difficulty=Difficulty.DIFFICULT,
        )

        self.hiker_standard = HikerProfile(
            name="Alex Rover",
            weight_kg=75.0,
            experience_level=ExperienceLevel.INTERMEDIATE,
            is_guide=False,
        )

        self.planner = ExpeditionPlanner()

    def test_gear_filtering_freezing_and_high_elevation(self) -> None:
        required, optional = recommend_gear(
            trail=self.trail_alpine,
            weather=WeatherCondition.FREEZING,
            hiker=self.hiker_standard,
        )
        req_names = [g.name for g in required]
        self.assertIn("Mountaineering Crampons", req_names)
        self.assertIn("Technical Ice Axe", req_names)
        self.assertIn("Merino Thermal Base Layer", req_names)
        self.assertIn("Insulated Mountaineering Gloves & Liner", req_names)
        self.assertIn("Breathable Waterproof Hardshell Jacket", req_names)

    def test_gear_filtering_rainy_weather(self) -> None:
        trail = MountainTrail(
            name="Rainforest Ridge",
            elevation_meters=900.0,
            elevation_gain=300.0,
            distance_km=10.0,
            estimated_hours=3.5,
            default_weather=WeatherCondition.RAINY,
            difficulty=Difficulty.MODERATE,
        )
        required, _ = recommend_gear(
            trail=trail,
            weather=WeatherCondition.RAINY,
            hiker=self.hiker_standard,
        )
        req_names = [g.name for g in required]
        self.assertIn("Breathable Waterproof Hardshell Jacket", req_names)
        self.assertIn("Waterproof Rain Pants", req_names)

    def test_gear_filtering_multiday_shelter_inclusion(self) -> None:
        required, _ = recommend_gear(
            trail=self.trail_multiday,
            weather=WeatherCondition.STORMY,
            hiker=self.hiker_standard,
        )
        req_names = [g.name for g in required]
        self.assertIn("4-Season Mountaineering Tent", req_names)
        self.assertIn("Lightweight Camp Stove & Pot Set", req_names)

    def test_hydration_calculation_physics_and_scaling(self) -> None:
        # Sunny hot hike with more distance and gain requires more water
        water_sunny = calculate_hydration(
            distance_km=20.0,
            elevation_gain=1000.0,
            weather=WeatherCondition.SUNNY,
            hiker_weight_kg=70.0,
        )
        # 20 * 0.08 = 1.6; (1000/100)*0.12 = 1.2; sum = 2.8 * 1.35 * 1.0 = 3.78L
        self.assertAlmostEqual(water_sunny, 3.78, places=2)

        # Heavier hiker needs proportionately more water
        water_heavy = calculate_hydration(
            distance_km=20.0,
            elevation_gain=1000.0,
            weather=WeatherCondition.SUNNY,
            hiker_weight_kg=105.0,
        )
        self.assertGreater(water_heavy, water_sunny)

        # Minimum baseline check for 0 distance/gain
        water_zero = calculate_hydration(0.0, 0.0, WeatherCondition.RAINY, 70.0)
        self.assertEqual(water_zero, 0.5)

    def test_hydration_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            calculate_hydration(-5.0, 100.0, WeatherCondition.SUNNY, 70.0)
        with self.assertRaises(ValueError):
            calculate_hydration(10.0, 100.0, WeatherCondition.SUNNY, -10.0)

    def test_calorie_calculation(self) -> None:
        calories = calculate_calories(
            hiker_weight_kg=70.0,
            pack_weight_kg=10.0,
            distance_km=15.0,
            elevation_gain=800.0,
            hours=5.0,
        )
        # Positive physically realistic calorie value (typical day hike ~ 2000-3500 kcal)
        self.assertGreater(calories, 1500.0)
        self.assertLess(calories, 4500.0)

    def test_calorie_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            calculate_calories(-70.0, 10.0, 10.0, 500.0, 3.0)

    def test_planner_creates_complete_plan(self) -> None:
        plan = self.planner.create_plan(
            trail=self.trail_alpine,
            hiker=self.hiker_standard,
        )
        self.assertIsInstance(plan, ExpeditionPlan)
        self.assertGreater(plan.water_liters, 1.0)
        self.assertGreater(plan.total_calories, 1000.0)
        self.assertGreater(plan.total_base_weight_kg, 1.0)
        self.assertTrue(len(plan.required_gear) > 0)

    def test_safety_checklist_validation_pass(self) -> None:
        plan = self.planner.create_plan(
            trail=self.trail_alpine,
            hiker=self.hiker_standard,
        )
        is_safe, issues = self.planner.validate_safety_checklist(plan)
        self.assertTrue(is_safe)
        self.assertEqual(len(issues), 0)

    def test_safety_checklist_validation_fail_when_missing_criticals(self) -> None:
        # Create a flawed plan missing first aid & tools
        sparse_gear = [
            GearItem(
                name="Simple Map",
                category=GearCategory.NAVIGATION,
                weight_grams=50.0,
            )
        ]
        custom_plan = ExpeditionPlan(
            trail=self.trail_alpine,
            hiker=self.hiker_standard,
            required_gear=sparse_gear,
            optional_gear=[],
            water_liters=2.0,
            total_calories=2000.0,
            total_base_weight_kg=0.05,
        )
        is_safe, issues = self.planner.validate_safety_checklist(custom_plan)
        self.assertFalse(is_safe)
        self.assertTrue(any("First Aid" in msg for msg in issues))
        self.assertTrue(any("Headlamp" in msg for msg in issues))
        self.assertTrue(any("Emergency Bivy" in msg for msg in issues))

    def test_edge_case_zero_elevation_gain(self) -> None:
        flat_trail = MountainTrail(
            name="Lakeside Stroll",
            elevation_meters=200.0,
            elevation_gain=0.0,
            distance_km=5.0,
            estimated_hours=1.0,
            default_weather=WeatherCondition.SUNNY,
            difficulty=Difficulty.EASY,
        )
        plan = self.planner.create_plan(trail=flat_trail, hiker=self.hiker_standard)
        self.assertGreater(plan.water_liters, 0.0)
        self.assertGreater(plan.total_calories, 0.0)
        is_safe, _ = self.planner.validate_safety_checklist(plan)
        self.assertTrue(is_safe)


if __name__ == "__main__":
    unittest.main()
