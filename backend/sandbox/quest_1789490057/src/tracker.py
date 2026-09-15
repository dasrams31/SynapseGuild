from typing import Dict, List, Optional
from src.models import RequirementItem, ReadinessReport


class RequirementTracker:
    """Manages requirements, status tracking, and readiness evaluation."""

    def __init__(self):
        self._items: Dict[str, RequirementItem] = {}

    def add_requirement(self, item: RequirementItem) -> None:
        """Adds a new requirement item. Raises ValueError if ID already exists."""
        if item.id in self._items:
            raise ValueError(f"Requirement with ID '{item.id}' already exists.")
        self._items[item.id] = item

    def toggle_status(self, item_id: str, is_met: Optional[bool] = None) -> RequirementItem:
        """Updates or toggles completion status for an item."""
        if item_id not in self._items:
            raise KeyError(f"Requirement with ID '{item_id}' not found.")
        
        item = self._items[item_id]
        if is_met is None:
            item.is_met = not item.is_met
        else:
            item.is_met = is_met
        return item

    def get_missing_items(self, category: Optional[str] = None) -> List[RequirementItem]:
        """Returns all unmet requirements, optionally filtered by category."""
        missing = [item for item in self._items.values() if not item.is_met]
        if category is not None:
            missing = [item for item in missing if item.category.lower() == category.lower()]
        return missing

    def calculate_readiness_score(self) -> float:
        """Calculates weighted completion score as a percentage [0.0 - 100.0].
        Weights: HIGH=3, MEDIUM=2, LOW=1.
        Returns 0.0 for empty checklists.
        """
        if not self._items:
            return 0.0

        total_weighted_points = sum(item.priority.weight for item in self._items.values())
        met_weighted_points = sum(item.priority.weight for item in self._items.values() if item.is_met)

        if total_weighted_points == 0:
            return 0.0

        score = (met_weighted_points / total_weighted_points) * 100.0
        return round(score, 2)

    def generate_summary(self) -> ReadinessReport:
        """Generates a readiness assessment report."""
        total_items = len(self._items)
        met_items = sum(1 for item in self._items.values() if item.is_met)
        missing_items = total_items - met_items
        score = self.calculate_readiness_score()

        category_breakdown: Dict[str, Dict[str, int]] = {}
        for item in self._items.values():
            cat = item.category
            if cat not in category_breakdown:
                category_breakdown[cat] = {"total": 0, "met": 0, "missing": 0}
            category_breakdown[cat]["total"] += 1
            if item.is_met:
                category_breakdown[cat]["met"] += 1
            else:
                category_breakdown[cat]["missing"] += 1

        return ReadinessReport(
            total_items=total_items,
            met_items=met_items,
            missing_items=missing_items,
            readiness_score=score,
            category_breakdown=category_breakdown,
        )
