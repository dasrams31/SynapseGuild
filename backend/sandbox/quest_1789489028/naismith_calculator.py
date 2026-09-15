from dataclasses import dataclass, field
import math
from typing import List, Optional


@dataclass
class RouteSegment:
    distance_km: float
    elevation_gain_m: float = 0.0
    elevation_loss_m: float = 0.0
    name: Optional[str] = None

    def __post_init__(self):
        if self.distance_km < 0:
            raise ValueError("distance_km cannot be negative")
        if self.elevation_gain_m < 0:
            raise ValueError("elevation_gain_m cannot be negative")
        if self.elevation_loss_m < 0:
            raise ValueError("elevation_loss_m cannot be negative")


@dataclass
class EstimationResult:
    total_hours: float
    hours: int
    minutes: int
    formatted_time: str
    segment_results: List["EstimationResult"] = field(default_factory=list)
    segment_name: Optional[str] = None


class NaismithCalculator:
    def __init__(
        self,
        base_speed_kmh: float = 5.0,
        ascent_rate_m_per_hour: float = 600.0,
        apply_langmuir_correction: bool = False,
    ):
        if base_speed_kmh <= 0:
            raise ValueError("base_speed_kmh must be positive")
        if ascent_rate_m_per_hour <= 0:
            raise ValueError("ascent_rate_m_per_hour must be positive")

        self.base_speed_kmh = base_speed_kmh
        self.ascent_rate_m_per_hour = ascent_rate_m_per_hour
        self.apply_langmuir_correction = apply_langmuir_correction

    def _format_time(self, total_hours: float) -> tuple[int, int, str]:
        total_minutes = round(total_hours * 60)
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        formatted = f"{hours} jam {minutes} menit"
        return hours, minutes, formatted

    def calculate_segment(self, segment: RouteSegment) -> EstimationResult:
        if segment.distance_km < 0 or segment.elevation_gain_m < 0 or segment.elevation_loss_m < 0:
            raise ValueError("Segment values cannot be negative")

        horizontal_hours = segment.distance_km / self.base_speed_kmh
        ascent_hours = segment.elevation_gain_m / self.ascent_rate_m_per_hour
        descent_hours = 0.0

        if self.apply_langmuir_correction and segment.elevation_loss_m > 0:
            horizontal_distance_m = segment.distance_km * 1000.0
            if horizontal_distance_m > 0:
                angle_rad = math.atan(segment.elevation_loss_m / horizontal_distance_m)
                angle_deg = math.degrees(angle_rad)
            else:
                angle_deg = 90.0

            if 5.0 <= angle_deg <= 12.0:
                # -10 minutes per 300m descent
                descent_hours = -(segment.elevation_loss_m / 300.0) * (10.0 / 60.0)
            elif angle_deg > 12.0:
                # +10 minutes per 300m descent
                descent_hours = (segment.elevation_loss_m / 300.0) * (10.0 / 60.0)

        total_hours = max(0.0, horizontal_hours + ascent_hours + descent_hours)
        hours, minutes, formatted_time = self._format_time(total_hours)

        return EstimationResult(
            total_hours=total_hours,
            hours=hours,
            minutes=minutes,
            formatted_time=formatted_time,
            segment_name=segment.name,
        )

    def calculate_route(self, segments: List[RouteSegment]) -> EstimationResult:
        segment_results = [self.calculate_segment(seg) for seg in segments]
        total_hours = sum(res.total_hours for res in segment_results)
        hours, minutes, formatted_time = self._format_time(total_hours)

        return EstimationResult(
            total_hours=total_hours,
            hours=hours,
            minutes=minutes,
            formatted_time=formatted_time,
            segment_results=segment_results,
        )
