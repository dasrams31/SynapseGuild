"""Unit tests for needs_tracker package."""

import unittest
from needs_tracker.exporter import export_to_dict, export_to_markdown
from needs_tracker.manager import NeedsManager
from needs_tracker.models import Priority, Requirement, Status


class TestNeedsTracker(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = NeedsManager()

    def test_requirement_defaults(self) -> None:
        req = Requirement(id="REQ-01", title="Initialize Core")
        self.assertEqual(req.id, "REQ-01")
        self.assertEqual(req.title, "Initialize Core")
        self.assertEqual(req.description, "")
        self.assertEqual(req.category, "general")
        self.assertEqual(req.priority, Priority.MEDIUM)
        self.assertEqual(req.status, Status.PENDING)
        self.assertEqual(req.dependencies, [])
        self.assertEqual(req.metadata, {})

    def test_add_and_retrieve_requirement(self) -> None:
        req = Requirement(
            id="REQ-01",
            title="Setup DB",
            description="PostgreSQL setup",
            category="infrastructure",
            priority=Priority.HIGH,
        )
        result_id = self.manager.add_requirement(req)
        self.assertEqual(result_id, "REQ-01")

        retrieved = self.manager.get_requirement("REQ-01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Setup DB")

        self.assertIsNone(self.manager.get_requirement("NON-EXISTENT"))

    def test_dependencies_and_status_update_enforcement(self) -> None:
        dep1 = Requirement(id="DEP-1", title="Base Schema")
        dep2 = Requirement(id="DEP-2", title="User Table")
        target = Requirement(
            id="TARGET-1",
            title="Auth Service",
            dependencies=["DEP-1", "DEP-2"],
        )

        self.manager.add_requirement(dep1)
        self.manager.add_requirement(dep2)
        self.manager.add_requirement(target)

        # Target cannot be completed when dependencies are pending
        missing = self.manager.get_missing_dependencies("TARGET-1")
        self.assertEqual(set(missing), {"DEP-1", "DEP-2"})
        self.assertFalse(self.manager.update_status("TARGET-1", Status.COMPLETED))
        self.assertEqual(self.manager.get_requirement("TARGET-1").status, Status.PENDING)

        # Complete one dependency
        self.assertTrue(self.manager.update_status("DEP-1", Status.COMPLETED))
        self.assertEqual(self.manager.get_missing_dependencies("TARGET-1"), ["DEP-2"])
        self.assertFalse(self.manager.update_status("TARGET-1", Status.COMPLETED))

        # Complete remaining dependency
        self.assertTrue(self.manager.update_status("DEP-2", Status.COMPLETED))
        self.assertEqual(self.manager.get_missing_dependencies("TARGET-1"), [])
        self.assertTrue(self.manager.update_status("TARGET-1", Status.COMPLETED))
        self.assertEqual(self.manager.get_requirement("TARGET-1").status, Status.COMPLETED)

    def test_missing_dependency_for_nonexistent_requirement(self) -> None:
        self.assertEqual(self.manager.get_missing_dependencies("UNKNOWN"), [])
        self.assertFalse(self.manager.update_status("UNKNOWN", Status.COMPLETED))

    def test_summary_metrics(self) -> None:
        # Empty manager summary
        summary_empty = self.manager.get_summary()
        self.assertEqual(summary_empty["total"], 0)
        self.assertEqual(summary_empty["completion_rate"], 0.0)

        r1 = Requirement(id="1", title="Task 1", status=Status.COMPLETED)
        r2 = Requirement(id="2", title="Task 2", status=Status.PENDING)
        r3 = Requirement(id="3", title="Task 3", status=Status.IN_PROGRESS)
        r4 = Requirement(id="4", title="Task 4", status=Status.BLOCKED)
        r5 = Requirement(id="5", title="Task 5", status=Status.COMPLETED)

        for r in [r1, r2, r3, r4, r5]:
            self.manager.add_requirement(r)

        summary = self.manager.get_summary()
        self.assertEqual(summary["total"], 5)
        self.assertEqual(summary["completed"], 2)
        self.assertEqual(summary["pending"], 1)
        self.assertEqual(summary["in_progress"], 1)
        self.assertEqual(summary["blocked"], 1)
        self.assertAlmostEqual(summary["completion_rate"], 40.0)

    def test_filter_by_criteria(self) -> None:
        r1 = Requirement(id="1", title="T1", category="backend", priority=Priority.HIGH, status=Status.PENDING)
        r2 = Requirement(id="2", title="T2", category="frontend", priority=Priority.LOW, status=Status.COMPLETED)
        r3 = Requirement(id="3", title="T3", category="backend", priority=Priority.CRITICAL, status=Status.IN_PROGRESS)
        r4 = Requirement(id="4", title="T4", category="backend", priority=Priority.HIGH, status=Status.COMPLETED)

        for r in [r1, r2, r3, r4]:
            self.manager.add_requirement(r)

        self.assertEqual(len(self.manager.filter_by(category="backend")), 3)
        self.assertEqual(len(self.manager.filter_by(priority=Priority.HIGH)), 2)
        self.assertEqual(len(self.manager.filter_by(status=Status.COMPLETED)), 2)
        self.assertEqual(
            len(self.manager.filter_by(category="backend", priority=Priority.HIGH, status=Status.COMPLETED)),
            1,
        )

    def test_export_to_dict_and_markdown(self) -> None:
        r1 = Requirement(
            id="REQ-01",
            title="Setup Environment",
            description="Install Python 3.11",
            category="setup",
            priority=Priority.CRITICAL,
            status=Status.COMPLETED,
            metadata={"owner": "forge_master"},
        )
        r2 = Requirement(
            id="REQ-02",
            title="Run Tests",
            category="testing",
            priority=Priority.MEDIUM,
            status=Status.PENDING,
            dependencies=["REQ-01"],
        )
        self.manager.add_requirement(r1)
        self.manager.add_requirement(r2)

        # Dictionary export
        data = export_to_dict(self.manager)
        self.assertIn("summary", data)
        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["completed"], 1)
        self.assertEqual(len(data["requirements"]), 2)
        self.assertEqual(data["requirements"][0]["metadata"]["owner"], "forge_master")

        # Markdown export
        md = export_to_markdown(self.manager)
        self.assertIn("# Requirements Checklist", md)
        self.assertIn("### Setup", md)
        self.assertIn("### Testing", md)
        self.assertIn("- [x] **[REQ-01]** Setup Environment", md)
        self.assertIn("- [ ] **[REQ-02]** Run Tests", md)
        self.assertIn("(Depends on: REQ-01)", md)
        self.assertIn("Install Python 3.11", md)

    def test_empty_manager_markdown_export(self) -> None:
        empty_manager = NeedsManager()
        md = export_to_markdown(empty_manager)
        self.assertIn("_No requirements found._", md)


if __name__ == "__main__":
    unittest.main()
