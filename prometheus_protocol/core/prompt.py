from typing import List

class PromptObject:
    """
    Represents a structured prompt for an AI model, encompassing various
    components to guide the AI's response generation.
    """
    def __init__(self,
                 role: str,
                 context: str,
                 task: str,
                 constraints: List[str],
                 examples: List[str]):
        """
        Initializes the PromptObject with its core components.

        Args:
            role: The role the AI should adopt (e.g., 'expert Python programmer').
            context: Background information relevant to the task.
            task: The specific action the AI is expected to perform.
            constraints: Rules or limitations for the AI's output
                         (e.g., 'response must be under 200 words').
            examples: Concrete examples of desired input/output pairs.
        """
        self.role: str = role
        self.context: str = context
        self.task: str = task
        self.constraints: List[str] = constraints
        self.examples: List[str] = examples
