from typing import List
from .prompt import PromptObject
from .exceptions import (
    MissingRequiredFieldError,
    InvalidListTypeError,
    InvalidListItemError
)

def validate_prompt(prompt: PromptObject) -> None:
    """
    Validates a PromptObject to ensure it meets basic quality criteria.

    Raises:
        MissingRequiredFieldError: If 'role', 'task', or 'context' are empty or whitespace.
        InvalidListTypeError: If 'constraints' or 'examples' are provided but are not lists.
        InvalidListItemError: If items in 'constraints' or 'examples' lists are not non-empty strings.
    """
    if not prompt.role or not prompt.role.strip():
        raise MissingRequiredFieldError("Role must be a non-empty string.")

    if not prompt.task or not prompt.task.strip():
        raise MissingRequiredFieldError("Task must be a non-empty string.")

    if not prompt.context or not prompt.context.strip():
        raise MissingRequiredFieldError("Context must be a non-empty string.")

    if prompt.constraints is not None:
        if not isinstance(prompt.constraints, List):
            raise InvalidListTypeError("Constraints, if provided, must be a list.")
        for item in prompt.constraints:
            if not isinstance(item, str) or not item.strip():
                raise InvalidListItemError("Each constraint must be a non-empty string.")

    if prompt.examples is not None:
        if not isinstance(prompt.examples, List):
            raise InvalidListTypeError("Examples, if provided, must be a list.")
        for item in prompt.examples:
            if not isinstance(item, str) or not item.strip():
                raise InvalidListItemError("Each example must be a non-empty string.")

    # If all checks pass, the function returns None implicitly.
