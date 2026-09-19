"""Unit tests for diet_calculator functions."""

import pytest
from diet_calculator import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    calculate_water_intake,
    generate_meal_plan,
    TIPS_DATABASE
)

def test_calculate_bmi_normal():
    result = calculate_bmi(70, 175)
    assert result["bmi"] == 22.86
    assert result["classification"] == "Normal"

def test_calculate_bmi_categories():
    assert calculate_bmi(45, 170)["classification"] == "Underweight"
    assert calculate_bmi(65, 170)["classification"] == "Normal"
    assert calculate_bmi(80, 170)["classification"] == "Overweight"
    assert calculate_bmi(100, 170)["classification"] == "Obese"

def test_calculate_bmi_invalid_input():
    with pytest.raises(ValueError):
        calculate_bmi(-10, 170)
    with pytest.raises(ValueError):
        calculate_bmi(70, 0)

def test_calculate_bmr_male_and_female():
    bmr_m = calculate_bmr(75, 180, 25, "male")
    # 10*75 + 6.25*180 - 5*25 + 5 = 750 + 1125 - 125 + 5 = 1755
    assert bmr_m == 1755.0

    bmr_f = calculate_bmr(60, 165, 30, "female")
    # 10*60 + 6.25*165 - 5*30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
    assert bmr_f == 1320.25

def test_calculate_bmr_invalid_gender_or_values():
    with pytest.raises(ValueError):
        calculate_bmr(70, 170, 25, "alien")
    with pytest.raises(ValueError):
        calculate_bmr(-5, 170, 25, "male")

def test_calculate_tdee():
    bmr = 1500.0
    assert calculate_tdee(bmr, "sedentary") == 1800.0
    assert calculate_tdee(bmr, "light") == 2062.5
    assert calculate_tdee(bmr, "moderate") == 2325.0
    assert calculate_tdee(bmr, "active") == 2587.5
    assert calculate_tdee(bmr, "very_active") == 2850.0
    # fallback to sedentary
    assert calculate_tdee(bmr, "unknown") == 1800.0

def test_calculate_target_calories():
    tdee = 2200.0
    assert calculate_target_calories(tdee, "weight_loss") == 1700.0
    assert calculate_target_calories(tdee, "muscle_gain") == 2600.0
    assert calculate_target_calories(tdee, "maintenance") == 2200.0

def test_calculate_macros_distribution():
    res_balanced = calculate_macros(2000, "balanced")
    assert res_balanced["protein_g"] == 150.0  # 600 / 4
    assert res_balanced["carbs_g"] == 200.0    # 800 / 4
    assert res_balanced["fat_g"] == 66.7       # 600 / 9

    res_keto = calculate_macros(2000, "keto")
    assert res_keto["protein_g"] == 125.0      # 500 / 4
    assert res_keto["carbs_g"] == 25.0         # 100 / 4
    assert res_keto["fat_g"] == 155.6          # 1400 / 9

def test_calculate_water_intake():
    assert calculate_water_intake(70) == 2.45
    assert calculate_water_intake(0) == 2.5

def test_generate_meal_plan():
    plan = generate_meal_plan(2100, "balanced")
    assert "meals" in plan
    assert len(plan["meals"]) == 4
    assert plan["target_calories"] == 2100
    assert plan["actual_calories"] > 0
    assert plan["total_protein_g"] > 0

def test_tips_database_integrity():
    assert "weight_loss" in TIPS_DATABASE
    assert "general_health" in TIPS_DATABASE
    assert "hydration" in TIPS_DATABASE
    assert "superfoods" in TIPS_DATABASE
    assert len(TIPS_DATABASE["weight_loss"]) >= 2
