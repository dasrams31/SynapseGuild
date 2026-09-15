"""Coordinates trail planning, safety verification, and gear compilation."""

from typing import List, Optional, Tuple
from hiking_planner.models import (
    ExpeditionPlan,
    GearCategory,
    GearItem,
    HikerProfile,
    MountainTrail,
    WeatherCondition,
)
from hiking_planner.gear_recommender import recommend_gear
from hiking_planner.calculator import calculate_hydration, calculate_calories


class ExpeditionPlanner:
    """Coordinates trail selection, gear recommendations, nutrition, and safety."""

    ESSENTIAL_CATEGORIES = {
        GearCategory.FIRST_AID,
        GearCategory.NAVIGATION,
        GearCategory.HYDRATION,
        GearCategory.TOOLS,
    }

    def __init__(self, gear_catalog: Optional[List[GearItem]] = None) -> None:
        self.gear_catalog = gear_catalog

    def create_plan(
        self,
        trail: MountainTrail,
        hiker: HikerProfile,
        weather: Optional[WeatherCondition] = None,
        custom_pack_weight_kg: Optional[float] = None,
    ) -> ExpeditionPlan:
        """Creates a comprehensive expedition plan."""
        active_weather = weather if weather is not None else trail.default_weather

        required_gear, optional_gear = recommend_gear(
            trail=trail,
            weather=active_weather,
            hiker=hiker,
            catalog=self.gear_catalog,
        )

        # Base pack weight calculation from mandatory and optional gear
        computed_gear_weight_kg = sum(g.weight_grams for g in required_gear) / 1000.0
        pack_weight = custom_pack_weight_kg if custom_pack_weight_kg is not None else computed_gear_weight_kg

        water_liters = calculate_hydration(
            distance_km=trail.distance_km,
            elevation_gain=trail.elevation_gain,
            weather=active_weather,
            hiker_weight_kg=hiker.weight_kg,
        )

        total_calories = calculate_calories(
            hiker_weight_kg=hiker.weight_kg,
            pack_weight_kg=pack_weight + water_liters,  # 1 liter water ~ 1 kg
            distance_km=trail.distance_km,
            elevation_gain=trail.elevation_gain,
            hours=trail.estimated_hours,
        )

        return ExpeditionPlan(
            trail=trail,
            hiker=hiker,
            required_gear=required_gear,
            optional_gear=optional_gear,
            water_liters=water_liters,
            total_calories=total_calories,
            total_base_weight_kg=round(pack_weight, 2),
        )

    @staticmethod
    def validate_safety_checklist(plan: ExpeditionPlan) -> Tuple[bool, List[str]]:
        """Validates that critical safety gear is present in required gear list."""
        missing_issues: List[str] = []
        gear_names = {item.name.lower() for item in plan.required_gear}
        gear_categories = {item.category for item in plan.required_gear}

        # Check essential categories
        for category in ExpeditionPlanner.ESSENTIAL_CATEGORIES:
            if category not in gear_categories:
                missing_issues.append(f"Missing essential category: {category.value}")

        # Check key individual safety tools
        if not any("first aid" in name for name in gear_names):
            missing_issues.append("Missing First Aid Kit")
        if not any("headlamp" in name for name in gear_names):
            missing_issues.append("Missing Headlamp / Lighting source")
        if not any("bivy" in name or "blanket" in name for name in gear_names):
            missing_issues.append("Missing Emergency Bivy or Blanket")

        # Trail-specific safety validations
        if plan.trail.elevation_meters >= 2500.0 and plan.trail.default_weather == WeatherCondition.FREEZING:
            has_crampons = any("crampon" in name for name in gear_names)
            if not has_crampons:
                missing_issues.append("Missing crampons for high altitude freezing conditions")

        is_safe = len(missing_issues) == 0
        return is_safe, missing_issues
