import re
from .consent import UserConsent

class DataClassifier:
    """
    A class for classifying data.
    """

    def __init__(self):
        self.pii_patterns = {
            "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
            "phone": re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
        }

    def classify(self, data: str) -> list[str]:
        """
        Classifies data as PII or not.

        Args:
            data: The data to classify.

        Returns:
            A list of PII types found in the data.
        """
        pii_types = []
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(data):
                pii_types.append(pii_type)
        return pii_types

class ObfuscationEngine:
    """
    A class for obfuscating data.
    """

    def obfuscate(self, data: str, pii_types: list[str]) -> str:
        """
        Obfuscates PII in data.

        Args:
            data: The data to obfuscate.
            pii_types: The types of PII to obfuscate.

        Returns:
            The obfuscated data.
        """
        for pii_type in pii_types:
            if pii_type == "email":
                data = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", data)
            elif pii_type == "phone":
                data = re.sub(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[PHONE]", data)
        return data

class MinimizerEngine:
    """
    A class for minimizing data.
    """

    def __init__(self):
        self.classifier = DataClassifier()
        self.obfuscator = ObfuscationEngine()

    def process_data(self, data: str, user_consent: UserConsent) -> str:
        """
        Processes data to minimize PII.

        Args:
            data: The data to process.
            user_consent: The user's consent for data processing.

        Returns:
            The processed data.
        """
        pii_types = self.classifier.classify(data)
        if pii_types:
            # In a real implementation, we would check the user's consent
            # to determine whether we can process the PII.
            # For now, we'll just obfuscate it.
            data = self.obfuscator.obfuscate(data, pii_types)
        return data
