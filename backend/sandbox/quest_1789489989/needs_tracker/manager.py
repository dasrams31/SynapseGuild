"""Manager module for requirement tracking, dependency checking, and querying."""

from typing import Any, Dict, List, Optional
from needs_tracker.models import Priority, Requirement, Status


class NeedsManager:
    """Manages requirements, lifecycle states, and dependency resolution."""

    def __init__(self) -> None:
        self._requirements: Dict[str, Requirement] = {}

    def add_requirement(self, requirement: Requirement) -> str:
        """Adds or updates a requirement in the tracker."""
        self._requirements[requirement.id] = requirement
        return requirement.id

    def get_requirement(self, req_id: str) -> Optional[Requirement]:
        """Retrieves a requirement by its unique identifier."""
        return self._requirements.get(req_id)

    def get_missing_dependencies(self, req_id: str) -> List[str]:
        """Returns the list of dependency IDs that are not marked as COMPLETED or do not exist."""
        req = self.get_requirement(req_id)
        if not req:
            return []
        
        missing: List[str] = []
        for dep_id in req.dependencies:
            dep = self.get_requirement(dep_id)
            if dep is None or dep.status != Status.COMPLETED:
                missing.append(dep_id)
        return missing

    def update_status(self, req_id: str, new_status: Status) -> bool:
        """Updates the status of a requirement. Returns False if prerequisite dependencies are incomplete."""
        req = self.get_requirement(req_id)
        if not req:
            return False

        if new_status == Status.COMPLETED:
            missing = self.get_missing_dependencies(req_id)
            if missing:
                return False

        req.status = new_status
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Calculates summary metrics for all managed requirements."""
        total = len(self._requirements)
        completed = sum(1 for r in self._requirements.values() if r.status == Status.COMPLETED)
        pending = sum(1 for r in self._requirements.values() if r.status == Status.PENDING)
        in_progress = sum(1 for r in self._requirements.values() if r.status == Status.IN_PROGRESS)
        blocked = sum(1 for r in self._requirements.values() if r.status == Status.BLOCKED)
        
        completion_rate = (completed / total * 100.0) if total > 0 else 0.0
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "blocked": blocked,
            "completion_rate": completion_rate,
        }

    def filter_by(
        self,
        category: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None,
    ) -> List[Requirement]:
        """Filters requirements by optional category, priority, and status criteria."""
        results: List[Requirement] = []
        for req in self._requirements.values():
            if category is not None and req.category != category:
                continue
            if priority is not None and req.priority != priority:
                continue
            if status is not None and req.status != status:
                continue
            results.append(req)
        return results

    def list_all(self) -> List[Requirement]:
        """Returns all registered requirements."""
        return list(self._requirements.values())
