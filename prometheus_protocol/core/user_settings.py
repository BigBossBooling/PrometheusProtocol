import uuid # Though user_id will likely come from an auth system
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List # List might be needed for some settings in future
from dataclasses import dataclass, field

@dataclass
class UserSettings:
    """
    Represents user-specific settings and preferences for Prometheus Protocol.

    Attributes:
        user_id (str): The unique identifier for the user these settings belong to.
        default_jules_api_key (Optional[str]): User's personal API key for Jules.
                                                (Note: Secure storage is critical if implemented).
        default_jules_model (Optional[str]): User's preferred default Jules model.
        default_execution_settings (Dict[str, Any]): User's default settings for
                                                     PromptObject execution (e.g., temperature).
                                                     Defaults to an empty dict.
        ui_theme (Optional[str]): User's preferred UI theme (e.g., "dark", "light").
        preferred_output_language (Optional[str]): User's preferred language for AI outputs.
        creative_catalyst_defaults (Dict[str, str]): User's preferred default "Creativity Level"
                                                      for different catalyst modules.
                                                      Keyed by module name + setting type.
                                                      Defaults to an empty dict.
        last_updated_at (str): ISO 8601 UTC timestamp of the last update to these settings.
                               Auto-updates when settings are modified (conceptually).
    """
    user_id: str # Must be provided during instantiation
    default_jules_api_key: Optional[str] = None
    default_jules_model: Optional[str] = None
    default_execution_settings: Dict[str, Any] = field(default_factory=dict)
    ui_theme: Optional[str] = None
    preferred_output_language: Optional[str] = None # e.g., "en-US"
    creative_catalyst_defaults: Dict[str, str] = field(default_factory=dict)
    # Example for creative_catalyst_defaults:
    # {"RolePersonaGenerator_creativity": "balanced", "WhatIfScenarioGenerator_creativity": "adventurous"}

    last_updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the UserSettings instance to a dictionary."""
        return {
            "user_id": self.user_id,
            "default_jules_api_key": self.default_jules_api_key,
            "default_jules_model": self.default_jules_model,
            "default_execution_settings": self.default_execution_settings,
            "ui_theme": self.ui_theme,
            "preferred_output_language": self.preferred_output_language,
            "creative_catalyst_defaults": self.creative_catalyst_defaults,
            "last_updated_at": self.last_updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """
        Creates a new UserSettings instance from a dictionary.
        'user_id' is mandatory in the data.
        'last_updated_at' will be set to current time if not in data, or use provided.
        """
        if "user_id" not in data:
            raise ValueError("UserSettings.from_dict: 'user_id' is a required field in the input data.")

        return cls(
            user_id=data["user_id"],
            default_jules_api_key=data.get("default_jules_api_key"),
            default_jules_model=data.get("default_jules_model"),
            default_execution_settings=data.get("default_execution_settings", {}), # Default to empty dict
            ui_theme=data.get("ui_theme"),
            preferred_output_language=data.get("preferred_output_language"),
            creative_catalyst_defaults=data.get("creative_catalyst_defaults", {}), # Default to empty dict
            last_updated_at=data.get("last_updated_at", datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
        )

    def touch(self) -> None:
        """Updates the last_modified_at timestamp to the current time."""
        # In UserSettings, this field is last_updated_at, not last_modified_at
        self.last_updated_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
