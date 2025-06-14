import json
import os
from pathlib import Path
from typing import List, Dict # Dict might be used later for more complex return types or internal structures

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

    def save_template(self, prompt: PromptObject, template_name: str) -> None:
        """
        Saves a PromptObject instance as a JSON template file.

        The template_name is sanitized to create a valid filename.
        If a template with the sanitized name already exists, it will be overwritten.

        Args:
            prompt (PromptObject): The PromptObject instance to save.
            template_name (str): The desired name for the template.

        Raises:
            ValueError: If the template_name is empty or sanitizes to an empty string.
            IOError: If there's an issue writing the file to disk.
        """
        if not isinstance(template_name, str) or not template_name.strip():
            raise ValueError("Template name cannot be empty.")

        # Basic sanitization: replace spaces with underscores, remove most special characters.
        # Allow alphanumeric, underscore, hyphen.
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

        if not safe_name: # Check if sanitization resulted in an empty string
            raise ValueError(f"Template name '{template_name}' sanitized to an empty string, please use a different name.")

        file_path = self.templates_dir_path / f"{safe_name}.json"
        prompt_data = prompt.to_dict()

        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=4)
            # print(f"Template '{safe_name}' saved to {file_path}") # For debugging
        except IOError as e:
            # Handle potential I/O errors, e.g., disk full, permissions
            # For now, re-raise as a generic exception or a custom one if defined
            # This could be more specific, e.g., CantWriteTemplateError(IOError)
            raise IOError(f"Could not save template to {file_path}: {e}") from e

    def load_template(self, template_name: str) -> PromptObject:
        """
        Loads a PromptObject from a JSON template file.

        The template_name is sanitized to find the corresponding filename.

        Args:
            template_name (str): The name of the template to load.

        Returns:
            PromptObject: The loaded PromptObject instance.

        Raises:
            FileNotFoundError: If the template file does not exist.
            TemplateCorruptedError: If the template file is not valid JSON or
                                    cannot be deserialized into a PromptObject.
            ValueError: If the template_name is empty or sanitizes to an empty string.
        """
        if not isinstance(template_name, str) or not template_name.strip():
            raise ValueError("Template name cannot be empty.")

        # Basic sanitization (consistent with save_template)
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
            raise ValueError(f"Template name '{template_name}' sanitized to an empty string, cannot load.")

        file_path = self.templates_dir_path / f"{safe_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Template '{safe_name}' (from original name '{template_name}') not found at {file_path}")

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            # Assuming PromptObject.from_dict might raise errors if data is malformed
            # (e.g., TypeError if required keys are missing and not handled by .get() in from_dict)
            prompt_object = PromptObject.from_dict(data)
            return prompt_object
        except json.JSONDecodeError as e:
            from .exceptions import TemplateCorruptedError # Defined in step 5
            raise TemplateCorruptedError(f"Template file {file_path} is corrupted (not valid JSON): {e}") from e
        except Exception as e: # Catching other errors from PromptObject.from_dict or unexpected issues
            from .exceptions import TemplateCorruptedError # Defined in step 5
            # This broad catch is to ensure any issue during deserialization beyond JSON format is caught.
            # PromptObject.from_dict should ideally be robust or raise specific errors if data is present but incorrect.
            raise TemplateCorruptedError(f"Error deserializing template {file_path} (e.g., mismatched data structure): {e}") from e

    def list_templates(self) -> List[str]:
        """
        Lists the names of all available templates.

        Scans the templates directory for .json files and returns their names
        (without the .json extension).

        Returns:
            List[str]: A list of template names. Returns an empty list if no
                       templates are found or if the directory doesn't exist
                       (though __init__ ensures it exists).
        """
        if not self.templates_dir_path.exists() or not self.templates_dir_path.is_dir():
            # This case should ideally not be reached if __init__ ran correctly
            # and the directory hasn't been deleted/replaced by a file externally.
            return []

        template_names = []
        for file_path in self.templates_dir_path.iterdir():
            if file_path.is_file() and file_path.suffix == ".json":
                template_names.append(file_path.stem) # .stem gives filename without extension

        return sorted(template_names) # Return sorted list for consistent order
