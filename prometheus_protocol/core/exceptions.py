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
