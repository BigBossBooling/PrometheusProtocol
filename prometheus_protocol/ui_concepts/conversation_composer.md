# Prometheus Protocol: Conversation Composer UI Concepts

This document outlines the conceptual design for the Conversation Composer UI, enabling users to create, edit, and manage multi-turn AI dialogues (`Conversation` objects).

## I. Composer Purpose and Goals

The Conversation Composer allows users to:
- Create new multi-turn `Conversation` flows.
- Edit existing `Conversation` instances (e.g., loaded from saved files).
- Manage a sequence of `PromptTurn` objects within a `Conversation`.
- Edit the `PromptObject` for each `PromptTurn` using an embedded editor with GIGO Guardrail feedback.
- Save valid `Conversation` instances and load them.

## II. Main Composer Layout

The composer interface is envisioned with several coordinated panels/areas:

### A. Conversation Metadata Panel

This panel is dedicated to the metadata of the `Conversation` itself.

1.  **Title:**
    *   **UI Element:** Single-line text input.
    *   **Label:** "Conversation Title"
    *   **Description:** The main title for this multi-turn dialogue. (Bound to `Conversation.title`)
2.  **Description:**
    *   **UI Element:** Multi-line text area (resizable).
    *   **Label:** "Conversation Description"
    *   **Description:** Optional detailed description of the conversation's purpose or flow. (Bound to `Conversation.description`)
3.  **Tags:**
    *   **UI Element:** Tag input field (similar to the one in PromptObject Editor).
    *   **Label:** "Conversation Tags"
    *   **Description:** Keywords for categorizing this conversation. (Bound to `Conversation.tags`)
4.  **Read-only Information:**
    *   **Conversation ID:** (e.g., `ID: conv_abcdef-1234...`) (From `Conversation.conversation_id`)
    *   **Created At:** (e.g., `Created: 2023-11-01T10:00:00Z`) (From `Conversation.created_at`)
    *   **Last Modified At:** (e.g., `Modified: 2023-11-01T12:30:00Z`) (From `Conversation.last_modified_at`)

### B. Turn Sequence Display/Editor Area

This is the central area where the sequence of `PromptTurn` objects is displayed and managed.

*   **Visual Representation:** Turns are displayed as a vertical list of "Turn Cards."
    *   Each card provides a summary of the turn (e.g., "Turn 1: [Role/Task Snippet from PromptObject]", "Turn 2: Follow-up on [Context Snippet]").
    *   The currently selected turn card is visually highlighted.
*   **Actions Associated with this Area (or individual cards):**
    *   **Global Action:** An "[Add Turn]" button, typically at the end of the list or on a toolbar, to append a new `PromptTurn` to the sequence.
    *   **Per-Card Actions (visible on hover/selection):**
        *   "Delete Turn" icon/button.
        *   "Move Up" icon/button.
        *   "Move Down" icon/button.
        *   (Optional V2: "Duplicate Turn" icon/button).

### C. Selected Turn Detail Panel

This panel becomes active when a "Turn Card" from Area B is selected. It's where the details of that specific `PromptTurn` are edited.

*   **Embedded PromptObject Editor:**
    *   The UI defined in `prometheus_protocol/ui_concepts/prompt_editor.md` is embedded here.
    *   It is bound to the `prompt_object` attribute of the selected `PromptTurn`.
    *   All GIGO Guardrail feedback mechanisms described for the standalone PromptObject Editor apply here, within the context of this specific turn's prompt.
