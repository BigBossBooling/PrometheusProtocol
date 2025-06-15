import json
from pathlib import Path
from typing import Optional, Dict, List, Any # Keep Dict, List, Any for future even if not used in this exact stub

from prometheus_protocol.core.user_settings import UserSettings
from prometheus_protocol.core.exceptions import UserSettingsCorruptedError

class UserSettingsManager:
    """
    Manages the persistence (saving and loading) of UserSettings objects
    to the file system. Each user's settings are stored in a separate JSON file.
    """

    def __init__(self, settings_base_dir: str = "prometheus_protocol/user_data/settings"):
        """
        Initializes the UserSettingsManager.

        Args:
            settings_base_dir (str, optional):
                The base directory where user settings files will be stored.
                Defaults to "prometheus_protocol/user_data/settings".
                This directory will be created if it doesn't exist.
        """
        self.settings_base_dir_path = Path(settings_base_dir)
        self.settings_base_dir_path.mkdir(parents=True, exist_ok=True)
        # print(f"UserSettingsManager initialized. Settings base directory: {self.settings_base_dir_path.resolve()}") # For debugging

    def _get_user_settings_filepath(self, user_id: str) -> Path:
        """
        Constructs the file path for a given user's settings JSON file.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            Path: The absolute file path to the user's settings file.
        """
        if not user_id or not isinstance(user_id, str): # Basic validation
            raise ValueError("user_id must be a non-empty string.")
        return self.settings_base_dir_path / f"settings_{user_id}.json"

    def save_settings(self, settings: UserSettings) -> UserSettings:
        """
        Saves a UserSettings object to a JSON file specific to the user.

        The user_id from the settings object is used to determine the filename.
        The settings object's 'last_updated_at' timestamp is updated before saving.
        If a settings file for the user already exists, it will be overwritten.

        Args:
            settings (UserSettings): The UserSettings instance to save.
                                     Its 'last_updated_at' attribute will be updated.

        Returns:
            UserSettings: The updated UserSettings instance.

        Raises:
            TypeError: If the provided settings object is not an instance of UserSettings.
            IOError: If there's an error writing the file to disk.
            ValueError: If settings.user_id is invalid (caught by _get_user_settings_filepath).
        """
        if not isinstance(settings, UserSettings):
            raise TypeError("Input 'settings' must be an instance of UserSettings.")

        settings.touch()  # Update the last_updated_at timestamp

        file_path = self._get_user_settings_filepath(settings.user_id)

        try:
            settings_data = settings.to_dict()
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            # print(f"UserSettings for user '{settings.user_id}' saved to {file_path}") # For debugging
        except IOError as e:
            # This will catch errors from file_path.open() or json.dump() related to I/O
            raise IOError(
                f"Could not save settings for user '{settings.user_id}' to {file_path}: {e}"
            ) from e

        return settings

    def load_settings(self, user_id: str) -> Optional[UserSettings]:
        """
        Loads a UserSettings object from a JSON file specific to the user.

        Args:
            user_id (str): The unique identifier of the user whose settings are to be loaded.

        Returns:
            Optional[UserSettings]: The loaded UserSettings instance if found and valid,
                                    otherwise None (if the settings file does not exist).

        Raises:
            UserSettingsCorruptedError: If the settings file exists but is corrupted
                                        (e.g., invalid JSON, missing required 'user_id' field,
                                         or data structure mismatch).
            ValueError: If the provided user_id is invalid (caught by _get_user_settings_filepath).
        """
        file_path = self._get_user_settings_filepath(user_id) # Can raise ValueError

        if not file_path.exists():
            return None # No settings file found for this user

        try:
            with file_path.open('r', encoding='utf-8') as f:
                settings_data = json.load(f)

            # UserSettings.from_dict will raise ValueError if 'user_id' is missing in data.
            # It also handles setting defaults for other missing optional fields.
            loaded_settings = UserSettings.from_dict(settings_data)

            # Optional: Sanity check if user_id in file matches requested user_id
            # This is important if filenames could somehow be manually created/mismatched.
            # UserSettings.from_dict already requires 'user_id' from the data.
            if loaded_settings.user_id != user_id:
                # This case indicates a potential internal issue or manual file tampering,
                # as the filename is derived from user_id.
                # UserSettingsCorruptedError is now globally imported
                raise UserSettingsCorruptedError(
                    f"User ID mismatch in settings file: Expected '{user_id}', "
                    f"found '{loaded_settings.user_id}' in {file_path}."
                )

            return loaded_settings

        except json.JSONDecodeError as e:
            # UserSettingsCorruptedError is now globally imported
            raise UserSettingsCorruptedError(
                f"Corrupted settings file for user '{user_id}' (invalid JSON) at {file_path}: {e}"
            ) from e
        except ValueError as e: # Catches ValueError from UserSettings.from_dict (e.g. missing user_id)
            # UserSettingsCorruptedError is now globally imported
            raise UserSettingsCorruptedError(
                f"Invalid data structure or missing required fields in settings file "
                f"for user '{user_id}' at {file_path}: {e}"
            ) from e
        except Exception as e: # Catch any other unexpected errors during loading/deserialization
            # This is a general fallback.
            # UserSettingsCorruptedError is now globally imported
            raise UserSettingsCorruptedError(
                f"An unexpected error occurred while loading settings for user '{user_id}' from {file_path}: {e}"
            ) from e
