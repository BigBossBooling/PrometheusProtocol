# Prometheus Protocol: PromptObject Editor UI Concepts

This document outlines the conceptual design for the PromptObject Editor UI, with a focus on integrating feedback from the GIGO (Garbage In, Garbage Out) Guardrail.

## I. Editor Purpose and Goals

The PromptObject Editor allows users to:
- Create new `PromptObject` instances from scratch.
- Edit existing `PromptObject` instances (e.g., loaded from templates).
- Receive real-time and on-demand validation feedback via the GIGO Guardrail.
- Save valid `PromptObject` instances as templates.

## II. Main Editor Layout

The editor will be divided into logical sections for clarity and ease of use.

### A. Core Prompt Components Panel

This panel contains input fields for the primary elements of a `PromptObject`.

1.  **Role:**
    *   **UI Element:** Single-line text input field.
    *   **Label:** "Role"
    *   **Placeholder Text (Example):** "e.g., Expert Python programmer, Sarcastic pirate, Helpful assistant"
    *   **Description:** Defines the persona or role the AI should adopt.

2.  **Context:**
    *   **UI Element:** Multi-line text area (resizable).
    *   **Label:** "Context"
    *   **Placeholder Text (Example):** "Provide background information, relevant history, or situational details..."
    *   **Description:** The broader situation or background for the AI's task.

3.  **Task:**
    *   **UI Element:** Multi-line text area (resizable).
    *   **Label:** "Task"
    *   **Placeholder Text (Example):** "Clearly define the specific action the AI should perform..."
    *   **Description:** The specific, actionable instruction for the AI.

4.  **Constraints:**
    *   **UI Element:** Dynamic list editor.
        *   An "Add Constraint" button allows users to add new constraint input fields.
        *   Each constraint is a single-line text input.
        *   Each constraint input has a "Remove" button (e.g., an 'X' icon) next to it.
    *   **Label:** "Constraints"
    *   **Placeholder Text (for new constraint input):** "e.g., Response must be under 200 words, Use a friendly tone"
    *   **Description:** Rules or limitations the AI's output must adhere to.

5.  **Examples:**
    *   **UI Element:** Dynamic list editor (similar to Constraints).
        *   An "Add Example" button.
        *   Each example is a single-line text input (for V1, could be expanded to input/output pairs later).
        *   Each example input has a "Remove" button.
    *   **Label:** "Examples"
    *   **Placeholder Text (for new example input):** "e.g., User: Hello -> AI: Hi there!"
    *   **Description:** Concrete examples to guide the AI's response style or format.

6.  **Tags:**
    *   **UI Element:** Tag input field.
        *   Allows users to type multiple tags.
        *   Tags could be separated by commas or Enter key.
        *   Displayed tags might appear as "pills" with a remove ('X') button on each.
    *   **Label:** "Tags"
    *   **Placeholder Text (Example):** "e.g., summarization, creative-writing, python"
    *   **Description:** Keywords for categorizing and searching for this prompt.

### B. Metadata Information Panel (Read-only)

This panel displays non-editable metadata associated with the current `PromptObject`. It might be a collapsible section or a footer area.

*   **Prompt ID:** (e.g., `prompt_id: abcdef-1234...`)
*   **Version:** (e.g., `Version: 3`)
*   **Created At:** (e.g., `Created: 2023-10-27T10:00:00Z`)
*   **Last Modified At:** (e.g., `Modified: 2023-10-27T12:30:00Z`)

### C. Actions Panel / Toolbar

This area contains buttons for performing actions related to the prompt being edited.

*   **[Validate Prompt] Button:**
    *   Manually triggers a full validation of the current prompt content against the GIGO Guardrail.
*   **[Save as Template] Button:**
    *   Initiates the process of saving the current `PromptObject` as a named template (interacts with `TemplateManager`).
*   **[Load Template] Button:**
    *   Opens an interface to browse and load existing templates (interacts with `TemplateManager`).
*   **(Optional) [Clear Editor] Button:**
    *   Resets all fields to their default empty state.
*   **(Optional) [Duplicate Prompt] Button:**
    *   Creates a new unsaved prompt pre-filled with the current editor's content (gets a new `prompt_id`).
