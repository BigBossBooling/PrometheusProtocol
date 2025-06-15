from typing import List, Dict, Any # Added Dict, Any for future use in __init__ or methods
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.risk_types import PotentialRisk, RiskLevel, RiskType

class RiskIdentifier:
    """
    Analyzes PromptObject instances to identify potential risks or areas
    for improvement beyond basic GIGO Guardrail syntax checks.
    """

    def __init__(self):
        """
        Initializes the RiskIdentifier.
        Future versions might accept configuration for rules, thresholds, etc.
        """
        # For V1, no specific configuration needed in constructor.
        pass

    def identify_risks(self, prompt: PromptObject) -> List[PotentialRisk]:
        """
        Identifies potential risks in the given PromptObject.

        Args:
            prompt (PromptObject): The prompt to analyze.

        Returns:
            List[PotentialRisk]: A list of identified potential risks.
                                 Returns an empty list if no risks are found.
        """
        risks: List[PotentialRisk] = []

        # Rule 1: Lack of Specificity in Task
        # Check if the task is very short (e.g., < 5 words) AND constraints is empty.
        if len(prompt.task.split()) < 5 and not prompt.constraints:
            risks.append(PotentialRisk(
                risk_type=RiskType.LACK_OF_SPECIFICITY,
                risk_level=RiskLevel.WARNING,
                message="Task is very brief and has no constraints. This could lead to overly broad or unpredictable AI responses. Consider adding more detail to the task or providing specific constraints.",
                offending_field="task"
            ))

        # Rule 2: Keyword Watch (Simple V1)
        # Define a small, hardcoded list of keywords and categories.
        # Using a dictionary where keys are categories and values are lists of keyword stems.
        keywords_to_watch = {
            "sensitive_financial_advice": ["invest", "loan", "stock tip", "market prediction"],
            "sensitive_medical_advice": ["diagnos", "treat", "cure", "medical condition", "symptom"]
            # "diagnos" will match "diagnosis", "diagnose", etc.
        }

        prompt_text_lower = (prompt.task + " " + prompt.context).lower() # Combine task and context for keyword search

        flagged_categories = set() # To ensure only one warning per category

        for category, keywords in keywords_to_watch.items():
            if category in flagged_categories:
                continue # Already flagged this category

            for keyword_stem in keywords:
                if keyword_stem in prompt_text_lower:
                    risks.append(PotentialRisk(
                        risk_type=RiskType.KEYWORD_WATCH,
                        risk_level=RiskLevel.INFO,
                        message=f"Prompt mentions terms related to '{category.replace('_', ' ')}'. Ensure outputs are appropriate and consider adding disclaimers or specific constraints if generating content in this domain, especially if it could be interpreted as advice.",
                        offending_field="task", # Could also be context
                        details={"category": category, "matched_keyword_stem": keyword_stem}
                    ))
                    flagged_categories.add(category)
                    break # Move to next category once a keyword in current category is found


        # Rule 3: Potentially Unconstrained Complex Task
        # If prompt.task implies a complex output and has very few constraints.
        complex_task_indicators = [
            "detailed report", "in-depth analysis", "comprehensive plan",
            "research paper", "full script", "entire book outline", "legal document"
        ]

        task_lower = prompt.task.lower()
        found_complex_indicator = False
        for indicator in complex_task_indicators:
            if indicator in task_lower:
                found_complex_indicator = True
                break

        if found_complex_indicator and len(prompt.constraints) < 2:
            risks.append(PotentialRisk(
                risk_type=RiskType.UNCONSTRAINED_GENERATION,
                risk_level=RiskLevel.WARNING,
                message="The task appears to require a complex or detailed output but has fewer than two constraints. This might lead to unfocused, overly lengthy, or incomplete responses. Consider adding specific constraints to better guide the AI for this type of task.",
                offending_field="constraints",
                details={"task_complexity_indicators_found": [ind for ind in complex_task_indicators if ind in task_lower]}
            ))

        return risks
