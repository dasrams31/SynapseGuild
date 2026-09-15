"""Unit test untuk modul naismith_calculator."""
import pytest
from naismith_calculator import calculate_naismith_time, calculate_naismith_breakdown


def test_flat_route():
    """Acceptance criteria: Rute datar 5.0 km, 0 m -> 1.0 jam."""
    assert calculate_naismith_time(5.0, 0.0) == pytest.approx(1.0)


def test_pure_vertical_route():
    """Acceptance criteria: Rute vertikal murni 0.0 km, 600 m -> 1.0 jam."""
    assert calculate_naismith_time(0.0, 600.0) == pytest.approx(1.0)


def test_combined_common_route():
    """Acceptance criteria: Rute kombinasi umum 10.0 km, 1200 m -> 4.0 jam."""
    assert calculate_naismith_time(10.0, 1200.0) == pytest.approx(4.0)


def test_fractional_route():
    """Acceptance criteria: Rute pecahan 2.5 km, 300 m -> 1.0 jam."""
    assert calculate_naismith_time(2.5, 300.0) == pytest.approx(1.0)


def test_zero_point():
    """Acceptance criteria: Titik nol 0 km, 0 m -> 0.0 jam."""
    assert calculate_naismith_time(0, 0) == pytest.approx(0.0)


@pytest.mark.parametrize(
    "distance_km, elevation_gain_m",
    [
        (-5.0, 100.0),
        (5.0, -100.0),
        (-1.0, -50.0),
    ],
)
def test_negative_values_raise_value_error(distance_km, elevation_gain_m):
    """Acceptance criteria: Input negatif memicu ValueError."""
    with pytest.raises(ValueError):
        calculate_naismith_time(distance_km, elevation_gain_m)


@pytest.mark.parametrize(
    "distance_km, elevation_gain_m",
    [
        ("5.0", 100.0),
        (5.0, "100.0"),
        (None, 200.0),
        (10.0, None),
        (True, 300.0),
        (5.0, False),
        ([5.0], 100.0),
    ],
)
def test_invalid_types_raise_type_error(distance_km, elevation_gain_m):
    """Acceptance criteria: Input non-numerik dan bool memicu TypeError."""
    with pytest.raises(TypeError):
        calculate_naismith_time(distance_km, elevation_gain_m)


def test_calculate_naismith_breakdown():
    """Menguji fungsi pendukung pemecah waktu jam dan menit."""
    breakdown = calculate_naismith_breakdown(7.5, 450.0)
    # 7.5 / 5 = 1.5 jam; 450 / 600 = 0.75 jam; Total = 2.25 jam = 2 jam 15 menit
    assert breakdown["total_hours"] == pytest.approx(2.25)
    assert breakdown["hours"] == 2
    assert breakdown["minutes"] == 15
