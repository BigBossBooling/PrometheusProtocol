import unittest
from prometheus_protocol.core.preanalysis_types import PreanalysisSeverity, PreanalysisFinding

class TestPreanalysisTypes(unittest.TestCase):

    def test_preanalysis_severity_enum_values(self):
        """Test the values and types of PreanalysisSeverity enum members."""
        self.assertEqual(PreanalysisSeverity.INFO.value, "Info")
        self.assertEqual(PreanalysisSeverity.SUGGESTION.value, "Suggestion")
        self.assertEqual(PreanalysisSeverity.WARNING.value, "Warning")

        self.assertIsInstance(PreanalysisSeverity.INFO, PreanalysisSeverity)
        self.assertIsInstance(PreanalysisSeverity.INFO.value, str)

    def test_preanalysis_finding_instantiation_defaults(self):
        """Test PreanalysisFinding instantiation with minimal required fields."""
        finding = PreanalysisFinding(
            check_name="TestCheck_Minimal",
            severity=PreanalysisSeverity.INFO,
            message="This is a minimal test message."
        )
        self.assertEqual(finding.check_name, "TestCheck_Minimal")
        self.assertEqual(finding.severity, PreanalysisSeverity.INFO)
        self.assertEqual(finding.message, "This is a minimal test message.")
        self.assertIsNone(finding.details)
        self.assertIsNone(finding.ui_target_field)

    def test_preanalysis_finding_instantiation_all_fields(self):
        """Test PreanalysisFinding instantiation with all fields provided."""
        details_dict = {"score": 80, "notes": "Further details here"}
        finding = PreanalysisFinding(
            check_name="TestCheck_Full",
            severity=PreanalysisSeverity.WARNING,
            message="This is a full test message with all fields.",
            details=details_dict,
            ui_target_field="task.constraints[0]"
        )
        self.assertEqual(finding.check_name, "TestCheck_Full")
        self.assertEqual(finding.severity, PreanalysisSeverity.WARNING)
        self.assertEqual(finding.message, "This is a full test message with all fields.")
        self.assertEqual(finding.details, details_dict)
        self.assertEqual(finding.ui_target_field, "task.constraints[0]")

    def test_preanalysis_finding_post_init_severity_conversion(self):
        """Test __post_init__ converts string severity to enum (if applicable for direct instantiation)."""
        # Note: from_dict is the primary path for string->enum conversion during deserialization.
        # The __post_init__ in the dataclass was a more direct instantiation helper.
        finding_str_sev = PreanalysisFinding(
            check_name="TestCheck_StrSev",
            severity="Warning", # Pass as string
            message="Test message with string severity."
        )
        self.assertIsInstance(finding_str_sev.severity, PreanalysisSeverity)
        self.assertEqual(finding_str_sev.severity, PreanalysisSeverity.WARNING)

    def test_preanalysis_finding_to_dict(self):
        """Test serialization of PreanalysisFinding to dictionary."""
        details_dict = {"key": "value"}
        finding = PreanalysisFinding(
            check_name="ToCheck",
            severity=PreanalysisSeverity.SUGGESTION,
            message="To message",
            details=details_dict,
            ui_target_field="context"
        )
        finding_dict = finding.to_dict()
        expected_dict = {
            "check_name": "ToCheck",
            "severity": "Suggestion", # Enum value is serialized
            "message": "To message",
            "details": details_dict,
            "ui_target_field": "context"
        }
        self.assertEqual(finding_dict, expected_dict)

    def test_preanalysis_finding_to_dict_with_nones(self):
        """Test to_dict when optional fields are None."""
        finding = PreanalysisFinding(
            check_name="ToCheckNone",
            severity=PreanalysisSeverity.INFO,
            message="Message for None test"
            # details and ui_target_field are None by default
        )
        finding_dict = finding.to_dict()
        expected_dict = {
            "check_name": "ToCheckNone",
            "severity": "Info",
            "message": "Message for None test",
            "details": None,
            "ui_target_field": None
        }
        self.assertEqual(finding_dict, expected_dict)

    def test_preanalysis_finding_from_dict_full(self):
        """Test deserialization of PreanalysisFinding from a full dictionary."""
        details_dict = {"score": 90}
        data = {
            "check_name": "FromCheck",
            "severity": "Info", # Pass as string value, as it would be in JSON
            "message": "From message",
            "details": details_dict,
            "ui_target_field": "task"
        }
        finding = PreanalysisFinding.from_dict(data)
        self.assertEqual(finding.check_name, "FromCheck")
        self.assertEqual(finding.severity, PreanalysisSeverity.INFO)
        self.assertEqual(finding.message, "From message")
        self.assertEqual(finding.details, details_dict)
        self.assertEqual(finding.ui_target_field, "task")

    def test_preanalysis_finding_from_dict_minimal(self):
        """Test from_dict with only required fields (details and ui_target_field missing)."""
        data = {
            "check_name": "FromCheckMin",
            "severity": "Warning",
            "message": "Minimal message from dict"
        }
        finding = PreanalysisFinding.from_dict(data)
        self.assertEqual(finding.check_name, "FromCheckMin")
        self.assertEqual(finding.severity, PreanalysisSeverity.WARNING)
        self.assertEqual(finding.message, "Minimal message from dict")
        self.assertIsNone(finding.details)
        self.assertIsNone(finding.ui_target_field)

    def test_preanalysis_finding_from_dict_invalid_severity(self):
        """Test from_dict raises ValueError for an invalid severity string."""
        data = {
            "check_name": "InvalidSevCheck",
            "severity": "SuperCritical", # Not a valid PreanalysisSeverity value
            "message": "Test invalid severity"
        }
        with self.assertRaisesRegex(ValueError, "Invalid severity value: SuperCritical"):
            PreanalysisFinding.from_dict(data)

    def test_preanalysis_finding_from_dict_missing_required_field(self):
        """Test from_dict raises ValueError if a required field is missing."""
        data_no_message = {"check_name": "NoMsg", "severity": "Info"}
        with self.assertRaisesRegex(ValueError, "Missing required fields for PreanalysisFinding: 'check_name', 'severity', 'message'"):
            PreanalysisFinding.from_dict(data_no_message) # 'message' is missing

    def test_preanalysis_finding_str_representation(self):
        """Test the __str__ representation of PreanalysisFinding."""
        finding = PreanalysisFinding(
            check_name="TestStrFormat",
            severity=PreanalysisSeverity.SUGGESTION,
            message="This is a test of str format."
        )
        self.assertEqual(str(finding), "[Suggestion] TestStrFormat: This is a test of str format.")

if __name__ == '__main__':
    unittest.main()
