"""Unit tests for fibonacci module using standard library unittest."""
import unittest
from fibonacci import fibonacci, fibonacci_sequence


class TestFibonacci(unittest.TestCase):
    """Test suite for fibonacci calculation."""

    def test_base_cases(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_known_values(self):
        expected_pairs = [
            (2, 1),
            (3, 2),
            (4, 3),
            (5, 5),
            (6, 8),
            (7, 13),
            (8, 21),
            (9, 34),
            (10, 55),
            (20, 6765),
            (30, 832040),
        ]
        for n, expected in expected_pairs:
            with self.subTest(n=n):
                self.assertEqual(fibonacci(n), expected)

    def test_negative_values_raise_value_error(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)
        with self.assertRaises(ValueError):
            fibonacci(-10)

    def test_invalid_types_raise_type_error(self):
        invalid_inputs = ["abc", 3.14, None, [0], {1: 2}, (1,)]
        for val in invalid_inputs:
            with self.subTest(val=val):
                with self.assertRaises(TypeError):
                    fibonacci(val)

    def test_booleans_raise_type_error(self):
        with self.assertRaises(TypeError):
            fibonacci(True)
        with self.assertRaises(TypeError):
            fibonacci(False)


class TestFibonacciSequence(unittest.TestCase):
    """Test suite for fibonacci sequence generation."""

    def test_empty_and_single_element_sequences(self):
        self.assertEqual(fibonacci_sequence(0), [])
        self.assertEqual(fibonacci_sequence(1), [0])

    def test_sequence_generation(self):
        self.assertEqual(fibonacci_sequence(2), [0, 1])
        self.assertEqual(fibonacci_sequence(5), [0, 1, 1, 2, 3])
        self.assertEqual(fibonacci_sequence(10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_sequence_negative_values_raise_value_error(self):
        with self.assertRaises(ValueError):
            fibonacci_sequence(-1)
        with self.assertRaises(ValueError):
            fibonacci_sequence(-5)

    def test_sequence_invalid_types_raise_type_error(self):
        invalid_inputs = ["5", 2.5, True, False, None, [5]]
        for val in invalid_inputs:
            with self.subTest(val=val):
                with self.assertRaises(TypeError):
                    fibonacci_sequence(val)


if __name__ == "__main__":
    unittest.main()
