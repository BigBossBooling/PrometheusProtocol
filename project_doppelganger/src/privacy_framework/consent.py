from dataclasses import dataclass
from enum import Enum

class ConsentStatus(Enum):
    """
    An enum for consent statuses.
    """
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"

@dataclass
class UserConsent:
    """
    A class for representing user consent.
    """
    user_id: str
    policy_id: str
    status: ConsentStatus

    def to_dict(self) -> dict:
        """
        Converts the user consent to a dictionary.

        Returns:
            A dictionary representation of the user consent.
        """
        return {
            "user_id": self.user_id,
            "policy_id": self.policy_id,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserConsent":
        """
        Creates a user consent from a dictionary.

        Args:
            data: The dictionary to create the user consent from.

        Returns:
            A new user consent.
        """
        return cls(
            user_id=data["user_id"],
            policy_id=data["policy_id"],
            status=ConsentStatus(data["status"]),
        )
