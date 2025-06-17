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
    """
    Manages saving, loading, listing, and deletion of Conversation instances,
    supporting context-specific storage paths (e.g., for users or workspaces).
    """

    def __init__(self, data_storage_base_path: str):
        """
        Initializes the ConversationManager.

        Args:
            data_storage_base_path (str): The root directory for all application data.
                                           Conversations will be stored in a subdirectory.
        """
        self.data_storage_base_path = Path(data_storage_base_path)
        self.conversations_subdir = "conversations" # Instance attribute
        # Specific context paths are determined per-method call.

    def _get_context_specific_conversations_path(self, context_id: Optional[str] = None) -> Path:
        """
        Determines the conversations directory path for a given context.
        Creates the directory if it doesn't exist.
        """
        effective_user_id_for_personal = "default_user_conversations" # Fallback

        context_path: Path
        if context_id and context_id.startswith("ws_"): # Workspace context
            context_path = self.data_storage_base_path / "workspaces" / context_id / self.conversations_subdir
        else: # Personal space context
            user_id_to_use = context_id if context_id else effective_user_id_for_personal
            context_path = self.data_storage_base_path / "user_personal_spaces" / user_id_to_use / self.conversations_subdir

        context_path.mkdir(parents=True, exist_ok=True)
        return context_path

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

    def _get_versions_for_base_name(self, base_name: str, context_id: Optional[str] = None) -> List[int]:
        """
        Scans the context-specific conversations directory for files matching
        base_name_v*.json and returns a sorted list of found integer versions.
        """
        target_dir = self._get_context_specific_conversations_path(context_id)
        versions = []
        if not target_dir.exists():
            return []

        pattern = re.compile(f"^{re.escape(base_name)}_v(\d+)\.json$")

        for f_path in target_dir.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    try:
                        versions.append(int(match.group(1)))
                    except ValueError:
                        pass
        return sorted(versions)

    def _get_highest_version(self, base_name: str, context_id: Optional[str] = None) -> int:
        """
        Gets the highest existing version number for a given base_name in a specific context.
        Returns 0 if no versions exist.
        """
        versions = self._get_versions_for_base_name(base_name, context_id=context_id)
        return versions[-1] if versions else 0

    def save_conversation(self, conversation: Conversation, conversation_name: str, context_id: Optional[str] = None) -> Conversation:
        """
        Saves a Conversation instance as a versioned JSON file.
        Assigns a new version number (incremented from the highest existing).
        Updates conversation.version and conversation.last_modified_at.

        Args:
            conversation (Conversation): The Conversation instance to save.
            conversation_name (str): The base name for the conversation.
            context_id (Optional[str]): The context (user or workspace) for storage.

        Returns:
            Conversation: The updated Conversation instance.
        """
        if not isinstance(conversation, Conversation):
            raise TypeError("Input 'conversation' must be an instance of Conversation.")

        base_name = self._sanitize_base_name(conversation_name)
        target_dir = self._get_context_specific_conversations_path(context_id)

        highest_existing_version = self._get_highest_version(base_name, context_id=context_id)
        new_version = highest_existing_version + 1

        conversation.version = new_version
        conversation.touch()

        file_name_str = self._construct_filename(base_name, new_version)
        file_path = target_dir / file_name_str

        conversation_data = conversation.to_dict()

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=4)
        except IOError as e:
            raise IOError(
                f"Could not save conversation '{base_name}' version {new_version} to {file_path} in context '{context_id}': {e}"
            ) from e

        return conversation

    def load_conversation(self, conversation_name: str, version: Optional[int] = None, context_id: Optional[str] = None) -> Conversation:
        """
        Loads a Conversation from a versioned JSON file.
        Loads latest version if 'version' is None.

        Args:
            conversation_name (str): Base name of the conversation.
            version (Optional[int]): Specific version to load. Defaults to latest.
            context_id (Optional[str]): The context (user or workspace) for storage.

        Returns:
            Conversation: The loaded Conversation instance.

        Raises:
            FileNotFoundError, ConversationCorruptedError, ValueError.
        """
        base_name = self._sanitize_base_name(conversation_name)
        target_dir = self._get_context_specific_conversations_path(context_id)

        version_to_load: int
        if version is None:
            highest_version = self._get_highest_version(base_name, context_id=context_id)
            if highest_version == 0:
                raise FileNotFoundError(f"No versions found for conversation '{base_name}' in context '{context_id}'.")
            version_to_load = highest_version
        else:
            available_versions = self._get_versions_for_base_name(base_name, context_id=context_id)
            if version not in available_versions:
                raise FileNotFoundError(
                    f"Version {version} for conversation '{base_name}' not found in context '{context_id}'. "
                    f"Available versions: {available_versions if available_versions else 'None'}."
                )
            version_to_load = version

        file_name_str = self._construct_filename(base_name, version_to_load)
        file_path = target_dir / file_name_str

        if not file_path.exists():
            raise FileNotFoundError(f"Conversation file '{file_name_str}' not found at {file_path} in context '{context_id}'.")

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            conv_object = Conversation.from_dict(data)
            if conv_object.version != version_to_load:
                 print(f"Warning: Version mismatch for {base_name} in context '{context_id}'. File parsed as v{conv_object.version}, expected v{version_to_load}.")
            return conv_object
        except json.JSONDecodeError as e:
            raise ConversationCorruptedError(f"Corrupted conversation file (invalid JSON) for '{base_name}' v{version_to_load} in context '{context_id}': {e}") from e
        except ValueError as e:
            raise ConversationCorruptedError(f"Invalid data structure in conversation file for '{base_name}' v{version_to_load} in context '{context_id}': {e}") from e
        except Exception as e:
            raise ConversationCorruptedError(f"Unexpected error loading conversation '{base_name}' v{version_to_load} in context '{context_id}': {e}") from e

    def list_conversations(self, context_id: Optional[str] = None) -> Dict[str, List[int]]:
        """
        Lists available conversations and their versions for a given context.

        Args:
            context_id (Optional[str]): The context (user or workspace) to list for.

        Returns:
            Dict[str, List[int]]: Dict mapping base names to sorted lists of versions.
        """
        target_dir = self._get_context_specific_conversations_path(context_id)
        conversations_with_versions: Dict[str, List[int]] = {}

        if not target_dir.exists() or not target_dir.is_dir():
            return conversations_with_versions

        pattern = re.compile(r"^(.*?)_v(\d+)\.json$")

        for f_path in target_dir.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    base_name = match.group(1)
                    try:
                        version = int(match.group(2))
                        if base_name not in conversations_with_versions:
                            conversations_with_versions[base_name] = []
                        if version not in conversations_with_versions[base_name]:
                             conversations_with_versions[base_name].append(version)
                    except ValueError:
                        pass

        for base_name in conversations_with_versions:
            conversations_with_versions[base_name].sort()

        return conversations_with_versions

    def delete_conversation_version(self, conversation_name: str, version: int, context_id: Optional[str] = None) -> bool:
        """
        Deletes a specific version of a conversation from a given context.

        Args:
            conversation_name (str): The base name of the conversation.
            version (int): The specific version to delete.
            context_id (Optional[str]): The context (user or workspace).

        Returns:
            bool: True if the version was successfully deleted, False otherwise.
        """
        base_name = self._sanitize_base_name(conversation_name)
        target_dir = self._get_context_specific_conversations_path(context_id)

        file_name_str = self._construct_filename(base_name, version)
        file_path = target_dir / file_name_str

        if file_path.exists() and file_path.is_file():
            try:
                file_path.unlink()
                return True
            except IOError as e:
                print(f"IOError deleting conversation version {file_path} in context '{context_id}': {e}")
                return False
        else:
            return False

    def delete_conversation_all_versions(self, conversation_name: str, context_id: Optional[str] = None) -> int:
        """
        Deletes all versions of a given conversation from a specific context.

        Args:
            conversation_name (str): The base name of the conversation.
            context_id (Optional[str]): The context (user or workspace).

        Returns:
            int: The number of versions successfully deleted.
        """
        base_name = self._sanitize_base_name(conversation_name)
        target_dir = self._get_context_specific_conversations_path(context_id)

        versions_to_delete = self._get_versions_for_base_name(base_name, context_id=context_id)
        if not versions_to_delete:
            return 0

        deleted_count = 0
        for v_num in versions_to_delete:
            file_name_str = self._construct_filename(base_name, v_num)
            file_path = target_dir / file_name_str
            if file_path.exists() and file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_count += 1
                except IOError as e:
                    print(f"IOError deleting conversation version {file_path} in context '{context_id}' during delete_all: {e}")

        return deleted_count
