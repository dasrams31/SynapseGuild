import unittest
from src.models import RequirementItem, Priority, ReadinessReport
from src.tracker import RequirementTracker


class TestRequirementTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = RequirementTracker()

    def test_requirement_item_defaults_and_explicit(self):
        default_item = RequirementItem(id="REQ-1", title="Database Migration", category="Backend")
        self.assertEqual(default_item.priority, Priority.MEDIUM)
        self.assertFalse(default_item.is_met)
        self.assertEqual(default_item.notes, "")

        explicit_item = RequirementItem(
            id="REQ-2",
            title="TLS 1.3",
            category="Security",
            priority="HIGH",
            is_met=True,
            notes="Strict enforcement enabled",
        )
        self.assertEqual(explicit_item.priority, Priority.HIGH)
        self.assertTrue(explicit_item.is_met)
        self.assertEqual(explicit_item.notes, "Strict enforcement enabled")

    def test_invalid_priority_raises_error(self):
        with self.assertRaises(ValueError):
            RequirementItem(id="REQ-3", title="Bad Priority", category="Core", priority="URGENT")

    def test_duplicate_id_raises_value_error(self):
        item1 = RequirementItem(id="REQ-1", title="Auth Flow", category="Security")
        item2 = RequirementItem(id="REQ-1", title="Duplicate Auth Flow", category="Security")
        
        self.tracker.add_requirement(item1)
        with self.assertRaises(ValueError):
            self.tracker.add_requirement(item2)

    def test_toggle_status(self):
        item = RequirementItem(id="REQ-1", title="Auth Flow", category="Security", is_met=False)
        self.tracker.add_requirement(item)

        # Explicit set to True
        self.tracker.toggle_status("REQ-1", is_met=True)
        self.assertTrue(item.is_met)

        # Invert
        self.tracker.toggle_status("REQ-1")
        self.assertFalse(item.is_met)

        # Non-existent ID
        with self.assertRaises(KeyError):
            self.tracker.toggle_status("REQ-999")

    def test_calculate_readiness_score_empty_and_zero(self):
        # Empty checklist
        self.assertEqual(self.tracker.calculate_readiness_score(), 0.0)

        # Items present but none met
        self.tracker.add_requirement(RequirementItem(id="REQ-1", title="Item 1", category="Core", is_met=False))
        self.assertEqual(self.tracker.calculate_readiness_score(), 0.0)

    def test_calculate_readiness_score_all_met(self):
        self.tracker.add_requirement(RequirementItem(id="REQ-1", title="1", category="Core", priority=Priority.HIGH, is_met=True))
        self.tracker.add_requirement(RequirementItem(id="REQ-2", title="2", category="Core", priority=Priority.LOW, is_met=True))
        self.assertEqual(self.tracker.calculate_readiness_score(), 100.0)

    def test_calculate_readiness_score_weighted(self):
        # HIGH weight = 3, MEDIUM weight = 2, LOW weight = 1
        # Total weight = 3 + 2 + 1 = 6
        # Met: HIGH (3) -> 3 / 6 * 100 = 50.0%
        self.tracker.add_requirement(RequirementItem(id="REQ-1", title="High Item", category="A", priority=Priority.HIGH, is_met=True))
        self.tracker.add_requirement(RequirementItem(id="REQ-2", title="Med Item", category="A", priority=Priority.MEDIUM, is_met=False))
        self.tracker.add_requirement(RequirementItem(id="REQ-3", title="Low Item", category="B", priority=Priority.LOW, is_met=False))

        self.assertEqual(self.tracker.calculate_readiness_score(), 50.0)

        # Met: HIGH (3) + LOW (1) = 4 / 6 * 100 = 66.67%
        self.tracker.toggle_status("REQ-3", is_met=True)
        self.assertEqual(self.tracker.calculate_readiness_score(), 66.67)

    def test_get_missing_items(self):
        self.tracker.add_requirement(RequirementItem(id="REQ-1", title="A", category="Security", is_met=False))
        self.tracker.add_requirement(RequirementItem(id="REQ-2", title="B", category="Security", is_met=True))
        self.tracker.add_requirement(RequirementItem(id="REQ-3", title="C", category="Ops", is_met=False))

        missing_all = self.tracker.get_missing_items()
        self.assertEqual(len(missing_all), 2)
        self.assertEqual({item.id for item in missing_all}, {"REQ-1", "REQ-3"})

        missing_sec = self.tracker.get_missing_items(category="security")
        self.assertEqual(len(missing_sec), 1)
        self.assertEqual(missing_sec[0].id, "REQ-1")

    def test_generate_summary(self):
        self.tracker.add_requirement(RequirementItem(id="REQ-1", title="Auth", category="Security", priority=Priority.HIGH, is_met=True))
        self.tracker.add_requirement(RequirementItem(id="REQ-2", title="Audit", category="Security", priority=Priority.MEDIUM, is_met=False))
        self.tracker.add_requirement(RequirementItem(id="REQ-3", title="CI/CD", category="DevOps", priority=Priority.LOW, is_met=True))

        report: ReadinessReport = self.tracker.generate_summary()
        self.assertEqual(report.total_items, 3)
        self.assertEqual(report.met_items, 2)
        self.assertEqual(report.missing_items, 1)
        # Weights: Met (HIGH=3 + LOW=1 = 4), Total (3 + 2 + 1 = 6) -> 4/6 = 66.67%
        self.assertEqual(report.readiness_score, 66.67)
        self.assertEqual(report.category_breakdown["Security"], {"total": 2, "met": 1, "missing": 1})
        self.assertEqual(report.category_breakdown["DevOps"], {"total": 1, "met": 1, "missing": 0})


if __name__ == "__main__":
    unittest.main()
