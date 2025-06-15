from typing import List, Optional
import uuid
from datetime import datetime

class PromptObject:
    """
    Represents a structured prompt for an AI model, encompassing various
    components to guide the AI's response generation.

    Attributes:
        role (str): The role the AI should adopt.
        context (str): Background information or context for the prompt.
        task (str): The specific task the AI needs to perform.
        constraints (List[str]): A list of rules or limitations for the AI's response.
        examples (List[str]): A list of example inputs/outputs to guide the AI.
        prompt_id (str): Unique identifier for the prompt.
        version (int): Version number of the prompt.
        created_at (str): ISO 8601 timestamp of when the prompt was created (UTC).
        last_modified_at (str): ISO 8601 timestamp of the last modification (UTC).
        tags (List[str]): A list of keywords or tags for categorization.
        created_by_user_id (Optional[str]): The ID of the user who originally created this prompt object.
    """
    def __init__(self,
                 role: str,
                 context: str,
                 task: str,
                 constraints: List[str],
                 examples: List[str],
                 prompt_id: str = None,
                 version: int = 1,
                 created_at: str = None,
                 last_modified_at: str = None,
                 tags: List[str] = None,
                 created_by_user_id: Optional[str] = None):
        """
        Initializes the PromptObject with its core and metadata components.

        Args:
            role: The role the AI should adopt (e.g., 'expert Python programmer').
            context: Background information relevant to the task.
            task: The specific action the AI is expected to perform.
            constraints: Rules or limitations for the AI's output
                         (e.g., 'response must be under 200 words').
            examples: Concrete examples of desired input/output pairs.
            prompt_id (str, optional): A unique identifier for the prompt.
                                       Auto-generated if not provided. Defaults to None.
            version (int, optional): Version number of the prompt. Defaults to 1.
            created_at (str, optional): ISO 8601 timestamp for creation (UTC).
                                        Auto-generated if not provided. Defaults to None.
            last_modified_at (str, optional): ISO 8601 timestamp for last modification (UTC).
                                              Auto-generated if not provided. Defaults to None.
            tags (List[str], optional): A list of keywords or tags for categorization.
                                        Defaults to None, which is then converted to an empty list.
            created_by_user_id (Optional[str], optional): The ID of the user who created the prompt.
                                                          Defaults to None.
        """
        self.role: str = role
        self.context: str = context
        self.task: str = task
        self.constraints: List[str] = constraints
        self.examples: List[str] = examples

        self.prompt_id: str = prompt_id if prompt_id is not None else str(uuid.uuid4())
        self.version: int = version
        current_time_iso = datetime.utcnow().isoformat() + 'Z'
        self.created_at: str = created_at if created_at is not None else current_time_iso
        self.last_modified_at: str = last_modified_at if last_modified_at is not None else self.created_at
        self.tags: List[str] = tags if tags is not None else []
        self.created_by_user_id: Optional[str] = created_by_user_id

    def to_dict(self) -> dict:
        """Serializes the PromptObject instance to a dictionary."""
        return {
            "role": self.role,
            "context": self.context,
            "task": self.task,
            "constraints": self.constraints,
            "examples": self.examples,
            "prompt_id": self.prompt_id,
            "version": self.version,
            "created_at": self.created_at,
            "last_modified_at": self.last_modified_at,
            "tags": self.tags,
            "created_by_user_id": self.created_by_user_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PromptObject':
        """
        Creates a new PromptObject instance from a dictionary.

        Args:
            data (dict): A dictionary containing the prompt object's attributes.

        Returns:
            PromptObject: A new instance of PromptObject.
        """
        return cls(
            role=data.get("role"),
            context=data.get("context"),
            task=data.get("task"),
            constraints=data.get("constraints"),
            examples=data.get("examples"),
            prompt_id=data.get("prompt_id"),
            version=data.get("version"),
            created_at=data.get("created_at"),
            last_modified_at=data.get("last_modified_at"),
            tags=data.get("tags", []), # Ensure tags default to [] if missing in data
            created_by_user_id=data.get("created_by_user_id")
        )

    def touch(self): # Added from previous step, ensure it's still here.
        """Updates the last_modified_at timestamp to the current UTC time."""
        self.last_modified_at = datetime.utcnow().isoformat() + 'Z'
