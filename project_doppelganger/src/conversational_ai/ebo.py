class EBO:
    """
    A class for representing the EchoSphere Behavioral Orchestrator.
    """

    def __init__(self, rules: list[dict]):
        self.rules = rules

    def evaluate(self, inputs: dict) -> dict:
        """
        Evaluates the EBO rules.

        Args:
            inputs: The inputs to the EBO rules.

        Returns:
            A dictionary of outputs from the EBO rules.
        """
        print("Evaluating EBO rules...")
        for rule in self.rules:
            if all(condition(inputs) for condition in rule["conditions"]):
                return rule["action"]
        return {}
