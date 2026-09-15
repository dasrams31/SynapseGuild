"""Data models for requirement tracking."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


@dataclass
class Requirement:
    id: str
    title: str
    description: str = ""
    category: str = "general"
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
