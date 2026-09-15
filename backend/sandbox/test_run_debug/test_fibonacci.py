"""Unit tests for the fibonacci module."""

import pytest
from fibonacci import fibonacci


def test_fibonacci_base_cases():
    """Verify base cases fibonacci(0) and fibonacci(1)."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1


def test_fibonacci_known_values():
    """Verify known Fibonacci sequence values."""
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765


def test_fibonacci_negative_input():
    """Verify ValueError is raised for negative numbers."""
    with pytest.raises(ValueError, match="must be a non-negative integer"):
        fibonacci(-1)

    with pytest.raises(ValueError):
        fibonacci(-10)


def test_fibonacci_invalid_types():
    """Verify TypeError is raised for non-integer inputs."""
    with pytest.raises(TypeError, match="must be an integer"):
        fibonacci("invalid")

    with pytest.raises(TypeError):
        fibonacci(3.14)

    with pytest.raises(TypeError):
        fibonacci(None)

    with pytest.raises(TypeError):
        fibonacci(True)

    with pytest.raises(TypeError):
        fibonacci(False)

    with pytest.raises(TypeError):
        fibonacci([1, 2])
