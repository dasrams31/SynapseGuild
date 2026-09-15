import unittest
from requirements_checker import Requirement, RequirementChecker


class TestRequirementChecker(unittest.TestCase):
    def setUp(self):
        self.checker = RequirementChecker()

    def test_parse_requirements_file(self):
        content = """
        # Core packages
        requests>=2.28.0
        flask==2.3.2
        pytest
        numpy<=1.24.0 # scientific
        # Comment line
        rich>10.0.0
        """
        self.checker.parse_requirements_file(content)
        reqs = self.checker._requirements

        self.assertIn("requests", reqs)
        self.assertEqual(reqs["requests"].version_spec, ">=2.28.0")
        self.assertIn("flask", reqs)
        self.assertEqual(reqs["flask"].version_spec, "==2.3.2")
        self.assertIn("pytest", reqs)
        self.assertIsNone(reqs["pytest"].version_spec)
        self.assertIn("numpy", reqs)
        self.assertEqual(reqs["numpy"].version_spec, "<=1.24.0")
        self.assertIn("rich", reqs)
        self.assertEqual(reqs["rich"].version_spec, ">10.0.0")

    def test_detect_missing_required_packages(self):
        self.checker.add_requirement(Requirement(name="requests", version_spec=">=2.28.0", is_required=True))
        self.checker.add_requirement(Requirement(name="scipy", version_spec=">=1.9.0", is_required=True))

        installed = {"requests": "2.28.1"}
        result = self.checker.validate_installed_packages(installed)

        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["name"], "scipy")
        self.assertEqual(len(result["satisfied"]), 1)
        self.assertEqual(result["satisfied"][0]["name"], "requests")
        self.assertFalse(self.checker.is_environment_ready(result))

    def test_detect_version_mismatch(self):
        self.checker.add_requirement(Requirement(name="flask", version_spec="==2.3.2", is_required=True))
        self.checker.add_requirement(Requirement(name="pydantic", version_spec=">=2.0.0", is_required=True))

        installed = {
            "flask": "2.3.1",
            "pydantic": "2.1.0",
        }
        result = self.checker.validate_installed_packages(installed)

        self.assertEqual(len(result["mismatched"]), 1)
        self.assertEqual(result["mismatched"][0]["name"], "flask")
        self.assertEqual(len(result["satisfied"]), 1)
        self.assertEqual(result["satisfied"][0]["name"], "pydantic")
        self.assertFalse(self.checker.is_environment_ready(result))

    def test_environment_ready_with_optional_missing(self):
        self.checker.add_requirement(Requirement(name="pytest", version_spec=">=7.0.0", is_required=True))
        self.checker.add_requirement(Requirement(name="black", version_spec=">=22.0.0", is_required=False))

        installed = {"pytest": "7.4.0"}
        result = self.checker.validate_installed_packages(installed)

        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["name"], "black")
        self.assertTrue(self.checker.is_environment_ready(result))

    def test_generate_summary_report(self):
        self.checker.add_requirement(Requirement(name="requests", version_spec=">=2.28.0", is_required=True))
        self.checker.add_requirement(Requirement(name="fastapi", version_spec="==0.100.0", is_required=True))
        self.checker.add_requirement(Requirement(name="uvicorn", is_required=False))

        installed = {
            "requests": "2.31.0",
            "fastapi": "0.99.0",
        }
        result = self.checker.validate_installed_packages(installed)
        report = self.checker.generate_summary_report(result)

        self.assertIn("# Requirement Validation Report", report)
        self.assertIn("ACTION REQUIRED", report)
        self.assertIn("Missing Packages", report)
        self.assertIn("Version Mismatches", report)
        self.assertIn("Satisfied Packages", report)
        self.assertIn("requests", report)
        self.assertIn("fastapi", report)
        self.assertIn("uvicorn", report)

    def test_case_and_punctuation_insensitivity(self):
        self.checker.add_requirement(Requirement(name="my_awesome_pkg", version_spec=">=1.0.0"))
        installed = {"my-awesome-pkg": "1.2.0"}
        result = self.checker.validate_installed_packages(installed)

        self.assertEqual(len(result["satisfied"]), 1)
        self.assertEqual(len(result["missing"]), 0)
        self.assertEqual(len(result["mismatched"]), 0)
        self.assertTrue(self.checker.is_environment_ready(result))


if __name__ == "__main__":
    unittest.main()
