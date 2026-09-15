"""Unit tests for the fibonacci module."""

import unittest
from fibonacci import fibonacci, fibonacci_sequence


class TestFibonacci(unittest.TestCase):
    def test_base_cases(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_known_values(self):
        self.assertEqual(fibonacci(2), 1)
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(20), 6765)

    def test_large_input(self):
        self.assertEqual(fibonacci(100), 354224848179261915075)

    def test_fibonacci_sequence(self):
        self.assertEqual(fibonacci_sequence(0), [])
        self.assertEqual(fibonacci_sequence(1), [0])
        self.assertEqual(fibonacci_sequence(2), [0, 1])
        self.assertEqual(fibonacci_sequence(6), [0, 1, 1, 2, 3, 5])

    def test_negative_values(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)
        with self.assertRaises(ValueError):
            fibonacci(-5)
        with self.assertRaises(ValueError):
            fibonacci_sequence(-1)
        with self.assertRaises(ValueError):
            fibonacci_sequence(-10)

    def test_invalid_types(self):
        invalid_inputs = [3.14, "5", True, False, None, [1], {"n": 5}]
        for val in invalid_inputs:
            with self.subTest(val=val):
                with self.assertRaises(TypeError):
                    fibonacci(val)
                with self.assertRaises(TypeError):
                    fibonacci_sequence(val)


if __name__ == "__main__":
    unittest.main()
