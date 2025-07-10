import yaml
from jinja2 import Environment, select_autoescape, FileSystemLoader, meta, StrictUndefined
from jinja2.exceptions import UndefinedError # Import UndefinedError
from typing import Dict, Any, List, Optional

class PromptGeneratorError(ValueError):
    """Custom exception for prompt generation errors."""
    pass

class PromptTemplateValidationError(PromptGeneratorError):
    """Custom exception for template validation errors."""
    pass

class PromptInputValidationError(PromptGeneratorError):
    """Custom exception for input variable validation errors."""
    pass

class PromptRenderingError(PromptGeneratorError):
    """Custom exception for errors during template rendering."""
    pass

class PromptGenerator:
    """
    Handles loading, parsing, and generating final LLM prompts from templates
    defined in YAML with Jinja2 syntax for dynamic content.
    """

    def __init__(self, template_path: str = "./templates"):
        """
        Initializes the PromptGenerator.

        Args:
            template_path (str): Path to the directory containing prompt templates.
                                 This is used by Jinja2's FileSystemLoader if templates
                                 are stored as separate files and referenced by name.
                                 For direct YAML string loading, this path might be conceptual.
        """
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(['html', 'xml'], disabled_extensions=('txt',)),
            undefined=StrictUndefined,  # Raise errors for undefined variables
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _validate_template_schema(self, template_data: Dict[str, Any]) -> List[str]:
        """
        Validates the basic structure of the loaded prompt template.
        """
        errors = []
        if not isinstance(template_data, dict): # Handles empty string case resulting in None
            errors.append("Template YAML must be a dictionary (object).")
            return errors # No point in further checks if not a dict

        required_keys = ["template_id", "version", "prompt_structure"]
        for key in required_keys:
            if key not in template_data:
                errors.append(f"Missing required top-level key: '{key}'")

        if "prompt_structure" in template_data:
            if not isinstance(template_data["prompt_structure"], list):
                errors.append("'prompt_structure' must be a list.")
            else:
                for i, segment in enumerate(template_data["prompt_structure"]):
                    if not isinstance(segment, dict):
                        errors.append(f"Segment {i} in 'prompt_structure' is not a dictionary.")
                        continue
                    if "role" not in segment:
                        errors.append(f"Segment {i} in 'prompt_structure' missing 'role'.")
                    if "content" not in segment:
                        errors.append(f"Segment {i} in 'prompt_structure' missing 'content'.")

        if "input_variables" in template_data:
            if not isinstance(template_data["input_variables"], list):
                errors.append("'input_variables' must be a list of objects.")
            else:
                for i, var_def in enumerate(template_data["input_variables"]):
                    if not isinstance(var_def, dict) or "name" not in var_def: # Relaxed: only 'name' is mandatory for schema
                        errors.append(f"Invalid definition for input_variable at index {i}. Must be dict with at least a 'name'.")
        return errors

    def _get_all_jinja_variables_from_template_data(self, template_data: Dict[str, Any]) -> set:
        """
        Parses all content and condition strings in template_data to find all Jinja variables.
        """
        all_vars = set()
        if not isinstance(template_data, dict): # Should have been caught by schema validation
            return all_vars

        for segment in template_data.get("prompt_structure", []):
            if not isinstance(segment, dict): continue # Should have been caught by schema

            content = segment.get("content", "")
            conditions = segment.get("conditions", "")
            try:
                if content:
                    parsed_content = self.jinja_env.parse(content)
                    all_vars.update(meta.find_undeclared_variables(parsed_content))
                if conditions:
                    parsed_conditions = self.jinja_env.parse(conditions)
                    all_vars.update(meta.find_undeclared_variables(parsed_conditions))
            except Exception as e:
                raise PromptRenderingError(f"Error parsing Jinja variables from segment: {segment}. Details: {e}")
        return all_vars

    def _validate_input_variables(
        self,
        template_data: Dict[str, Any],
        provided_variables: Dict[str, Any],
        all_jinja_vars_in_template: set
    ) -> List[str]:
        """
        Validates provided variables against the template's input_variables definition
        and actual variables used in Jinja expressions.
        """
        errors = []
        defined_vars_spec = template_data.get("input_variables", [])
        defined_var_names_in_spec = {v["name"] for v in defined_vars_spec}

        # 1. Check for missing required variables if they are defined in spec AND used in template
        for var_def in defined_vars_spec:
            var_name = var_def["name"]
            is_required = var_def.get("required", True)
            has_spec_default = "default" in var_def

            if is_required and var_name not in provided_variables and not has_spec_default:
                # Only error if it's genuinely used and will cause a Jinja UndefinedError
                # Jinja's StrictUndefined will catch this if it's rendered without a value or Jinja default filter
                # This explicit check here is more about contract adherence for 'required' flag.
                # We rely on StrictUndefined for actual rendering safety.
                # This specific check might be redundant if StrictUndefined is always active.
                # However, it can give more specific "missing required" errors vs generic "undefined".
                if var_name in all_jinja_vars_in_template:
                     # Check if Jinja default filter is used for this var in the template text
                    has_jinja_default_filter = False
                    for segment in template_data.get("prompt_structure", []):
                        content = segment.get("content", "")
                        if f"{{{{ {var_name} | default(" in content or f"{{{{ {var_name}|default(" in content :
                            has_jinja_default_filter = True
                            break
                    if not has_jinja_default_filter:
                        errors.append(f"Missing required input variable (defined in spec, used in template, no spec/Jinja default): '{var_name}'")


        # 2. Check for variables provided but not defined in 'input_variables' spec NOR used in template
        for provided_var_name in provided_variables.keys():
            if provided_var_name == "context_modifiers": continue # Special case

            is_in_spec = provided_var_name in defined_var_names_in_spec
            is_used_in_template = provided_var_name in all_jinja_vars_in_template

            # Also check for direct attribute access like {{ context_modifiers.persona }}
            # This is a bit naive, a full AST parse of Jinja would be better for complex cases.
            is_used_as_attribute_of_known_object = False
            for known_obj_name in all_jinja_vars_in_template: # e.g. known_obj_name = "context_modifiers"
                if f"{known_obj_name}.{provided_var_name}" in " ".join(
                    [s.get("content","") + s.get("conditions","") for s in template_data.get("prompt_structure",[]) if isinstance(s, dict)]
                ):
                    is_used_as_attribute_of_known_object = True
                    break

            if not is_in_spec and not is_used_in_template and not is_used_as_attribute_of_known_object:
                errors.append(f"Provided variable '{provided_var_name}' is not defined in 'input_variables' spec, not directly used in Jinja, nor as a direct attribute of a used object.")
        return errors

    def load_prompt_template_from_string(self, template_yaml_string: str) -> Dict[str, Any]:
        """
        Loads and parses a prompt template from a YAML string.
        """
        try:
            template_data = yaml.safe_load(template_yaml_string)
        except yaml.YAMLError as e:
            raise PromptTemplateValidationError(f"Invalid YAML format: {e}")

        schema_errors = self._validate_template_schema(template_data)
        if schema_errors:
            raise PromptTemplateValidationError(f"Template schema validation failed: {'; '.join(schema_errors)}")

        return template_data

    def generate_prompt(
        self,
        template_data: Dict[str, Any],
        dynamic_variables: Dict[str, Any],
        context_modifiers: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Generates the final list of prompt messages.
        """
        try:
            all_jinja_vars_in_template = self._get_all_jinja_variables_from_template_data(template_data)
        except PromptRenderingError as e: # Catch parsing errors from _get_all_jinja_variables_from_template_data
            raise PromptRenderingError(f"Failed to parse Jinja variables from template structure: {e}")

        input_validation_errors = self._validate_input_variables(template_data, dynamic_variables, all_jinja_vars_in_template)
        if input_validation_errors:
            raise PromptInputValidationError(f"Input variable validation failed: {'; '.join(input_validation_errors)}")

        final_prompt_messages = []
        render_context = dynamic_variables.copy()
        render_context["context_modifiers"] = context_modifiers if context_modifiers is not None else {}

        # Apply spec defaults to render_context if variable not provided
        for var_def in template_data.get("input_variables", []):
            var_name = var_def["name"]
            if var_name not in render_context and "default" in var_def:
                render_context[var_name] = var_def["default"]

        response_formatting = template_data.get("response_formatting", {})
        render_context["response_formatting_instructions"] = response_formatting.get("instructions", "")
        render_context["response_format_type"] = response_formatting.get("format_type", "text")

        safety_guardrails = template_data.get("safety_guardrails", {})
        render_context["safety_global_instructions"] = safety_guardrails.get("global_instructions", "")

        for segment_template in template_data.get("prompt_structure", []):
            role = segment_template["role"]
            content_template_str = segment_template["content"]

            if "conditions" in segment_template and segment_template["conditions"]:
                condition_expr_str = str(segment_template["conditions"])
                try:
                    # Compile the condition as an expression.
                    # The condition string from YAML *is* the Jinja expression.
                    # undefined_to_none=False ensures StrictUndefined behavior if var is missing.
                    condition = self.jinja_env.compile_expression(condition_expr_str, undefined_to_none=False)

                    # Evaluate the compiled expression in the current context.
                    if not condition(render_context):
                        continue
                except UndefinedError as e:
                     # e.message from Jinja's UndefinedError is usually like "'var_name' is undefined"
                     raise PromptRenderingError(f"Error evaluating condition '{condition_expr_str}': {e.message}.")
                except Exception as e:
                    # Catch other potential errors during condition compilation/evaluation
                    raise PromptRenderingError(f"Error evaluating condition '{condition_expr_str}': {e}")

            try:
                jinja_template = self.jinja_env.from_string(content_template_str)
                rendered_content = jinja_template.render(render_context)
                final_prompt_messages.append({"role": role, "content": rendered_content.strip()})
            except UndefinedError as e:
                 # e.message from Jinja's UndefinedError is usually like "'var_name' is undefined"
                 raise PromptRenderingError(f"Error rendering prompt segment: {e.message}. Segment: {segment_template}")
            except Exception as e:
                raise PromptRenderingError(f"Error rendering prompt segment content: {e}. Segment: {segment_template}")

        return final_prompt_messages

    def get_declared_input_variables(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns the 'input_variables' section from the template data.
        """
        return template_data.get("input_variables", [])


# Example Usage (can be moved to a test or example script)
if __name__ == "__main__":
    # Assume templates are in a ./templates directory or adjust path
    # For this example, we'll use load_prompt_template_from_string
    # Create a dummy templates directory if FileSystemLoader needs it, even if not directly used by string loading
    import os
    if not os.path.exists("templates"):
        os.makedirs("templates")

    generator = PromptGenerator(template_path="templates") # Path for Jinja loader

    sample_template_yaml = """
template_id: "greeting_v1"
version: 1
description: "A simple greeting prompt."
input_variables:
  - name: "user_name"
    description: "The name of the user."
    type: "string"
    required: true
  - name: "time_of_day"
    description: "e.g., morning, afternoon, evening"
    type: "string"
    required: false
    default: "day"
prompt_structure:
  - role: "system"
    content: |
      You are a friendly assistant.
      Current persona: {{ context_modifiers.persona | default('default') }}
      Response format hint: {{ response_formatting_instructions }}
      Global safety: {{ safety_global_instructions }}
  - role: "user"
    content: "Hello, my name is {{ user_name }}. Good {{ time_of_day }}!"
  - role: "user"
    content: "What's the weather like?"
    conditions: "context_modifiers.include_weather == true"
response_formatting:
  format_type: "text"
  instructions: "Keep it brief and friendly."
safety_guardrails:
  global_instructions: "Be polite."
    """

    try:
        template = generator.load_prompt_template_from_string(sample_template_yaml)
        print("Template loaded successfully:")
        # print(template)

        print("\n--- Variables declared in template's input_variables section ---")
        declared_vars = [v["name"] for v in template.get("input_variables", [])]
        print(declared_vars)

        print("\n--- Jinja variables found by parsing template content ---")
        # Note: get_template_variables also calls load_prompt_template_from_string
        # For efficiency, you might pass the loaded 'template' dict to a modified get_template_variables
        # This internal method call is for the example, tests use the public API or direct _method for whitebox.
        # found_jinja_vars = generator._get_all_jinja_variables_from_template_data(template)
        # print(found_jinja_vars)


        print("\n--- Generating prompt (Scenario 1) ---")
        dyn_vars1 = {"user_name": "Alice"}
        ctx_mods1 = {"persona": "cheerful_assistant", "include_weather": False}
        final_prompt1 = generator.generate_prompt(template, dyn_vars1, ctx_mods1)
        print("Generated Prompt 1:")
        for msg in final_prompt1:
            print(f"  Role: {msg['role']}, Content: {msg['content']}")

        print("\n--- Generating prompt (Scenario 2 - with weather) ---")
        dyn_vars2 = {"user_name": "Bob", "time_of_day": "evening"}
        ctx_mods2 = {"persona": "formal_bot", "include_weather": True}
        final_prompt2 = generator.generate_prompt(template, dyn_vars2, ctx_mods2)
        print("Generated Prompt 2:")
        for msg in final_prompt2:
            print(f"  Role: {msg['role']}, Content: {msg['content']}")

        print("\n--- Generating prompt (Scenario 3 - missing required var, should fail) ---")
        try:
            dyn_vars3 = {} # Missing user_name
            generator.generate_prompt(template, dyn_vars3, ctx_mods1)
        except ValueError as e:
            print(f"Error (expected): {e}")

        print("\n--- Generating prompt (Scenario 4 - undefined variable in template, should fail due to StrictUndefined) ---")
        # Modify template to include an undefined variable for testing StrictUndefined
        faulty_template_yaml = sample_template_yaml.replace("Good {{ time_of_day }}!", "Good {{ time_of_day }} and {{ undefined_var }}!") # type: ignore
        try:
            faulty_template = generator.load_prompt_template_from_string(faulty_template_yaml)
            generator.generate_prompt(faulty_template, dyn_vars1, ctx_mods1) # type: ignore
        except (PromptGeneratorError, UndefinedError) as e: # Catch Jinja's UndefinedError too
            print(f"Error (expected for undefined_var): {e}")


    except PromptGeneratorError as e:
        print(f"A PromptGeneratorError occurred: {e}")
    except ImportError:
        print("ImportError: Make sure 'PyYAML' and 'Jinja2' are installed. Run: pip install PyYAML Jinja2")
    except Exception as e:
        print(f"An unexpected error occurred in example: {e}")
