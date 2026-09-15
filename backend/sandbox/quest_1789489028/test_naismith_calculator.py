import pytest
from naismith_calculator import NaismithCalculator, RouteSegment


def test_base_flat_calculation():
    calc = NaismithCalculator(base_speed_kmh=5.0, ascent_rate_m_per_hour=600.0)
    segment = RouteSegment(distance_km=5.0, elevation_gain_m=0.0)
    result = calc.calculate_segment(segment)

    assert result.total_hours == 1.0
    assert result.hours == 1
    assert result.minutes == 0
    assert result.formatted_time == "1 jam 0 menit"


def test_ascent_calculation():
    calc = NaismithCalculator(base_speed_kmh=5.0, ascent_rate_m_per_hour=600.0)
    segment = RouteSegment(distance_km=0.0, elevation_gain_m=600.0)
    result = calc.calculate_segment(segment)

    assert result.total_hours == 1.0
    assert result.hours == 1
    assert result.minutes == 0
    assert result.formatted_time == "1 jam 0 menit"


def test_combined_standard_calculation():
    calc = NaismithCalculator(base_speed_kmh=5.0, ascent_rate_m_per_hour=600.0)
    segment = RouteSegment(distance_km=10.0, elevation_gain_m=1200.0)
    result = calc.calculate_segment(segment)

    # 10 / 5 = 2.0 hrs, 1200 / 600 = 2.0 hrs -> total 4.0 hrs
    assert result.total_hours == 4.0
    assert result.hours == 4
    assert result.minutes == 0
    assert result.formatted_time == "4 jam 0 menit"


def test_multi_segment_route():
    calc = NaismithCalculator(base_speed_kmh=5.0, ascent_rate_m_per_hour=600.0)
    segments = [
        RouteSegment(distance_km=5.0, elevation_gain_m=0.0, name="Pos 1 ke Pos 2"),
        RouteSegment(distance_km=2.5, elevation_gain_m=300.0, name="Pos 2 ke Pos 3"),
        RouteSegment(distance_km=2.5, elevation_gain_m=300.0, name="Pos 3 ke Puncak"),
    ]
    route_result = calc.calculate_route(segments)

    # Segment 1: 1.0 hr
    # Segment 2: 0.5 hr + 0.5 hr = 1.0 hr
    # Segment 3: 0.5 hr + 0.5 hr = 1.0 hr
    # Total: 3.0 hrs
    assert len(route_result.segment_results) == 3
    assert route_result.total_hours == 3.0
    assert route_result.hours == 3
    assert route_result.minutes == 0
    assert route_result.formatted_time == "3 jam 0 menit"
    assert route_result.segment_results[0].segment_name == "Pos 1 ke Pos 2"


def test_langmuir_gentle_descent():
    # Distance 3000m (3km), Drop 300m -> atan(300/3000) ~ 5.71 degrees (between 5 and 12)
    calc = NaismithCalculator(apply_langmuir_correction=True)
    segment = RouteSegment(distance_km=3.0, elevation_loss_m=300.0)
    result = calc.calculate_segment(segment)

    # Base horizontal: 3.0 / 5.0 = 0.6 hours (36 mins)
    # Langmuir gentle descent correction: -10 mins (-10/60 hr)
    # Total hours: 36 - 10 = 26 mins = 26 / 60 hours = 0.43333333333333335 hours
    assert result.hours == 0
    assert result.minutes == 26
    assert result.formatted_time == "0 jam 26 menit"


def test_langmuir_steep_descent():
    # Distance 1000m (1km), Drop 300m -> atan(300/1000) ~ 16.7 degrees (> 12)
    calc = NaismithCalculator(apply_langmuir_correction=True)
    segment = RouteSegment(distance_km=1.0, elevation_loss_m=300.0)
    result = calc.calculate_segment(segment)

    # Base horizontal: 1.0 / 5.0 = 0.2 hours (12 mins)
    # Langmuir steep descent correction: +10 mins (+10/60 hr)
    # Total hours: 12 + 10 = 22 mins
    assert result.hours == 0
    assert result.minutes == 22
    assert result.formatted_time == "0 jam 22 menit"


def test_langmuir_flat_descent():
    # Distance 5000m (5km), Drop 100m -> atan(100/5000) ~ 1.14 degrees (< 5)
    calc = NaismithCalculator(apply_langmuir_correction=True)
    segment = RouteSegment(distance_km=5.0, elevation_loss_m=100.0)
    result = calc.calculate_segment(segment)

    # Base horizontal: 5.0 / 5.0 = 1.0 hour (60 mins), no correction applied
    assert result.total_hours == 1.0
    assert result.hours == 1
    assert result.minutes == 0
    assert result.formatted_time == "1 jam 0 menit"


def test_edge_cases_zero_input():
    calc = NaismithCalculator()
    segment = RouteSegment(distance_km=0.0, elevation_gain_m=0.0, elevation_loss_m=0.0)
    result = calc.calculate_segment(segment)

    assert result.total_hours == 0.0
    assert result.hours == 0
    assert result.minutes == 0
    assert result.formatted_time == "0 jam 0 menit"


def test_negative_validations():
    with pytest.raises(ValueError):
        RouteSegment(distance_km=-1.0)

    with pytest.raises(ValueError):
        RouteSegment(distance_km=1.0, elevation_gain_m=-100.0)

    with pytest.raises(ValueError):
        RouteSegment(distance_km=1.0, elevation_loss_m=-50.0)

    with pytest.raises(ValueError):
        NaismithCalculator(base_speed_kmh=-5.0)

    with pytest.raises(ValueError):
        NaismithCalculator(ascent_rate_m_per_hour=0.0)
