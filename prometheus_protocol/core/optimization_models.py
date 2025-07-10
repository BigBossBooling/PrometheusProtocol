from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone # Added timezone

@dataclass
class OptimizationFeedback:
    """
    Represents the feedback received from an LLM interaction, used for optimizing prompts.
    """
    prompt_id: str  # Identifier for the specific prompt instance or template version used
    response_quality_score: float  # Objective or subjective score of the LLM response quality (e.g., 0.0 to 1.0)

    # Optional detailed metrics
    user_satisfaction_score: Optional[float] = None # e.g., Thumbs up/down mapped to a score, or a rating
    task_success_status: Optional[bool] = None # Did the LLM interaction lead to successful task completion?

    # Contextual information
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) # Changed to aware UTC
    llm_response_id: Optional[str] = None # ID of the specific LLM response, for traceability
    error_message: Optional[str] = None # If an error occurred during LLM interaction

    # Further metadata that might be useful
    feedback_source: Optional[str] = None # e.g., "user_rating", "automated_evaluator", "task_completion_logic"
    context_snapshot: Optional[Dict[str, Any]] = None # Key variables or context active during the prompt

    # __post_init__ validations were relaxed for prototype as per previous decision.

@dataclass
class PromptOptimizationState:
    """
    Stores the current state of an optimization process for a given prompt template.
    """
    prompt_template_id: str # Identifier of the base prompt template being optimized
    current_version_hash: str # Hash or version identifier of the current "best" or "active" variant of the template

    performance_history: List[OptimizationFeedback] = field(default_factory=list) # Log of feedback for different versions/trials
    last_optimized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) # Changed to aware UTC

    optimization_config: Dict[str, Any] = field(default_factory=dict)

    def add_feedback(self, feedback: OptimizationFeedback):
        """Adds new feedback to the performance history and updates last_optimized_at."""
        self.performance_history.append(feedback)
        self.performance_history.sort(key=lambda f: f.timestamp, reverse=True)
        self.last_optimized_at = datetime.now(timezone.utc) # Changed to aware UTC

    def get_average_response_quality(self) -> Optional[float]:
        """
        Calculates the average response quality score from the history.
        """
        if not self.performance_history:
            return None

        # Filter out feedback items where response_quality_score might be None if that becomes possible
        valid_scores = [f.response_quality_score for f in self.performance_history if f.response_quality_score is not None]
        if not valid_scores:
            return None

        return sum(valid_scores) / len(valid_scores)
