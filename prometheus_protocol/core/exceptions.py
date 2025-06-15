# This file will define custom exceptions for the Prometheus Protocol.
# These exceptions will help in handling errors more gracefully and specifically.

class PromptValidationError(ValueError):
    """Base class for errors raised during PromptObject validation."""
    pass

class MissingRequiredFieldError(PromptValidationError):
    """Raised when a required field in PromptObject is missing or empty."""
    pass

class InvalidListTypeError(PromptValidationError):
    """Raised when 'constraints' or 'examples' are not lists (if provided)."""
    pass

class InvalidListItemError(PromptValidationError):
    """Raised when items within 'constraints' or 'examples' lists are not valid
    (e.g., not non-empty strings)."""
    pass

# Add this class to the existing exceptions

class TemplateCorruptedError(ValueError):
    """Raised when a template file is corrupted, not valid JSON,
    or cannot be deserialized into a PromptObject."""
    pass

# Add this class to the existing exceptions

class ConversationCorruptedError(ValueError):
    """Raised when a conversation file is corrupted, not valid JSON,
    or cannot be deserialized into a Conversation object."""
    pass

# Add these classes for Advanced GIGO Guardrail Rules

class UnresolvedPlaceholderError(PromptValidationError):
    """Raised when a common placeholder pattern (e.g., [INSERT_X])
    is found in a prompt field, indicating incomplete content."""
    pass

class RepetitiveListItemError(PromptValidationError):
    """Raised when duplicate or very similar items are found within
    list-based prompt fields like 'constraints' or 'examples'."""
    pass

# ConstraintConflictError deferred for V1 of advanced rules.
# class ConstraintConflictError(PromptValidationError):
#     """Raised when conflicting or contradictory constraints are detected."""
#     pass

# Add this class for UserSettingsManager
class UserSettingsCorruptedError(ValueError):
    """Raised when user settings data is found to be corrupted,
    improperly formatted, or inconsistent (e.g., user_id mismatch)."""
    pass
