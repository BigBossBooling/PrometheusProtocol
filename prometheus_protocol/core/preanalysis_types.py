from enum import Enum
from dataclasses import dataclass, field # field might be needed if we add default_factory later
from typing import Optional, Dict, Any, List # List for from_dict if it returns list of findings

class PreanalysisSeverity(str, Enum):
    """
    Defines the severity level of a finding from the Prompt Pre-analysis Module.
    These are distinct from GIGO errors (which are blocking) and Risk levels
    (which relate to safety/ethical/effectiveness pitfalls).
    """
    INFO = "Info"          # General information or observation.
    SUGGESTION = "Suggestion"  # A recommendation for improvement, non-critical.
    WARNING = "Warning"      # Highlights an issue that might impact clarity/performance,
                             # but isn't a blocking GIGO error.

@dataclass
class PreanalysisFinding:
    """
    Represents a single finding or suggestion from a pre-analysis check.
    """
    check_name: str
    # Unique identifier for the specific check that generated this finding.
    # e.g., "ReadabilityScore_Task", "ConstraintActionability_Item_0", "TokenEstimator_Input"

    severity: PreanalysisSeverity
    # The severity level of the finding.

    message: str
    # The user-facing message describing the finding and offering advice.
    # e.g., "Task Readability: College Level. Consider simplifying."

    details: Optional[Dict[str, Any]] = None
    # Optional dictionary for any additional structured data related to the finding.
    # e.g., {"score": 75.0, "level_description": "8th Grade"} for readability.

    ui_target_field: Optional[str] = None
    # An optional string indicating which part of the PromptObject UI this finding
    # most directly relates to (e.g., "task", "context", "constraints[2]").

    def __post_init__(self):
        # Ensure severity is of the correct enum type if a string was passed (e.g. from from_dict)
        if isinstance(self.severity, str):
            try:
                self.severity = PreanalysisSeverity(self.severity)
            except ValueError:
                # Handle cases where string doesn't match enum members, e.g. default or raise
                # For now, let's assume valid strings or direct enum usage for simplicity in stub.
                # A more robust from_dict would handle this.
                pass


    def to_dict(self) -> Dict[str, Any]:
        """Serializes the PreanalysisFinding instance to a dictionary."""
        return {
            "check_name": self.check_name,
            "severity": self.severity.value, # Store enum value
            "message": self.message,
            "details": self.details,
            "ui_target_field": self.ui_target_field,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreanalysisFinding':
        """Creates a new PreanalysisFinding instance from a dictionary."""
        if not all(k in data for k in ["check_name", "severity", "message"]):
            raise ValueError("Missing required fields for PreanalysisFinding: 'check_name', 'severity', 'message'.")

        try:
            severity_enum = PreanalysisSeverity(data["severity"])
        except ValueError as e:
            raise ValueError(f"Invalid severity value: {data['severity']}. Allowed: {[s.value for s in PreanalysisSeverity]}") from e

        return cls(
            check_name=data["check_name"],
            severity=severity_enum,
            message=data["message"],
            details=data.get("details"),
            ui_target_field=data.get("ui_target_field")
        )

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.check_name}: {self.message}"
