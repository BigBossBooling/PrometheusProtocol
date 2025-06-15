import uuid
from datetime import datetime, timezone # Added timezone for explicit UTC
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from .prompt import PromptObject

@dataclass
class PromptTurn:
    """
    Represents a single turn in a multi-turn conversation.

    Attributes:
        prompt_object (PromptObject): The core prompt for this turn.
        turn_id (str): Unique identifier for this turn. Auto-generated.
        parent_turn_id (Optional[str]): ID of the preceding turn, if any.
        conditions (Optional[Dict[str, Any]]): Conditions from a previous AI response
                                               that might trigger this turn. (Placeholder for V1)
        notes (Optional[str]): User notes or comments specific to this turn.
    """
    prompt_object: PromptObject
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_turn_id: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None # Placeholder for future logic
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the PromptTurn instance to a dictionary."""
        return {
            "turn_id": self.turn_id,
            "prompt_object": self.prompt_object.to_dict(), # Serialize PromptObject
            "parent_turn_id": self.parent_turn_id,
            "conditions": self.conditions,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTurn':
        """Creates a new PromptTurn instance from a dictionary."""
        prompt_obj_data = data.get("prompt_object")
        if prompt_obj_data is None:
            raise ValueError("Missing 'prompt_object' data in PromptTurn dictionary.")

        return cls(
            turn_id=data.get("turn_id"),
            prompt_object=PromptObject.from_dict(prompt_obj_data), # Deserialize PromptObject
            parent_turn_id=data.get("parent_turn_id"),
            conditions=data.get("conditions"),
            notes=data.get("notes")
        )


@dataclass
class Conversation:
    """
    Represents a multi-turn conversation or a sequence of prompts.

    Attributes:
        title (str): A user-friendly title for the conversation.
        conversation_id (str): Unique identifier for the conversation. Auto-generated.
        version (int): The version number of this conversation object, defaults to 1.
        description (Optional[str]): A brief description of the conversation's purpose.
        turns (List[PromptTurn]): An ordered list of PromptTurn objects defining the conversation flow.
        created_at (str): ISO 8601 timestamp of when the conversation was created (UTC). Auto-generated.
        last_modified_at (str): ISO 8601 timestamp of the last modification (UTC). Auto-generated.
        tags (List[str]): A list of keywords or tags for categorization. Defaults to an empty list.
    """
    title: str
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1 # New field
    description: Optional[str] = None
    turns: List[PromptTurn] = field(default_factory=list)
    # Ensure consistent ISO 8601 format with 'Z' for UTC
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    tags: List[str] = field(default_factory=list) # Using List directly in default_factory

    # Method to update last_modified_at, useful for a manager class later
    def touch(self):
        """Updates the last_modified_at timestamp to the current time."""
        self.last_modified_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Conversation instance to a dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "description": self.description,
            "version": self.version, # New line
            "turns": [turn.to_dict() for turn in self.turns], # Serialize list of PromptTurns
            "created_at": self.created_at,
            "last_modified_at": self.last_modified_at,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Creates a new Conversation instance from a dictionary."""
        turns_data = data.get("turns", [])
        # Ensure turns_data is a list, even if it's None in the input dict (though default_factory usually prevents this)
        if turns_data is None:
            turns_data = []

        return cls(
            conversation_id=data.get("conversation_id"),
            title=data.get("title", "Untitled Conversation"), # Provide a default for title if missing
            description=data.get("description"),
            version=data.get("version", 1), # New line
            turns=[PromptTurn.from_dict(turn_data) for turn_data in turns_data], # Deserialize list of PromptTurns
            created_at=data.get("created_at"),
            last_modified_at=data.get("last_modified_at"),
            tags=data.get("tags", []) # Default to empty list if tags are missing
        )

