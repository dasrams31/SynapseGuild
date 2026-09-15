"""Data models and enums for hiking and mountaineering expeditions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Difficulty(str, Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    DIFFICULT = "DIFFICULT"
    EXTREME = "EXTREME"


class WeatherCondition(str, Enum):
    SUNNY = "SUNNY"
    RAINY = "RAINY"
    COLD = "COLD"
    STORMY = "STORMY"
    FREEZING = "FREEZING"


class ExperienceLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class GearCategory(str, Enum):
    CLOTHING = "CLOTHING"
    SHELTER = "SHELTER"
    NAVIGATION = "NAVIGATION"
    COOKING = "COOKING"
    FIRST_AID = "FIRST_AID"
    HYDRATION = "HYDRATION"
    TOOLS = "TOOLS"


@dataclass(frozen=True)
class GearItem:
    name: str
    category: GearCategory
    weight_grams: float
    is_mandatory: bool = False
    weather_conditions: List[WeatherCondition] = field(default_factory=list)
    min_elevation: float = 0.0


@dataclass(frozen=True)
class MountainTrail:
    name: str
    elevation_meters: float
    elevation_gain: float
    distance_km: float
    estimated_hours: float
    default_weather: WeatherCondition
    difficulty: Difficulty


@dataclass(frozen=True)
class HikerProfile:
    name: str
    weight_kg: float
    experience_level: ExperienceLevel
    is_guide: bool = False


@dataclass
class ExpeditionPlan:
    trail: MountainTrail
    hiker: HikerProfile
    required_gear: List[GearItem]
    optional_gear: List[GearItem]
    water_liters: float
    total_calories: float
    total_base_weight_kg: float
