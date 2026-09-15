"""Unit tests for bmi_calculator module."""

import pytest
from bmi_calculator import calculate_bmi, get_bmi_category, evaluate_bmi


class TestCalculateBmi:
    """Tests for calculate_bmi function."""

    def test_calculate_bmi_standard(self):
        assert calculate_bmi(70.0, 1.75) == 22.86
        assert calculate_bmi(50.0, 1.60) == 19.53
        assert calculate_bmi(90.0, 1.80) == 27.78

    @pytest.mark.parametrize("weight,height", [
        (0, 1.75),
        (-10, 1.75),
        (70, 0),
        (70, -1.75),
        (0, 0),
        (-50, -1.60),
    ])
    def test_calculate_bmi_invalid_inputs(self, weight, height):
        with pytest.raises(ValueError):
            calculate_bmi(weight, height)


class TestGetBmiCategory:
    """Tests for get_bmi_category function."""

    @pytest.mark.parametrize("bmi,expected_category", [
        (10.0, "Underweight"),
        (18.49, "Underweight"),
        (18.5, "Normal weight"),
        (22.0, "Normal weight"),
        (24.99, "Normal weight"),
        (25.0, "Overweight"),
        (27.5, "Overweight"),
        (29.99, "Overweight"),
        (30.0, "Obesity"),
        (35.5, "Obesity"),
        (45.0, "Obesity"),
    ])
    def test_get_bmi_category_boundaries(self, bmi, expected_category):
        assert get_bmi_category(bmi) == expected_category

    @pytest.mark.parametrize("invalid_bmi", [0, -0.01, -15.0])
    def test_get_bmi_category_invalid_inputs(self, invalid_bmi):
        with pytest.raises(ValueError):
            get_bmi_category(invalid_bmi)


class TestEvaluateBmi:
    """Tests for evaluate_bmi function."""

    def test_evaluate_bmi_valid(self):
        result = evaluate_bmi(70.0, 1.75)
        assert result == {"bmi": 22.86, "category": "Normal weight"}

    def test_evaluate_bmi_underweight(self):
        result = evaluate_bmi(45.0, 1.70)
        assert result == {"bmi": 15.57, "category": "Underweight"}

    def test_evaluate_bmi_overweight(self):
        result = evaluate_bmi(85.0, 1.75)
        assert result == {"bmi": 27.76, "category": "Overweight"}

    def test_evaluate_bmi_obesity(self):
        result = evaluate_bmi(100.0, 1.70)
        assert result == {"bmi": 34.6, "category": "Obesity"}

    @pytest.mark.parametrize("weight,height", [
        (0, 1.75),
        (-70, 1.75),
        (70, 0),
        (70, -1.75),
    ])
    def test_evaluate_bmi_invalid_inputs(self, weight, height):
        with pytest.raises(ValueError):
            evaluate_bmi(weight, height)
