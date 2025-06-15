import unittest
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.risk_identifier import RiskIdentifier
from prometheus_protocol.core.risk_types import PotentialRisk, RiskLevel, RiskType

class TestRiskIdentifier(unittest.TestCase):

    def setUp(self):
        """Set up a RiskIdentifier instance before each test."""
        self.identifier = RiskIdentifier()

    def create_prompt(self, task="Default task", context="Default context", constraints=None, examples=None, tags=None):
        """Helper to create PromptObject instances for testing."""
        # Ensure constraints, examples, and tags are lists if None (as PromptObject expects)
        # PromptObject's __init__ handles None for prompt_id, version, created_at, last_modified_at, and tags (defaults to [])
        # but it expects role, context, task, constraints, examples.
        # For simplicity in these tests, we'll focus on fields relevant to risk identification.
        return PromptObject(
            role="Test Role", # Add a default role
            task=task,
            context=context,
            constraints=constraints if constraints is not None else [],
            examples=examples if examples is not None else [],
            tags=tags # PromptObject handles None for tags by defaulting to []
        )

    # --- Tests for Rule 1: Lack of Specificity in Task ---
    def test_lack_of_specificity_triggered(self):
        """Task is short and no constraints."""
        prompt = self.create_prompt(task="Do it", constraints=[])
        risks = self.identifier.identify_risks(prompt)
        self.assertTrue(any(r.risk_type == RiskType.LACK_OF_SPECIFICITY and r.risk_level == RiskLevel.WARNING for r in risks))

    def test_lack_of_specificity_long_task_not_triggered(self):
        """Task is long, no constraints - should not trigger this specific rule."""
        prompt = self.create_prompt(task="Do this very specific thing now please", constraints=[])
        risks = self.identifier.identify_risks(prompt)
        self.assertFalse(any(r.risk_type == RiskType.LACK_OF_SPECIFICITY for r in risks))

    def test_lack_of_specificity_short_task_with_constraints_not_triggered(self):
        """Task is short, but has constraints - should not trigger."""
        prompt = self.create_prompt(task="Do it", constraints=["Under 10 words."])
        risks = self.identifier.identify_risks(prompt)
        self.assertFalse(any(r.risk_type == RiskType.LACK_OF_SPECIFICITY for r in risks))

    # --- Tests for Rule 2: Keyword Watch ---
    def test_keyword_watch_financial_triggered_in_task(self):
        """Financial keyword in task."""
        prompt = self.create_prompt(task="Give me stock tips.")
        risks = self.identifier.identify_risks(prompt)
        self.assertTrue(any(
            r.risk_type == RiskType.KEYWORD_WATCH and
            r.risk_level == RiskLevel.INFO and
            "sensitive_financial_advice" in r.details.get("category", "")
            for r in risks
        ))

    def test_keyword_watch_medical_triggered_in_context(self):
        """Medical keyword in context."""
        prompt = self.create_prompt(context="The patient shows symptoms of flu, what is the diagnosis?")
        risks = self.identifier.identify_risks(prompt)
        self.assertTrue(any(
            r.risk_type == RiskType.KEYWORD_WATCH and
            r.risk_level == RiskLevel.INFO and
            "sensitive_medical_advice" in r.details.get("category", "")
            for r in risks
        ))

    def test_keyword_watch_multiple_keywords_same_category_one_warning(self):
        """Multiple keywords from same category, should only trigger one warning for that category."""
        prompt = self.create_prompt(task="What stock tips for investment?")
        risks = self.identifier.identify_risks(prompt)
        financial_warnings = [r for r in risks if r.risk_type == RiskType.KEYWORD_WATCH and r.details.get("category") == "sensitive_financial_advice"]
        self.assertEqual(len(financial_warnings), 1)

    def test_keyword_watch_no_keywords_not_triggered(self):
        """No watched keywords present."""
        prompt = self.create_prompt(task="Write a poem about a tree.")
        risks = self.identifier.identify_risks(prompt)
        self.assertFalse(any(r.risk_type == RiskType.KEYWORD_WATCH for r in risks))

    # --- Tests for Rule 3: Potentially Unconstrained Complex Task ---
    def test_unconstrained_complex_task_triggered(self):
        """Complex task indicator with few constraints."""
        prompt = self.create_prompt(task="Write a detailed report on climate change.", constraints=["Be factual."])
        risks = self.identifier.identify_risks(prompt)
        self.assertTrue(any(r.risk_type == RiskType.UNCONSTRAINED_GENERATION and r.risk_level == RiskLevel.WARNING for r in risks))

    def test_unconstrained_complex_task_not_triggered_simple_task(self):
        """Simple task, few constraints - should not trigger."""
        prompt = self.create_prompt(task="Summarize this text.", constraints=[])
        risks = self.identifier.identify_risks(prompt)
        self.assertFalse(any(r.risk_type == RiskType.UNCONSTRAINED_GENERATION for r in risks))

    def test_unconstrained_complex_task_not_triggered_many_constraints(self):
        """Complex task, but many constraints - should not trigger."""
        prompt = self.create_prompt(
            task="Create a comprehensive plan for marketing.",
            constraints=["Target audience: young adults.", "Budget: $10k.", "Timeline: 3 months."]
        )
        risks = self.identifier.identify_risks(prompt)
        self.assertFalse(any(r.risk_type == RiskType.UNCONSTRAINED_GENERATION for r in risks))

    # --- Test for Multiple Risks ---
    def test_multiple_risks_triggered(self):
        """Prompt that should trigger multiple types of risks."""
        prompt = self.create_prompt(
            task="Give investment advice.", # Triggers KeywordWatch, LackOfSpecificity
            constraints=[]
        )
        risks = self.identifier.identify_risks(prompt)
        risk_types_found = {r.risk_type for r in risks}
        self.assertIn(RiskType.LACK_OF_SPECIFICITY, risk_types_found)
        self.assertIn(RiskType.KEYWORD_WATCH, risk_types_found)
        # Check details for keyword watch
        self.assertTrue(any("sensitive_financial_advice" in r.details.get("category", "") for r in risks if r.risk_type == RiskType.KEYWORD_WATCH))


    # --- Test for No Risks ---
    def test_no_risks_triggered(self):
        """A well-formed prompt that should trigger no risks from current ruleset."""
        prompt = self.create_prompt(
            task="Explain the concept of photosynthesis in simple terms.",
            context="For a middle school science class.",
            constraints=["Use analogies.", "Keep it under 150 words.", "Ensure it's scientifically accurate."],
            examples=["Example: Water + Sunlight -> Energy for plant"]
        )
        risks = self.identifier.identify_risks(prompt)
        self.assertEqual(len(risks), 0, f"Expected no risks, but found: {[str(r) for r in risks]}")

if __name__ == '__main__':
    unittest.main()