*   **Turn-Specific Fields:**
    1.  **Turn Notes:**
        *   **UI Element:** Multi-line text area.
        *   **Label:** "Turn Notes"
        *   **Description:** User's notes or comments about this specific turn's purpose or expected behavior. (Bound to `PromptTurn.notes`)
    2.  **Turn ID (Read-only):**
        *   **Label:** "Turn ID"
        *   **Display:** Shows `PromptTurn.turn_id`.
    3.  **Parent Turn ID (Read-only for V1):**
        *   **Label:** "Parent Turn"
        *   **Display:** Shows `PromptTurn.parent_turn_id` (for linear V1, this is implicitly the previous turn's ID).
    4.  **Conditions (Placeholder for V1):**
        *   **Label:** "Activation Conditions"
        *   **UI Element:** A disabled text area or a note.
        *   **Display/Note:** "Conditional logic for activating this turn will be available in a future version. (e.g., based on keywords in previous AI response)." (Bound to `PromptTurn.conditions` for data storage).

### D. Main Actions Toolbar

A global toolbar for actions related to the entire `Conversation`.

*   **[New Conversation] Button:** Clears the composer to start a new `Conversation`.
*   **[Load Conversation] Button:** Opens an interface to load a saved `Conversation`.
*   **[Save Conversation] Button:** Saves the current `Conversation`.
*   **[Run Conversation] Button:**
    *   Initiates the sequential execution of all turns in the current `Conversation` using the `JulesExecutor`.
    *   Responses and statuses are displayed for each turn.

### Initial State

*   When the Conversation Composer is first opened or after "[New Conversation]" is clicked, it should present a clean slate:
    *   Metadata panel shows a new `Conversation` object with fresh IDs and timestamps, empty title/description/tags.
    *   Turn Sequence area is empty, perhaps with a prompt like "No turns yet. Click 'Add Turn' to begin."
    *   Selected Turn Detail Panel is empty or shows placeholder text.

---
*Next sections will detail interactions for adding/editing/reordering turns, `ConversationManager` integration, and validation flows.*

## III. Turn Sequence Display/Editor Area: Interactions

This area is central to building the conversation flow. For V1, we assume a linear sequence of turns.

### A. Displaying Turns

*   Each `PromptTurn` in the `Conversation.turns` list is rendered as a "Turn Card" in a vertical sequence.
*   **Turn Card Content (Summary):**
    *   **Turn Number:** "Turn 1", "Turn 2", etc., based on its order in the list.
    *   **Title/Snippet:** A brief identifying snippet derived from the turn's `PromptObject` (e.g., `prompt_object.role`, or the first few words of `prompt_object.task`). Example: "Turn 1: Asker of Questions" or "Turn 2: Explainer of Concepts".
    *   **Selection Indicator:** The currently selected Turn Card is visually distinct (e.g., different background color, border).

### B. Adding a New Turn

1.  **User Action:** Clicks the "[Add Turn]" button (located in Area B or D).
2.  **System Response:**
    *   A new `PromptTurn` instance is created programmatically.
        *   Its `prompt_object` is a new, default `PromptObject` (empty fields).
        *   `turn_id` is auto-generated.
        *   If the conversation already has turns, `parent_turn_id` could be set to the ID of the last turn in the current sequence (for linear V1).
    *   This new `PromptTurn` is appended to the `Conversation.turns` list.
    *   The Turn Sequence Display (Area B) updates to show the new Turn Card at the end of the sequence.
    *   The newly added turn is automatically selected, and its details (including the empty `PromptObject` editor) are displayed in the "Selected Turn Detail Panel" (Area C), ready for editing.

### C. Selecting a Turn

1.  **User Action:** Clicks on a Turn Card in the Turn Sequence Display (Area B).
2.  **System Response:**
    *   The clicked Turn Card becomes visually highlighted as the "selected turn."
    *   Any previously selected Turn Card reverts to its normal state.
    *   The "Selected Turn Detail Panel" (Area C) is populated with the data from the selected `PromptTurn`, including loading its `prompt_object` into the embedded PromptObject Editor.

### D. Deleting a Turn

1.  **User Action:**
    *   Selects a Turn Card.
    *   Clicks a "Delete Selected Turn" button (e.g., on the Turn Card itself via an icon, or a general button in Area B/D that acts on the selected turn).
2.  **System Confirmation:**
    *   A confirmation dialog appears (e.g., "Are you sure you want to delete 'Turn X: [Snippet]'? This action cannot be undone.").
3.  **System Response (on confirmation):**
    *   The selected `PromptTurn` is removed from the `Conversation.turns` list.
    *   The Turn Sequence Display (Area B) updates to remove the card.
    *   If a turn was deleted:
        *   The "Selected Turn Detail Panel" (Area C) might be cleared or might select the next available turn (e.g., the one after the deleted turn, or the previous one if the last turn was deleted). If no turns remain, it should clear.
        *   (V1.1/V2 Consideration): `parent_turn_id` links for subsequent turns in more complex (non-linear) scenarios would need updating. For linear V1, simple list removal is sufficient for order. We might need to adjust `parent_turn_id` if we strictly maintain it even for linear. For now, assume the list order primarily defines sequence for V1.

### E. Reordering Turns

1.  **User Action:**
    *   Selects a Turn Card.
    *   Clicks a "[Move Turn Up]" or "[Move Turn Down]" button (e.g., on the Turn Card or in Area B/D acting on the selected turn).
2.  **System Response:**
    *   The selected `PromptTurn` is moved one position up or down within the `Conversation.turns` list.
    *   The Turn Sequence Display (Area B) updates to reflect the new order.
    *   The selection remains on the moved turn.
    *   Buttons are disabled appropriately (e.g., "Move Up" is disabled for the first turn).
    *   (V1.1/V2 Consideration): `parent_turn_id` updates for affected turns would be needed for robust non-linear linking. For linear V1, list order is primary.

---
*Next section: Selected Turn Detail Panel Functionality.*

## IV. Selected Turn Detail Panel: Functionality

When a user selects a "Turn Card" from the "Turn Sequence Display/Editor Area" (Area B), this "Selected Turn Detail Panel" (Area C) becomes active, displaying the details of that specific `PromptTurn` and allowing edits.

### A. Embedded PromptObject Editor

*   **Core Component:** The most significant part of this panel is an embedded instance of the "PromptObject Editor" as defined in `prometheus_protocol/ui_concepts/prompt_editor.md`.
*   **Data Binding:** This embedded editor is directly bound to the `prompt_object` attribute of the currently selected `PromptTurn`.
    *   When a turn is selected, its `prompt_object` data (role, context, task, constraints, examples, tags, and all metadata like `prompt_id`, `version`, etc.) populates the fields of the embedded editor.
    *   Any changes made by the user within this embedded editor (e.g., modifying the task, adding a constraint) directly update the corresponding attributes of the `prompt_object` within the selected `PromptTurn` in the in-memory `Conversation` data structure.
*   **GIGO Guardrail Integration:**
    *   All inline validation feedback mechanisms (as described in `prompt_editor.md`, Section III) function within this embedded editor context.
    *   If the user edits the `role` of the selected turn's `prompt_object` and leaves it empty, the red border and error message appear directly within this embedded editor section.
    *   The "Overall Validation Status Display" and "GIGO Guardrail Error Summary List" (described in `prompt_editor.md`, Sections IV and V) also function in the context of *this specific `PromptObject`* being edited. There might be a global validation status for the whole conversation (see Section V below on `ConversationManager` interaction) and a local one for the current turn's prompt.

### B. Additional `PromptTurn`-Specific Fields

Besides the embedded `PromptObject` editor, this panel also displays and allows editing of fields unique to the `PromptTurn` itself.

1.  **Turn Notes:**
    *   **UI Element:** A multi-line text area.
    *   **Label:** "Turn Notes" (or similar, e.g., "Notes for this Turn").
    *   **Binding:** Editable, bound to `selected_turn.notes`.
    *   **Purpose:** Allows the user to add free-text annotations or comments about the purpose, expected outcome, or strategy for this specific turn in the conversation.

2.  **Turn ID (Read-only):**
    *   **UI Element:** Simple text display.
    *   **Label:** "Turn ID:"
    *   **Display:** Shows the `selected_turn.turn_id`. This is system-generated and not editable by the user.

3.  **Parent Turn ID (Read-only for V1):**
    *   **UI Element:** Simple text display.
    *   **Label:** "Preceded By:" (or "Parent Turn ID:").
    *   **Display:** Shows `selected_turn.parent_turn_id`. For V1 (linear sequences), this will typically be the `turn_id` of the immediately preceding turn in the list, or "None" / "Start of Conversation" for the first turn.
    *   **(V2 Consideration):** In future versions with branching logic, this might become a searchable dropdown or a more interactive element to re-link turns.

4.  **Conditions (Placeholder for V1):**
    *   **UI Element:** A disabled text area or a descriptive label.
    *   **Label:** "Activation Conditions:"
    *   **Display/Note:** "Define conditions based on previous AI responses to trigger this turn (e.g., 'AI mentions keyword X'). Feature planned for a future version."
    *   **Binding (Conceptual):** While not editable in V1 UI, the `selected_turn.conditions` attribute in the data model can store this information if set programmatically or by loading an advanced template.

### C. Behavior on Turn Selection Change

*   When the user selects a different Turn Card in Area B:
    *   If there were unsaved changes to the `prompt_object` or `notes` of the previously selected turn, the system might:
        *   Option A (Auto-save): Silently save the changes to the in-memory `Conversation` object. (Simplest for V1).
        *   Option B (Confirm): Prompt the user "You have unsaved changes in the current turn. Save them?" (More complex, adds dialogs).
        *   For V1, **Option A (Auto-save)** is recommended for a smoother flow, as all changes are to the in-memory representation until the entire `Conversation` is explicitly saved.
    *   The "Selected Turn Detail Panel" then refreshes to display the data of the newly selected `PromptTurn`.

---
*Next section: ConversationManager Integration and Validation Flow.*

## V. `ConversationManager` Integration and Validation Flow

This section details how the Conversation Composer interacts with the `ConversationManager` for persistence and how overall validation (especially of embedded `PromptObject`s) is handled.

### A. [New Conversation] Button

1.  **User Action:** Clicks the "[New Conversation]" button on the Main Actions Toolbar.
2.  **System Response:**
    *   (Optional: If current conversation has unsaved changes, prompt "Discard unsaved changes and start a new conversation?").
    *   The composer interface is reset:
        *   A new, empty `Conversation` object is created in memory (with new `conversation_id`, default title, fresh timestamps, empty `turns` list, etc.).
        *   The Conversation Metadata Panel updates to reflect this new `Conversation`.
        *   The Turn Sequence Display Area is cleared.
        *   The Selected Turn Detail Panel is cleared or shows placeholder text.

### B. [Load Conversation] Button

1.  **User Action:** Clicks the "[Load Conversation]" button on the Main Actions Toolbar.
2.  **System Response:**
    *   (Optional: If current conversation has unsaved changes, prompt "Discard unsaved changes and load another conversation?").
    *   A modal dialog or a dedicated view appears, listing available saved conversations. This list is populated by conceptually calling `ConversationManager.list_conversations()`.
    *   The list should be searchable or sortable.
3.  **User Selection:** The user selects a conversation name from the list.
4.  **Loading Operation (Conceptual):**
    *   Upon selection, the system conceptually calls `ConversationManager.load_conversation(selected_conversation_name)`.
5.  **Populate Composer:**
    *   The `Conversation` object returned by `load_conversation` is used to populate the entire composer:
        *   Conversation Metadata Panel fields are updated.
        *   The Turn Sequence Display Area is populated with Turn Cards for each `PromptTurn` in `loaded_conversation.turns`.
        *   The Selected Turn Detail Panel is typically cleared or shows information for the first turn if available.
6.  **Feedback to User:**
    *   On successful load: The composer fields are updated. (Optional: a small confirmation like "Conversation '[Title]' loaded.")
    *   On failure (e.g., `ConversationManager` raises `FileNotFoundError` or `ConversationCorruptedError`): An appropriate error message is displayed to the user (e.g., "Error: Could not load conversation. File may be missing or corrupted.").

### C. [Save Conversation] Button

1.  **User Action:** Clicks the "[Save Conversation]" button on the Main Actions Toolbar.
2.  **Pre-Save Validation (Critical Step):**
    *   The system iterates through **all** `PromptTurn` objects currently in the `Conversation.turns` list.
    *   For each `turn.prompt_object`, it performs a full validation using the `core.guardrails.validate_prompt()` logic.
    *   **If any `PromptObject` within any `PromptTurn` is invalid:**
        *   The save operation is **blocked**.
        *   A global error message is displayed prominently (e.g., "Cannot save: One or more turns have validation errors. Please review and fix them.").
        *   The UI should automatically select the **first** `PromptTurn` in the sequence that contains an invalid `PromptObject`.
        *   The "Selected Turn Detail Panel" will then display that turn, and its embedded "PromptObject Editor" will show the specific GIGO Guardrail errors for that prompt (as per `prompt_editor.md` Section III & IV).
        *   The user must correct all such errors in all turns before the conversation can be saved.
    *   **If all `PromptObject`s in all `PromptTurn`s are valid:**
        *   Proceed to the next step.
3.  **Prompt for Conversation Name (if needed):**
    *   If the `Conversation` object doesn't yet have a persistent name (e.g., it's a new conversation or the user wants to "Save As"), or if a "Save As" command was initiated:
        *   A modal dialog or input prompt appears: "Enter a name for this conversation:".
        *   The current `Conversation.title` can be suggested as the default name.
        *   Input validation for the name (e.g., cannot be empty).
    *   If saving an already named conversation, this step is typically skipped unless it's a "Save As" operation.
