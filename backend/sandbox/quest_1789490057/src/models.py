from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @property
    def weight(self) -> int:
        weights = {
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
        }
        return weights[self]


@dataclass
class RequirementItem:
    id: str
    title: str
    category: str
    priority: Priority = Priority.MEDIUM
    is_met: bool = False
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.priority, str):
            try:
                self.priority = Priority(self.priority.upper())
            except ValueError:
                raise ValueError(f"Invalid priority: {self.priority}. Must be HIGH, MEDIUM, or LOW.")


@dataclass
class ReadinessReport:
    total_items: int
    met_items: int
    missing_items: int
    readiness_score: float
    category_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)
