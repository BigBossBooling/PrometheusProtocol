# Prometheus Protocol: Prompt Engineering Framework - Technical Specification

## 1. Overview

This document details the technical specification for the Prometheus Protocol's Prompt Engineering Framework. This framework is the cornerstone of the system, enabling the creation, management, and execution of sophisticated AI prompts. It aims to provide a flexible, human-readable, and powerful way to define how humans interact with Large Language Models (LLMs).

## 2. Goals

*   Define a clear and extensible language for prompt templates.
*   Enable dynamic and secure injection of contextual information.
*   Allow precise control over LLM persona, tone, and style.
*   Specify how LLMs should format their responses.
*   Integrate safety guardrails and ethical considerations directly into prompts.
*   Ensure seamless integration with the broader EchoSphere ecosystem.

## 3. Prompt Template Language

Prometheus Protocol will adopt a **YAML-based schema** for defining prompt templates, combined with **Jinja2-like syntax** for dynamic content within text fields. YAML provides a human-readable structure for the template, while Jinja2 offers powerful templating capabilities.

**Schema Definition (`PromptTemplate`):**

A `PromptTemplate` will be a YAML object with the following top-level keys:

*   `template_id`: (String, Required) A unique identifier for the template (e.g., `user_greeting_formal_v1`).
*   `version`: (Integer, Required) Version number of the template.
*   `description`: (String, Optional) A brief description of the template's purpose.
*   `metadata`: (Object, Optional)
    *   `tags`: (List of Strings) Keywords for categorization.
    *   `created_by`: (String) Identifier of the creator.
    *   `created_at`: (Timestamp) Creation timestamp.
    *   `last_modified_at`: (Timestamp) Last modification timestamp.
*   `input_variables`: (List of Objects, Optional) Defines the dynamic variables the template expects. Each object has:
    *   `name`: (String, Required) The variable name (e.g., `user_name`).
    *   `description`: (String, Optional) Explanation of the variable.
    *   `type`: (String, Required) Data type (e.g., `string`, `integer`, `boolean`, `list`, `object`).
    *   `required`: (Boolean, Default: `true`) Whether the variable is mandatory.
    *   `default`: (Any, Optional) A default value if not provided.
*   `context_modifiers_schema`: (Object, Optional) Defines expected context modifiers from EchoSphere Behavioral Orchestrator (EBO).
    *   `persona`: (String, Optional) Expected persona identifier (e.g., `jules_formal`, `critter_playful`).
    *   `tone`: (String, Optional) Expected tone (e.g., `empathetic`, `assertive`).
    *   `style`: (String, Optional) Expected communication style (e.g., `concise`, `detailed`).
*   `prompt_structure`: (List of Objects, Required) Defines the sequence of messages or parts that form the final LLM prompt. Each object represents a message segment and has:
    *   `role`: (String, Required) The role of the message sender (e.g., `system`, `user`, `assistant`).
    *   `content`: (String, Required) The textual content of the message. Can include Jinja2 templating.
    *   `conditions`: (String, Optional) A Jinja2 expression. If it evaluates to false, this segment is skipped.
*   `response_formatting`: (Object, Optional) Directives for how the LLM should structure its output.
    *   `format_type`: (String, Required) Type of desired format (e.g., `json`, `bullet_points`, `text_summary`).
    *   `schema`: (Object, Optional) If `format_type` is `json`, this can be a JSON schema definition for the expected output.
    *   `instructions`: (String, Optional) Natural language instructions for formatting (e.g., "Summarize in 3 sentences or less.").
*   `safety_guardrails`: (Object, Optional)
    *   `global_instructions`: (String, Optional) General safety instructions to be prepended or appended (e.g., "Do not generate harmful content.").
    *   `topic_exclusions`: (List of Strings, Optional) Topics the LLM should avoid.
    *   `compliance_references`: (List of Strings, Optional) Links or references to Privacy Protocol principles or other compliance documents.

**Example YAML Prompt Template:**

```yaml
template_id: "customer_support_issue_resolution_v1"
version: 1
description: "A prompt to guide an assistant in resolving a customer issue."
metadata:
  tags: ["support", "resolution", "customer_service"]
  created_by: "josephis.wade"
  created_at: "2023-10-27T10:00:00Z"
  last_modified_at: "2023-10-27T10:00:00Z"
input_variables:
  - name: "customer_name"
    description: "The name of the customer."
    type: "string"
    required: true
  - name: "issue_description"
    description: "A summary of the customer's issue."
    type: "string"
    required: true
  - name: "previous_interactions_summary"
    description: "Summary of previous interactions, if any."
    type: "string"
    required: false
context_modifiers_schema:
  persona: "support_agent_empathetic"
  tone: "helpful"
  style: "clear_and_concise"
prompt_structure:
  - role: "system"
    content: |
      You are a helpful and empathetic customer support agent.
      Your goal is to resolve the customer's issue efficiently and courteously.
      Adhere to the company's support policies.
      Persona: {{ context_modifiers.persona | default('default_agent') }}
      Tone: {{ context_modifiers.tone | default('neutral') }}
      Style: {{ context_modifiers.style | default('standard') }}
  - role: "user"
    content: |
      Hello, my name is {{ customer_name }}.
      I am having an issue: {{ issue_description }}.
      {% if previous_interactions_summary %}
      Previous context: {{ previous_interactions_summary }}
      {% endif %}
      Please help me.
response_formatting:
  format_type: "text_summary"
  instructions: "Provide a step-by-step solution or clearly state the next actions. Keep the response under 150 words."
safety_guardrails:
  global_instructions: "Ensure all advice is constructive and safe. Do not ask for personally identifiable information unless strictly necessary for the resolution process and as per company guidelines."
  topic_exclusions:
    - "financial_advice"
    - "medical_diagnosis"
```

