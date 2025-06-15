import re # For placeholder regex
from typing import List
from .prompt import PromptObject
from .exceptions import (
    MissingRequiredFieldError,
    InvalidListTypeError,
    InvalidListItemError,
    UnresolvedPlaceholderError, # New
    RepetitiveListItemError    # New
)

def validate_prompt(prompt: PromptObject) -> List[PromptValidationError]:
    """
    Validates a PromptObject to ensure it meets basic quality criteria.

    Returns:
        List[PromptValidationError]: A list of validation errors found.
                                     An empty list signifies that the prompt is valid.
    """
    errors_found: List[PromptValidationError] = []

    if not prompt.role or not prompt.role.strip():
        errors_found.append(MissingRequiredFieldError("Role: Must be a non-empty string."))

    if not prompt.task or not prompt.task.strip():
        errors_found.append(MissingRequiredFieldError("Task: Must be a non-empty string."))

    if not prompt.context or not prompt.context.strip():
        errors_found.append(MissingRequiredFieldError("Context: Must be a non-empty string."))

    if prompt.constraints is not None:
        if not isinstance(prompt.constraints, List):
            errors_found.append(InvalidListTypeError("Constraints: If provided, must be a list."))
        else:
            for i, item in enumerate(prompt.constraints):
                if not isinstance(item, str) or not item.strip():
                    errors_found.append(InvalidListItemError(f"Constraints (Item {i+1}): Must be a non-empty string."))

    if prompt.examples is not None:
        if not isinstance(prompt.examples, List):
            errors_found.append(InvalidListTypeError("Examples: If provided, must be a list."))
        else:
            for i, item in enumerate(prompt.examples):
                if not isinstance(item, str) or not item.strip():
                    errors_found.append(InvalidListItemError(f"Examples (Item {i+1}): Must be a non-empty string."))

    if prompt.tags is not None and prompt.tags: # Check if tags is provided and not an empty list
        if not isinstance(prompt.tags, List):
            errors_found.append(InvalidListTypeError("Tags: If provided and not empty, must be a list."))
        else:
            for i, item in enumerate(prompt.tags):
                if not isinstance(item, str) or not item.strip():
                    errors_found.append(InvalidListItemError(f"Tags (Item {i+1}): Must be a non-empty string."))

    # --- Advanced GIGO Rules ---

    # Rule 1: Unresolved Placeholder Detection
    placeholder_patterns = [
        r'\[INSERT[^]]*?\]',    # Matches [INSERT...], [INSERT_SOMETHING_HERE]
        r'\{\{[^}]*?\}\}',      # Matches {{VARIABLE}}, {{ANY_THING}}
        r'<[^>]*?>',              # Matches <placeholder>, <DESCRIPTION> (simple angle brackets)
        r'YOUR_TEXT_HERE',       # Matches specific string YOUR_TEXT_HERE
        r'PLACEHOLDER_FOR'       # Matches specific string PLACEHOLDER_FOR...
    ]
    # Combine patterns into one for efficiency in search
    # We need to be careful with regex flags if patterns have different needs, but these are simple.
    combined_placeholder_regex = re.compile("|".join(placeholder_patterns), re.IGNORECASE)

    fields_to_check_for_placeholders = {
        "Role": prompt.role,
        "Context": prompt.context,
        "Task": prompt.task
    }

    for field_name, field_value in fields_to_check_for_placeholders.items():
        if isinstance(field_value, str): # Should always be str based on PromptObject
            match = combined_placeholder_regex.search(field_value)
            if match:
                errors_found.append(UnresolvedPlaceholderError(
                    f"{field_name}: Contains unresolved placeholder text like '{match.group(0)}'. "
                    "Please replace it with specific content."
                ))

    list_fields_for_placeholders = {
        "Constraints": prompt.constraints,
        "Examples": prompt.examples
        # Tags are usually short and less likely for complex placeholders, but could be added.
    }

    for field_name, item_list in list_fields_for_placeholders.items():
        if item_list: # Ensure list is not None and not empty
            for index, item in enumerate(item_list):
                if isinstance(item, str): # Items should be strings per earlier checks
                    match = combined_placeholder_regex.search(item)
                    if match:
                        errors_found.append(UnresolvedPlaceholderError(
                            f"{field_name} (Item {index + 1}): Contains unresolved placeholder "
                            f"text like '{match.group(0)}' in '{item[:50]}...'. "
                            "Please replace it with specific content."
                        ))

    # Rule 2: Repetitive List Items
    def check_repetitive_items_and_collect_errors(items: List[str], field_name: str, errors_list: List[PromptValidationError]):
        if not items or len(items) < 2: # No repetition possible with 0 or 1 item
            return

        normalized_items = set()
        for index, item in enumerate(items):
            # Normalize by lowercasing and stripping whitespace
            normalized_item = item.strip().lower()
            if normalized_item in normalized_items:
                errors_list.append(RepetitiveListItemError(
                    f"{field_name} (Item {index + 1}): Duplicate or very similar item found: '{item[:50]}...'. "
                    "Ensure each item is unique and adds distinct value."
                ))
            normalized_items.add(normalized_item)

    if prompt.constraints:
        check_repetitive_items_and_collect_errors(prompt.constraints, "Constraints", errors_found)

    if prompt.examples:
        check_repetitive_items_and_collect_errors(prompt.examples, "Examples", errors_found)

    # Tags are often single words; repetition might be less of an "error" and more of a style issue.
    # If needed, check_repetitive_items_and_collect_errors(prompt.tags, "Tags", errors_found) could be added.

    return errors_found