# Note: Python's datetime.isoformat() for aware objects (like those with timezone.utc)
# by default includes the UTC offset like "+00:00".
# While this is ISO 8601 compliant, some systems or users prefer 'Z' (Zulu time) for UTC.
# The .replace('+00:00', 'Z') is added for this preference. If PromptObject's
# timestamps are also to strictly use 'Z', they should be updated similarly.
# For now, this ensures Conversation timestamps use 'Z'.
# If PromptObject uses +00:00 and Conversation uses Z, it's a minor inconsistency
# but both are valid ISO 8601 UTC representations.
# I will make a note to check PromptObject's timestamp format for 'Z' consistency
# if it becomes important for interoperability or specific requirements.
# For PromptObject: current_time_iso = datetime.utcnow().isoformat() + 'Z' was used, so it should be consistent.
# The .replace here is more robust for datetime.now(timezone.utc).isoformat() which might not add 'Z'.
# Actually, datetime.utcnow().isoformat() + 'Z' is fine.
# For datetime.now(timezone.utc).isoformat(), it correctly produces "+00:00".
# To be absolutely sure and consistent with PromptObject, I will use `datetime.utcnow().isoformat() + 'Z'`
# for `created_at` and `last_modified_at` in the Conversation dataclass.
# Let me regenerate the code for the Conversation class with this small adjustment for full consistency.
# Re-evaluating: datetime.now(timezone.utc).isoformat() is the more modern way for timezone-aware objects.
# The format "YYYY-MM-DDTHH:MM:SS.ffffff+00:00" is perfectly valid.
# PromptObject used datetime.utcnow().isoformat() + 'Z'.
# To ensure they are identical, I will adjust Conversation to match PromptObject's format.
# It's better to stick to one explicit method.
#
# Final decision: Use `datetime.utcnow().isoformat() + 'Z'` for consistency with `PromptObject`.
# The previous `replace` logic was an alternative way to get 'Z'.
# Let's correct the Conversation class default factories for timestamps.
# The current code block for create_file_with_block has the .replace method. I will remove it and use the simpler + 'Z'
# if I regenerate. Given the current tool, I will proceed with the existing code which is:
# created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
# last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
# This is fine. The key is that it's UTC and ISO 8601. 'Z' or '+00:00' are both valid.
# I'll stick with what was in the prompt for this step.
# The prompt has: created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
# This produces "+00:00". I will use this.
# The subtask description actually shows `datetime.now(timezone.utc).isoformat()` for the fields.
# I will use that directly without the .replace() for now.
# This means PromptObject will use 'Z' and Conversation will use '+00:00'. This is a minor inconsistency
# but acceptable for now as both are valid ISO 8601 UTC.
#
# Let's re-read the prompt carefully for the `Conversation` dataclass timestamps:
# `created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())`
# This is what I should implement.
# The `touch` method should also use `datetime.now(timezone.utc).isoformat()`.
# The current code in the `create_file_with_block` has the `.replace('+00:00', 'Z')`.
# I will remove these `.replace` calls to match the prompt's direct specification.
#
# Corrected thought process: The prompt's code block for the file content *does* include `.replace('+00:00', 'Z')`.
# My initial interpretation of the prompt's example `datetime.now(timezone.utc).isoformat()` was that it *didn't* have the replace.
# I will proceed with the content *exactly as provided in the prompt's code block for the file*, which includes the `.replace()`.
# This means the timestamps *will* use 'Z'.
#
# Okay, the prompt's code block to be written to file is:
# created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
# last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
# touch(): self.last_modified_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
# This is what I will generate. This ensures 'Z' notation.
# PromptObject used: current_time_iso = datetime.utcnow().isoformat() + 'Z'
# This is consistent. Both will produce the 'Z' notation for UTC.
# datetime.utcnow().isoformat() produces a naive datetime string. Adding 'Z' makes it explicit UTC.
# datetime.now(timezone.utc).isoformat() produces an aware datetime string like "YYYY-MM-DDTHH:MM:SS.ffffff+00:00".
# Replacing "+00:00" with "Z" also makes it explicit UTC with 'Z' notation. Both are fine and achieve the same 'Z' notation.
# The provided code in the prompt for `conversation.py` is good.
#
# One final check: The original prompt for this step states:
# `created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())`
# `last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())`
#
# However, the *code block to be written to the file* in the same prompt shows:
# `created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))`
# `last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))`
#
# This is a contradiction in the prompt. I will follow the *code block to be written to the file*, as that's the direct instruction for file content.
# So, the `.replace('+00:00', 'Z')` versions will be used.
# This ensures 'Z' notation for Conversation timestamps, consistent with PromptObject's 'Z' notation.
#
# My thought process got a bit tangled by re-reading the descriptive text vs. the code block.
# The rule is: the code block for `create_file_with_block` is king.
# The code block in the prompt is:
# ```python
# import uuid
# from datetime import datetime, timezone # Added timezone for explicit UTC
# from typing import List, Dict, Optional, Any
# from dataclasses import dataclass, field
#
# from .prompt import PromptObject
#
# @dataclass
# class PromptTurn:
#     # ... (content as in prompt) ...
#     prompt_object: PromptObject
#     turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     parent_turn_id: Optional[str] = None
#     conditions: Optional[Dict[str, Any]] = None # Placeholder for future logic
#     notes: Optional[str] = None
#
#
# @dataclass
# class Conversation:
#     # ... (content as in prompt) ...
#     title: str
#     conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     description: Optional[str] = None
#     turns: List[PromptTurn] = field(default_factory=list)
#     # Ensure consistent ISO 8601 format with 'Z' for UTC
#     created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
#     last_modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
#     tags: List[str] = field(default_factory=list) # Using List directly in default_factory
#
#     # Method to update last_modified_at, useful for a manager class later
#     def touch(self):
#         """Updates the last_modified_at timestamp to the current time."""
#         self.last_modified_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
# ```
# This looks correct and consistent.
#
# One final detail from the prompt:
# "The field `conditions` in `PromptTurn` uses `Dict[str, Any]` for flexibility in this version." - This is in the code.
# "Changed `metadata` in `PromptTurn` to `notes: Optional[str]` for simpler initial implementation." - This is in the code.
# All good.Okay, I will create the file `prometheus_protocol/core/conversation.py` with the specified content. This includes the `PromptTurn` and `Conversation` dataclasses, using `datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')` for timestamps to ensure UTC 'Z' notation, consistent with `PromptObject`.
