from dataclasses import dataclass
from enum import Enum

class DataCategory(Enum):
    """
    An enum for data categories.
    """
    PERSONAL = "personal"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"

@dataclass
class PrivacyPolicy:
    """
    A class for representing a privacy policy.
    """
    policy_id: str
    policy_text: str
    data_categories: list[DataCategory]

    def to_dict(self) -> dict:
        """
        Converts the privacy policy to a dictionary.

        Returns:
            A dictionary representation of the privacy policy.
        """
        return {
            "policy_id": self.policy_id,
            "policy_text": self.policy_text,
            "data_categories": [category.value for category in self.data_categories],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PrivacyPolicy":
        """
        Creates a privacy policy from a dictionary.

        Args:
            data: The dictionary to create the privacy policy from.

        Returns:
            A new privacy policy.
        """
        return cls(
            policy_id=data["policy_id"],
            policy_text=data["policy_text"],
            data_categories=[DataCategory(category) for category in data["data_categories"]],
        )
