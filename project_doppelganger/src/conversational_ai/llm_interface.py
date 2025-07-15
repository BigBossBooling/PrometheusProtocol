from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    An abstract base class for LLM interfaces.
    """

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            The response from the LLM.
        """
        pass
