import unittest
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.guardrails import validate_prompt
from prometheus_protocol.core.exceptions import (
    MissingRequiredFieldError,
    InvalidListTypeError,
    InvalidListItemError,
    PromptValidationError,
    UnresolvedPlaceholderError,
    RepetitiveListItemError
)

class TestGuardrails(unittest.TestCase):

    def create_valid_prompt_object(self, **kwargs):
        """Helper method to create a valid PromptObject with default values."""
        defaults = {
            "role": "Test Role",
            "task": "Test Task",
            "context": "Test Context",
            "constraints": ["Constraint 1", "Constraint 2"],
            "examples": ["Example 1", "Example 2"]
        }
        defaults.update(kwargs)
        return PromptObject(**defaults)

    def test_valid_prompt(self):
        """Test that a valid PromptObject passes validation."""
        prompt = self.create_valid_prompt_object()
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly!")

    def test_empty_role(self):
        """Test that an empty role raises MissingRequiredFieldError."""
        with self.assertRaisesRegex(MissingRequiredFieldError, "Role must be a non-empty string."):
            prompt = self.create_valid_prompt_object(role="")
            validate_prompt(prompt)
        with self.assertRaisesRegex(MissingRequiredFieldError, "Role must be a non-empty string."):
            prompt = self.create_valid_prompt_object(role="   ")
            validate_prompt(prompt)

    def test_empty_task(self):
        """Test that an empty task raises MissingRequiredFieldError."""
        with self.assertRaisesRegex(MissingRequiredFieldError, "Task must be a non-empty string."):
            prompt = self.create_valid_prompt_object(task="")
            validate_prompt(prompt)

    def test_empty_context(self):
        """Test that an empty context raises MissingRequiredFieldError."""
        with self.assertRaisesRegex(MissingRequiredFieldError, "Context must be a non-empty string."):
            prompt = self.create_valid_prompt_object(context="")
            validate_prompt(prompt)

    def test_constraints_not_a_list(self):
        """Test that non-list constraints raise InvalidListTypeError."""
        with self.assertRaisesRegex(InvalidListTypeError, "Constraints, if provided, must be a list."):
            prompt = self.create_valid_prompt_object(constraints="not a list")
            validate_prompt(prompt)

    def test_constraints_list_invalid_item_type(self):
        """Test that constraints list with non-string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each constraint must be a non-empty string."):
            prompt = self.create_valid_prompt_object(constraints=["Valid", 123])
            validate_prompt(prompt)

    def test_constraints_list_empty_item(self):
        """Test that constraints list with empty string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each constraint must be a non-empty string."):
            prompt = self.create_valid_prompt_object(constraints=["Valid", "   "])
            validate_prompt(prompt)

    def test_constraints_none(self):
        """Test that constraints can be None and pass validation if other fields are valid."""
        prompt = self.create_valid_prompt_object(constraints=None)
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly for None constraints!")


    def test_examples_not_a_list(self):
        """Test that non-list examples raise InvalidListTypeError."""
        with self.assertRaisesRegex(InvalidListTypeError, "Examples, if provided, must be a list."):
            prompt = self.create_valid_prompt_object(examples=False) # Using boolean as an example of wrong type
            validate_prompt(prompt)

    def test_examples_list_invalid_item_type(self):
        """Test that examples list with non-string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each example must be a non-empty string."):
            prompt = self.create_valid_prompt_object(examples=["Valid", {"key": "value"}])
            validate_prompt(prompt)

    def test_examples_list_empty_item(self):
        """Test that examples list with empty string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each example must be a non-empty string."):
            prompt = self.create_valid_prompt_object(examples=["Valid", ""])
            validate_prompt(prompt)

    def test_examples_none(self):
        """Test that examples can be None and pass validation if other fields are valid."""
        prompt = self.create_valid_prompt_object(examples=None)
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly for None examples!")

    # Tests for tags
    def test_tags_none(self):
        """Test that tags can be None and pass validation."""
        prompt = self.create_valid_prompt_object(tags=None)
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly for None tags!")

    def test_tags_empty_list(self):
        """Test that tags can be an empty list and pass validation."""
        prompt = self.create_valid_prompt_object(tags=[])
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly for empty list tags!")

    def test_tags_valid_list(self):
        """Test that a valid list of non-empty string tags passes validation."""
        prompt = self.create_valid_prompt_object(tags=["valid", "tag"])
        try:
            validate_prompt(prompt)
        except PromptValidationError:
            self.fail("validate_prompt() raised PromptValidationError unexpectedly for valid tags!")

    # --- Tests for Advanced Rule: Unresolved Placeholder Detection ---

    def test_placeholder_in_role(self):
        """Test for placeholder [INSERT_ROLE_HERE] in role."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Role: Contains unresolved placeholder text like '\[INSERT_ROLE_HERE\]'"):
            prompt = self.create_valid_prompt_object(role="Act as [INSERT_ROLE_HERE].")
            validate_prompt(prompt)

    def test_placeholder_in_context_curly(self):
        """Test for placeholder {{VARIABLE}} in context."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Context: Contains unresolved placeholder text like '\{\{VARIABLE\}\}'"):
            prompt = self.create_valid_prompt_object(context="The current situation is {{VARIABLE}}.")
            validate_prompt(prompt)

    def test_placeholder_in_task_angle_brackets(self):
        """Test for placeholder <description> in task."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Task: Contains unresolved placeholder text like '<description>'"):
            prompt = self.create_valid_prompt_object(task="Please describe <description>.")
            validate_prompt(prompt)

    def test_placeholder_your_text_here_in_task(self):
        """Test for 'YOUR_TEXT_HERE' in task."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Task: Contains unresolved placeholder text like 'YOUR_TEXT_HERE'"):
            prompt = self.create_valid_prompt_object(task="Please fill in YOUR_TEXT_HERE with details.")
            validate_prompt(prompt)

    def test_placeholder_in_constraint_item(self):
        """Test for placeholder [DETAIL] in a constraint item."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Constraints \(Item 1\): Contains unresolved placeholder text like '\[DETAIL\]'"):
            prompt = self.create_valid_prompt_object(constraints=["Ensure response includes [DETAIL]."])
            validate_prompt(prompt)

    def test_placeholder_in_example_item(self):
        """Test for placeholder <EXAMPLE_INPUT> in an example item."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Examples \(Item 1\): Contains unresolved placeholder text like '<EXAMPLE_INPUT>'"):
            prompt = self.create_valid_prompt_object(examples=["User: <EXAMPLE_INPUT> -> AI: Response"])
            validate_prompt(prompt)

    def test_placeholder_case_insensitive(self):
        """Test placeholder detection is case-insensitive."""
        with self.assertRaisesRegex(UnresolvedPlaceholderError, "Task: Contains unresolved placeholder text like '[insert_topic]'"):
            prompt = self.create_valid_prompt_object(task="Summarize [insert_topic].")
            validate_prompt(prompt)

    def test_no_placeholders_no_error(self):
        """Test a prompt with no placeholders passes this check."""
        prompt = self.create_valid_prompt_object(
            role="A specific role.",
            context="A specific context.",
            task="A specific task.",
            constraints=["A specific constraint."],
            examples=["A specific example."]
        )
        try:
            validate_prompt(prompt)
        except UnresolvedPlaceholderError:
            self.fail("validate_prompt() raised UnresolvedPlaceholderError unexpectedly!")

    # --- Tests for Advanced Rule: Repetitive List Items ---

    def test_repetitive_constraints_exact_duplicate(self):
        """Test for exact duplicate constraints."""
        with self.assertRaisesRegex(RepetitiveListItemError, "Constraints: Duplicate or very similar item found: 'Be concise.'"):
            prompt = self.create_valid_prompt_object(constraints=["Be concise.", "Be concise."])
            validate_prompt(prompt)

    def test_repetitive_constraints_case_insensitive_whitespace(self):
        """Test for duplicate constraints ignoring case and whitespace."""
        with self.assertRaisesRegex(RepetitiveListItemError, "Constraints: Duplicate or very similar item found: 'be concise  '"):
            prompt = self.create_valid_prompt_object(constraints=["Be Concise", "be concise  "])
            validate_prompt(prompt)

    def test_repetitive_constraints_among_others(self):
        """Test for duplicate constraints when other unique constraints exist."""
        with self.assertRaisesRegex(RepetitiveListItemError, "Constraints: Duplicate or very similar item found: 'be brief.'"):
            prompt = self.create_valid_prompt_object(constraints=["Be clear.", "Be brief.", "be brief."])
            validate_prompt(prompt)


    def test_no_repetitive_constraints(self):
        """Test with unique constraints passes this check."""
        prompt = self.create_valid_prompt_object(constraints=["Be concise.", "Be clear."])
        try:
            validate_prompt(prompt)
        except RepetitiveListItemError:
            self.fail("validate_prompt() raised RepetitiveListItemError unexpectedly for constraints!")

    def test_repetitive_examples_exact_duplicate(self):
        """Test for exact duplicate examples."""
        with self.assertRaisesRegex(RepetitiveListItemError, "Examples: Duplicate or very similar item found: 'User: Hi -> AI: Hello'"):
            prompt = self.create_valid_prompt_object(examples=["User: Hi -> AI: Hello", "User: Hi -> AI: Hello"])
            validate_prompt(prompt)

    def test_repetitive_examples_normalized_duplicate(self):
        """Test for normalized duplicate examples."""
        with self.assertRaisesRegex(RepetitiveListItemError, "Examples: Duplicate or very similar item found: 'user: bye -> ai: goodbye  '"):
            prompt = self.create_valid_prompt_object(examples=["User: Bye -> AI: Goodbye", "user: bye -> ai: goodbye  "])
            validate_prompt(prompt)

    def test_no_repetitive_examples(self):
        """Test with unique examples passes this check."""
        prompt = self.create_valid_prompt_object(examples=["User: Hi -> AI: Hello", "User: Bye -> AI: Goodbye"])
        try:
            validate_prompt(prompt)
        except RepetitiveListItemError:
            self.fail("validate_prompt() raised RepetitiveListItemError unexpectedly for examples!")

    def test_empty_or_single_item_lists_no_repetition_error(self):
        """Test that empty or single-item lists do not trigger repetition errors."""
        prompt_empty_constraints = self.create_valid_prompt_object(constraints=[])
        prompt_single_constraint = self.create_valid_prompt_object(constraints=["One constraint."])
        prompt_empty_examples = self.create_valid_prompt_object(examples=[])
        prompt_single_example = self.create_valid_prompt_object(examples=["One example."])
        try:
            validate_prompt(prompt_empty_constraints)
            validate_prompt(prompt_single_constraint)
            validate_prompt(prompt_empty_examples)
            validate_prompt(prompt_single_example)
        except RepetitiveListItemError:
            self.fail("validate_prompt() raised RepetitiveListItemError unexpectedly for empty/single item lists!")

    def test_tags_not_a_list(self):
        """Test that non-list tags raise InvalidListTypeError."""
        with self.assertRaisesRegex(InvalidListTypeError, "Tags, if provided, must be a list."):
            prompt = self.create_valid_prompt_object(tags="not a list")
            validate_prompt(prompt)

    def test_tags_list_invalid_item_type(self):
        """Test that tags list with non-string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each tag must be a non-empty string."):
            prompt = self.create_valid_prompt_object(tags=["Valid", 123])
            validate_prompt(prompt)

    def test_tags_list_empty_item(self):
        """Test that tags list with empty string items raises InvalidListItemError."""
        with self.assertRaisesRegex(InvalidListItemError, "Each tag must be a non-empty string."):
            prompt = self.create_valid_prompt_object(tags=["Valid", "   "])
            validate_prompt(prompt)

if __name__ == '__main__':
    unittest.main()