4.  **Saving Operation (Conceptual):**
    *   The `ConversationManager.save_conversation(current_conversation_object, conversation_name)` method is conceptually called.
    *   The `ConversationManager` handles filename sanitization and file system operations. The `save_conversation` method also calls `current_conversation_object.touch()` to update `last_modified_at`.
5.  **Feedback to User:**
    *   On successful save:
        *   A confirmation message (e.g., "Conversation '[Title]' saved successfully!").
        *   The `last_modified_at` field in the Conversation Metadata Panel is updated to reflect the new timestamp from the saved `Conversation` object.
    *   On failure (e.g., `ConversationManager` raises an `IOError`): An appropriate error message is displayed.

---
*End of Conversation Composer UI Concepts document.*

## VI. Conversation Execution and Response Display

This section outlines how a multi-turn `Conversation` is executed and how responses for each turn are displayed.

### A. Initiating Conversation Execution
*   The user clicks the **"[Run Conversation]"** button on the Main Actions Toolbar.
*   **Pre-Execution Checks (Conceptual):**
    *   Similar to single prompt execution, the system iterates through all `PromptTurn` objects. For each `turn.prompt_object`, it performs GIGO Guardrail validation and Risk Identification.
    *   If any `PromptObject` has GIGO errors, execution is **blocked**. The UI guides the user to the first problematic turn (as described in Section V.C for saving).
    *   If risks are identified, they are displayed (perhaps in a summary before execution starts), and the user can choose to proceed or cancel to revise.

