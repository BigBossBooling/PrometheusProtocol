import unittest
from unittest.mock import patch # For ensuring sub-methods are called

from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.preanalysis_types import PreanalysisFinding, PreanalysisSeverity
from prometheus_protocol.core.prompt_analyzer import PromptAnalyzer

class TestPromptAnalyzerStubs(unittest.TestCase):

    def setUp(self):
        """Set up a PromptAnalyzer instance before each test."""
        self.analyzer = PromptAnalyzer()
        # Create a generic PromptObject for testing; content doesn't deeply matter for stub tests
        self.dummy_prompt = PromptObject(
            role="Test Role",
            context="Test context for analyzer.",
            task="Test task for analyzer.",
            constraints=["Constraint 1."],
            examples=["Example 1."]
        )
        self.empty_prompt = PromptObject(role="", context="", task="", constraints=[], examples=[])


    def test_analyze_prompt_calls_all_check_methods(self):
        """Test that analyze_prompt calls all individual check methods."""
        with patch.object(self.analyzer, 'check_readability', return_value=[]) as mock_readability,              patch.object(self.analyzer, 'check_constraint_actionability', return_value=[]) as mock_constraint,              patch.object(self.analyzer, 'estimate_input_tokens', return_value=[]) as mock_tokens:

            self.analyzer.analyze_prompt(self.dummy_prompt)

            mock_readability.assert_called_once_with(self.dummy_prompt)
            mock_constraint.assert_called_once_with(self.dummy_prompt)
            mock_tokens.assert_called_once_with(self.dummy_prompt)

    def test_analyze_prompt_aggregates_findings(self):
        """Test that analyze_prompt aggregates findings from all checks."""
        finding1 = PreanalysisFinding("Readability", PreanalysisSeverity.INFO, "Readability OK.")
        finding2 = PreanalysisFinding("Constraint", PreanalysisSeverity.SUGGESTION, "Constraint vague.")
        finding3 = PreanalysisFinding("Tokens", PreanalysisSeverity.INFO, "Tokens: ~50.")

        with patch.object(self.analyzer, 'check_readability', return_value=[finding1]),              patch.object(self.analyzer, 'check_constraint_actionability', return_value=[finding2]),              patch.object(self.analyzer, 'estimate_input_tokens', return_value=[finding3]):

            results = self.analyzer.analyze_prompt(self.dummy_prompt)

            self.assertEqual(len(results), 3)
            self.assertIn(finding1, results)
            self.assertIn(finding2, results)
            self.assertIn(finding3, results)

    def test_analyze_prompt_handles_empty_findings_from_checks(self):
        """Test analyze_prompt when individual checks return empty lists."""
        with patch.object(self.analyzer, 'check_readability', return_value=[]),              patch.object(self.analyzer, 'check_constraint_actionability', return_value=[]),              patch.object(self.analyzer, 'estimate_input_tokens', return_value=[]):

            results = self.analyzer.analyze_prompt(self.dummy_prompt)
            self.assertEqual(len(results), 0)
            self.assertEqual(results, [])

    def test_individual_check_stubs_return_list_of_findings(self):
        """Test that individual stubbed check methods return the expected structure (list of Findings)."""
        # Test one of them, e.g., check_readability, for its direct stub output
        # This also implicitly tests the dummy data generation in the stub.
        readability_findings = self.analyzer.check_readability(self.dummy_prompt)
        self.assertIsInstance(readability_findings, list)
        if readability_findings: # Stubs might return empty if prompt fields are empty
            for finding in readability_findings:
                self.assertIsInstance(finding, PreanalysisFinding)
                self.assertIn(finding.severity, [PreanalysisSeverity.INFO, PreanalysisSeverity.SUGGESTION, PreanalysisSeverity.WARNING])

        # Example for a check that should return something based on default dummy_prompt
        token_findings = self.analyzer.estimate_input_tokens(self.dummy_prompt)
        self.assertIsInstance(token_findings, list)
        self.assertTrue(len(token_findings) >= 1) # estimate_input_tokens stub always returns one
        self.assertIsInstance(token_findings[0], PreanalysisFinding)
        self.assertEqual(token_findings[0].check_name, "InputTokenEstimator")

    def test_analyze_prompt_with_empty_prompt_fields(self):
        """Test how stubs behave with a prompt that has empty fields."""
        # The stubs have some minor logic based on field content (e.g. if prompt.task:)
        # This test ensures it doesn't crash and returns lists.
        readability_findings = self.analyzer.check_readability(self.empty_prompt)
        self.assertIsInstance(readability_findings, list)
        # For empty prompt, check_readability stub might return empty list or specific findings.
        # Based on current stub: it returns empty if task and context are empty.
        self.assertEqual(len(readability_findings), 0)


        constraint_findings = self.analyzer.check_constraint_actionability(self.empty_prompt)
        self.assertIsInstance(constraint_findings, list)
        # Based on current stub: returns empty if no constraints
        self.assertEqual(len(constraint_findings), 0)

        token_findings = self.analyzer.estimate_input_tokens(self.empty_prompt)
        self.assertIsInstance(token_findings, list)
        self.assertTrue(len(token_findings) == 1) # Still estimates tokens (will be low)
        self.assertEqual(token_findings[0].details["estimated_tokens"], 0) # Role is "" etc.

        all_results = self.analyzer.analyze_prompt(self.empty_prompt)
        self.assertIsInstance(all_results, list)
        self.assertEqual(len(all_results), 1) # Only token estimator finding

    def test_analyze_prompt_invalid_input_type(self):
        """Test analyze_prompt with non-PromptObject input (should return empty list)."""
        results = self.analyzer.analyze_prompt(None) # type: ignore
        self.assertEqual(results, [])
        results_str = self.analyzer.analyze_prompt("not a prompt") # type: ignore
        self.assertEqual(results_str, [])


if __name__ == '__main__':
    unittest.main()
