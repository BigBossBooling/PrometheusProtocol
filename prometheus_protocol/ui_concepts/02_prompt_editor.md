# UI Concept: PromptObject Editor

## 1. Overview

The PromptObject Editor is where users craft and refine individual prompts (instances of `PromptObject`). It provides dedicated input fields for each component of a prompt (role, context, task, constraints, examples, tags) and actions for managing templates. The design should facilitate clear and precise prompt construction.

## 2. Layout

A multi-panel layout is envisioned, possibly with a main editing area and a sidebar for actions, metadata, and validation feedback.

*   **Main Editing Panel:** Contains form fields for all editable `PromptObject` attributes.
*   **Side/Action Panel:** Contains action buttons (Save, Load), metadata display, and GIGO Guardrail feedback.

## 3. Key Elements

### 3.1. Main Editing Panel (Prompt Fields)

This panel is the core of the editor, allowing users to define their prompt.

*   **`role` Field:**
    *   **UI Element:** Single-line text input field.
    *   **Label:** "Role" or "AI Role"
    *   **Placeholder/Tooltip:** "e.g., Expert Python programmer, Sarcastic historian, Helpful assistant"

*   **`context` Field:**
    *   **UI Element:** Multi-line text area (resizable).
    *   **Label:** "Context"
    *   **Placeholder/Tooltip:** "Provide background information, relevant data, or the scenario for the AI."

*   **`task` Field:**
    *   **UI Element:** Multi-line text area (resizable).
    *   **Label:** "Task"
    *   **Placeholder/Tooltip:** "Clearly define what the AI should do. Start with an action verb."

*   **`constraints` Field (Dynamic List Input):**
    *   **UI Element:** A list editor.
    *   **Label:** "Constraints"
    *   **Functionality:**
        *   Displays current constraints as a list of editable text items.
        *   Button: "+ Add Constraint" to append a new, empty text input to the list.
        *   Each constraint item has a "Remove" (X) button next to it.
        *   Each constraint item is an editable text field.
    *   **Placeholder/Tooltip for list:** "Define rules or limitations for the AI's response (e.g., 'Response must be under 200 words', 'Output in JSON format')."

*   **`examples` Field (Dynamic List Input):**
    *   **UI Element:** A list editor, similar to `constraints`.
    *   **Label:** "Examples"
    *   **Functionality:**
        *   Displays current examples as a list of editable text items (or perhaps pairs of input/output if more advanced). For V1, simple text items.
        *   Button: "+ Add Example" to append a new, empty text input.
        *   Each example item has a "Remove" (X) button.
        *   Each example item is an editable text field (or text area for longer examples).
    *   **Placeholder/Tooltip for list:** "Provide concrete examples of desired input/output or style."

*   **`tags` Field (Dynamic List Input):**
    *   **UI Element:** A list editor for tags, often displayed as "pills" or "chips".
    *   **Label:** "Tags"
    *   **Functionality:**
        *   Displays current tags.
        *   Text input field to type a new tag; pressing Enter or comma adds it to the list.
        *   Each tag pill has a "Remove" (X) button.
        *   (Conceptual V2: Autocomplete suggestions from existing tags).
    *   **Placeholder/Tooltip:** "Add keywords for organization (e.g., 'blogging', 'python', 'summary')."

### 3.2. Side/Action Panel

This panel provides controls for managing the prompt and displays supplementary information.

*   **Action Buttons:**
    *   **"Save as Template" Button:**
        *   **Action:** Triggers `TemplateManager.save_template()`.
        *   **Interaction:** Prompts the user for a `template_name` (modal dialog or inline input).
    *   **"Load Template" Button:**
        *   **Action:** Allows loading an existing template.
        *   **Interaction:** Opens a modal dialog or dropdown listing available templates (from `TemplateManager.list_templates()`). Selecting a template populates the editor fields with its data.
    *   **(Conceptual) "Run/Execute Prompt" Button:** (Out of scope for pure UI concept, but a natural fit here for a full application).

*   **GIGO Guardrail Status Area:**
    *   **UI Element:** A small, non-intrusive section.
    *   **Functionality:**
        *   Displays real-time feedback from `GIGO Guardrail` (`validate_prompt()`).
        *   Example messages: "Role field is empty," "Constraint item #2 is invalid."
        *   Could use icons (e.g., green check for valid, yellow warning for issues).
        *   Initially, this might just be a static display area; dynamic updates as user types would be V2.

*   **Metadata Display Area:**
    *   **UI Element:** Read-only text fields or a formatted block.
    *   **Label:** "Prompt Details" or "Information"
    *   **Fields Displayed (from `PromptObject`):**
        *   `prompt_id`
        *   `version`
        *   `created_at` (formatted for readability)
        *   `last_modified_at` (formatted for readability)

## 4. Conceptual Note on Advanced UI

*   **Drag-and-Drop:** "Future enhancements could include a more visual 'drag-and-drop' interface for constructing prompt elements, allowing users to assemble prompts from a palette of predefined components (like 'Role Setter', 'Context Block', 'Task Definer') rather than just filling forms. This aligns with the 'K' principle's vision of a visual, intuitive construction process."

## 5. User Flow Examples

*   **Creating a new prompt:** User fills fields, adds constraints/examples/tags. Clicks "Save as Template", provides a name.
*   **Editing an existing template:** User clicks "Load Template", selects a template. Editor fields populate. User modifies content, saves again (potentially as a new template or overwriting).
*   **GIGO Guardrail Interaction:** As user types, if `validate_prompt()` (triggered on blur or periodically) finds an issue, a message appears in the GIGO Guardrail Status Area.

## 6. Design Principles Embodied

*   **KISS (Know Your Core, Keep it Clear):** Clearly defined fields for each part of the prompt. GIGO Guardrail helps maintain clarity.
*   **KISS (Iterate Intelligently, Integrate Intuitively):** Easy loading and saving of templates promotes iteration.
*   **KISS (Systematize for Scalability):** Consistent structure for all prompts.
