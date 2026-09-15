"""Unit tests for the calorie_calculator module."""

import pytest
from calorie_calculator import (
    calculate_bmr,
    calculate_daily_hiking_calories,
    calculate_hiking_burn,
)


def test_calculate_bmr_male():
    # 10*70 + 6.25*175 - 5*28 + 5 = 700 + 1093.75 - 140 + 5 = 1658.75
    bmr = calculate_bmr(weight_kg=70.0, height_cm=175.0, age=28, gender="male")
    assert pytest.approx(bmr, rel=1e-3) == 1658.75


def test_calculate_bmr_female():
    # 10*55 + 6.25*160 - 5*24 - 161 = 550 + 1000 - 120 - 161 = 1269.0
    bmr = calculate_bmr(weight_kg=55.0, height_cm=160.0, age=24, gender="female")
    assert pytest.approx(bmr, rel=1e-3) == 1269.0


def test_calculate_bmr_case_insensitive_gender():
    bmr_lower = calculate_bmr(weight_kg=60.0, height_cm=165.0, age=30, gender="female")
    bmr_upper = calculate_bmr(weight_kg=60.0, height_cm=165.0, age=30, gender="FEMALE")
    assert bmr_lower == bmr_upper


def test_calculate_hiking_burn_standard():
    # Body 65kg, carrier 15kg -> Total weight = 80kg
    # Base burn = 6.0 * 80 * 5 = 2400 kcal
    # Elevation burn = 80 * (1000 / 100.0) * 0.5 = 80 * 10 * 0.5 = 400 kcal
    # Total burn = 2400 + 400 = 2800 kcal
    burn = calculate_hiking_burn(
        body_weight_kg=65.0,
        carrier_weight_kg=15.0,
        duration_hours=5.0,
        elevation_gain_m=1000.0,
        base_met=6.0,
    )
    assert pytest.approx(burn, rel=1e-3) == 2800.0


def test_calculate_hiking_burn_edge_zero_load_and_flat():
    # Edge case: Trail run / daypack with 0kg carrier and 0m elevation gain
    # Body 60kg, carrier 0kg -> Total weight = 60kg
    # Base burn = 6.0 * 60 * 2 = 720 kcal
    # Elevation burn = 0 kcal
    burn = calculate_hiking_burn(
        body_weight_kg=60.0,
        carrier_weight_kg=0.0,
        duration_hours=2.0,
        elevation_gain_m=0.0,
    )
    assert pytest.approx(burn, rel=1e-3) == 720.0


def test_calculate_daily_hiking_calories_structure_and_values():
    result = calculate_daily_hiking_calories(
        body_weight_kg=70.0,
        carrier_weight_kg=10.0,
        elevation_gain_m=800.0,
        duration_hours=6.0,
        height_cm=170.0,
        age=25,
        gender="male",
    )

    assert "bmr" in result
    assert "hiking_burn" in result
    assert "total_calories" in result
    assert "details" in result

    # BMR: 10*70 + 6.25*170 - 5*25 + 5 = 700 + 1062.5 - 125 + 5 = 1642.5
    assert pytest.approx(result["bmr"], rel=1e-3) == 1642.5

    # Total weight: 80kg
    # Base burn: 6.0 * 80 * 6 = 2880
    # Elevation: 80 * (800 / 100) * 0.5 = 80 * 8 * 0.5 = 320
    # Hiking burn: 2880 + 320 = 3200
    assert pytest.approx(result["hiking_burn"], rel=1e-3) == 3200.0

    # Total: 1642.5 + 3200 = 4842.5
    assert pytest.approx(result["total_calories"], rel=1e-3) == 4842.5
    assert result["details"]["body_weight_kg"] == 70.0


@pytest.mark.parametrize(
    "weight,height,age,gender",
    [
        (-10.0, 170.0, 25, "male"),
        (70.0, -170.0, 25, "male"),
        (70.0, 170.0, -5, "male"),
        (70.0, 170.0, 25, "other"),
    ],
)
def test_calculate_bmr_invalid_inputs(weight, height, age, gender):
    with pytest.raises(ValueError):
        calculate_bmr(weight_kg=weight, height_cm=height, age=age, gender=gender)


@pytest.mark.parametrize(
    "body_weight,carrier_weight,duration,elevation",
    [
        (-70.0, 10.0, 5.0, 500.0),
        (70.0, -10.0, 5.0, 500.0),
        (70.0, 10.0, -1.0, 500.0),
        (70.0, 10.0, 5.0, -100.0),
    ],
)
def test_calculate_hiking_burn_invalid_inputs(body_weight, carrier_weight, duration, elevation):
    with pytest.raises(ValueError):
        calculate_hiking_burn(
            body_weight_kg=body_weight,
            carrier_weight_kg=carrier_weight,
            duration_hours=duration,
            elevation_gain_m=elevation,
        )


def test_calculate_daily_hiking_calories_negative_raises_error():
    with pytest.raises(ValueError):
        calculate_daily_hiking_calories(
            body_weight_kg=-65.0,
            carrier_weight_kg=10.0,
            elevation_gain_m=500.0,
        )
