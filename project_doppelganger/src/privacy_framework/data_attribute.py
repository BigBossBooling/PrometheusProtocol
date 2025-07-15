from dataclasses import dataclass
from enum import Enum

class DataAttributeType(Enum):
    """
    An enum for data attribute types.
    """
    NAME = "name"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"

@dataclass
class DataAttribute:
    """
    A class for representing a data attribute.
    """
    attribute_type: DataAttributeType
    value: str

    def to_dict(self) -> dict:
        """
        Converts the data attribute to a dictionary.

        Returns:
            A dictionary representation of the data attribute.
        """
        return {
            "attribute_type": self.attribute_type.value,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataAttribute":
        """
        Creates a data attribute from a dictionary.

        Args:
            data: The dictionary to create the data attribute from.

        Returns:
            A new data attribute.
        """
        return cls(
            attribute_type=DataAttributeType(data["attribute_type"]),
            value=data["value"],
        )
