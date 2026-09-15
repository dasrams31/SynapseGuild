from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class BMIResult:
    weight_kg: float
    height_m: float
    bmi: float
    category: str
    health_risk: str


def calculate_bmi(weight_kg: Union[int, float], height_m: Union[int, float]) -> BMIResult:
    """Calculate Body Mass Index (BMI) and classify health risk based on WHO standards.

    Args:
        weight_kg: Weight in kilograms (positive number).
        height_m: Height in meters (positive number).

    Returns:
        BMIResult: Frozen dataclass with weight, height, rounded BMI, category, and health risk.

    Raises:
        TypeError: If input is not numeric or is a boolean.
        ValueError: If input is zero or negative.
    """
    for name, val in [("weight_kg", weight_kg), ("height_m", height_m)]:
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise TypeError(f"{name} must be a numeric value (int or float), got {type(val).__name__}.")
        if val <= 0:
            raise ValueError(f"{name} must be greater than zero, got {val}.")

    raw_bmi = weight_kg / (height_m ** 2)
    bmi = round(raw_bmi, 2)

    if bmi < 18.5:
        category = "Underweight"
        health_risk = "Malnutrition risk"
    elif bmi < 25.0:
        category = "Normal weight"
        health_risk = "Low risk"
    elif bmi < 30.0:
        category = "Overweight"
        health_risk = "Enhanced risk"
    elif bmi < 35.0:
        category = "Obesity Class I"
        health_risk = "Medium risk"
    elif bmi < 40.0:
        category = "Obesity Class II"
        health_risk = "High risk"
    else:
        category = "Obesity Class III"
        health_risk = "Very high risk"

    return BMIResult(
        weight_kg=float(weight_kg),
        height_m=float(height_m),
        bmi=bmi,
        category=category,
        health_risk=health_risk,
    )
