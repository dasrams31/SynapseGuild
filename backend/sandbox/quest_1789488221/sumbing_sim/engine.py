"""Simulation engine for Mount Sumbing mountain climbs."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import math

from sumbing_sim.models import Checkpoint, Climber, GearCategory, Weather
from sumbing_sim.data import get_garung_route, get_mandatory_checklist


class ExpeditionStatus(Enum):
    PREPARATION = "Preparation"
    IN_PROGRESS = "In Progress"
    CAMPING = "Camping"
    SUCCESS_SUMMIT = "Success Summit"
    EVACUATION_REQUIRED = "Evacuation Required"
    HYPOTHERMIA_DEFEAT = "Hypothermia Defeat"
    EXHAUSTION_DEFEAT = "Exhaustion Defeat"


@dataclass
class ReadinessReport:
    score: float  # 0 to 100
    is_ready: bool
    warnings: List[str] = field(default_factory=list)
    missing_categories: List[GearCategory] = field(default_factory=list)


class ExpeditionSimulator:
    """State machine and physics engine simulating Mount Sumbing expedition."""

    def __init__(self, climber: Climber, route: List[Checkpoint] = None):
        self.climber = climber
        self.route = route or get_garung_route()
        self.current_checkpoint_idx: int = 0
        self.hour_of_day: float = 6.0  # Starts at 06:00 AM
        self.weather: Weather = Weather.SUNNY
        self.status: ExpeditionStatus = ExpeditionStatus.PREPARATION
        self.log: List[str] = []
        self.log_event(f"Expedition initialized for {climber.name} at {self.current_checkpoint.name}.")

    @property
    def current_checkpoint(self) -> Checkpoint:
        return self.route[self.current_checkpoint_idx]

    @property
    def ambient_temperature(self) -> float:
        """Temperature calculated based on elevation lapse rate (-6.5C per 1000m) and time/weather."""
        base_temp = 24.0  # Base temperature at sea level
        lapse_rate = 0.0065  # 6.5 C per meter
        elevation_temp = base_temp - (self.current_checkpoint.elevation_masl * lapse_rate)

        # Time-of-day fluctuation (colder at night)
        if 20.0 <= self.hour_of_day or self.hour_of_day < 5.0:
            time_penalty = -6.0
        elif 5.0 <= self.hour_of_day < 8.0 or 17.0 <= self.hour_of_day < 20.0:
            time_penalty = -2.0
        else:
            time_penalty = 2.0

        # Weather penalty
        weather_modifiers = {
            Weather.SUNNY: 1.0,
            Weather.FOGGY: -2.0,
            Weather.RAINY: -5.0,
            Weather.STORM: -8.0,
            Weather.FREEZING_NIGHT: -12.0,
        }
        temp = elevation_temp + time_penalty + weather_modifiers.get(self.weather, 0.0)
        return round(temp, 1)

    def log_event(self, message: str) -> None:
        time_str = f"{int(self.hour_of_day):02d}:{int((self.hour_of_day % 1) * 60):02d}"
        self.log.append(f"[{time_str} - {self.current_checkpoint.name}] {message}")

    def validate_gear_readiness(self) -> ReadinessReport:
        """Checks mandatory gear categories and weight balance."""
        warnings = []
        missing = []
        mandatory = get_mandatory_checklist()

        for category, description in mandatory.items():
            if not self.climber.has_category(category):
                missing.append(category)
                warnings.append(f"Missing mandatory gear: {description} ({category.value})")

        total_items = len(mandatory)
        found_items = total_items - len(missing)
        score = (found_items / total_items) * 100.0

        if self.climber.current_carry_weight > self.climber.max_carry_weight_kg:
            overweight = self.climber.current_carry_weight - self.climber.max_carry_weight_kg
            warnings.append(f"Overweight baggage by {overweight:.1f}kg! Will severely drain stamina.")
            score = max(0.0, score - 15.0)

        is_ready = len(missing) == 0 and score >= 80.0
        return ReadinessReport(score=round(score, 1), is_ready=is_ready, warnings=warnings, missing_categories=missing)

    def set_weather(self, weather: Weather) -> None:
        self.weather = weather
        self.log_event(f"Weather changed to {weather.value}.")

    def _check_survival_state(self) -> bool:
        """Check if climber is alive and capable. Returns False if defeated."""
        if self.climber.body_temp < 35.0:
            self.status = ExpeditionStatus.HYPOTHERMIA_DEFEAT
            self.log_event(f"CRITICAL: Climber body temperature dropped to {self.climber.body_temp:.1f}°C! Hypothermia collapse.")
            return False
        if self.climber.stamina <= 0:
            self.status = ExpeditionStatus.EXHAUSTION_DEFEAT
            self.log_event("CRITICAL: Stamina completely exhausted (0.0). Climber cannot continue.")
            return False
        if self.climber.ams_symptoms >= 85.0:
            self.status = ExpeditionStatus.EVACUATION_REQUIRED
            self.log_event("CRITICAL: Severe Acute Mountain Sickness (HAPE/HACE warning). Evacuation required.")
            return False
        return True

    def _apply_environmental_drain(self, duration_hours: float, pace_multiplier: float = 1.0) -> None:
        """Calculate stamina, hydration, thermal regulation, and AMS impacts."""
        weight_ratio = self.climber.current_carry_weight / max(1.0, self.climber.max_carry_weight_kg)
        weight_penalty = max(1.0, weight_ratio ** 1.8)

        # Weather multiplier
        weather_multiplier = {
            Weather.SUNNY: 1.0,
            Weather.FOGGY: 1.15,
            Weather.RAINY: 1.4,
            Weather.STORM: 1.8,
            Weather.FREEZING_NIGHT: 1.6,
        }[self.weather]

        # Stamina loss
        base_stamina_drain_per_hr = 10.0
        stamina_loss = base_stamina_drain_per_hr * duration_hours * pace_multiplier * weight_penalty * weather_multiplier
        self.climber.stamina = max(0.0, self.climber.stamina - stamina_loss)

        # Hydration loss
        base_hydration_drain = 8.0
        if self.weather == Weather.SUNNY:
            base_hydration_drain += 3.0
        hydration_loss = base_hydration_drain * duration_hours * pace_multiplier
        self.climber.hydration = max(0.0, self.climber.hydration - hydration_loss)

        if self.climber.hydration <= 20.0:
            # Dehydration accelerates exhaustion and AMS
            self.climber.stamina = max(0.0, self.climber.stamina - (12.0 * duration_hours))

        # Thermal regulation
        amb_temp = self.ambient_temperature
        insulation = self.climber.total_warmth_rating
        effective_cold = max(0.0, (15.0 - amb_temp) - insulation)

        if effective_cold > 0:
            # Cold stress drops body temperature
            temp_drop = (effective_cold * 0.18) * duration_hours
            self.climber.body_temp = max(30.0, self.climber.body_temp - temp_drop)
        else:
            # Recover towards normal 36.8°C if warm enough
            if self.climber.body_temp < 36.8:
                self.climber.body_temp = min(36.8, self.climber.body_temp + (0.4 * duration_hours))

        # Altitude sickness calculation (elevation above 2400m)
        elevation = self.current_checkpoint.elevation_masl
        if elevation > 2400:
            elevation_factor = (elevation - 2400) / 1000.0
            ams_risk = elevation_factor * 15.0 * duration_hours * (100.0 - self.climber.altitude_adaptation) / 100.0
            if pace_multiplier > 1.0:
                ams_risk *= 1.5
            self.climber.ams_symptoms = min(100.0, self.climber.ams_symptoms + ams_risk)

    def trek(self, pace: str = "normal") -> bool:
        """Advance to the next checkpoint."""
        if self.status in [ExpeditionStatus.HYPOTHERMIA_DEFEAT, ExpeditionStatus.EXHAUSTION_DEFEAT, ExpeditionStatus.EVACUATION_REQUIRED]:
            self.log_event("Cannot trek: expedition ended due to critical condition.")
            return False

        if self.current_checkpoint_idx >= len(self.route) - 1:
            self.status = ExpeditionStatus.SUCCESS_SUMMIT
            self.log_event("Already reached the final destination!")
            return True

        target_checkpoint = self.route[self.current_checkpoint_idx + 1]
        dist_km = target_checkpoint.distance_from_prev_km
        elevation_gain = target_checkpoint.elevation_masl - self.current_checkpoint.elevation_masl

        pace_factors = {"slow": 0.7, "normal": 1.0, "fast": 1.5}
        speed_factor = pace_factors.get(pace, 1.0)

        # Base speed in steep terrain is roughly 1.5 km/h normalized
        base_trekking_speed_kmh = 1.2 * speed_factor
        hours = max(0.5, dist_km / base_trekking_speed_kmh + (elevation_gain / 600.0))

        self.status = ExpeditionStatus.IN_PROGRESS
        self.log_event(f"Trekking {pace} pace to {target_checkpoint.name} ({target_checkpoint.elevation_masl}m) for {hours:.1f} hrs...")

        self._apply_environmental_drain(duration_hours=hours, pace_multiplier=speed_factor)
        self.hour_of_day = (self.hour_of_day + hours) % 24

        if not self._check_survival_state():
            return False

        self.current_checkpoint_idx += 1
        self.log_event(f"Arrived at {self.current_checkpoint.name}. Stamina: {self.climber.stamina:.1f}, Temp: {self.climber.body_temp:.1f}°C.")

        if self.current_checkpoint.name == "Puncak Sejati":
            self.status = ExpeditionStatus.SUCCESS_SUMMIT
            self.log_event("SUMMIT VICTORY! Successfully stood on Puncak Sejati 3371m!")

        return True

    def rest(self, duration_hours: float = 1.0) -> bool:
        """Short rest to recover stamina."""
        if self.status in [ExpeditionStatus.HYPOTHERMIA_DEFEAT, ExpeditionStatus.EXHAUSTION_DEFEAT]:
            return False

        self.log_event(f"Taking a short rest for {duration_hours} hour(s).")
        self.climber.stamina = min(100.0, self.climber.stamina + (15.0 * duration_hours))
        self.hour_of_day = (self.hour_of_day + duration_hours) % 24
        self._apply_environmental_drain(duration_hours=duration_hours * 0.3, pace_multiplier=0.3)
        return self._check_survival_state()

    def camp(self, hours: float = 6.0) -> bool:
        """Camp overnight at a viable checkpoint."""
        if not self.current_checkpoint.camp_spot and not self.current_checkpoint.shelter_available:
            self.log_event(f"Cannot pitch camp here at {self.current_checkpoint.name}: terrain unsuitable!")
            return False

        has_tent = self.climber.has_category(GearCategory.SHELTER)
        has_sb = self.climber.has_category(GearCategory.SLEEPING)

        self.status = ExpeditionStatus.CAMPING
        self.log_event(f"Pitching camp at {self.current_checkpoint.name} for {hours} hours.")

        # Camp thermal protection
        tent_bonus = 5.0 if has_tent else 0.0
        sb_bonus = 6.0 if has_sb else 0.0
        shelter_bonus = 3.0 if self.current_checkpoint.shelter_available else 0.0
        total_camp_warmth = tent_bonus + sb_bonus + shelter_bonus

        amb_temp = self.ambient_temperature
        effective_temp = amb_temp + total_camp_warmth + self.climber.total_warmth_rating

        if effective_temp < 10.0:
            temp_drop = (10.0 - effective_temp) * 0.15 * (hours / 4.0)
            self.climber.body_temp = max(30.0, self.climber.body_temp - temp_drop)
        else:
            self.climber.body_temp = 36.8

        self.climber.stamina = min(100.0, self.climber.stamina + (8.0 * hours))
        self.climber.ams_symptoms = max(0.0, self.climber.ams_symptoms - (5.0 * hours))
        self.climber.altitude_adaptation = min(100.0, self.climber.altitude_adaptation + 15.0)
        self.hour_of_day = (self.hour_of_day + hours) % 24

        if not self._check_survival_state():
            return False

        self.status = ExpeditionStatus.IN_PROGRESS
        self.log_event(f"Woke up refreshed. Stamina: {self.climber.stamina:.1f}, Body Temp: {self.climber.body_temp:.1f}°C.")
        return True

    def consume(self, item_name: str) -> bool:
        """Consume water or rations from inventory."""
        item = self.climber.inventory.get(item_name)
        if not item:
            self.log_event(f"Cannot consume '{item_name}': not found in inventory.")
            return False

        consumed = self.climber.remove_item(item_name, 1)
        if not consumed:
            return False

        if consumed.hydration_bonus > 0:
            self.climber.hydration = min(100.0, self.climber.hydration + consumed.hydration_bonus)
            self.log_event(f"Drank/used {consumed.name}. Hydration is now {self.climber.hydration:.1f}.")

        if consumed.nutrition_value > 0:
            self.climber.stamina = min(100.0, self.climber.stamina + consumed.nutrition_value)
            self.log_event(f"Ate {consumed.name}. Stamina restored to {self.climber.stamina:.1f}.")

        return True

    def summit_attack(self) -> bool:
        """Final push from Watu Kotak (3050m) to Puncak Sejati (3371m)."""
        if self.current_checkpoint.name != "Watu Kotak":
            self.log_event("Summit attack should ideally be launched from Watu Kotak!")
        return self.trek(pace="slow")
