"""Module for calculating BMR and calories burned during hiking."""

from typing import Any, Dict


def calculate_bmr(
    weight_kg: float,
    height_cm: float = 170.0,
    age: int = 25,
    gender: str = "male",
) -> float:
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor formula.

    Args:
        weight_kg: Weight in kilograms.
        height_cm: Height in centimeters.
        age: Age in years.
        gender: 'male' or 'female'.

    Returns:
        BMR value in kcal.

    Raises:
        ValueError: If any numerical input is negative or gender is invalid.
    """
    if weight_kg < 0:
        raise ValueError("Weight cannot be negative.")
    if height_cm < 0:
        raise ValueError("Height cannot be negative.")
    if age < 0:
        raise ValueError("Age cannot be negative.")

    normalized_gender = gender.strip().lower()
    if normalized_gender == "male":
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0
    elif normalized_gender == "female":
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age - 161.0
    else:
        raise ValueError(f"Invalid gender '{gender}'. Expected 'male' or 'female'.")


def calculate_hiking_burn(
    body_weight_kg: float,
    carrier_weight_kg: float,
    duration_hours: float,
    elevation_gain_m: float,
    base_met: float = 6.0,
) -> float:
    """Calculate total calories burned during a hike considering pack load and elevation gain.

    Args:
        body_weight_kg: Body weight in kilograms.
        carrier_weight_kg: Backpack / carrier weight in kilograms.
        duration_hours: Hiking duration in hours.
        elevation_gain_m: Total elevation gain in meters.
        base_met: Base metabolic equivalent of task (default is 6.0).

    Returns:
        Total calories burned in kcal.

    Raises:
        ValueError: If any input value is negative.
    """
    if body_weight_kg < 0:
        raise ValueError("Body weight cannot be negative.")
    if carrier_weight_kg < 0:
        raise ValueError("Carrier weight cannot be negative.")
    if duration_hours < 0:
        raise ValueError("Duration cannot be negative.")
    if elevation_gain_m < 0:
        raise ValueError("Elevation gain cannot be negative.")
    if base_met < 0:
        raise ValueError("Base MET cannot be negative.")

    total_weight = body_weight_kg + carrier_weight_kg
    base_calories = base_met * total_weight * duration_hours
    elevation_calories = total_weight * (elevation_gain_m / 100.0) * 0.5
    return base_calories + elevation_calories


def calculate_daily_hiking_calories(
    body_weight_kg: float,
    carrier_weight_kg: float,
    elevation_gain_m: float,
    duration_hours: float = 6.0,
    height_cm: float = 170.0,
    age: int = 25,
    gender: str = "male",
) -> Dict[str, Any]:
    """Calculate total daily caloric requirements including BMR and hiking energy burn.

    Returns:
        Dictionary containing 'bmr', 'hiking_burn', 'total_calories', and input summary.
    """
    bmr = calculate_bmr(
        weight_kg=body_weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
    )
    hiking_burn = calculate_hiking_burn(
        body_weight_kg=body_weight_kg,
        carrier_weight_kg=carrier_weight_kg,
        duration_hours=duration_hours,
        elevation_gain_m=elevation_gain_m,
    )
    total_calories = bmr + hiking_burn

    return {
        "bmr": bmr,
        "hiking_burn": hiking_burn,
        "total_calories": total_calories,
        "details": {
            "body_weight_kg": body_weight_kg,
            "carrier_weight_kg": carrier_weight_kg,
            "duration_hours": duration_hours,
            "elevation_gain_m": elevation_gain_m,
            "height_cm": height_cm,
            "age": age,
            "gender": gender,
        },
    }
