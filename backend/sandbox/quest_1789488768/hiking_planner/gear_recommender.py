"""Catalog and gear recommendation engine for expeditions."""

from typing import List, Optional, Tuple
from hiking_planner.models import (
    Difficulty,
    GearCategory,
    GearItem,
    HikerProfile,
    MountainTrail,
    WeatherCondition,
)

DEFAULT_GEAR_CATALOG: List[GearItem] = [
    # Essentials / Navigation / First Aid
    GearItem(
        name="Topographic Map & Magnetic Compass",
        category=GearCategory.NAVIGATION,
        weight_grams=150.0,
        is_mandatory=True,
    ),
    GearItem(
        name="GPS Satellite Messenger",
        category=GearCategory.NAVIGATION,
        weight_grams=220.0,
        is_mandatory=False,
    ),
    GearItem(
        name="Comprehensive First Aid Kit",
        category=GearCategory.FIRST_AID,
        weight_grams=450.0,
        is_mandatory=True,
    ),
    GearItem(
        name="Emergency Bivy / Foil Blanket",
        category=GearCategory.FIRST_AID,
        weight_grams=120.0,
        is_mandatory=True,
    ),
    GearItem(
        name="LED Headlamp with Spare Batteries",
        category=GearCategory.TOOLS,
        weight_grams=110.0,
        is_mandatory=True,
    ),
    GearItem(
        name="Multi-tool Knife",
        category=GearCategory.TOOLS,
        weight_grams=180.0,
        is_mandatory=False,
    ),
    GearItem(
        name="Water Filtration System & Reservoir",
        category=GearCategory.HYDRATION,
        weight_grams=300.0,
        is_mandatory=True,
    ),
    # Clothing & Weather Specifics
    GearItem(
        name="Breathable Waterproof Hardshell Jacket",
        category=GearCategory.CLOTHING,
        weight_grams=400.0,
        weather_conditions=[WeatherCondition.RAINY, WeatherCondition.STORMY, WeatherCondition.FREEZING],
    ),
    GearItem(
        name="Waterproof Rain Pants",
        category=GearCategory.CLOTHING,
        weight_grams=320.0,
        weather_conditions=[WeatherCondition.RAINY, WeatherCondition.STORMY],
    ),
    GearItem(
        name="Merino Thermal Base Layer",
        category=GearCategory.CLOTHING,
        weight_grams=250.0,
        weather_conditions=[WeatherCondition.COLD, WeatherCondition.FREEZING, WeatherCondition.STORMY],
    ),
    GearItem(
        name="Heavy Insulated Down Parka",
        category=GearCategory.CLOTHING,
        weight_grams=650.0,
        weather_conditions=[WeatherCondition.FREEZING, WeatherCondition.COLD],
        min_elevation=2000.0,
    ),
    GearItem(
        name="Insulated Mountaineering Gloves & Liner",
        category=GearCategory.CLOTHING,
        weight_grams=180.0,
        weather_conditions=[WeatherCondition.FREEZING, WeatherCondition.COLD],
    ),
    GearItem(
        name="Wide Brim UV Sun Hat & Polarized Sunglasses",
        category=GearCategory.CLOTHING,
        weight_grams=90.0,
        weather_conditions=[WeatherCondition.SUNNY],
    ),
    # High-Altitude & Technical Gear
    GearItem(
        name="Mountaineering Crampons",
        category=GearCategory.TOOLS,
        weight_grams=850.0,
        min_elevation=2500.0,
        weather_conditions=[WeatherCondition.FREEZING],
    ),
    GearItem(
        name="Technical Ice Axe",
        category=GearCategory.TOOLS,
        weight_grams=480.0,
        min_elevation=2500.0,
    ),
    GearItem(
        name="Trekking Poles",
        category=GearCategory.TOOLS,
        weight_grams=420.0,
    ),
    # Multi-day Shelter & Cooking
    GearItem(
        name="4-Season Mountaineering Tent",
        category=GearCategory.SHELTER,
        weight_grams=2400.0,
        weather_conditions=[WeatherCondition.STORMY, WeatherCondition.FREEZING],
    ),
    GearItem(
        name="3-Season Ultralight Backpacking Tent",
        category=GearCategory.SHELTER,
        weight_grams=1600.0,
    ),
    GearItem(
        name="0-Degree Sub-Zero Sleeping Bag",
        category=GearCategory.SHELTER,
        weight_grams=1300.0,
        weather_conditions=[WeatherCondition.COLD, WeatherCondition.FREEZING],
    ),
    GearItem(
        name="Lightweight Camp Stove & Pot Set",
        category=GearCategory.COOKING,
        weight_grams=450.0,
    ),
]


