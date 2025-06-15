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
            "constraints": ["Constraint 1", "Constraint 2"], # Unique by default
            "examples": ["Example 1", "Example 2"], # Unique by default
            "tags": ["Tag1", "Tag2"] # Unique by default
        }
        # Ensure that if constraints, examples, or tags are explicitly passed as None,
        # they remain None, otherwise use the defaults.
        for key in ["constraints", "examples", "tags"]:
            if key in kwargs and kwargs[key] is None:
                defaults[key] = None
            elif key not in kwargs: # Use default if not in kwargs
                pass # defaults[key] is already set
            # If key is in kwargs and not None, it will be handled by defaults.update(kwargs)

        defaults.update(kwargs)
        return PromptObject(**defaults)

    def test_valid_prompt(self):
        """Test that a valid PromptObject passes validation."""
        prompt = self.create_valid_prompt_object()
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors, but got: {[str(e) for e in errors]}")

    def test_empty_role(self):
        """Test that an empty role returns a MissingRequiredFieldError."""
        prompt = self.create_valid_prompt_object(role="")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], MissingRequiredFieldError)
        self.assertIn("Role: Must be a non-empty string.", str(errors[0]))

        prompt_whitespace = self.create_valid_prompt_object(role="   ")
        errors_whitespace = validate_prompt(prompt_whitespace)
        self.assertEqual(len(errors_whitespace), 1)
        self.assertIsInstance(errors_whitespace[0], MissingRequiredFieldError)
        self.assertIn("Role: Must be a non-empty string.", str(errors_whitespace[0]))

    def test_empty_task(self):
        """Test that an empty task returns a MissingRequiredFieldError."""
        prompt = self.create_valid_prompt_object(task="")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], MissingRequiredFieldError)
        self.assertIn("Task: Must be a non-empty string.", str(errors[0]))

    def test_empty_context(self):
        """Test that an empty context returns a MissingRequiredFieldError."""
        prompt = self.create_valid_prompt_object(context="")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], MissingRequiredFieldError)
        self.assertIn("Context: Must be a non-empty string.", str(errors[0]))

    def test_constraints_not_a_list(self):
        """Test that non-list constraints returns an InvalidListTypeError."""
        prompt = self.create_valid_prompt_object(constraints="not a list")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListTypeError)
        self.assertIn("Constraints: If provided, must be a list.", str(errors[0]))

    def test_constraints_list_invalid_item_type(self):
        """Test that constraints list with non-string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(constraints=["Valid", 123])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Constraints (Item 2): Must be a non-empty string.", str(errors[0]))

    def test_constraints_list_empty_item(self):
        """Test that constraints list with empty string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(constraints=["Valid", "   "])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Constraints (Item 2): Must be a non-empty string.", str(errors[0]))

    def test_constraints_none(self):
        """Test that constraints can be None and pass validation if other fields are valid."""
        prompt = self.create_valid_prompt_object(constraints=None)
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors for None constraints, but got: {[str(e) for e in errors]}")

    def test_examples_not_a_list(self):
        """Test that non-list examples returns an InvalidListTypeError."""
        prompt = self.create_valid_prompt_object(examples=False)
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListTypeError)
        self.assertIn("Examples: If provided, must be a list.", str(errors[0]))

    def test_examples_list_invalid_item_type(self):
        """Test that examples list with non-string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(examples=["Valid", {"key": "value"}])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Examples (Item 2): Must be a non-empty string.", str(errors[0]))

    def test_examples_list_empty_item(self):
        """Test that examples list with empty string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(examples=["Valid", ""])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Examples (Item 2): Must be a non-empty string.", str(errors[0]))

    def test_examples_none(self):
        """Test that examples can be None and pass validation if other fields are valid."""
        prompt = self.create_valid_prompt_object(examples=None)
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors for None examples, but got: {[str(e) for e in errors]}")

    def test_tags_none(self):
        """Test that tags can be None and pass validation."""
        prompt = self.create_valid_prompt_object(tags=None)
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors for None tags, but got: {[str(e) for e in errors]}")

    def test_tags_empty_list(self):
        """Test that tags can be an empty list and pass validation."""
        prompt = self.create_valid_prompt_object(tags=[])
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors for empty list tags, but got: {[str(e) for e in errors]}")

    def test_tags_valid_list(self):
        """Test that a valid list of non-empty string tags passes validation."""
        prompt = self.create_valid_prompt_object(tags=["valid", "tag"])
        errors = validate_prompt(prompt)
        self.assertEqual(errors, [], f"Expected no errors for valid tags, but got: {[str(e) for e in errors]}")

    def test_tags_not_a_list(self):
        """Test that non-list tags returns an InvalidListTypeError."""
        prompt = self.create_valid_prompt_object(tags="not a list")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListTypeError)
        self.assertIn("Tags: If provided and not empty, must be a list.", str(errors[0]))

    def test_tags_list_invalid_item_type(self):
        """Test that tags list with non-string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(tags=["Valid", 123])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Tags (Item 2): Must be a non-empty string.", str(errors[0]))

    def test_tags_list_empty_item(self):
        """Test that tags list with empty string items returns InvalidListItemError."""
        prompt = self.create_valid_prompt_object(tags=["Valid", "   "])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InvalidListItemError)
        self.assertIn("Tags (Item 2): Must be a non-empty string.", str(errors[0]))

    # --- Tests for Advanced Rule: Unresolved Placeholder Detection ---

    def test_placeholder_in_role(self):
        """Test for placeholder [INSERT_ROLE_HERE] in role."""
        prompt = self.create_valid_prompt_object(role="Act as [INSERT_ROLE_HERE].")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Role: Contains unresolved placeholder text like '[INSERT_ROLE_HERE]'", str(errors[0]))

    def test_placeholder_in_context_curly(self):
        """Test for placeholder {{VARIABLE}} in context."""
        prompt = self.create_valid_prompt_object(context="The current situation is {{VARIABLE}}.")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Context: Contains unresolved placeholder text like '{{VARIABLE}}'", str(errors[0]))

    def test_placeholder_in_task_angle_brackets(self):
        """Test for placeholder <description> in task."""
        prompt = self.create_valid_prompt_object(task="Please describe <description>.")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Task: Contains unresolved placeholder text like '<description>'", str(errors[0]))

    def test_placeholder_your_text_here_in_task(self):
        """Test for 'YOUR_TEXT_HERE' in task."""
        prompt = self.create_valid_prompt_object(task="Please fill in YOUR_TEXT_HERE with details.")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Task: Contains unresolved placeholder text like 'YOUR_TEXT_HERE'", str(errors[0]))

    def test_placeholder_in_constraint_item(self):
        """Test for placeholder [DETAIL] in a constraint item."""
        prompt = self.create_valid_prompt_object(constraints=["Ensure response includes [DETAIL]."])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Constraints (Item 1): Contains unresolved placeholder text like '[DETAIL]'", str(errors[0]))

    def test_placeholder_in_example_item(self):
        """Test for placeholder <EXAMPLE_INPUT> in an example item."""
        prompt = self.create_valid_prompt_object(examples=["User: <EXAMPLE_INPUT> -> AI: Response"])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Examples (Item 1): Contains unresolved placeholder text like '<EXAMPLE_INPUT>'", str(errors[0]))

    def test_placeholder_case_insensitive(self):
        """Test placeholder detection is case-insensitive."""
        prompt = self.create_valid_prompt_object(task="Summarize [insert_topic].")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], UnresolvedPlaceholderError)
        self.assertIn("Task: Contains unresolved placeholder text like '[insert_topic]'", str(errors[0]))

    def test_no_placeholders_no_error(self):
        """Test a prompt with no placeholders passes this check when other fields are valid."""
        prompt = self.create_valid_prompt_object(
            role="A specific role.",
            context="A specific context.",
            task="A specific task.",
            constraints=["A specific constraint."],
            examples=["A specific example."]
        )
        errors = validate_prompt(prompt)
        # This test assumes that the default create_valid_prompt_object doesn't have other errors.
        # We are primarily checking that *no placeholder errors* are added.
        has_placeholder_error = any(isinstance(e, UnresolvedPlaceholderError) for e in errors)
        self.assertFalse(has_placeholder_error, "validate_prompt() raised UnresolvedPlaceholderError unexpectedly!")


    # --- Tests for Advanced Rule: Repetitive List Items ---

    def test_repetitive_constraints_exact_duplicate(self):
        """Test for exact duplicate constraints."""
        prompt = self.create_valid_prompt_object(constraints=["Be concise.", "Be concise."])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RepetitiveListItemError)
        self.assertIn("Constraints (Item 2): Duplicate or very similar item found: 'Be concise.'", str(errors[0]))

    def test_repetitive_constraints_case_insensitive_whitespace(self):
        """Test for duplicate constraints ignoring case and whitespace."""
        prompt = self.create_valid_prompt_object(constraints=["Be Concise", "be concise  "])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RepetitiveListItemError)
        self.assertIn("Constraints (Item 2): Duplicate or very similar item found: 'be concise  '", str(errors[0]))

    def test_repetitive_constraints_among_others(self):
        """Test for duplicate constraints when other unique constraints exist."""
        prompt = self.create_valid_prompt_object(constraints=["Be clear.", "Be brief.", "be brief."])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RepetitiveListItemError)
        self.assertIn("Constraints (Item 3): Duplicate or very similar item found: 'be brief.'", str(errors[0]))

    def test_no_repetitive_constraints(self):
        """Test with unique constraints passes this check when other fields are valid."""
        prompt = self.create_valid_prompt_object(constraints=["Be concise.", "Be clear."])
        errors = validate_prompt(prompt)
        has_repetitive_error = any(isinstance(e, RepetitiveListItemError) and "Constraints" in str(e) for e in errors)
        self.assertFalse(has_repetitive_error, "validate_prompt() raised RepetitiveListItemError unexpectedly for constraints!")

    def test_repetitive_examples_exact_duplicate(self):
        """Test for exact duplicate examples."""
        prompt = self.create_valid_prompt_object(examples=["User: Hi -> AI: Hello", "User: Hi -> AI: Hello"])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RepetitiveListItemError)
        self.assertIn("Examples (Item 2): Duplicate or very similar item found: 'User: Hi -> AI: Hello'", str(errors[0]))

    def test_repetitive_examples_normalized_duplicate(self):
        """Test for normalized duplicate examples."""
        prompt = self.create_valid_prompt_object(examples=["User: Bye -> AI: Goodbye", "user: bye -> ai: goodbye  "])
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RepetitiveListItemError)
        self.assertIn("Examples (Item 2): Duplicate or very similar item found: 'user: bye -> ai: goodbye  '", str(errors[0]))

    def test_no_repetitive_examples(self):
        """Test with unique examples passes this check when other fields are valid."""
        prompt = self.create_valid_prompt_object(examples=["User: Hi -> AI: Hello", "User: Bye -> AI: Goodbye"])
        errors = validate_prompt(prompt)
        has_repetitive_error = any(isinstance(e, RepetitiveListItemError) and "Examples" in str(e) for e in errors)
        self.assertFalse(has_repetitive_error, "validate_prompt() raised RepetitiveListItemError unexpectedly for examples!")

    def test_empty_or_single_item_lists_no_repetition_error(self):
        """Test that empty or single-item lists do not trigger repetition errors."""
        prompts_to_check = [
            self.create_valid_prompt_object(constraints=[]),
            self.create_valid_prompt_object(constraints=["One constraint."]),
            self.create_valid_prompt_object(examples=[]),
            self.create_valid_prompt_object(examples=["One example."])
        ]
        for prompt in prompts_to_check:
            errors = validate_prompt(prompt)
            has_repetitive_error = any(isinstance(e, RepetitiveListItemError) for e in errors)
            self.assertFalse(has_repetitive_error,
                             f"validate_prompt() raised RepetitiveListItemError unexpectedly for {prompt=}")

    # --- New tests for multiple error detection ---

    def test_multiple_basic_errors_detected(self):
        """Test that multiple basic GIGO errors are detected and returned."""
        prompt = self.create_valid_prompt_object(role="", task="", context="Valid context")
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any(isinstance(e, MissingRequiredFieldError) and "Role:" in str(e) for e in errors))
        self.assertTrue(any(isinstance(e, MissingRequiredFieldError) and "Task:" in str(e) for e in errors))

    def test_multiple_advanced_errors_detected(self):
        """Test that multiple advanced GIGO errors are detected."""
        prompt = self.create_valid_prompt_object(
            task="Explain [CONCEPT]", # Placeholder
            constraints=["Be brief.", "Be brief.", "Then expand on <DETAIL>"] # Repetitive + Placeholder
        )
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 3)
        self.assertTrue(any(isinstance(e, UnresolvedPlaceholderError) and "Task:" in str(e) and "[CONCEPT]" in str(e) for e in errors))
        self.assertTrue(any(isinstance(e, RepetitiveListItemError) and "Constraints (Item 2):" in str(e) and "Be brief." in str(e) for e in errors))
        self.assertTrue(any(isinstance(e, UnresolvedPlaceholderError) and "Constraints (Item 3):" in str(e) and "<DETAIL>" in str(e) for e in errors))

    def test_mixed_basic_and_advanced_errors_detected(self):
        """Test detection of both basic and advanced errors simultaneously."""
        prompt = self.create_valid_prompt_object(
            role="", # Basic error
            task="Do <THING>", # Advanced error (placeholder)
            constraints=["Repeat", "Repeat", ""], # Advanced error (repetitive) + Basic error (empty item)
            examples=[123, "Valid example"] # Basic error (invalid type)
        )
        errors = validate_prompt(prompt)
        self.assertEqual(len(errors), 4) # role, task placeholder, constraint repetitive, constraint empty, example type

        # Check for specific errors - order might not be guaranteed, so check for presence
        found_role_error = any(isinstance(e, MissingRequiredFieldError) and "Role:" in str(e) for e in errors)
        found_task_placeholder_error = any(isinstance(e, UnresolvedPlaceholderError) and "Task:" in str(e) and "<THING>" in str(e) for e in errors)
        found_constraint_repetitive_error = any(isinstance(e, RepetitiveListItemError) and "Constraints (Item 2):" in str(e) and "Repeat" in str(e) for e in errors)
        # The empty constraint "" is Item 3
        found_constraint_empty_item_error = any(isinstance(e, InvalidListItemError) and "Constraints (Item 3):" in str(e) for e in errors)
        # Example error is now only one because the loop for list items stops if the list itself is not of the correct type,
        # but here we are checking individual items.
        # The previous change made the InvalidListItemError check happen inside an else block
        # if not isinstance(prompt.examples, List):
        #    errors_found.append(InvalidListTypeError("Examples: If provided, must be a list."))
        # else:  <-- this part
        #    for i, item in enumerate(prompt.examples):
        #        if not isinstance(item, str) or not item.strip():
        #            errors_found.append(InvalidListItemError(f"Examples (Item {i+1}): Must be a non-empty string."))
        # So if examples is [123, "Valid example"], it will find one error for item 123.
        # The original test_examples_list_invalid_item_type() was correct.

        # Let's re-evaluate the count for the mixed test.
        # 1. Role empty (MissingRequiredFieldError)
        # 2. Task placeholder (UnresolvedPlaceholderError)
        # 3. Constraint "Repeat" (Item 2) is repetitive (RepetitiveListItemError)
        # 4. Constraint "" (Item 3) is empty (InvalidListItemError)
        # 5. Example 123 (Item 1) is not string (InvalidListItemError)
        # So, 5 errors.

        # Re-checking the prompt for test_mixed_basic_and_advanced_errors_detected
        # role="",                                                           -> 1. MissingRequiredFieldError (Role)
        # task="Do <THING>",                                                 -> 2. UnresolvedPlaceholderError (Task)
        # constraints=["Repeat", "Repeat", ""],                              -> 3. RepetitiveListItemError (Constraints Item 2: "Repeat")
        #                                                                    -> 4. InvalidListItemError (Constraints Item 3: "")
        # examples=[123, "Valid example"]                                    -> 5. InvalidListItemError (Examples Item 1: 123)
        # Total = 5 errors.

        self.assertEqual(len(errors), 5, f"Expected 5 errors, got {len(errors)}: {[str(e) for e in errors]}")

        self.assertTrue(found_role_error, "Missing Role error not found.")
        self.assertTrue(found_task_placeholder_error, "Task Placeholder error not found.")
        self.assertTrue(found_constraint_repetitive_error, "Constraint Repetitive error not found.")
        self.assertTrue(found_constraint_empty_item_error, "Constraint Empty Item error not found.")

        found_example_type_error = any(isinstance(e, InvalidListItemError) and "Examples (Item 1):" in str(e) for e in errors)
        self.assertTrue(found_example_type_error, "Example Type error not found.")

if __name__ == '__main__':
    unittest.main()
