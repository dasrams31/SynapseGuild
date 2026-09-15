"""Fibonacci calculation module providing single-term and sequence generation."""


def _validate_input(n: int) -> None:
    if type(n) is not int:
        raise TypeError(f"Input must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"Input must be a non-negative integer, got {n}")


def fibonacci(n: int) -> int:
    """Compute the n-th Fibonacci number (0-indexed) using an iterative O(n) approach."""
    _validate_input(n)
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(n: int) -> list[int]:
    """Return a list of the first n Fibonacci numbers."""
    _validate_input(n)
    if n == 0:
        return []
    if n == 1:
        return [0]

    seq = [0, 1]
    a, b = 0, 1
    for _ in range(2, n):
        a, b = b, a + b
        seq.append(b)
    return seq
