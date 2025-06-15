import json
import os # os might not be strictly needed if only using pathlib
import re # For version parsing
from pathlib import Path
from typing import List, Dict, Optional, Any # Added Any for future

from prometheus_protocol.core.conversation import Conversation
from prometheus_protocol.core.exceptions import ConversationCorruptedError
# UserSettingsCorruptedError is not directly used here, but Conversation might have UserSettings in future
# from prometheus_protocol.core.exceptions import UserSettingsCorruptedError


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

    def _sanitize_base_name(self, conversation_name: str) -> str:
        """
        Sanitizes the conversation name to be used as a base for versioned filenames.
        Raises ValueError if conversation_name is empty/whitespace or sanitizes to empty.
        """
        if not isinstance(conversation_name, str) or not conversation_name.strip():
            raise ValueError("Conversation name cannot be empty or just whitespace.")

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
        return safe_name

    def _construct_filename(self, base_name: str, version: int) -> str:
        """Constructs a versioned filename for a conversation."""
        return f"{base_name}_v{version}.json" # Consistent with TemplateManager

    def _get_versions_for_base_name(self, base_name: str) -> List[int]:
        """
        Scans the conversations directory for files matching base_name_v*.json
        and returns a sorted list of found integer versions.
        """
        versions = []
        if not self.conversations_dir_path.exists():
            return []

        pattern = re.compile(f"^{re.escape(base_name)}_v(\d+)\.json$")

        for f_path in self.conversations_dir_path.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    try:
                        versions.append(int(match.group(1)))
                    except ValueError:
                        pass
        return sorted(versions)

    def _get_highest_version(self, base_name: str) -> int:
        """
        Gets the highest existing version number for a given base_name.
        Returns 0 if no versions exist.
        """
        versions = self._get_versions_for_base_name(base_name)
        return versions[-1] if versions else 0

    def save_conversation(self, conversation: Conversation, conversation_name: str) -> Conversation:
        """
        Saves a Conversation instance as a versioned JSON file.
        Assigns a new version number (incremented from the highest existing).
        Updates conversation.version and conversation.last_modified_at.

        Args:
            conversation (Conversation): The Conversation instance to save.
            conversation_name (str): The base name for the conversation.

        Returns:
            Conversation: The updated Conversation instance.
        """
        if not isinstance(conversation, Conversation): # Keep existing type check
            raise TypeError("Input 'conversation' must be an instance of Conversation.")

        base_name = self._sanitize_base_name(conversation_name)

        highest_existing_version = self._get_highest_version(base_name)
        new_version = highest_existing_version + 1

        conversation.version = new_version # Set version on the object
        conversation.touch() # Updates last_modified_at

        file_name_str = self._construct_filename(base_name, new_version)
        file_path = self.conversations_dir_path / file_name_str

        conversation_data = conversation.to_dict()

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=4)
        except IOError as e:
            raise IOError(
                f"Could not save conversation '{base_name}' version {new_version} to {file_path}: {e}"
            ) from e

        return conversation

    def load_conversation(self, conversation_name: str, version: Optional[int] = None) -> Conversation:
        """
        Loads a Conversation from a versioned JSON file.
        Loads latest version if 'version' is None.

        Args:
            conversation_name (str): Base name of the conversation.
            version (Optional[int]): Specific version to load. Defaults to latest.

        Returns:
            Conversation: The loaded Conversation instance.

        Raises:
            FileNotFoundError, ConversationCorruptedError, ValueError.
        """
        base_name = self._sanitize_base_name(conversation_name)

        version_to_load: int
        if version is None:
            highest_version = self._get_highest_version(base_name)
            if highest_version == 0:
                raise FileNotFoundError(f"No versions found for conversation '{base_name}'.")
            version_to_load = highest_version
        else:
            available_versions = self._get_versions_for_base_name(base_name)
            if version not in available_versions:
                raise FileNotFoundError(
                    f"Version {version} for conversation '{base_name}' not found. "
                    f"Available versions: {available_versions if available_versions else 'None'}."
                )
            version_to_load = version

        file_name_str = self._construct_filename(base_name, version_to_load)
        file_path = self.conversations_dir_path / file_name_str

        if not file_path.exists(): # Safeguard, should be caught by version checks
            raise FileNotFoundError(f"Conversation file '{file_name_str}' not found at {file_path}.")

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            conv_object = Conversation.from_dict(data)
            # Sanity check for version consistency between filename and content (optional but good)
            if conv_object.version != version_to_load:
                 # This could be a specific type of ConversationCorruptedError
                 print(f"Warning: Version mismatch for {base_name}. File parsed as v{conv_object.version}, expected v{version_to_load}.")
                 # For strictness, one might raise an error here. For now, let's assume file content is king for version.
                 # Or, better, trust the filename's version and ensure from_dict sets it if it's in data.
                 # The current Conversation.from_dict uses data.get('version', 1).
                 # If the loaded data's version is different, it's an inconsistency.
                 # The object returned will have the version from the file's content.
            return conv_object
        except json.JSONDecodeError as e:
            raise ConversationCorruptedError(f"Corrupted conversation file (invalid JSON) for '{base_name}' v{version_to_load}: {e}") from e
        except ValueError as e:
            raise ConversationCorruptedError(f"Invalid data structure in conversation file for '{base_name}' v{version_to_load}: {e}") from e
        except Exception as e:
            raise ConversationCorruptedError(f"Unexpected error loading conversation '{base_name}' v{version_to_load}: {e}") from e

    def list_conversations(self) -> Dict[str, List[int]]:
        """
        Lists available conversations and their versions.

        Returns:
            Dict[str, List[int]]: Dict mapping base names to sorted lists of versions.
                                   Example: {"my_chat": [1, 2], "project_alpha": [1]}
        """
        conversations_with_versions: Dict[str, List[int]] = {}

        if not self.conversations_dir_path.exists() or            not self.conversations_dir_path.is_dir():
            return conversations_with_versions

        pattern = re.compile(r"^(.*?)_v(\d+)\.json$")

        for f_path in self.conversations_dir_path.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    base_name = match.group(1)
                    try:
                        version = int(match.group(2))
                        if base_name not in conversations_with_versions:
                            conversations_with_versions[base_name] = []
                        if version not in conversations_with_versions[base_name]: # Ensure unique versions
                             conversations_with_versions[base_name].append(version)
                    except ValueError:
                        pass

        for base_name in conversations_with_versions:
            conversations_with_versions[base_name].sort()

        return conversations_with_versions
