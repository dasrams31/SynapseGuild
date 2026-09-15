"""Hydration and caloric expenditure calculations for hiking and mountaineering."""

from hiking_planner.models import WeatherCondition


def calculate_hydration(
    distance_km: float,
    elevation_gain: float,
    weather: WeatherCondition,
    hiker_weight_kg: float,
) -> float:
    """Calculates minimum water required in liters.

    Base consumption is approximately 0.08L per km and 0.12L per 100m vertical ascent.
    Weather and body mass adjust the rate.
    """
    if distance_km < 0.0 or elevation_gain < 0.0 or hiker_weight_kg <= 0.0:
        raise ValueError("Metrics must be non-negative and hiker weight must be greater than 0.")

    base_distance_liters = distance_km * 0.08
    base_ascent_liters = (elevation_gain / 100.0) * 0.12
    raw_liters = base_distance_liters + base_ascent_liters

    # Weather modifiers
    weather_multiplier = {
        WeatherCondition.SUNNY: 1.35,
        WeatherCondition.COLD: 1.10,
        WeatherCondition.FREEZING: 1.15,
        WeatherCondition.RAINY: 1.00,
        WeatherCondition.STORMY: 1.05,
    }.get(weather, 1.0)

    # Weight modifier relative to 70kg baseline standard
    weight_multiplier = max(0.7, hiker_weight_kg / 70.0)

    total_liters = raw_liters * weather_multiplier * weight_multiplier

    # Safety baseline minimum is 0.5L
    return round(max(0.5, total_liters), 2)


def calculate_calories(
    hiker_weight_kg: float,
    pack_weight_kg: float,
    distance_km: float,
    elevation_gain: float,
    hours: float,
) -> float:
    """Calculates total caloric expenditure using energetic expenditure modeling.

    Accounts for body mass, carried load, distance traversed, gravitational work,
    and baseline metabolic burn over expedition duration.
    """
    if hiker_weight_kg <= 0.0 or pack_weight_kg < 0.0 or distance_km < 0.0 or elevation_gain < 0.0 or hours < 0.0:
        raise ValueError("Invalid arguments for caloric calculation.")

    total_mass = hiker_weight_kg + pack_weight_kg

    # Flat walking energy: ~0.75 kcal per kg total mass per km
    flat_burn = 0.75 * total_mass * distance_km

    # Vertical ascent work (efficiency of human climbing ~22%, 1 kcal = 4184 J)
    # Work (kcal) = (mass_kg * 9.81 m/s^2 * elevation_gain_m) / (4184 * 0.22)
    vertical_burn = (total_mass * 9.80665 * elevation_gain) / (4184.0 * 0.22)

    # Basal / resting metabolic burn during hours: ~1.0 kcal per kg bodyweight per hour
    bmr_burn = 1.0 * hiker_weight_kg * hours

    total_calories = flat_burn + vertical_burn + bmr_burn
    return round(total_calories, 2)
