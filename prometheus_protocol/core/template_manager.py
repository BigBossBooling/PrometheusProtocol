import json
import os
import re # Added for version parsing
from pathlib import Path
from typing import List, Dict, Optional # Added Optional, Dict might be used later

from .prompt import PromptObject
from .exceptions import TemplateCorruptedError

class TemplateManager:
    """Manages saving, loading, and listing of PromptObject templates."""

    def __init__(self, templates_dir: str = "prometheus_protocol/templates"):
        """
        Initializes the TemplateManager.

        Args:
            templates_dir (str, optional): The directory to store prompt templates.
                                           Defaults to "prometheus_protocol/templates".
                                           The directory will be created if it doesn't exist.
        """
        self.templates_dir_path = Path(templates_dir)
        self.templates_dir_path.mkdir(parents=True, exist_ok=True)
        # print(f"TemplateManager initialized. Templates directory: {self.templates_dir_path.resolve()}") # For debugging, can be removed

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

    def _get_versions_for_base_name(self, base_name: str) -> List[int]:
        """
        Scans the template directory for files matching base_name_v*.json
        and returns a sorted list of found integer versions.
        """
        versions = []
        if not self.templates_dir_path.exists(): # Should exist due to __init__
            return []

        # Regex to match base_name_v<digits>.json
        # Example: my_prompt_v1.json, my_prompt_v12.json
        # We need to escape base_name if it can contain regex special characters,
        # but our sanitization should prevent this.
        pattern = re.compile(f"^{re.escape(base_name)}_v(\d+)\.json$")

        for f_path in self.templates_dir_path.iterdir():
            if f_path.is_file():
                match = pattern.match(f_path.name)
                if match:
                    try:
                        versions.append(int(match.group(1)))
                    except ValueError:
                        # Should not happen if regex is correct
                        pass # Or log this anomaly
        return sorted(versions)

    def _get_highest_version(self, base_name: str) -> int:
        """
        Gets the highest existing version number for a given base_name.
        Returns 0 if no versions exist.
        """
        versions = self._get_versions_for_base_name(base_name)
        return versions[-1] if versions else 0

    def save_template(self, prompt: PromptObject, template_name: str) -> PromptObject:
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
                                   Its 'version' and 'last_modified_at' attributes
                                   will be updated by this method.
            template_name (str): The desired base name for the template.

        Returns:
            PromptObject: The updated PromptObject instance with new version and
                          last_modified_at timestamp.

        Raises:
            ValueError: If the template_name is empty, whitespace-only, or
                        sanitizes to an empty string.
            IOError: If there's an error writing the file to disk.
        """
        base_name = self._sanitize_base_name(template_name) # Raises ValueError if invalid

        highest_existing_version = self._get_highest_version(base_name)
        new_version = highest_existing_version + 1

        # Update the prompt object itself
        prompt.version = new_version
        prompt.touch() # Updates last_modified_at

        file_name_str = self._construct_filename(base_name, new_version)
        file_path = self.templates_dir_path / file_name_str

        prompt_data = prompt.to_dict() # Get data after updates

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=4)
            # print(f"Template '{base_name}' version {new_version} saved to {file_path}") # For debugging
        except IOError as e:
            # Clean up: if file was partially created, should we attempt to delete it?
            # For now, let the partial file exist if IOError occurs during write.
            raise IOError(
                f"Could not save template '{base_name}' version {new_version} to {file_path}: {e}"
            ) from e

        return prompt

    def load_template(self, template_name: str, version: Optional[int] = None) -> PromptObject:
        """
        Loads a PromptObject from a versioned JSON template file.

        If 'version' is None, it loads the highest available version.
        If 'version' is specified, it attempts to load that specific version.

        Args:
            template_name (str): The base name of the template to load.
            version (Optional[int], optional): The specific version to load.
                                               Defaults to None (load latest).

        Returns:
            PromptObject: The loaded PromptObject instance.

        Raises:
            FileNotFoundError: If the template or specified version does not exist.
            TemplateCorruptedError: If the template file is not valid JSON or
                                    cannot be deserialized into a PromptObject.
            ValueError: If the template_name is empty, whitespace-only, or
                        sanitizes to an empty string.
        """
        base_name = self._sanitize_base_name(template_name) # Raises ValueError if invalid

        version_to_load: int
        if version is None:
            highest_version = self._get_highest_version(base_name)
            if highest_version == 0:
                raise FileNotFoundError(f"No versions found for template '{base_name}'.")
            version_to_load = highest_version
        else:
            # Check if this specific version exists by looking it up in available versions.
            # This is more robust than just trying to construct filename and checking file.exists(),
            # as _get_versions_for_base_name confirms the naming pattern.
            available_versions = self._get_versions_for_base_name(base_name)
            if version not in available_versions:
                raise FileNotFoundError(
                    f"Version {version} for template '{base_name}' not found. "
                    f"Available versions: {available_versions if available_versions else 'None'}."
                )
            version_to_load = version

        file_name_str = self._construct_filename(base_name, version_to_load)
        file_path = self.templates_dir_path / file_name_str

        # This check is technically redundant if `version in available_versions` passed,
        # but it's a good safeguard before file access.
        if not file_path.exists():
            # This state should ideally not be reached if logic above is correct
            raise FileNotFoundError(
                f"Template file '{file_name_str}' for '{base_name}' version {version_to_load} not found at {file_path}."
            )

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)

            prompt_object = PromptObject.from_dict(data)
            return prompt_object
        except json.JSONDecodeError as e:
            # Ensure TemplateCorruptedError is imported (globally or locally as before)
            from .exceptions import TemplateCorruptedError
            raise TemplateCorruptedError(
                f"Template file {file_path} is corrupted (not valid JSON): {e}"
            ) from e
        except Exception as e:
            from .exceptions import TemplateCorruptedError
            raise TemplateCorruptedError(
                f"Error deserializing template {file_path} "
                f"(e.g., mismatched data structure or other error in from_dict): {e}"
            ) from e

    def list_templates(self) -> Dict[str, List[int]]:
        """
        Lists available templates and their versions.

        Scans the templates directory for versioned .json files (e.g., name_v1.json).

        Returns:
            Dict[str, List[int]]: A dictionary where keys are base template names
                                   and values are sorted lists of available integer
                                   versions for that template.
                                   Example: {"my_prompt": [1, 2], "another": [1]}
        """
        templates_with_versions: Dict[str, List[int]] = {}

        if not self.templates_dir_path.exists() or            not self.templates_dir_path.is_dir():
            return templates_with_versions # Return empty dict if dir doesn't exist

        # Regex to match <base_name>_v<digits>.json and capture base_name and version
        # Example: my_prompt_v1.json -> base_name="my_prompt", version="1"
        # The base_name can contain underscores but not end with _v<digits> itself.
        # This regex assumes base_name does not contain '_v' followed by digits at the end.
        # Our _sanitize_base_name should ensure this.
        pattern = re.compile(r"^(.*?)_v(\d+)\.json$")

        for f_path in self.templates_dir_path.iterdir():
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
                        # Should not happen if regex is correct and version is digits
                        pass # Or log this anomaly

        # Sort versions for each template
        for base_name in templates_with_versions:
            templates_with_versions[base_name].sort()

        return templates_with_versions
