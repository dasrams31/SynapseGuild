"""Hiking & Mountain Climbing Expedition System."""

from hiking_planner.models import (
    Difficulty,
    WeatherCondition,
    GearCategory,
    ExperienceLevel,
    MountainTrail,
    HikerProfile,
    GearItem,
    ExpeditionPlan,
)
from hiking_planner.gear_recommender import recommend_gear, DEFAULT_GEAR_CATALOG
from hiking_planner.calculator import calculate_hydration, calculate_calories
from hiking_planner.planner import ExpeditionPlanner

__all__ = [
    "Difficulty",
    "WeatherCondition",
    "GearCategory",
    "ExperienceLevel",
    "MountainTrail",
    "HikerProfile",
    "GearItem",
    "ExpeditionPlan",
    "recommend_gear",
    "DEFAULT_GEAR_CATALOG",
    "calculate_hydration",
    "calculate_calories",
    "ExpeditionPlanner",
]
