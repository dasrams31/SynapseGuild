"""BMI Calculator module providing body mass index calculation and categorization."""


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate Body Mass Index (BMI) rounded to 2 decimal places.

    Args:
        weight_kg: Body weight in kilograms.
        height_m: Height in meters.

    Returns:
        Calculated BMI value rounded to 2 decimal places.

    Raises:
        ValueError: If weight_kg <= 0 or height_m <= 0.
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")

    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi: float) -> str:
    """Determine the BMI category according to WHO standards.

    Args:
        bmi: Body Mass Index value.

    Returns:
        Category string ('Underweight', 'Normal weight', 'Overweight', 'Obesity').

    Raises:
        ValueError: If bmi <= 0.
    """
    if bmi <= 0:
        raise ValueError("BMI must be greater than zero.")

    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obesity"


def evaluate_bmi(weight_kg: float, height_m: float) -> dict:
    """Calculate BMI and determine its category.

    Args:
        weight_kg: Body weight in kilograms.
        height_m: Height in meters.

    Returns:
        Dictionary containing 'bmi' and 'category'.

    Raises:
        ValueError: If weight_kg <= 0 or height_m <= 0.
    """
    bmi_value = calculate_bmi(weight_kg, height_m)
    category = get_bmi_category(bmi_value)
    return {
        "bmi": bmi_value,
        "category": category,
    }
