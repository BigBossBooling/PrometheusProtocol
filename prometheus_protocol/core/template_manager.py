import json
import os
import re # Added for version parsing
from pathlib import Path
from typing import List, Dict, Optional # Added Optional, Dict might be used later

from .prompt import PromptObject
from .exceptions import TemplateCorruptedError

class TemplateManager:
    """
    Manages saving, loading, listing, and deletion of PromptObject templates,
    supporting context-specific storage paths (e.g., for users or workspaces).
    """

    def __init__(self, data_storage_base_path: str):
        """
        Initializes the TemplateManager.

        Args:
            data_storage_base_path (str): The root directory for all application data.
                                           Templates will be stored in a subdirectory under this path.
        """
        self.data_storage_base_path = Path(data_storage_base_path)
        self.templates_subdir = "templates" # Instance attribute
        # Specific context paths are now determined per-method call or via a helper.

    def _get_context_specific_templates_path(self, context_id: Optional[str] = None) -> Path:
        """
        Determines the templates directory path for a given context (user or workspace).
        Creates the directory if it doesn't exist.

        Args:
            context_id (Optional[str]): The ID of the user (for personal space)
                                        or workspace. If None, uses a default user ID.
        Returns:
            Path: The path to the context-specific templates directory.
        """
        effective_user_id_for_personal = "default_user_prompts"

        context_path: Path
        if context_id and context_id.startswith("ws_"): # Workspace context
            context_path = self.data_storage_base_path / "workspaces" / context_id / self.templates_subdir
        else: # Personal space context (either specific user_id or default)
            user_id_to_use = context_id if context_id else effective_user_id_for_personal
            context_path = self.data_storage_base_path / "user_personal_spaces" / user_id_to_use / self.templates_subdir

        context_path.mkdir(parents=True, exist_ok=True)
        return context_path

    def _sanitize_base_name(self, template_name: str) -> str:
        """
        Sanitizes the template name to be used as a base for versioned filenames.
        Raises ValueError if template_name is empty/whitespace or sanitizes to empty.
        """
        if not isinstance(template_name, str) or not template_name.strip():
            raise ValueError("Template name cannot be empty or just whitespace.")

        # Allow alphanumeric, underscore, hyphen. Replace space with underscore.
        # This logic is similar to what was in save_template before.
        sanitized_name_parts = []
        for char_code in [ord(c) for c in template_name]:
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
                f"Template name '{template_name}' sanitized to an empty string, "
                "please use a different name."
            )
        return safe_name

    def _construct_filename(self, base_name: str, version: int) -> str:
        """Constructs a versioned filename."""
        return f"{base_name}_v{version}.json"

    def _get_versions_for_base_name(self, base_name: str, context_id: Optional[str] = None) -> List[int]:
        """
        Scans the context-specific template directory for files matching
        base_name_v*.json and returns a sorted list of found integer versions.
        """
        target_dir = self._get_context_specific_templates_path(context_id)
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

    def save_template(self, prompt: PromptObject, template_name: str, context_id: Optional[str] = None) -> PromptObject:
        """
        Saves a PromptObject instance as a versioned JSON template file.

        The template_name is sanitized to create a base filename.
        A new version number is automatically assigned (incremented from the
        highest existing version for that base name).
        The prompt's 'version' and 'last_modified_at' attributes are updated.
        If a template with the same base name and new version already exists
        (highly unlikely with this logic), it will be overwritten.

        Args:
            prompt (PromptObject): The PromptObject instance to save.
            template_name (str): The desired base name for the template.
            context_id (Optional[str]): The context (user or workspace) for storage.

        Returns:
            PromptObject: The updated PromptObject instance.

        Raises:
            ValueError: If template_name is invalid.
            IOError: If file writing fails.
        """
        base_name = self._sanitize_base_name(template_name)
        target_dir = self._get_context_specific_templates_path(context_id)

        highest_existing_version = self._get_highest_version(base_name, context_id=context_id)
        new_version = highest_existing_version + 1

        prompt.version = new_version
        prompt.touch()

        file_name_str = self._construct_filename(base_name, new_version)
        file_path = target_dir / file_name_str

        prompt_data = prompt.to_dict()

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=4)
        except IOError as e:
            raise IOError(
                f"Could not save template '{base_name}' version {new_version} to {file_path} in context '{context_id}': {e}"
            ) from e

        return prompt

    def load_template(self, template_name: str, version: Optional[int] = None, context_id: Optional[str] = None) -> PromptObject:
        """
        Loads a PromptObject from a versioned JSON template file.

        If 'version' is None, it loads the highest available version.
        If 'version' is specified, it attempts to load that specific version.

        Args:
            template_name (str): The base name of the template to load.
            version (Optional[int], optional): The specific version to load.
                                               Defaults to None (load latest).
            context_id (Optional[str]): The context (user or workspace) for storage.

        Returns:
            PromptObject: The loaded PromptObject instance.

        Raises:
            FileNotFoundError: If the template or specified version does not exist.
            TemplateCorruptedError: If the template file is not valid JSON or
                                    cannot be deserialized into a PromptObject.
            ValueError: If template_name is invalid.
        """
        base_name = self._sanitize_base_name(template_name)
        target_dir = self._get_context_specific_templates_path(context_id)

        version_to_load: int
        if version is None:
            highest_version = self._get_highest_version(base_name, context_id=context_id)
            if highest_version == 0:
                raise FileNotFoundError(f"No versions found for template '{base_name}' in context '{context_id}'.")
            version_to_load = highest_version
        else:
            available_versions = self._get_versions_for_base_name(base_name, context_id=context_id)
            if version not in available_versions:
                raise FileNotFoundError(
                    f"Version {version} for template '{base_name}' not found in context '{context_id}'. "
                    f"Available versions: {available_versions if available_versions else 'None'}."
                )
            version_to_load = version

        file_name_str = self._construct_filename(base_name, version_to_load)
        file_path = target_dir / file_name_str

        if not file_path.exists():
            raise FileNotFoundError(
                f"Template file '{file_name_str}' for '{base_name}' version {version_to_load} not found at {file_path} in context '{context_id}'."
            )

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            prompt_object = PromptObject.from_dict(data)
            return prompt_object
        except json.JSONDecodeError as e:
            raise TemplateCorruptedError(
                f"Template file {file_path} in context '{context_id}' is corrupted (not valid JSON): {e}"
            ) from e
        except Exception as e:
            raise TemplateCorruptedError(
                f"Error deserializing template {file_path} in context '{context_id}' "
                f"(e.g., mismatched data structure or other error in from_dict): {e}"
            ) from e

    def list_templates(self, context_id: Optional[str] = None) -> Dict[str, List[int]]:
        """
        Lists available templates and their versions for a given context.

        Args:
            context_id (Optional[str]): The context (user or workspace) to list for.

        Returns:
            Dict[str, List[int]]: A dictionary where keys are base template names
                                   and values are sorted lists of available integer
                                   versions for that template in the given context.
        """
        target_dir = self._get_context_specific_templates_path(context_id)
        templates_with_versions: Dict[str, List[int]] = {}

        if not target_dir.exists() or not target_dir.is_dir():
            return templates_with_versions

        pattern = re.compile(r"^(.*?)_v(\d+)\.json$")

        for f_path in target_dir.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    base_name = match.group(1)
                    try:
                        version = int(match.group(2))
                        if base_name not in templates_with_versions:
                            templates_with_versions[base_name] = []
                        templates_with_versions[base_name].append(version)
                    except ValueError:
                        pass

        for base_name in templates_with_versions:
            templates_with_versions[base_name].sort()

        return templates_with_versions

    def delete_template_version(self, template_name: str, version: int, context_id: Optional[str] = None) -> bool:
        """
        Deletes a specific version of a prompt template from a given context.

        Args:
            template_name (str): The base name of the template.
            version (int): The specific version to delete.
            context_id (Optional[str]): The context (user or workspace).

        Returns:
            bool: True if the version was successfully deleted, False otherwise.
        """
        base_name = self._sanitize_base_name(template_name)
        target_dir = self._get_context_specific_templates_path(context_id)

        file_name_str = self._construct_filename(base_name, version)
        file_path = target_dir / file_name_str

        if file_path.exists() and file_path.is_file():
            try:
                file_path.unlink()
                return True
            except IOError as e:
                print(f"IOError deleting template version {file_path} in context '{context_id}': {e}")
                return False
        else:
            return False

    def delete_template_all_versions(self, template_name: str, context_id: Optional[str] = None) -> int:
        """
        Deletes all versions of a given prompt template from a specific context.

        Args:
            template_name (str): The base name of the template.
            context_id (Optional[str]): The context (user or workspace).

        Returns:
            int: The number of versions successfully deleted.
        """
        base_name = self._sanitize_base_name(template_name)
        target_dir = self._get_context_specific_templates_path(context_id)

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
                    print(f"IOError deleting template version {file_path} in context '{context_id}' during delete_all: {e}")

        return deleted_count
