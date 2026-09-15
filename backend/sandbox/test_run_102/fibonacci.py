"""Fibonacci number and sequence generator module."""
from __future__ import annotations


def fibonacci(n: int) -> int:
    """Compute the nth Fibonacci number (0-indexed).

    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2) for n >= 2.

    Args:
        n: The index of the Fibonacci number to compute.

    Returns:
        The nth Fibonacci number.

    Raises:
        TypeError: If n is not an integer or is a boolean.
        ValueError: If n is negative.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"Index must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"Index must be non-negative, got {n}")

    if n == 0:
        return 0
    if n == 1:
        return 1

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def fibonacci_sequence(n: int) -> list[int]:
    """Generate a list of the first n Fibonacci numbers [F(0), ..., F(n-1)].

    Args:
        n: The number of terms to generate.

    Returns:
        A list containing the first n Fibonacci numbers.

    Raises:
        TypeError: If n is not an integer or is a boolean.
        ValueError: If n is negative.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"Count must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"Count must be non-negative, got {n}")

    if n == 0:
        return []
    if n == 1:
        return [0]

    sequence = [0, 1]
    prev, curr = 0, 1
    for _ in range(2, n):
        prev, curr = curr, prev + curr
        sequence.append(curr)
    return sequence