*   **[Execute with Jules] Button:**
    *   Triggers the execution of the current `PromptObject` with the hypothetical Jules AI engine (conceptually calling `JulesExecutor.execute_prompt()`).
    *   The response (content or error) is displayed in a new "Jules Response Panel."
    *   This button might be disabled if the prompt has GIGO Guardrail errors.

### D. Execution Settings Panel (Optional)

This panel allows users to specify common execution parameters for the hypothetical Jules AI, which would override any system defaults set by the `JulesExecutor`. If values are not set here by the user for a particular prompt, the `JulesExecutor`'s defaults for those specific parameters would apply. These settings are stored in the `PromptObject.settings` dictionary.

1.  **Temperature:**
    *   **UI Element:** Number input field or a slider.
    *   **Label:** "Temperature (e.g., 0.0 - 1.0)"
    *   **Placeholder/Default Hint:** "Default: 0.7 (from executor)"
    *   **Description:** Controls the randomness/creativity of the AI's output. Lower values (e.g., 0.2) make the output more focused and deterministic; higher values (e.g., 0.9) make it more random and creative.
    *   **Binding (Conceptual):** `PromptObject.settings['temperature']`

2.  **Max Tokens:**
    *   **UI Element:** Number input field.
    *   **Label:** "Max Tokens (e.g., 10 - 2048)"
    *   **Placeholder/Default Hint:** "Default: 500 (from executor)"
    *   **Description:** Sets a limit on the maximum number of tokens (roughly words or parts of words) the AI should generate in its response.
    *   **Binding (Conceptual):** `PromptObject.settings['max_tokens']`

3.  **Other Potential Settings (Examples - V2+ or if Jules API supports):**
    *   **Top-p:** (Number input/slider) - Controls nucleus sampling.
    *   **Top-k:** (Number input/slider) - Controls top-k sampling.
    *   **Presence Penalty:** (Number input/slider) - Penalizes new tokens based on whether they appear in the text so far.
    *   **Frequency Penalty:** (Number input/slider) - Penalizes new tokens based on their existing frequency in the text so far.

**Note on UI Behavior:**
*   This panel might be collapsible or appear in an "Advanced Settings" section of the editor to keep the primary interface clean for users who don't need to adjust these parameters.
*   Clear indication should be given if a field is left blank, implying the system/executor default will be used.

---
*Next sections will detail GIGO Guardrail integration, validation messages, and interaction flows.*

## III. GIGO Guardrail Integration: Inline Validation Feedback

This section details how feedback from `core.guardrails.validate_prompt()` is presented directly to the user within the editor UI. The goal is to provide immediate and contextual guidance.

### A. General Principles

*   **Real-time/Near Real-time:** Validation should occur as the user interacts, providing swift feedback.
*   **Clarity:** Error messages should be user-friendly and clearly indicate the issue and the field involved.
*   **Non-intrusive:** While clear, feedback should not be overly disruptive to the user's flow.

### B. Field-Specific Inline Feedback

Validation is conceptually triggered by `core.guardrails.validate_prompt()`. The UI then reflects any raised exceptions (e.g., `MissingRequiredFieldError`, `InvalidListTypeError`, `InvalidListItemError`).

1.  **`role` (Text Input):**
    *   **Validation:** Checks if empty or whitespace (triggers `MissingRequiredFieldError`).
    *   **UI Feedback on Error:**
        *   A descriptive error message (e.g., "Role must be a non-empty string.") appears directly below the input field.
        *   Example for placeholder: 'Role: Contains unresolved placeholder text like "[INSERT_ACTOR_TYPE]". Please replace it with specific content.'
        *   The input field's border turns red.
        *   (Optional) An error icon (e.g., a small red circle with an '!') appears next to the field.

2.  **`context` (Text Area):**
    *   **Validation:** Checks if empty or whitespace (triggers `MissingRequiredFieldError`).
    *   **UI Feedback on Error:** Similar to `role` (message "Context must be a non-empty string.", red border, optional icon).
        *   Example for placeholder: 'Context: Contains unresolved placeholder text like "{{IMPORTANT_DETAIL}}". Please replace it with specific content.'

3.  **`task` (Text Area):**
    *   **Validation:** Checks if empty or whitespace (triggers `MissingRequiredFieldError`).
    *   **UI Feedback on Error:** Similar to `role` (message "Task must be a non-empty string.", red border, optional icon).
        *   Example for placeholder: 'Task: Contains unresolved placeholder text like "<SPECIFIC_ACTION>". Please replace it with specific content.'

