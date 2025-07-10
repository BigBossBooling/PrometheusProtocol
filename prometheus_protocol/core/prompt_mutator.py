import yaml
import random
from typing import Dict, Any, Optional, List, Tuple
from copy import deepcopy

# Attempt to import PromptGenerator for type hinting and potential use,
# but make it optional for environments where it might not be directly needed by PromptMutator alone.
try:
    from prometheus_protocol.core.prompt_generator import PromptGenerator
except ImportError:
    PromptGenerator = None # type: ignore

class PromptMutator:
    """
    Conceptually takes an existing prompt template (as YAML string or parsed data)
    and generates variations (mutations) based on a set of predefined rules.
    This is a simple rule-based system for a prototype.
    """

    def __init__(self, prompt_generator: Optional[PromptGenerator] = None):
        """
        Initializes the PromptMutator.

        Args:
            prompt_generator (Optional[PromptGenerator]): An instance of PromptGenerator.
                Used if `mutate_template` is called with a YAML string and needs to parse it.
                If always called with pre-parsed `existing_template_data`, this can be None.
        """
        if PromptGenerator is None and prompt_generator is not None:
            # This condition implies PromptGenerator failed to import but an instance was passed.
            # This shouldn't happen if imports are set up correctly, but good for robustness.
            print("Warning: PromptGenerator class was not imported, but an instance was provided to PromptMutator.")

        # If a prompt_generator is not provided, and the class is needed, methods relying on it will fail.
        # This design allows PromptMutator to be used without a full PromptGenerator if mutations
        # are applied to already-parsed data structures.
        self.prompt_generator = prompt_generator

        # Predefined lists for mutations
        self.common_tones: List[str] = ["formal", "friendly", "empathetic", "assertive", "neutral", "concise", "detailed", "humorous"]
        self.common_personas: List[str] = ["expert", "assistant", "teacher", "coach", "friend", "devil's advocate"]
        self.clarification_phrases: List[str] = [
            "To be more specific, ",
            "Could you elaborate on ",
            "Please ensure that ",
            "Remember to consider ",
            "For clarity, "
        ]
        self.alternative_phrasings: Dict[str, List[str]] = {
            "You are an assistant.": [
                "You are a helpful AI assistant.",
                "Your role is that of an assistant.",
                "Function as an AI assistant."
            ],
            "Please provide details.": [
                "Kindly furnish the specifics.",
                "Could you give me more information?",
                "Details are requested."
            ]
            # Add more common phrases and their alternatives
        }


    def _load_template_if_needed(self, template_yaml_string: str,
                                 existing_template_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Helper to load template from YAML string if not already parsed."""
        if existing_template_data:
            return deepcopy(existing_template_data) # Work on a copy

        if not self.prompt_generator:
            raise ValueError("PromptGenerator instance is required to load template from YAML string.")
        try:
            # Use the load_prompt_template_from_string method of PromptGenerator
            return deepcopy(self.prompt_generator.load_prompt_template_from_string(template_yaml_string))
        except Exception as e:
            # Catch potential errors from loading/parsing (e.g., YAMLError, validation errors)
            raise ValueError(f"Failed to load or parse template YAML for mutation: {e}")


    def _mutate_context_modifier(self, template_data: Dict[str, Any]) -> bool:
        """Attempts to mutate a context modifier (e.g., tone, persona)."""
        if "context_modifiers_schema" not in template_data or not template_data["context_modifiers_schema"]:
            return False

        schema = template_data["context_modifiers_schema"]
        modifiable_keys: List[Tuple[str, List[str]]] = []
        if "tone" in schema: modifiable_keys.append(("tone", self.common_tones))
        if "persona" in schema: modifiable_keys.append(("persona", self.common_personas))
        # Add more like "style" if defined in common_tones or a separate list

        if not modifiable_keys:
            return False

        key_to_mutate,
        value_options = random.choice(modifiable_keys)
        current_value = schema.get(key_to_mutate)

        new_value_options = [v for v in value_options if v != current_value]
        if not new_value_options: # Only one option or current value is the only one
            return False

        schema[key_to_mutate] = random.choice(new_value_options)
        # Also update the system prompt if it directly references these via {{ context_modifiers.key }}
        # This is tricky as it requires parsing and re-rendering the system prompt.
        # For this prototype, we only change the schema value. The template should use these.
        # A more advanced mutator might try to find and replace in the prompt_structure.
        # For instance, if system prompt has "Persona: {{ context_modifiers.persona | default('default_agent') }}"
        # and we change schema.persona, the Jinja rendering will pick it up.
        # If it has "Persona: specific_value_here", this mutation won't affect it.
        # This assumes templates are written to leverage the context_modifiers_schema dynamically.
        return True

    def _mutate_add_clarification_phrase(self, template_data: Dict[str, Any]) -> bool:
        """Attempts to add a clarification phrase to a message content."""
        if "prompt_structure" not in template_data or not template_data["prompt_structure"]:
            return False

        # Choose a random segment to modify (user or system role preferably)
        mutable_segments_indices = [
            i for i, seg in enumerate(template_data["prompt_structure"])
            if isinstance(seg, dict) and seg.get("role") in ["user", "system"] and "content" in seg
        ]
        if not mutable_segments_indices:
            return False

        idx_to_mutate = random.choice(mutable_segments_indices)
        segment = template_data["prompt_structure"][idx_to_mutate]

        phrase_to_add = random.choice(self.clarification_phrases)

        # Add to beginning or end (randomly)
        if random.choice([True, False]):
            segment["content"] = phrase_to_add + segment["content"]
        else:
            segment["content"] = segment["content"] + " " + phrase_to_add.strip() # Ensure space
        return True

    def _mutate_rephrase_static_message(self, template_data: Dict[str, Any]) -> bool:
        """Attempts to rephrase a known static part of a message."""
        if "prompt_structure" not in template_data or not template_data["prompt_structure"]:
            return False

        found_and_mutated = False
        for segment in template_data["prompt_structure"]:
            if not isinstance(segment, dict) or "content" not in segment:
                continue

            original_content = segment["content"]
            for static_phrase, alternatives in self.alternative_phrasings.items():
                if static_phrase in original_content:
                    # Choose a random alternative (that isn't the current phrase)
                    valid_alternatives = [alt for alt in alternatives if alt != static_phrase] # Should not be empty
                    if not valid_alternatives: # if static_phrase is the only one, pick any other from list
                        valid_alternatives = [alt for alt in alternatives if alt != original_content] # a bit redundant
                        if not valid_alternatives and len(alternatives) > 0 : valid_alternatives = alternatives


                    if valid_alternatives:
                        new_phrase = random.choice(valid_alternatives)
                        segment["content"] = original_content.replace(static_phrase, new_phrase, 1) # Replace first instance
                        found_and_mutated = True
                        break # Mutate only one per call for simplicity
            if found_and_mutated:
                break
        return found_and_mutated

    # Placeholder for other mutation types
    def _mutate_numerical_constraint(self, template_data: Dict[str, Any]) -> bool:
        """Placeholder: Attempts to alter a numerical value in a constraint by a small percentage."""
        # This would require identifying numerical constraints within the template structure,
        # e.g. "Summarize in {{ max_sentences }} sentences." where max_sentences is part of the template,
        # or within a 'constraints' section of the YAML if defined.
        # For this prototype, this is too complex without a very specific template structure.
        return False


    def mutate_template(self, template_yaml_string: str,
                        existing_template_data: Optional[Dict[str, Any]] = None,
                        mutation_type: Optional[str] = None) -> str:
        """
        Applies a random mutation (or a specific type if provided) to the given prompt template.

        Args:
            template_yaml_string (str): The original prompt template as a YAML string.
            existing_template_data (Optional[Dict[str, Any]]): Pre-parsed template data.
                If provided, `template_yaml_string` might only be used if parsing fails
                or as a fallback (though current logic prioritizes this).
            mutation_type (Optional[str]): Specific type of mutation to apply.
                If None, a random mutation is chosen.
                Supported: "context_modifier", "add_clarification", "rephrase_static"

        Returns:
            str: The mutated prompt template as a YAML string.
                 Returns the original YAML string if no mutation could be applied.
        """
        template_data = self._load_template_if_needed(template_yaml_string, existing_template_data)

        # Available mutation functions
        mutation_functions = {
            "context_modifier": self._mutate_context_modifier,
            "add_clarification": self._mutate_add_clarification_phrase,
            "rephrase_static": self._mutate_rephrase_static_message,
            # "numerical_constraint": self._mutate_numerical_constraint, # Add when implemented
        }

        chosen_mutation_func = None
        if mutation_type and mutation_type in mutation_functions:
            chosen_mutation_func = mutation_functions[mutation_type]
        elif mutation_type:
            print(f"Warning: Unknown mutation_type '{mutation_type}'. Choosing randomly.")

        if not chosen_mutation_func:
            # Shuffle and try mutations until one succeeds or all fail
            available_types = list(mutation_functions.keys())
            random.shuffle(available_types)

            success = False
            for m_type in available_types:
                if mutation_functions[m_type](template_data):
                    success = True
                    # print(f"Applied mutation: {m_type}") # For debugging
                    break
            if not success:
                return yaml.dump(template_data, sort_keys=False, allow_unicode=True) # No mutation applied or original data
        else:
            if not chosen_mutation_func(template_data):
                 return yaml.dump(template_data, sort_keys=False, allow_unicode=True) # Chosen mutation failed

        # Convert mutated data back to YAML string
        try:
            mutated_yaml_string = yaml.dump(template_data, sort_keys=False, allow_unicode=True)
            return mutated_yaml_string
        except yaml.YAMLError as e:
            # Should not happen if template_data was valid and mutations are simple value changes
            print(f"Error dumping mutated template to YAML: {e}")
            return template_yaml_string # Fallback to original if dump fails


# Example Usage:
if __name__ == "__main__":
    # This example requires PromptGenerator to be in thePYTHONPATH or same directory for _load_template_if_needed
    # For standalone testing, you might mock or pass None for prompt_generator and use existing_template_data.

    # Setup a dummy PromptGenerator for the example if the class is available
    pg_instance = None
    if PromptGenerator:
        # Create a dummy templates directory if FileSystemLoader in PromptGenerator needs it
        import os
        if not os.path.exists("templates"):
            os.makedirs("templates")
        pg_instance = PromptGenerator(template_path="templates")

    mutator = PromptMutator(prompt_generator=pg_instance)

    sample_yaml = """
template_id: "sample_interaction_v1"
version: 1
description: "A sample prompt for testing mutations."
input_variables:
  - name: "user_query"
    type: "string"
context_modifiers_schema:
  tone: "formal"
  persona: "assistant"
prompt_structure:
  - role: "system"
    content: "You are an assistant. Your persona is {{ context_modifiers.persona | default('neutral_assistant') }} and tone is {{ context_modifiers.tone | default('neutral') }}."
  - role: "user"
    content: "Hello, I need help with {{ user_query }}."
  - role: "system"
    content: "Please provide details."
safety_guardrails:
  global_instructions: "Be helpful and harmless."
"""
    print("--- Original Template ---")
    print(sample_yaml)

    if not pg_instance:
        print("\nSkipping mutation example that requires PromptGenerator instance for YAML loading.")
        print("To run full example, ensure PromptGenerator is importable.")
    else:
        print("\n--- Attempting Random Mutation ---")
        mutated_template_1 = mutator.mutate_template(sample_yaml)
        print(mutated_template_1)

        print("\n--- Attempting Specific Mutation: Context Modifier ---")
        mutated_template_2 = mutator.mutate_template(sample_yaml, mutation_type="context_modifier")
        print(mutated_template_2)

        print("\n--- Attempting Specific Mutation: Add Clarification ---")
        mutated_template_3 = mutator.mutate_template(sample_yaml, mutation_type="add_clarification")
        print(mutated_template_3)

        print("\n--- Attempting Specific Mutation: Rephrase Static ---")
        mutated_template_4 = mutator.mutate_template(sample_yaml, mutation_type="rephrase_static")
        print(mutated_template_4)

        # Example with pre-parsed data (doesn't strictly need prompt_generator then)
        print("\n--- Mutation with pre-parsed data (rephrase_static) ---")
        mutator_no_pg = PromptMutator(prompt_generator=None) # Simulate no PG
        try:
            parsed_data = yaml.safe_load(sample_yaml)
            mutated_from_parsed = mutator_no_pg.mutate_template("",existing_template_data=parsed_data, mutation_type="rephrase_static")
            print(mutated_from_parsed)
        except Exception as e:
            print(f"Error in pre-parsed example: {e}")


```

**Key aspects of `PromptMutator`:**

*   **Conceptual Nature:** This is a simple, rule-based mutator. Real-world mutators for prompt engineering might involve more sophisticated NLP techniques, genetic algorithms for prompt structure, or learned mutation strategies.
*   **Dependency on `PromptGenerator`:** It can optionally take a `PromptGenerator` instance to load YAML strings. If mutations are always performed on pre-parsed dictionary data, the `PromptGenerator` is not strictly needed by `PromptMutator` itself. The import is made optional.
*   **Mutation Types:**
    *   `_mutate_context_modifier`: Changes values in `context_modifiers_schema` (e.g., `tone`, `persona`) from predefined lists. Assumes the template uses these schema values dynamically (e.g., `{{ context_modifiers.tone }}`).
    *   `_mutate_add_clarification_phrase`: Adds a random predefined phrase to the beginning or end of a system or user message.
    *   `_mutate_rephrase_static_message`: Looks for known static phrases in message content and replaces them with one of their predefined alternatives.
    *   `_mutate_numerical_constraint`: Placeholder for a more complex mutation type.
*   `mutate_template` method:
    *   Can apply a specific mutation type or choose one randomly.
    *   Loads YAML string to a dictionary using `PromptGenerator` if needed (and if an instance is available).
    *   Applies the chosen mutation function.
    *   Dumps the (potentially) modified dictionary back to a YAML string.
    *   Returns the original YAML if a mutation cannot be applied or fails.
*   Uses `deepcopy` to avoid modifying the original template data if it's passed around.
*   The `if __name__ == "__main__":` block shows example usage.

This class provides the "exploration" part of a conceptual optimization loop. The `OptimizationAgent` will use this to generate new prompt candidates.
