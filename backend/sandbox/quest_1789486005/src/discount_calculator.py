"""Modul kalkulator diskon dengan validasi ketat dan pembulatan presisi."""

from typing import Union

Numeric = Union[int, float]


def _validate_inputs(original_price: Numeric, discount_percent: Numeric) -> None:
    """Memvalidasi tipe data dan batasan nilai untuk kalkulasi diskon."""
    if isinstance(original_price, bool) or not isinstance(original_price, (int, float)):
        raise TypeError("original_price must be an int or float, not boolean or other types.")
    if isinstance(discount_percent, bool) or not isinstance(discount_percent, (int, float)):
        raise TypeError("discount_percent must be an int or float, not boolean or other types.")

    if original_price < 0:
        raise ValueError("original_price must be greater than or equal to 0.")
    if not (0 <= discount_percent <= 100):
        raise ValueError("discount_percent must be within the range [0, 100].")


def calculate_discount_amount(original_price: float, discount_percent: float) -> float:
    """Menghitung nominal potongan harga yang dibulatkan ke 2 desimal."""
    _validate_inputs(original_price, discount_percent)
    discount_amount = original_price * (discount_percent / 100.0)
    return round(discount_amount, 2)


def calculate_discounted_price(original_price: float, discount_percent: float) -> float:
    """Menghitung harga akhir setelah diskon yang dibulatkan ke 2 desimal."""
    _validate_inputs(original_price, discount_percent)
    discounted_price = original_price * (1.0 - (discount_percent / 100.0))
    return round(discounted_price, 2)