4.  **`constraints` (Dynamic List Editor - for each constraint item):**
    *   **Validation (for each item):** Checks if the constraint string is empty or whitespace (triggers `InvalidListItemError`).
    *   **Validation (for the list itself):** Checks if `constraints` (if not None) is a list (triggers `InvalidListTypeError` - less likely with a dedicated list editor UI but important for programmatic checks).
    *   **UI Feedback on Item Error:**
        *   The specific constraint text input field that is invalid gets a red border.
        *   An error message (e.g., "Each constraint must be a non-empty string.") appears directly below that specific input field.
        *   Example for placeholder: 'Constraints (Item 2): Contains unresolved placeholder text like "[DEFINE_LIMIT]". Please replace it.'
        *   Example for repetitive item: 'Constraints (Item 3): Duplicate or very similar item found: "Be concise". Ensure each item is unique.'
        *   (Optional) An error icon appears next to the invalid item.
    *   **UI Feedback on List Type Error (Conceptual):** If the entire list structure were somehow invalid (e.g., if it could be replaced by non-list data), a message would appear near the "Constraints" label.

5.  **`examples` (Dynamic List Editor - for each example item):**
    *   **Validation (for each item):** Checks if the example string is empty or whitespace (triggers `InvalidListItemError`).
    *   **Validation (for the list itself):** Checks if `examples` (if not None) is a list (triggers `InvalidListTypeError`).
    *   **UI Feedback on Item Error:** Similar to `constraints` items (red border on the specific item, message "Each example must be a non-empty string.", optional icon).
        *   Example for placeholder: 'Examples (Item 1): Contains unresolved placeholder text like "<USER_INPUT_EXAMPLE>". Please replace it.'
        *   Example for repetitive item: 'Examples (Item 2): Duplicate or very similar item found: "User: Hi -> AI: Hello". Ensure each item is unique.'
    *   **UI Feedback on List Type Error (Conceptual):** Similar to `constraints`.

6.  **`tags` (Tag Input Field - for each tag):**
    *   **Validation (for each tag):** Checks if a tag string is empty or whitespace (triggers `InvalidListItemError` if the `tags` list contains such an item).
    *   **Validation (for the list itself):** Checks if `tags` (if not None and not empty) is a list (triggers `InvalidListTypeError`).
    *   **UI Feedback on Item Error:**
        *   If a specific tag "pill" represents an invalid (e.g., empty) tag, that pill could be highlighted in red.
        *   An error message (e.g., "Each tag must be a non-empty string.") could appear below the tag input area if an attempt is made to add an invalid tag, or associated with the specific invalid tag pill.
    *   **UI Feedback on List Type Error (Conceptual):** Similar to `constraints`.

### C. Timing of Inline Validation

*   **On Blur:** For single-line text inputs (`role`) and text areas (`context`, `task`), validation for that specific field runs when the field loses focus.
*   **On Item Add/Edit (for Lists):**
    *   For `constraints` and `examples` items, validation for an individual item occurs when it's added or when an existing item loses focus after an edit.
    *   For `tags`, validation for a tag can occur as it's being entered or when the user attempts to finalize adding it (e.g., hits Enter or comma).
*   **On Full Validation Action:** A comprehensive validation of all fields is triggered when the user clicks the "[Validate Prompt]" button or attempts an action that requires a valid prompt (e.g., "[Save as Template]"). All current errors will be displayed simultaneously.

---
*Next section: Overall Validation Status Display and Error Summary List.*

## IV. Overall Validation Status Display

Beyond inline feedback for specific fields, the editor should provide a clear, at-a-glance summary of the entire prompt's validation status.

*   **UI Element:** A dedicated status bar or area, perhaps at the top or bottom of the editor interface.
*   **Content and Behavior:**
    *   **If Valid:**
        *   Displays a message like: "**Status: Valid**" (text could be green).
        *   (Optional) A green checkmark icon.
    *   **If Invalid:**
        *   Displays a message like: "**Status: 3 issues found**" (text could be red). The number dynamically updates based on the count of current validation errors.
        *   (Optional) A red warning or error icon.
        *   Clicking on this status message (when errors are present) could:
            *   Expand or scroll to the "GIGO Guardrail Error Summary List" (detailed in the next section).
            *   Alternatively, it could highlight or navigate to the first field with an error.
