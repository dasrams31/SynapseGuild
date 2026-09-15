"""Module for calculating Fibonacci numbers iteratively."""


def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using an iterative approach.

    Complexity:
        Time: O(n)
        Space: O(1)

    Args:
        n: Non-negative integer index in the Fibonacci sequence.

    Returns:
        The nth Fibonacci number.

    Raises:
        TypeError: If n is not an integer (or if n is a boolean).
        ValueError: If n is a negative integer.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("Input 'n' must be an integer.")
    if n < 0:
        raise ValueError("Input 'n' must be a non-negative integer.")
    if n == 0:
        return 0
    if n == 1:
        return 1

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr
