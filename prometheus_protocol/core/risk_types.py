from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class RiskLevel(Enum):
    """Defines the severity level of an identified potential risk."""
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical" # Though for V1, we might primarily use INFO and WARNING

class RiskType(Enum):
    """Defines the category or type of a potential risk identified in a prompt."""
    LACK_OF_SPECIFICITY = "Lack of Specificity"
    KEYWORD_WATCH = "Keyword Watch"
    UNCONSTRAINED_GENERATION = "Unconstrained Generation"
    AMBIGUITY = "Ambiguity"
    # Add more types as new risk identification rules are developed.
    # Example: POTENTIAL_BIAS, OVERLY_COMPLEX_CONSTRAINTS, etc.

@dataclass
class PotentialRisk:
    """
    Represents a potential risk identified in a PromptObject.

    Attributes:
        risk_type (RiskType): The category of the identified risk.
        risk_level (RiskLevel): The severity level of the risk.
        message (str): A user-friendly message describing the risk.
        offending_field (Optional[str]): The specific field in PromptObject
                                         where the risk was identified (e.g., "task").
                                         Defaults to None.
        details (Optional[Dict[str, Any]]): Additional structured data about the
                                            risk, if applicable. Defaults to None.
    """
    risk_type: RiskType
    risk_level: RiskLevel
    message: str
    offending_field: Optional[str] = None # e.g., "task", "constraints", "context"
    details: Optional[Dict[str, Any]] = None # For any extra context or data about the risk

    def __str__(self) -> str:
        return f"[{self.risk_level.value} - {self.risk_type.value}] {self.message} (Field: {self.offending_field or 'N/A'})"
