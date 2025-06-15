import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List # Added List for potential future use in from_dict or other areas

@dataclass
class AIResponse:
    """
    Represents a structured response from the hypothetical Jules AI engine.

    This class standardizes how AI outputs, metadata, and errors are handled
    within the Prometheus Protocol system after an API call.
    """
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_prompt_id: str # ID of the PromptObject that generated this response
    source_prompt_version: int # Version of the PromptObject

    source_conversation_id: Optional[str] = None # ID of the Conversation, if part of one
    source_turn_id: Optional[str] = None # Specific turn_id within a Conversation

    timestamp_request_sent: str # ISO 8601 UTC string, when the request to Jules was initiated
    timestamp_response_received: str # ISO 8601 UTC string, when the response from Jules was received

    content: Optional[str] = None # The main textual content from the AI
    raw_jules_response: Optional[Dict[str, Any]] = None # The full, raw JSON response from Jules API

    error_message: Optional[str] = None # Error message if Jules API indicated an error
    was_successful: bool = False # True if AI call resulted in successful content generation

    # Metadata from Jules response (based on hypothetical API contract)
    jules_request_id_client: Optional[str] = None # Client-provided request ID, echoed back
    jules_request_id_jules: Optional[str] = None # Jules's internal ID for the request
    jules_tokens_used: Optional[int] = None
    jules_finish_reason: Optional[str] = None # e.g., "stop", "length"
    jules_model_used: Optional[str] = None # e.g., "jules-xl-v2.3-apollo"
    jules_quality_assessment: Optional[Dict[str, Any]] = None # Hypothetical structured quality scores

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the AIResponse instance to a dictionary."""
        return {
            "response_id": self.response_id,
            "source_prompt_id": self.source_prompt_id,
            "source_prompt_version": self.source_prompt_version,
            "source_conversation_id": self.source_conversation_id,
            "source_turn_id": self.source_turn_id,
            "timestamp_request_sent": self.timestamp_request_sent,
            "timestamp_response_received": self.timestamp_response_received,
            "content": self.content,
            "raw_jules_response": self.raw_jules_response,
            "error_message": self.error_message,
            "was_successful": self.was_successful,
            "jules_request_id_client": self.jules_request_id_client,
            "jules_request_id_jules": self.jules_request_id_jules,
            "jules_tokens_used": self.jules_tokens_used,
            "jules_finish_reason": self.jules_finish_reason,
            "jules_model_used": self.jules_model_used,
            "jules_quality_assessment": self.jules_quality_assessment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Creates a new AIResponse instance from a dictionary."""
        # This basic from_dict assumes all keys are present or appropriately None.
        # More robust parsing (e.g. with .get() and defaults) might be needed if
        # the source dictionary structure can vary significantly.
        return cls(
            response_id=data.get("response_id", str(uuid.uuid4())), # Ensure response_id always exists
            source_prompt_id=data["source_prompt_id"], # Required
            source_prompt_version=data["source_prompt_version"], # Required
            source_conversation_id=data.get("source_conversation_id"),
            source_turn_id=data.get("source_turn_id"),
            timestamp_request_sent=data["timestamp_request_sent"], # Required
            timestamp_response_received=data["timestamp_response_received"], # Required
            content=data.get("content"),
            raw_jules_response=data.get("raw_jules_response"),
            error_message=data.get("error_message"),
            was_successful=data.get("was_successful", False), # Default to False
            jules_request_id_client=data.get("jules_request_id_client"),
            jules_request_id_jules=data.get("jules_request_id_jules"),
            jules_tokens_used=data.get("jules_tokens_used"),
            jules_finish_reason=data.get("jules_finish_reason"),
            jules_model_used=data.get("jules_model_used"),
            jules_quality_assessment=data.get("jules_quality_assessment"),
        )