### B. Displaying Execution Progress and Responses

1.  **Turn Sequence Display Area (Area B from Layout):**
    *   As the conversation executes, the "Turn Cards" could visually indicate their status:
        *   **Pending:** Default state before execution.
        *   **Executing:** When Jules is processing this turn (e.g., a spinner icon on the card).
        *   **Completed:** Successfully executed.
        *   **Error:** An error occurred during execution for this turn. The card might highlight in red. Clicking it shows details in Area C. The error message from `AIResponse.error_message` could be partially visible or available on hover on an error icon on the card.
        *   **Skipped:** If conditional logic (V2) caused this turn to be skipped.
    *   Clicking on an executed Turn Card would still populate the "Selected Turn Detail Panel" (Area C), including any AI response received for that turn.

2.  **Selected Turn Detail Panel (Area C from Layout) - Response Area:**
    *   When a `PromptTurn` has been executed (or is being viewed after execution):
        *   A dedicated read-only area within this panel (e.g., below the embedded PromptObject Editor for that turn) displays the `AIResponse` for that turn.
        *   **If `AIResponse.was_successful` is True (for the selected executed turn):**
            *   **AI-Generated Content for the Turn:**
                *   Displays the `AIResponse.content` for this turn in a read-only text area within the "Selected Turn Detail Panel".
                *   This text area should be scrollable and support standard text selection.
                *   A dedicated "[Copy Turn Response]" button should be available for this specific turn's content.
                *   If the AI response content is formatted (e.g., Markdown, code blocks), the UI should attempt to render it appropriately (e.g., display rendered Markdown, apply syntax highlighting). A "Raw Text" vs. "Rendered View" toggle could be beneficial here as well.
            *   **Turn-Specific Response Metadata:**
                *   Clearly display key metadata for this turn's response (e.g., `Tokens Used: 85`, `Finish Reason: stop`, `Model: jules-conceptual-stub-v1-conv-dynamic`). This could be a small, labeled section.
            *   **Feedback Collection UI for the Turn:**
                *   The "Feedback Collection UI" (for ratings, tags, notes on the output of this specific turn, as per `output_analytics.md`) should be clearly presented here, directly associated with this turn's `AIResponse`.
        *   **If `AIResponse.was_successful` is False:**
            *   Displays the user-friendly `AIResponse.error_message` clearly (e.g., "Network Error on this turn. Retries failed." or "Content policy violation for this turn's prompt.").
            *   Indicates if retries were attempted for this turn (e.g., "Retrying (attempt X of Y)..." if the user selects the turn while it's in a retry loop).
    *   This allows users to review the input prompt and the output for each turn side-by-side or in close proximity.

3.  **Conversation Log/Transcript View (Optional V1.1/V2):**
    *   A separate panel or view that shows the entire conversation transcript as it unfolds (User prompt 1, AI response 1, User prompt 2, AI response 2, etc.).
    *   This would provide a continuous narrative view of the dialogue. For V1, focusing on per-turn response display in Area C is primary.

3.  **Conversation Log/Transcript View:**
    *   **Purpose:** Provides a continuous, chronological, and easily readable consolidated view of the entire dialogue as it has occurred or been executed. This view is essential for understanding the full context and flow of the conversation.
    *   **Location:** This could be a prominent, scrollable panel within the Conversation Composer interface. For example:
        *   A central panel that can be toggled or resized.
        *   A tab within the main work area, switching from the "Turn Editor" view to a "Transcript View."
    *   **Layout & Content:**
        *   Each message (user input or AI response) in the log is clearly attributed to its speaker (e.g., "User (Turn X)" or "Jules (Turn X)"). Timestamps for each message could be an optional display setting.
        *   **User Messages:** Display the core input sent to Jules for that turn. For V1, this would typically be `PromptTurn.prompt_object.task`. A short snippet of `PromptTurn.prompt_object.role` or `PromptTurn.notes` might also be included if they provide key context for that turn's framing. Example:
            ```
            -----------------------------------
            User (Turn 1 - Role: Travel Agent)
            Task: Suggest a 3-day itinerary for Paris.
            -----------------------------------
            ```
        *   **AI Messages:** Display the `AIResponse.content` if the turn was successful. If an error occurred for that turn (`AIResponse.was_successful == False`), display the `AIResponse.error_message` clearly marked as an error. Example:
            ```
            Jules (Turn 1)
            Okay, here's a possible 3-day itinerary for Paris: Day 1...
            -----------------------------------
            User (Turn 2 - Role: Travel Agent)
            Task: error_test:content_policy
            -----------------------------------
            Jules (Turn 2) - ERROR
            Simulated content policy violation for turn [turn_id].
            -----------------------------------
            ```
        *   Messages are visually distinct (e.g., different background colors, text alignment, or icons for "User" vs. "Jules" vs. "Jules Error"), similar to common chat or messaging applications.
        *   The log should be scrollable, with an option or default behavior to keep the latest message in view as new turns are executed or added.
        *   Content within messages (especially AI responses) should support standard text selection and copying. A "[Copy Turn Content]" button could appear on hover for each message block.
        *   Formatted content (Markdown, code) from AI responses should be rendered appropriately within the log.
    *   **Interaction (Conceptual):**
        *   **Navigation:** Clicking on a specific "User (Turn X)" or "Jules (Turn X)" entry in the log could:
            *   Highlight the corresponding "Turn Card" in the "Turn Sequence Display/Editor Area" (Area B).
            *   Select that turn, populating the "Selected Turn Detail Panel" (Area C) with its full details (including the `PromptObject` editor and the `AIResponse`). This allows for easy navigation between the summarized transcript and the detailed turn editor.
        *   **Copy Full Transcript:** A "[Copy Full Transcript]" button should be available for this view, which copies the entire dialogue (perhaps in a simple text format or basic Markdown) to the clipboard.
        *   **Filtering (V2 Consideration):** Future versions might allow filtering the transcript (e.g., show only AI responses, show only turns with errors).

### C. Post-Execution and Error Handling in Conversations

*   Once all turns are processed or an unrecoverable error halts the sequence:
    *   The user can review all responses and errors for each turn.
    *   If the conversation was halted due to an error on a specific turn, that turn should be clearly marked as the point of failure. Subsequent turns might be marked as "Not Executed."
    *   A global status message for the conversation execution could summarize the outcome (e.g., "Conversation completed with errors on Turn X.", "Conversation halted due to network issues on Turn Y.").
*   Analytics feedback can still be provided for successfully executed turns' outputs.
*   The `Conversation` object (in memory) would now ideally have references to all the `AIResponse` objects generated (though this data linkage isn't explicitly part of the `Conversation` dataclass yet, it would be managed by the orchestrating execution logic).

---
*End of Conversation Composer UI Concepts document.*
