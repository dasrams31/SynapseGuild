"""Domain models for Mount Sumbing Expedition Simulation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GearCategory(Enum):
    SHELTER = "shelter"
    SLEEPING = "sleeping"
    APPAREL = "apparel"
    FOOTWEAR = "footwear"
    NAVIGATION_LIGHT = "navigation_light"
    FIRST_AID = "first_aid"
    COOKING = "cooking"
    HYDRATION = "hydration"
    NUTRITION = "nutrition"
    MISC = "misc"


class Weather(Enum):
    SUNNY = "Sunny"
    FOGGY = "Foggy"
    RAINY = "Rainy"
    STORM = "Storm"
    FREEZING_NIGHT = "Freezing Night"


@dataclass
class Item:
    name: str
    category: GearCategory
    weight_kg: float
    warmth_bonus: float = 0.0  # Offsets ambient cold
    hydration_bonus: float = 0.0  # Adds hydration points (e.g. Water)
    nutrition_value: float = 0.0  # Adds stamina points (e.g. Trail Mix, Logistik)
    durability: float = 100.0
    consumable: bool = False
    quantity: int = 1


@dataclass
class Checkpoint:
    name: str
    elevation_masl: int
    distance_from_prev_km: float
    shelter_available: bool = False
    camp_spot: bool = False
    description: str = ""


@dataclass
class Climber:
    name: str
    max_carry_weight_kg: float = 20.0
    stamina: float = 100.0  # 0.0 to 100.0
    hydration: float = 100.0  # 0.0 to 100.0
    body_temp: float = 36.8  # Normal: 36.5 - 37.5 °C. < 35.0 = Hypothermia
    altitude_adaptation: float = 50.0  # 0 to 100 AMS resistance
    ams_symptoms: float = 0.0  # Acute Mountain Sickness severity (0 - 100)
    inventory: Dict[str, Item] = field(default_factory=dict)

    @property
    def current_carry_weight(self) -> float:
        return sum(item.weight_kg * item.quantity for item in self.inventory.values())

    @property
    def total_warmth_rating(self) -> float:
        return sum(item.warmth_bonus for item in self.inventory.values() if not item.consumable)

    def add_item(self, item: Item) -> None:
        if item.name in self.inventory:
            self.inventory[item.name].quantity += item.quantity
        else:
            self.inventory[item.name] = Item(
                name=item.name,
                category=item.category,
                weight_kg=item.weight_kg,
                warmth_bonus=item.warmth_bonus,
                hydration_bonus=item.hydration_bonus,
                nutrition_value=item.nutrition_value,
                durability=item.durability,
                consumable=item.consumable,
                quantity=item.quantity,
            )

    def remove_item(self, item_name: str, quantity: int = 1) -> Optional[Item]:
        if item_name not in self.inventory:
            return None
        item = self.inventory[item_name]
        if item.quantity <= quantity:
            return self.inventory.pop(item_name)
        item.quantity -= quantity
        return Item(
            name=item.name,
            category=item.category,
            weight_kg=item.weight_kg,
            warmth_bonus=item.warmth_bonus,
            hydration_bonus=item.hydration_bonus,
            nutrition_value=item.nutrition_value,
            durability=item.durability,
            consumable=item.consumable,
            quantity=quantity,
        )

    def has_category(self, category: GearCategory) -> bool:
        return any(item.category == category and item.quantity > 0 for item in self.inventory.values())