*   **Updates:** This status display updates dynamically whenever a validation check occurs (on blur, on item add/edit, or on full validation action).

---
*Next section: GIGO Guardrail Error Summary List.*

## V. GIGO Guardrail Error Summary List

For situations where multiple validation errors exist, or when a user requests a full validation, a dedicated summary list provides a clear overview of all issues.

*   **UI Element:** A distinct panel or section within the editor. This could be:
    *   Initially collapsed and expandable by the user (e.g., by clicking the "Status: X issues found" message or a dedicated "Show Errors" button).
    *   Automatically shown when a "Validate Prompt" action reveals errors.
*   **Content:**
    *   If no errors, it might display a message like "No validation issues found." or remain hidden/collapsed.
    *   If errors are present, it displays a list of all current validation errors.
*   **Each Error Item in the List:**
    *   **Field Indication:** Clearly states which field or part of the prompt the error pertains to (e.g., "Role:", "Context:", "Constraint #2:", "Tag '  ':").
    *   **Error Message:** Displays the specific, user-friendly error message generated by the GIGO Guardrail (e.g., "Must be a non-empty string.", "Each tag must be a non-empty string.", "Unresolved placeholder '[PLACEHOLDER]' found.", "Duplicate item found in Constraints.").
    *   **Navigation (Recommended):** Clicking on an error item in this list should:
        *   Scroll the editor view to the corresponding input field or list item.
        *   Focus the cursor on that input field, if applicable.
        *   (Optional) Briefly highlight the problematic field.
*   **Dynamic Updates:** The list updates whenever a full validation is performed, reflecting the current set of errors.

---
*Next section: Interaction with TemplateManager.*

## VI. Interaction with TemplateManager

The PromptObject Editor seamlessly integrates with the `TemplateManager` to allow users to save their work as reusable templates and load existing templates. GIGO Guardrail validation is a key part of this workflow.

### A. Saving a Prompt as a Template

1.  **User Action:** Clicks the **"[Save as Template]"** button in the Actions Panel.
2.  **GIGO Validation:**
    *   The system first triggers a full validation of the current prompt content using the `core.guardrails.validate_prompt()` logic.
    *   **If Validation Fails:**
        *   The save operation is prevented.
        *   Inline validation errors and the Error Summary List are displayed/updated, showing all issues.
        *   A clear message informs the user (e.g., "Please fix the validation errors before saving as a template.").
    *   **If Validation Succeeds:**
        *   Proceed to the next step.
