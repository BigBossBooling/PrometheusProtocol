import json
import os # os might not be strictly needed if only using pathlib
from pathlib import Path
from typing import List, Dict # Dict might be used later

from .conversation import Conversation
from .exceptions import ConversationCorruptedError

class ConversationManager:
    """Manages saving, loading, and listing of Conversation instances."""

    def __init__(self, conversations_dir: str = "prometheus_protocol/conversations"):
        """
        Initializes the ConversationManager.

        Args:
            conversations_dir (str, optional): The directory to store conversation files.
                                             Defaults to "prometheus_protocol/conversations".
                                             The directory will be created if it doesn't exist.
        """
        self.conversations_dir_path = Path(conversations_dir)
        self.conversations_dir_path.mkdir(parents=True, exist_ok=True)
        # print(f"ConversationManager initialized. Conversations directory: {self.conversations_dir_path.resolve()}") # For debugging

    def save_conversation(self, conversation: Conversation, conversation_name: str) -> None:
        """
        Saves a Conversation instance as a JSON file.

        The conversation_name is sanitized to create a valid filename.
        The conversation's 'last_modified_at' timestamp is updated before saving.
        If a file with the sanitized name already exists, it will be overwritten.

        Args:
            conversation (Conversation): The Conversation instance to save.
            conversation_name (str): The desired name for the conversation file.

        Raises:
            ValueError: If the conversation_name is empty, whitespace-only, or
                        sanitizes to an empty string.
            IOError: If there's an error writing the file to disk.
        """
        if not isinstance(conversation_name, str) or not conversation_name.strip():
            raise ValueError("Conversation name cannot be empty.")

        # Basic sanitization (consistent with TemplateManager)
        # Allow alphanumeric, underscore, hyphen. Replace space with underscore.
        sanitized_name_parts = []
        for char_code in [ord(c) for c in conversation_name]:
            if (ord('a') <= char_code <= ord('z') or
                ord('A') <= char_code <= ord('Z') or
                ord('0') <= char_code <= ord('9') or
                char_code == ord('_') or char_code == ord('-')):
                sanitized_name_parts.append(chr(char_code))
            elif chr(char_code) == ' ': # Replace space with underscore
                 sanitized_name_parts.append('_')

        safe_name = "".join(sanitized_name_parts)

        if not safe_name:
            raise ValueError(
                f"Conversation name '{conversation_name}' sanitized to an empty string, "
                "please use a different name."
            )

        # Update the last_modified_at timestamp before saving
        conversation.touch()

        file_path = self.conversations_dir_path / f"{safe_name}.json"
        conversation_data = conversation.to_dict()

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=4)
            # print(f"Conversation '{safe_name}' saved to {file_path}") # For debugging
        except IOError as e:
            raise IOError(
                f"Could not save conversation to {file_path}: {e}"
            ) from e

    def load_conversation(self, conversation_name: str) -> Conversation:
        """
        Loads a Conversation instance from a JSON file.

        The conversation_name is sanitized to find the corresponding filename.

        Args:
            conversation_name (str): The name of the conversation file to load.

        Returns:
            Conversation: The loaded Conversation instance.

        Raises:
            FileNotFoundError: If the conversation file does not exist.
            ConversationCorruptedError: If the file is not valid JSON or
                                        cannot be deserialized into a Conversation object.
            ValueError: If the conversation_name is empty, whitespace-only, or
                        sanitizes to an empty string.
        """
        if not isinstance(conversation_name, str) or not conversation_name.strip():
            raise ValueError("Conversation name cannot be empty.")

        # Basic sanitization (consistent with save_conversation)
        sanitized_name_parts = []
        for char_code in [ord(c) for c in conversation_name]:
            if (ord('a') <= char_code <= ord('z') or
                ord('A') <= char_code <= ord('Z') or
                ord('0') <= char_code <= ord('9') or
                char_code == ord('_') or char_code == ord('-')):
                sanitized_name_parts.append(chr(char_code))
            elif chr(char_code) == ' ': # Replace space with underscore
                 sanitized_name_parts.append('_')

        safe_name = "".join(sanitized_name_parts)

        if not safe_name:
            raise ValueError(
                f"Conversation name '{conversation_name}' sanitized to an empty string, "
                "cannot load."
            )

        file_path = self.conversations_dir_path / f"{safe_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Conversation '{safe_name}' (from original name '{conversation_name}') "
                f"not found at {file_path}"
            )

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)

            # Conversation.from_dict should handle structure validation internally
            # or raise appropriate errors (e.g. TypeError, KeyError) if data is malformed.
            conversation_object = Conversation.from_dict(data)
            return conversation_object
        except json.JSONDecodeError as e:
            from .exceptions import ConversationCorruptedError # Defined in step 5
            raise ConversationCorruptedError(
                f"Conversation file {file_path} is corrupted (not valid JSON): {e}"
            ) from e
        except Exception as e: # Catch other errors from Conversation.from_dict or unexpected issues
            from .exceptions import ConversationCorruptedError # Defined in step 5
            # This broad catch ensures any issue during deserialization beyond JSON format is caught.
            raise ConversationCorruptedError(
                f"Error deserializing conversation {file_path} "
                f"(e.g., mismatched data structure or other error in from_dict): {e}"
            ) from e

    def list_conversations(self) -> List[str]:
        """
        Lists the names of all available conversation files.

        Scans the conversations directory for .json files and returns their names
        (without the .json extension).

        Returns:
            List[str]: A list of conversation names. Returns an empty list if no
                       conversation files are found or if the directory doesn't exist
                       (though __init__ ensures it exists).
        """
        if not self.conversations_dir_path.exists() or            not self.conversations_dir_path.is_dir():
            # This case should ideally not be reached if __init__ ran correctly
            # and the directory hasn't been deleted/replaced by a file externally.
            return []

        conversation_names = []
        for file_path in self.conversations_dir_path.iterdir():
            if file_path.is_file() and file_path.suffix == ".json":
                conversation_names.append(file_path.stem) # .stem gives filename without extension

        return sorted(conversation_names) # Return sorted list for consistent order
