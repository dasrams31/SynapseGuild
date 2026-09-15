import unittest
from dataclasses import FrozenInstanceError
from bmi_calculator import BMIResult, calculate_bmi


class TestBMICalculator(unittest.TestCase):
    def test_standard_calculation(self):
        result = calculate_bmi(70, 1.75)
        self.assertEqual(result.weight_kg, 70.0)
        self.assertEqual(result.height_m, 1.75)
        self.assertEqual(result.bmi, 22.86)
        self.assertEqual(result.category, "Normal weight")
        self.assertEqual(result.health_risk, "Low risk")

    def test_who_categories_and_boundaries(self):
        cases = [
            # (weight, height, expected_bmi, expected_category, expected_risk)
            (45.0, 1.60, 17.58, "Underweight", "Malnutrition risk"),
            (18.49, 1.00, 18.49, "Underweight", "Malnutrition risk"),
            (18.50, 1.00, 18.50, "Normal weight", "Low risk"),
            (24.99, 1.00, 24.99, "Normal weight", "Low risk"),
            (25.00, 1.00, 25.00, "Overweight", "Enhanced risk"),
            (29.99, 1.00, 29.99, "Overweight", "Enhanced risk"),
            (30.00, 1.00, 30.00, "Obesity Class I", "Medium risk"),
            (34.99, 1.00, 34.99, "Obesity Class I", "Medium risk"),
            (35.00, 1.00, 35.00, "Obesity Class II", "High risk"),
            (39.99, 1.00, 39.99, "Obesity Class II", "High risk"),
            (40.00, 1.00, 40.00, "Obesity Class III", "Very high risk"),
            (120.0, 1.60, 46.88, "Obesity Class III", "Very high risk"),
        ]
        for weight, height, expected_bmi, expected_category, expected_risk in cases:
            with self.subTest(weight=weight, height=height):
                res = calculate_bmi(weight, height)
                self.assertEqual(res.bmi, expected_bmi)
                self.assertEqual(res.category, expected_category)
                self.assertEqual(res.health_risk, expected_risk)

    def test_invalid_types_raise_type_error(self):
        invalid_inputs = [
            ("70", 1.75),
            (70, "1.75"),
            (None, 1.75),
            (70, None),
            (True, 1.75),
            (70, False),
            ([70], 1.75),
            (70, {'height': 1.75}),
        ]
        for weight, height in invalid_inputs:
            with self.subTest(weight=weight, height=height):
                with self.assertRaises(TypeError):
                    calculate_bmi(weight, height)

    def test_non_positive_values_raise_value_error(self):
        invalid_values = [
            (0, 1.75),
            (70, 0),
            (-70, 1.75),
            (70, -1.75),
            (-10, -2.0),
        ]
        for weight, height in invalid_values:
            with self.subTest(weight=weight, height=height):
                with self.assertRaises(ValueError):
                    calculate_bmi(weight, height)

    def test_bmi_result_immutability(self):
        result = calculate_bmi(70, 1.75)
        with self.assertRaises(FrozenInstanceError):
            result.bmi = 25.0
        with self.assertRaises(FrozenInstanceError):
            result.category = "Overweight"
        with self.assertRaises(FrozenInstanceError):
            result.weight_kg = 80.0


if __name__ == '__main__':
    unittest.main()
