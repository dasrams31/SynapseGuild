"""Official routes, checklist catalogs, and gear presets for Mount Sumbing."""

from typing import List, Dict
from sumbing_sim.models import Checkpoint, GearCategory, Item


def get_garung_route() -> List[Checkpoint]:
    """Standard Garung via Bowongso/Pestan route to Puncak Sejati 3371m."""
    return [
        Checkpoint(
            name="Basecamp Garung",
            elevation_masl=1400,
            distance_from_prev_km=0.0,
            shelter_available=True,
            camp_spot=True,
            description="Starting registration basecamp at the foot of Mt. Sumbing.",
        ),
        Checkpoint(
            name="Pos 1 Malim",
            elevation_masl=1800,
            distance_from_prev_km=2.2,
            shelter_available=True,
            camp_spot=False,
            description="End of agricultural farm tracks; entrance to pine forest.",
        ),
        Checkpoint(
            name="Pos 2 Godean",
            elevation_masl=2250,
            distance_from_prev_km=1.8,
            shelter_available=True,
            camp_spot=True,
            description="Dense vegetation clearing with small shelter.",
        ),
        Checkpoint(
            name="Pos 3 Pestan",
            elevation_masl=2600,
            distance_from_prev_km=1.5,
            shelter_available=False,
            camp_spot=True,
            description="Open windy ridge, steep gravel trail ahead.",
        ),
        Checkpoint(
            name="Pasar Watu",
            elevation_masl=2850,
            distance_from_prev_km=1.0,
            shelter_available=False,
            camp_spot=False,
            description="Rocky boulder field with high wind exposure.",
        ),
        Checkpoint(
            name="Watu Kotak",
            elevation_masl=3050,
            distance_from_prev_km=0.8,
            shelter_available=False,
            camp_spot=True,
            description="Summit attack camp staging area below the rocky crags.",
        ),
        Checkpoint(
            name="Puncak Sejati",
            elevation_masl=3371,
            distance_from_prev_km=0.7,
            shelter_available=False,
            camp_spot=False,
            description="Summit of Mount Sumbing with sweeping caldera views.",
        ),
    ]


def get_mandatory_checklist() -> Dict[GearCategory, str]:
    """Mandatory equipment categories required for safety clearance."""
    return {
        GearCategory.SHELTER: "Tenda Dome (Double Layer)",
        GearCategory.SLEEPING: "Sleeping Bag (Extreme -5C Rating)",
        GearCategory.APPAREL: "Jaket Windproof / Down Jacket",
        GearCategory.FOOTWEAR: "Sepatu Trekking Berprofil Grip",
        GearCategory.NAVIGATION_LIGHT: "Headlamp + Cadangan Baterai",
        GearCategory.FIRST_AID: "P3K & Emergency Oxycan",
        GearCategory.COOKING: "Nesting & Kompor Gas Portable",
        GearCategory.HYDRATION: "Air Minum Minimum 3 Liter",
        GearCategory.NUTRITION: "Logistik Makanan & Makanan Darurat",
    }


def create_standard_gear_kit() -> List[Item]:
    """Predefined standard compliant gear kit for an expedition."""
    return [
        Item("Tenda Dome Double Layer", GearCategory.SHELTER, weight_kg=2.5, warmth_bonus=4.0),
        Item("Sleeping Bag Down -5C", GearCategory.SLEEPING, weight_kg=1.1, warmth_bonus=5.5),
        Item("Jaket Windproof Gore-Tex", GearCategory.APPAREL, weight_kg=0.8, warmth_bonus=4.0),
        Item("Sepatu Trekking Mid-Cut", GearCategory.FOOTWEAR, weight_kg=1.2, warmth_bonus=1.0),
        Item("Headlamp LED 300 Lumens", GearCategory.NAVIGATION_LIGHT, weight_kg=0.15, warmth_bonus=0.0),
        Item("P3K + Oxycan Set", GearCategory.FIRST_AID, weight_kg=0.6, warmth_bonus=0.0),
        Item("Kompor Portable + Nesting", GearCategory.COOKING, weight_kg=0.8, warmth_bonus=0.5),
        Item("Botol Air 3L", GearCategory.HYDRATION, weight_kg=3.0, hydration_bonus=100.0, consumable=True, quantity=1),
        Item("Ransum Makanan Tinggi Kalori", GearCategory.NUTRITION, weight_kg=1.5, nutrition_value=90.0, consumable=True, quantity=1),
        Item("Trekking Pole Ultralight", GearCategory.MISC, weight_kg=0.4, warmth_bonus=0.0),
    ]