def recommend_gear(
    trail: MountainTrail,
    weather: WeatherCondition,
    hiker: HikerProfile,
    catalog: Optional[List[GearItem]] = None,
) -> Tuple[List[GearItem], List[GearItem]]:
    """Recommends mandatory and optional gear based on trail metrics, weather, and hiker profile."""
    gear_pool = catalog if catalog is not None else DEFAULT_GEAR_CATALOG
    is_multi_day = trail.estimated_hours > 12.0 or trail.distance_km >= 30.0
    is_extreme_elevation = trail.elevation_meters >= 2500.0
    is_harsh_weather = weather in (WeatherCondition.FREEZING, WeatherCondition.STORMY, WeatherCondition.RAINY)

    required: List[GearItem] = []
    optional: List[GearItem] = []

    for item in gear_pool:
        must_include = False
        can_include = True

        # Universal essentials
        if item.is_mandatory:
            must_include = True

        # Weather matching
        if item.weather_conditions:
            if weather in item.weather_conditions:
                if is_harsh_weather or item.category == GearCategory.CLOTHING:
                    must_include = True
                else:
                    can_include = True
            else:
                # If item requires specific weather and current weather doesn't match
                if not must_include and item.min_elevation == 0.0:
                    can_include = False

        # Elevation checks
        if item.min_elevation > 0.0:
            if trail.elevation_meters >= item.min_elevation:
                if item.name in ["Mountaineering Crampons", "Technical Ice Axe"]:
                    if trail.difficulty in (Difficulty.DIFFICULT, Difficulty.EXTREME) or weather == WeatherCondition.FREEZING:
                        must_include = True
                    else:
                        can_include = True
                elif is_extreme_elevation and weather in (WeatherCondition.COLD, WeatherCondition.FREEZING):
                    must_include = True
                else:
                    can_include = True
            else:
                # Elevation not reached
                if not item.is_mandatory:
                    can_include = False

        # Shelter & Cooking checks based on trip duration
        if item.category in (GearCategory.SHELTER, GearCategory.COOKING):
            if is_multi_day:
                # Select appropriate tent
                if item.name == "4-Season Mountaineering Tent" and (weather in (WeatherCondition.FREEZING, WeatherCondition.STORMY) or is_extreme_elevation):
                    must_include = True
                elif item.name == "3-Season Ultralight Backpacking Tent" and weather not in (WeatherCondition.FREEZING, WeatherCondition.STORMY):
                    must_include = True
                elif item.name == "0-Degree Sub-Zero Sleeping Bag" and weather in (WeatherCondition.COLD, WeatherCondition.FREEZING):
                    must_include = True
                elif item.name == "Lightweight Camp Stove & Pot Set":
                    must_include = True
                else:
                    can_include = True
            else:
                # Day hike: heavy tents/stoves are generally omitted unless extreme
                if item.category == GearCategory.SHELTER and not item.is_mandatory:
                    can_include = False
                elif item.category == GearCategory.COOKING:
                    can_include = False

        # Trekking poles recommendation for steep elevation gains
        if item.name == "Trekking Poles":
            if trail.elevation_gain >= 800.0 or trail.difficulty in (Difficulty.DIFFICULT, Difficulty.EXTREME):
                must_include = True
            else:
                can_include = True

        # Add to appropriate bucket avoiding duplicates
        if must_include:
            if item not in required:
                required.append(item)
        elif can_include:
            if item not in optional and item not in required:
                optional.append(item)

    return required, optional
