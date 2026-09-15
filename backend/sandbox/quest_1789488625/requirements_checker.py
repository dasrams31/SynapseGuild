from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Requirement:
    name: str
    version_spec: Optional[str] = None
    is_required: bool = True
    category: str = "default"


def _normalize_name(name: str) -> str:
    """Normalize package names for comparison (PEP 503 compliant)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _parse_version(version_str: str) -> Tuple[Any, ...]:
    """Split a version string into comparable numeric and string tokens."""
    cleaned = re.sub(r"[^0-9a-zA-Z.]", "", version_str.strip())
    parts = re.split(r"[.]", cleaned)
    parsed: List[Any] = []
    for part in parts:
        chunks = re.findall(r"(\d+|[a-zA-Z]+)", part)
        for chunk in chunks:
            if chunk.isdigit():
                parsed.append(int(chunk))
            else:
                parsed.append(chunk.lower())
    return tuple(parsed)


def _compare_versions(v1: str, op: str, v2: str) -> bool:
    """Compare two version strings based on an operator."""
    parsed_v1 = _parse_version(v1)
    parsed_v2 = _parse_version(v2)

    # Normalize tuple lengths by padding with 0 for numeric comparisons
    max_len = max(len(parsed_v1), len(parsed_v2))
    norm_v1 = parsed_v1 + (0,) * (max_len - len(parsed_v1))
    norm_v2 = parsed_v2 + (0,) * (max_len - len(parsed_v2))

    if op == "==":
        return norm_v1 == norm_v2
    if op == "!=":
        return norm_v1 != norm_v2
    if op == ">=":
        return norm_v1 >= norm_v2
    if op == "<=":
        return norm_v1 <= norm_v2
    if op == ">":
        return norm_v1 > norm_v2
    if op == "<":
        return norm_v1 < norm_v2
    return False


def _satisfies_spec(installed_version: str, spec_string: str) -> bool:
    """Check if installed_version satisfies comma-separated specs (e.g., '>=1.0.0,<2.0.0')."""
    specs = [s.strip() for s in spec_string.split(",") if s.strip()]
    for spec in specs:
        match = re.match(r"^(==|!=|>=|<=|>|<)?\s*(.+)$", spec)
        if not match:
            continue
        op = match.group(1) or "=="
        target_version = match.group(2).strip()
        if not _compare_versions(installed_version, op, target_version):
            return False
    return True


class RequirementChecker:
    def __init__(self) -> None:
        self._requirements: Dict[str, Requirement] = {}

    def add_requirement(self, req: Requirement) -> None:
        """Register a requirement."""
        key = _normalize_name(req.name)
        self._requirements[key] = req

    def parse_requirements_file(self, content: str, default_category: str = "default", is_required: bool = True) -> None:
        """Parse standard pip-style requirements.txt string."""
        spec_pattern = re.compile(r"^([a-zA-Z0-9_.-]+)(.*)$")

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Strip inline comments
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

            match = spec_pattern.match(line)
            if match:
                pkg_name = match.group(1)
                spec = match.group(2).strip() or None
                self.add_requirement(
                    Requirement(
                        name=pkg_name,
                        version_spec=spec,
                        is_required=is_required,
                        category=default_category,
                    )
                )

    def validate_installed_packages(self, installed_map: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """Check a dictionary of {pkg_name: installed_version} against registered requirements."""
        normalized_installed = {
            _normalize_name(k): str(v).strip() for k, v in installed_map.items()
        }

        missing: List[Dict[str, Any]] = []
        mismatched: List[Dict[str, Any]] = []
        satisfied: List[Dict[str, Any]] = []

        for key, req in self._requirements.items():
            installed_version = normalized_installed.get(key)
            req_info = {
                "name": req.name,
                "required_spec": req.version_spec,
                "is_required": req.is_required,
                "category": req.category,
                "installed_version": installed_version,
            }

            if installed_version is None:
                missing.append(req_info)
            elif req.version_spec and not _satisfies_spec(installed_version, req.version_spec):
                mismatched.append(req_info)
            else:
                satisfied.append(req_info)

        return {
            "missing": missing,
            "mismatched": mismatched,
            "satisfied": satisfied,
        }

    def is_environment_ready(self, validation_result: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Return True if all mandatory requirements are satisfied."""
        for item in validation_result.get("missing", []):
            if item.get("is_required", True):
                return False
        for item in validation_result.get("mismatched", []):
            if item.get("is_required", True):
                return False
        return True

    def generate_summary_report(self, validation_result: Dict[str, List[Dict[str, Any]]]) -> str:
        """Return a formatted diagnostic report."""
        ready = self.is_environment_ready(validation_result)
        lines: List[str] = [
            "# Requirement Validation Report",
            f"**Status**: {'READY' if ready else 'ACTION REQUIRED'}",
            "",
        ]

        missing = validation_result.get("missing", [])
        mismatched = validation_result.get("mismatched", [])
        satisfied = validation_result.get("satisfied", [])

        lines.append(f"- **Satisfied**: {len(satisfied)}")
        lines.append(f"- **Missing**: {len(missing)}")
        lines.append(f"- **Mismatched**: {len(mismatched)}")
        lines.append("")

        if missing:
            lines.append("## Missing Packages")
            for item in missing:
                req_flag = "[Required]" if item.get("is_required") else "[Optional]"
                spec = item.get("required_spec") or "any"
                lines.append(f"- {req_flag} `{item['name']}` (Spec: `{spec}`, Category: `{item['category']}`)")
            lines.append("")

        if mismatched:
            lines.append("## Version Mismatches")
            for item in mismatched:
                req_flag = "[Required]" if item.get("is_required") else "[Optional]"
                lines.append(
                    f"- {req_flag} `{item['name']}` (Required: `{item['required_spec']}`, Installed: `{item['installed_version']}`)"
                )
            lines.append("")

        if satisfied:
            lines.append("## Satisfied Packages")
            for item in satisfied:
                spec = item.get("required_spec") or "any"
                lines.append(f"- `{item['name']}` (Spec: `{spec}`, Installed: `{item['installed_version']}`)")
            lines.append("")

        return "\n".join(lines).strip()