3.  **Prompt for Template Name:**
    *   A modal dialog or input prompt appears, asking the user to "Enter a name for this template:".
    *   Input validation for the template name itself (e.g., cannot be empty, perhaps character restrictions if not handled by `TemplateManager`'s sanitization transparently) should occur here.
4.  **Saving Operation (Conceptual):**
    *   Upon confirming a valid template name, the system conceptually calls `TemplateManager.save_template(current_prompt_object, template_name)`.
    *   `current_prompt_object` refers to the `PromptObject` instance constructed from the current state of the editor fields.
    *   The `TemplateManager` handles the actual file system operation and name sanitization for the filename. The `TemplateManager.save_template` method automatically handles version incrementing if a template with the same base name already exists. The `PromptObject` instance in the editor will have its `version` and `last_modified_at` attributes updated to match the saved version.
5.  **Feedback to User:**
    *   On successful save: A confirmation message (e.g., "Template 'My Awesome Prompt' saved as version X successfully!"). The `PromptObject` in the editor (including its displayed metadata like version and last modified at) should update to reflect the details of the saved version (as returned by `TemplateManager.save_template`).
    *   On failure (e.g., `TemplateManager` raises an error): An appropriate error message is displayed.

### B. Loading a Template

1.  **User Action:** Clicks the **"[Load Template]"** button in the Actions Panel.
2.  **Display Template List & Version Selection:**
    *   A modal dialog or a dedicated view appears.
    *   It first lists available base template names (derived from the keys of the dictionary returned by `TemplateManager.list_templates()`).
    *   The list should be searchable or sortable.
    *   When a user selects a base template name from this list:
        *   If multiple versions exist for that template (from the list of versions associated with that key), the UI then presents these available version numbers (e.g., in a secondary dropdown or list: "Available versions: [1, 2, 3] - Latest: 3").
        *   The user can select a specific version or choose an option like "Load Latest."
3.  **User Selection:** The user selects a template from the list.
4.  **Loading Operation (Conceptual):**
    *   Upon selection of a base name and a specific version (or "Latest"), the system conceptually calls `TemplateManager.load_template(selected_base_name, version=selected_version_or_none_for_latest)`.
5.  **Populate Editor:**
    *   The `PromptObject` returned by `load_template` is used to populate all the fields in the PromptObject Editor (Role, Context, Task, Constraints, Examples, Tags).
    *   Metadata fields (Prompt ID, Version, Created At, Last Modified At) are also updated from the loaded template.
    *   Since a loaded template should already be valid (as it passed GIGO checks before being saved), no immediate validation errors should appear.
6.  **Feedback to User:**
    *   On successful load: The editor fields are updated. (Optional: a small confirmation like "Template 'Existing Prompt' loaded.")
    *   On failure (e.g., `TemplateManager` raises `FileNotFoundError` or `TemplateCorruptedError`): An appropriate error message is displayed to the user.

---
*End of PromptObject Editor UI Concepts document.*

## VIII. Jules Execution and Response Display (for Single Prompt)

This section describes how the execution of a single `PromptObject` is initiated and how the resulting `AIResponse` is displayed.

### A. Initiating Execution
*   The user clicks the **"[Execute with Jules]"** button in the Actions Panel.
*   **Pre-Execution Checks (Conceptual):**
    *   The system should ensure the current `PromptObject` is valid according to GIGO Guardrail rules. If not, execution might be blocked, or a warning shown, guiding the user to validate/fix the prompt.
    *   The system might also run `RiskIdentifier` and display any identified risks, allowing the user to proceed with execution or revise the prompt. (Risks typically don't block execution but advise).

### B. "Jules Response Panel"
*   A new panel or area within the editor, possibly appearing or expanding upon execution.
*   **Content when `AIResponse.was_successful` is True:**
    *   **AI-Generated Content:**
        *   Displays `AIResponse.content` in a read-only text area.
        *   The text area should be scrollable and support standard text selection for copying.
        *   A dedicated "[Copy Response]" button should be available for easily copying the entire content.
        *   If the AI response content is formatted (e.g., Markdown, code blocks), the UI should attempt to render it appropriately for readability (e.g., display rendered Markdown, apply syntax highlighting to code). A toggle to view "Raw Text" vs. "Rendered View" could be beneficial for users needing to copy the exact source or inspect formatting.
    *   **Response Metadata:**
        *   Clearly display key metadata. This could be a small, well-labeled section within the response panel or a collapsible "Details" accordion.
        *   Example: `Tokens Used: 152`, `Finish Reason: stop`, `Model: jules-conceptual-stub-v1-dynamic`, `Response Time: 1.2s` (if calculable from `timestamp_request_sent` and `timestamp_response_received` in `AIResponse`).
    *   **Feedback Collection UI:**
        *   This feedback form (for ratings, tags, notes, "Used in Final Work" flag, as per `output_analytics.md`) should appear clearly associated with the displayed AI response, prompting the user to provide their assessment for *this specific execution*.
*   **Content when `AIResponse.was_successful` is False:**
        *   Displays `AIResponse.error_message` prominently. This message should be user-friendly and actionable, as defined in `prometheus_protocol/concepts/error_handling_recovery.md`.
        *   Examples:
            *   "Authentication Error: Invalid or missing API key. Please verify your settings." (Could link to settings page).
            *   "Network Error: Unable to connect after multiple retries. Please check your connection and try again later."
            *   "Content Policy Violation: The request was blocked. Please review your prompt's content."
            *   "AI Service Overloaded: The AI model is currently busy. Please try again in a few moments."
        *   Relevant metadata like `jules_request_id_jules` or a general internal `AIResponse.response_id` might be shown with instructions like "If contacting support, please provide this ID: [ID]".
        *   Avoid displaying raw technical error details from `AIResponse.raw_jules_response` directly to the user unless it's a "developer mode" feature.
*   **Loading/Pending State:**
    *   While waiting for Jules's response: This panel might show a loading indicator (e.g., "Executing prompt with Jules...").
    *   If retries are occurring (as per strategies in `error_handling_recovery.md` for network issues, rate limits, server errors, model overload):
        *   The UI should indicate this: e.g., "Connection issue. Retrying (attempt 2 of 3)... Please wait."
        *   "AI model is busy. Retrying (attempt 1 of 3) in 5 seconds..."

---
*End of PromptObject Editor UI Concepts document.*

## VII. Risk Identifier Feedback Display

In addition to GIGO Guardrail's structural validation, the PromptObject Editor will display feedback from the `RiskIdentifier` to alert users about potential semantic or ethical risks in their prompts. This feedback is advisory and aims to guide responsible prompt engineering.

### A. General Principles for Displaying Risks

*   **Advisory Nature:** Risks are typically informational or warnings and, unlike GIGO errors, usually do **not** block saving a template. However, they should strongly encourage user review.
*   **Visual Distinction:** Identified risks should be visually distinguishable from GIGO Guardrail validation errors (which are about structural correctness). This could be through different icons, colors, or placement.
*   **Clarity and Actionability:** Messages should be clear, explain the potential risk, and suggest what the user might consider or how they might mitigate it.

### B. UI Integration Options

Identified risks could be displayed in one or more of the following ways:

1.  **Dedicated "Risk Analysis" Panel/Tab:**
    *   A separate panel or tab within the editor (e.g., alongside or below the "GIGO Guardrail Error Summary List").
    *   This panel would list all `PotentialRisk` items returned by `RiskIdentifier.identify_risks(current_prompt_object)`.
    *   **Each Risk Item Display:**
        *   **Icon/Color Coding:**
            *   `RiskLevel.INFO`: e.g., Blue information icon (ℹ️).
            *   `RiskLevel.WARNING`: e.g., Yellow warning icon (⚠️).
            *   `RiskLevel.CRITICAL`: e.g., Red critical/stop icon (🛑) (though V1 rules might not generate CRITICAL).
        *   **Risk Type (Category):** Display `PotentialRisk.risk_type.value` (e.g., "Keyword Watch", "Lack of Specificity").
        *   **Message:** Display `PotentialRisk.message`.
        *   **Offending Field:** If `PotentialRisk.offending_field` is present, indicate it (e.g., "Relevant Field: Task"). Clicking this could highlight the field in the editor.
        *   **Details:** If `PotentialRisk.details` exist, they could be shown in a tooltip or an expandable section for that risk item.

2.  **Integration into Overall Status/Summary:**
    *   The "Overall Validation Status Display" (Section IV) could be augmented:
        *   If GIGO errors exist: "Status: 3 GIGO issues, 2 Potential Risks found".
        *   If only risks exist: "Status: Valid (2 Potential Risks found)".
        *   If no GIGO errors and no risks: "Status: Valid".
    *   The "GIGO Guardrail Error Summary List" (Section V) could have a separate subsection for "Potential Risks" below the GIGO errors, formatted as described above.

3.  **Inline Annotations (More Advanced - V2 Consideration):**
    *   For some risk types, especially those tied to an `offending_field`, a subtle inline annotation (e.g., a small colored underline or icon next to the field) could appear. Hovering over it would show the risk message. This should be less visually demanding than GIGO error styling.

### C. Timing of Risk Identification

*   Risk identification would typically run alongside GIGO Guardrail checks:
    *   When the user clicks the "[Validate Prompt]" button.
    *   Before a "[Save as Template]" operation (after GIGO validation passes).
    *   Potentially, with a debounce, as the user types or on blur from major fields (though this might be more performance-intensive than GIGO checks and could be reserved for explicit actions if necessary). For V1, on explicit "Validate" or pre-save is sufficient.

### D. User Interaction with Risks

*   **No Blocking:** As mentioned, risks (especially INFO and WARNING) generally don't prevent saving. The UI should make this clear – they are for user consideration.
*   **Dismissal (V2 Consideration):** Future versions might allow users to "dismiss" or "acknowledge" specific risks for a session if they've reviewed them.

---
*End of PromptObject Editor UI Concepts document.*
