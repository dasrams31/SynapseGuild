"""Unit test untuk modul kalkulator diskon."""

import pytest
from src.discount_calculator import (
    calculate_discount_amount,
    calculate_discounted_price,
)


def test_standard_discount_calculation():
    """Menguji kalkulasi diskon standar."""
    original_price = 100000
    discount_percent = 20
    assert calculate_discount_amount(original_price, discount_percent) == 20000.0
    assert calculate_discounted_price(original_price, discount_percent) == 80000.0


def test_boundary_zero_percent_discount():
    """Menguji batas bawah diskon 0% (harga tidak berkurang)."""
    original_price = 50000.0
    assert calculate_discount_amount(original_price, 0) == 0.0
    assert calculate_discounted_price(original_price, 0) == 50000.0


def test_boundary_hundred_percent_discount():
    """Menguji batas atas diskon 100% (harga akhir 0)."""
    original_price = 75000.0
    assert calculate_discount_amount(original_price, 100) == 75000.0
    assert calculate_discounted_price(original_price, 100) == 0.0


def test_boundary_zero_original_price():
    """Menguji harga awal bernilai 0."""
    assert calculate_discount_amount(0, 50) == 0.0
    assert calculate_discounted_price(0, 50) == 0.0


def test_decimal_precision_and_rounding():
    """Menguji nilai desimal dengan pembulatan 2 angka di belakang koma."""
    original_price = 99.99
    discount_percent = 15.5
    # 99.99 * 0.155 = 15.49845 -> dibulatkan 15.50
    # 99.99 * (1 - 0.155) = 84.49155 -> dibulatkan 84.49
    assert calculate_discount_amount(original_price, discount_percent) == 15.50
    assert calculate_discounted_price(original_price, discount_percent) == 84.49


@pytest.mark.parametrize("invalid_price", [-1, -0.01, -100.5])
def test_negative_original_price_raises_value_error(invalid_price):
    """Memastikan ValueError muncul saat harga negatif."""
    with pytest.raises(ValueError):
        calculate_discount_amount(invalid_price, 10)
    with pytest.raises(ValueError):
        calculate_discounted_price(invalid_price, 10)


@pytest.mark.parametrize("invalid_discount", [-0.1, -10, 100.01, 150])
def test_out_of_range_discount_percent_raises_value_error(invalid_discount):
    """Memastikan ValueError muncul saat persentase diskon < 0 atau > 100."""
    with pytest.raises(ValueError):
        calculate_discount_amount(1000, invalid_discount)
    with pytest.raises(ValueError):
        calculate_discounted_price(1000, invalid_discount)


@pytest.mark.parametrize("invalid_type_input", ["100", None, True, False, [20], {"price": 100}])
def test_invalid_types_raise_type_error(invalid_type_input):
    """Memastikan TypeError muncul saat tipe data bukan numerik atau bertipe boolean."""
    with pytest.raises(TypeError):
        calculate_discount_amount(invalid_type_input, 10)
    with pytest.raises(TypeError):
        calculate_discount_amount(100, invalid_type_input)
    with pytest.raises(TypeError):
        calculate_discounted_price(invalid_type_input, 10)
    with pytest.raises(TypeError):
        calculate_discounted_price(100, invalid_type_input)