## 4. Contextual Variable Injection

*   **Mechanism**: Variables defined in `input_variables` will be injected into the `content` fields of `prompt_structure` segments using Jinja2 syntax (e.g., `{{ user_name }}`).
*   **Security**:
    *   Input sanitization will be performed on variables before injection to prevent prompt injection attacks, especially if variables originate from external user inputs.
    *   The templating engine will be configured to auto-escape HTML/XML characters by default if outputs might be rendered in such contexts, though primary LLM interaction is text.
*   **Data Source**: Variables are expected to be provided by the calling service, potentially enriched by the EchoSphere Enrichment Engine.

## 5. Persona & Tone Modifiers

*   **Source**: `context_modifiers` (e.g., `persona`, `tone`, `style`) are received from the EchoSphere Behavioral Orchestrator (EBO) as part of the `action_request` or `interaction_goal`.
*   **Translation**:
    *   These modifiers are injected into the prompt, typically in the `system` message, to guide the LLM's behavior (e.g., `Persona: {{ context_modifiers.persona }}`).
    *   The template can define default values for these modifiers if not provided.
    *   More complex translations (e.g., mapping a high-level persona `jules_playful` to a detailed set of instructions) can be managed by a dedicated service or within the prompt template itself using Jinja2 logic if feasible.

## 6. Response Formatting Directives

*   **Mechanism**: The `response_formatting` section of the template allows specifying the desired structure of the LLM's output.
*   `format_type`:
    *   `json`: The LLM is instructed to return a valid JSON object. The `schema` sub-field can provide a JSON schema that the LLM should adhere to.
    *   `bullet_points`: The LLM is instructed to list information as bullet points.
    *   `text_summary`: The LLM is instructed to provide a summary, potentially with length constraints.
    *   `custom_xml`: For specific XML structures if needed.
    *   `none` or `text`: Default, free-form text.
*   `instructions`: Provides natural language cues to the LLM on how to format its response (e.g., "Respond with a JSON object containing 'name' and 'email' fields."). These instructions will be incorporated into the final prompt sent to the LLM, often as part of the last `user` message or a `system` instruction.

## 7. Safety & Guardrail Integration

*   **Mechanism**: The `safety_guardrails` section allows embedding safety instructions directly.
*   `global_instructions`: These are general directives (e.g., "Do not generate hateful speech," "Cite sources if providing factual information"). These can be prepended to the system prompt or appended to the user's final message.
*   `topic_exclusions`: A list of topics the LLM should explicitly avoid discussing or generating content about. Logic within the prompt generation process can either instruct the LLM to refuse or to state it cannot discuss these topics.
*   `compliance_references`: References to external documents (e.g., Privacy Protocol principles, content policies) that the LLM should be aware of or that inform the prompt's construction. These are more for meta-guidance and ensuring prompts align with broader ethical frameworks.
*   **Dynamic Guardrails**: Beyond template-defined static guardrails, the system should allow for dynamic guardrails to be applied at runtime, potentially by an intermediary service before sending the prompt to the LLM.

## 8. Synergies

*   **EchoSphere Behavioral Orchestrator (EBO)**:
    *   EBO provides `action_request`, `interaction_goal`, and `context_modifiers` which are key inputs for selecting and populating prompt templates.
*   **EchoSphere Enrichment Engine**:
    *   This engine can provide some of the dynamic `input_variables` by enriching the context from various data sources.
*   **Privacy Protocol**:
    *   The principles from Privacy Protocol directly inform the design of `safety_guardrails` and data handling practices for `input_variables`.

## 9. Implementation Considerations

*   **Templating Engine**: A Python library like Jinja2 will be used for processing the templates.
*   **Validation**: YAML schema validation (e.g., using `jsonschema` with YAML loading) should be implemented for prompt templates. Input variable types should also be validated.
*   **Versioning**: The `version` field is crucial. A system for managing and retrieving specific versions of templates will be needed (as handled by `TemplateManager` in the conceptual design).
*   **Error Handling**: Robust error handling for template loading, parsing, variable injection, and unmet requirements (e.g., missing required variables).

## 10. Future Considerations

*   **A/B Testing Hooks**: Allowing different versions of prompts or segments for A/B testing.
*   **Prompt Chaining**: Defining sequences of prompts where the output of one becomes the input for another.
*   **Internationalization/Localization**: Designing templates to be easily adaptable to different languages.

This specification provides the foundational blueprint for the Prompt Engineering Framework. It will be iterated upon as implementation progresses and new requirements emerge.
