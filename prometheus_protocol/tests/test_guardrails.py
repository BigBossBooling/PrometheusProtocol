import unittest
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.guardrails import validate_prompt
from prometheus_protocol.core.exceptions import (
    MissingRequiredFieldError,
    InvalidListTypeError,
    InvalidListItemError,
    PromptValidationError
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
