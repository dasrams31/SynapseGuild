"""Export utilities for requirement tracking reports."""

from typing import Any, Dict
from needs_tracker.manager import NeedsManager
from needs_tracker.models import Status


def export_to_dict(manager: NeedsManager) -> Dict[str, Any]:
    """Exports requirement registry and summary metrics to a serializable dictionary."""
    summary = manager.get_summary()
    requirements_data = []
    for req in manager.list_all():
        requirements_data.append({
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "category": req.category,
            "priority": req.priority.value,
            "status": req.status.value,
            "dependencies": list(req.dependencies),
            "metadata": dict(req.metadata),
        })
    return {
        "summary": summary,
        "requirements": requirements_data,
    }


def export_to_markdown(manager: NeedsManager) -> str:
    """Generates a formatted Markdown checklist report with categorized requirements."""
    summary = manager.get_summary()
    lines = [
        "# Requirements Checklist",
        "",
        f"**Summary:** Total: {summary['total']} | Completed: {summary['completed']} | Pending: {summary['pending']} | Completion Rate: {summary['completion_rate']:.1f}%",
        "",
        "## Checklist",
        "",
    ]

    all_reqs = manager.list_all()
    if not all_reqs:
        lines.append("_No requirements found._")
        return "\n".join(lines) + "\n"

    categories = sorted({r.category for r in all_reqs})
    for cat in categories:
        lines.append(f"### {cat.title()}")
        lines.append("")
        cat_reqs = manager.filter_by(category=cat)
        for r in cat_reqs:
            box = "[x]" if r.status == Status.COMPLETED else "[ ]"
            prio = r.priority.value
            stat = r.status.value
            dep_str = f" (Depends on: {', '.join(r.dependencies)})" if r.dependencies else ""
            lines.append(f"- {box} **[{r.id}]** {r.title} `[{prio}]` `[{stat}]`{dep_str}")
            if r.description:
                lines.append(f"  - _{r.description}_")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
