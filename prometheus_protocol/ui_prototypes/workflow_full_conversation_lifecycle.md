# Prometheus Protocol: Paper Prototype
## Workflow: Full Conversation Lifecycle (Create, Version, Run, Review)

## 1. Introduction

This document provides a detailed, step-by-step textual "paper prototype" for a key user workflow: creating a new multi-turn conversation, saving and versioning it, executing it with the (simulated) "Google Jules" AI engine, and reviewing the results and history.

Its purpose is to:
*   Illustrate how a user might interact with the various components and UI elements of the Conversation Composer.
*   Validate the conceptual coherence of the user journey, integrating concepts from `conversation_composer.md`, `prompt_editor.md`, and backend managers like `ConversationManager` and `ConversationOrchestrator`.
*   Identify potential usability issues or gaps in the conceptualized UI flow.

This prototype describes user actions and the corresponding system/UI responses.

## 2. Assumptions for this Workflow Prototype

*   **User Context:** The user is operating within their "Personal Space" (not a shared workspace, for simplicity in this V1 prototype).
*   **Authentication:** User is assumed to be "logged in" (though full user auth is a V2+ concept, we assume a user context exists for saving/loading personal items).
*   **Backend Stubs:** All interactions with `JulesExecutor`, `ConversationOrchestrator`, `ConversationManager`, and `TemplateManager` are based on their current (stubbed or V1 file-based) implementations. AI responses are simulated.
*   **GIGO & Risk Feedback:** The system will provide GIGO Guardrail and Risk Identifier feedback as defined in `prompt_editor.md` when `PromptObject`s are edited. This prototype will highlight key instances.
*   **Linear Conversation:** The conversation created will be linear; conditional branching (V2 `PromptTurn.conditions`) is not part of this V1 workflow.

## 3. Structure of the Prototype

The workflow will be presented as a sequence of steps. Each step will consist of:
*   **User Action:** A description of what the user does.
*   **System/UI Response:** A description of how the Prometheus Protocol interface and system (conceptually) respond to the user's action.

---

---

## 4. Workflow Part 1: Creating an Initial Conversation (2 Turns)

This part details the user's process of initiating a new conversation and defining its first two turns.

### Step 1.1: Initiate New Conversation

*   **User Action:** Navigates to the "Conversation Composer" section of Prometheus Protocol (assuming such navigation exists). Clicks the **"[New Conversation]"** button on the Main Actions Toolbar.
*   **System/UI Response:**
    *   The Conversation Composer interface loads or resets to a clean state.
    *   **Conversation Metadata Panel (II.A in `conversation_composer.md`):**
        *   `title`: Empty or "Untitled Conversation".
        *   `description`: Empty.
        *   `tags`: Empty.
        *   `conversation_id`: A new UUID is generated and displayed (e.g., "conv_uuid_1").
        *   `created_at`, `last_modified_at`: Set to current time and displayed.
        *   `version`: Displays "Version: 1" (as per `Conversation` dataclass default).
    *   **Turn Sequence Display/Editor Area (II.B):** Displays a message like "No turns yet. Click 'Add Turn' to begin."
    *   **Selected Turn Detail Panel (II.C):** Is empty or shows placeholder text indicating no turn is selected.

### Step 1.2: Define Conversation Metadata

*   **User Action:**
    1.  Clicks into the "Conversation Title" input field. Types: "Planet Explainer for Kids".
    2.  Clicks into the "Conversation Description" text area. Types: "A simple conversation to explain different planets to a young child, one planet at a time."
    3.  Clicks into the "Conversation Tags" input. Types "education", presses Enter. Types "space", presses Enter. Types "kids", presses Enter.
*   **System/UI Response:**
    *   The Conversation Metadata Panel updates in real-time as the user types.
    *   `title` now shows "Planet Explainer for Kids".
    *   `description` shows the entered text.
    *   `tags` display as pills: `[education] [space] [kids]`.
    *   The in-memory `Conversation` object is updated. `last_modified_at` timestamp might update upon these changes (conceptual detail for a richer UI).

### Step 1.3: Add First Turn

*   **User Action:** Clicks the **"[Add Turn]"** button (e.g., located in the Turn Sequence Display Area or Main Actions Toolbar).
*   **System/UI Response:**
    *   A new `PromptTurn` object is added to the in-memory `Conversation.turns` list.
    *   **Turn Sequence Display/Editor Area (II.B):**
        *   A new "Turn Card" appears, labeled "Turn 1". It might have a default snippet like "Turn 1: New Prompt".
        *   This "Turn 1" card is automatically selected and highlighted.
    *   **Selected Turn Detail Panel (II.C):**
        *   This panel now displays the details for "Turn 1".
        *   The embedded "PromptObject Editor" section is populated with a *new, default `PromptObject`*:
            *   `role`, `context`, `task` are empty.
            *   `constraints`, `examples`, `tags` (for the PromptObject) are empty lists.
            *   `prompt_id`, `version` (1), `created_at`, `last_modified_at` (for this new PromptObject) are set to their defaults. `created_by_user_id` is `None`. `settings` is `None`.
        *   The `PromptTurn.notes` field (specific to Turn 1) is empty.
        *   `PromptTurn.turn_id` is displayed (e.g., "turn_uuid_A").
        *   `PromptTurn.parent_turn_id` displays "None" or "Start of Conversation".
        *   `PromptTurn.conditions` displays its placeholder text.

### Step 1.4: Define Turn 1 `PromptObject` and Notes

*   **User Action:** Interacts with the "Selected Turn Detail Panel" for Turn 1:
    1.  In the embedded PromptObject Editor:
        *   Types into "Role": "Friendly Astronomer".
        *   Types into "Context": "The user is a 5-year-old child who is curious about space."
        *   Types into "Task": "Ask the child which planet they would like to learn about first. Offer a few popular choices like Mars, Jupiter, or Saturn."
        *   Adds a constraint: "Keep your question very simple and friendly."
    2.  Types into "Turn Notes" (the field specific to `PromptTurn`): "Goal: Elicit the child's choice of planet for the next turn."
*   **System/UI Response:**
    *   The embedded PromptObject Editor fields update in real-time.
    *   The "Turn Notes" field updates.
    *   **GIGO/Risk Feedback (Conceptual):**
        *   As the user types, GIGO checks run (e.g., on blur). Assume all inputs are valid according to basic GIGO.
        *   `RiskIdentifier` might flag (INFO): "Task appears to be a question. Ensure it's clear the AI should ask, not answer yet." (This is a more advanced risk we haven't implemented in `RiskIdentifier` V1, but good to note for a paper prototype). For this flow, assume user sees this and deems it acceptable for now.
    *   The in-memory `PromptObject` within Turn 1 and the `notes` for Turn 1 are updated.

### Step 1.5: Add Second Turn

*   **User Action:** Clicks the **"[Add Turn]"** button again.
*   **System/UI Response:**
    *   A new `PromptTurn` object is added to `Conversation.turns`.
    *   **Turn Sequence Display/Editor Area (II.B):**
        *   A new "Turn Card" appears below "Turn 1", labeled "Turn 2".
        *   "Turn 1" card is deselected.
        *   "Turn 2" card is automatically selected and highlighted.
    *   **Selected Turn Detail Panel (II.C):**
        *   This panel now displays details for "Turn 2".
        *   The embedded "PromptObject Editor" is populated with a *new, default `PromptObject`*.
        *   `PromptTurn.notes` for Turn 2 is empty.
        *   `PromptTurn.turn_id` is displayed (e.g., "turn_uuid_B").
        *   `PromptTurn.parent_turn_id` displays the `turn_id` of Turn 1 (e.g., "turn_uuid_A").
    *   (Conceptual: The content of Turn 1's `PromptObject` and notes are considered "auto-saved" to the in-memory `Conversation` object when focus shifted or the new turn was added).

### Step 1.6: Define Turn 2 `PromptObject` (with an initial error)

*   **User Action:** Interacts with the "Selected Turn Detail Panel" for Turn 2:
    1.  In the embedded PromptObject Editor:
        *   Types into "Role": "Friendly Astronomer".
        *   Types into "Context": "The child has just expressed interest in learning about [PLANET_FROM_TURN_1_RESPONSE]. I should now explain it."
        *   Types into "Task": "Explain the planet [PLANET_FROM_TURN_1_RESPONSE] in very simple terms for a 5-year-old. Use an analogy. Keep it under 100 words."
        *   Adds a constraint: "Use an enthusiastic and wondrous tone!"
*   **System/UI Response:**
    *   The embedded PromptObject Editor fields update.
    *   **GIGO/Risk Feedback:**
        *   `UnresolvedPlaceholderError` is triggered for the `[PLANET_FROM_TURN_1_RESPONSE]` placeholders in both "Context" and "Task".
        *   Inline error messages appear below the "Context" and "Task" fields (e.g., "Context: Contains unresolved placeholder text like '[PLANET_FROM_TURN_1_RESPONSE]'. Please replace it...").
        *   The borders of "Context" and "Task" fields turn red.
        *   The "Overall Validation Status Display" (for this `PromptObject`) shows "Status: 2 issues found".
    *   The in-memory `PromptObject` for Turn 2 is updated with the problematic text.

### Step 1.7: User Corrects Placeholder in Turn 2

*   **User Action:**
    1.  Reads the GIGO error messages.
    2.  Edits the "Context" field for Turn 2 to: "The child has just expressed interest in learning about Mars (we'll assume this for now, as we aren't simulating Turn 1's actual AI response in this *creation* phase). I should now explain it."
    3.  Edits the "Task" field for Turn 2 to: "Explain the planet Mars in very simple terms for a 5-year-old. Use an analogy. Keep it under 100 words."
*   **System/UI Response:**
    *   As the user types and on blur:
        *   The `UnresolvedPlaceholderError` messages for "Context" and "Task" disappear.
        *   The red borders are removed.
        *   The "Overall Validation Status Display" (for this `PromptObject`) changes to "Status: Valid".
    *   The in-memory `PromptObject` for Turn 2 is updated.

---
*(End of Part 1. Next: Part 2: Saving and Versioning the Conversation.)*

---

## 5. Workflow Part 2: Saving and Versioning the Conversation

This part details how the user saves the newly created conversation, establishing its first version, and then creates a subsequent version after making modifications.

### Step 2.1: First Save of the Conversation

*   **User Action:** With the two turns defined (and Turn 2's `PromptObject` now valid after placeholder correction), the user clicks the **"[Save Conversation]"** button on the Main Actions Toolbar.
*   **System/UI Response:**
    1.  **Pre-Save Validation:**
        *   The system iterates through all `PromptTurn`s in the current in-memory `Conversation` (Turn 1 and Turn 2).
        *   For each `turn.prompt_object`, it conceptually runs `core.guardrails.validate_prompt()`.
        *   (Assumption for this step: Both `PromptObject`s are currently valid according to GIGO rules).
        *   (Conceptual: `RiskIdentifier` might also run; assume no blocking risks, or user was already informed).
    2.  **Prompt for Conversation Name:**
        *   A modal dialog appears: "Enter a name for this conversation:".
        *   The input field might be pre-filled with a sanitized version of the `Conversation.title` (e.g., "Planet_Explainer_for_Kids"). User can edit this.
    3.  **User Confirms Name:** User types "Planet Explainer for Child" and clicks "Save" in the modal.
    4.  **Saving Operation:**
        *   The system conceptually calls `ConversationManager.save_conversation(current_conversation_object, "Planet Explainer for Child")`.
        *   `ConversationManager` sanitizes the name to "Planet_Explainer_for_Child", sees no existing versions, assigns `version = 1` to the `current_conversation_object` (which also updates its `last_modified_at` via `touch()`), and saves it as `Planet_Explainer_for_Child_v1.json`.
        *   The `save_conversation` method returns the updated `Conversation` object (now with `version = 1` and new LMT).
    5.  **UI Update:**
        *   A confirmation message appears (e.g., a toast notification): "Conversation 'Planet Explainer for Child' saved as version 1 successfully!"
        *   The **Conversation Metadata Panel (II.A)** updates:
            *   `Version:` now displays "1".
            *   `Last Modified At:` updates to the new timestamp from the saved object.
        *   The editor is now associated with the saved "Planet Explainer for Child", version 1.

### Step 2.2: User Modifies an Existing Turn

*   **User Action:**
    1.  Selects "Turn 2" card in the Turn Sequence Display Area.
    2.  In the "Selected Turn Detail Panel" (II.C), for Turn 2's `PromptObject`, the user changes the "Task" field from explaining "Mars" to explaining "Jupiter".
        *   Old Task: "Explain the planet Mars in very simple terms for a 5-year-old. Use an analogy. Keep it under 100 words."
        *   New Task: "Explain the planet Jupiter in very simple terms for a 5-year-old. Use its Great Red Spot as part of an analogy. Keep it under 120 words."
    3.  User might also update the `PromptTurn.notes` for Turn 2.
*   **System/UI Response:**
    *   The embedded PromptObject Editor for Turn 2 updates with the new task.
    *   GIGO/Risk checks run conceptually for Turn 2's `PromptObject`; assume it's valid.
    *   The in-memory `Conversation` object is updated.
    *   The `Conversation.last_modified_at` timestamp in the **Metadata Panel** might update to reflect this "dirty" state (or a visual indicator like an asterisk "*" appears next to the conversation title/version, e.g., "Planet Explainer for Child v1*").

### Step 2.3: Save as New Version

*   **User Action:** Clicks the **"[Save Conversation]"** button again.
*   **System/UI Response:**
    1.  **Pre-Save Validation:** (As in Step 2.1.1, all prompts checked, assume valid).
    2.  **Saving Operation (No Name Prompt this time for simple "Save"):**
        *   The system conceptually calls `ConversationManager.save_conversation(current_conversation_object, "Planet Explainer for Child")`.
        *   `ConversationManager` sanitizes the name to "Planet_Explainer_for_Child".
        *   It calls `_get_highest_version("Planet_Explainer_for_Child")` which returns `1`.
        *   `new_version` becomes `1 + 1 = 2`.
        *   The `current_conversation_object` (in memory) has its `version` attribute updated to `2` and `last_modified_at` is updated by `touch()`.
        *   It's saved as `Planet_Explainer_for_Child_v2.json`.
        *   The `save_conversation` method returns the updated `Conversation` object (now `version = 2`).
    3.  **UI Update:**
        *   Confirmation message: "Conversation 'Planet Explainer for Child' saved as version 2 successfully!"
        *   The **Conversation Metadata Panel (II.A)** updates:
            *   `Version:` now displays "2".
            *   `Last Modified At:` updates to the new timestamp.
        *   Any "dirty" state indicator is cleared.

---
*(End of Part 2. Next: Part 3: Running the Conversation (Simulated).)*

---

## 6. Workflow Part 3: Running the Conversation (Simulated)

This part details the user initiating the execution of their versioned conversation (e.g., Version 2 of "Planet Explainer for Child") and how the UI reflects the (simulated) turn-by-turn execution.

### Step 3.1: User Initiates Conversation Run

*   **User Action:** Clicks the **"[Run Conversation]"** button on the Main Actions Toolbar (while viewing Version 2 of "Planet Explainer for Child").
*   **System/UI Response:**
    1.  **Gather Current State:** The system uses the in-memory `Conversation` object (Version 2, with task for "Jupiter" in Turn 2).
    2.  **Pre-Execution Validation & Risk Assessment:**
        *   (As described in `conversation_composer.md` Section VI.A) GIGO checks are run for all `PromptObject`s in all turns. Assume they pass.
        *   Risk identification runs. Assume no blocking risks, or user chooses to proceed after warnings.
    3.  **Execution Start:**
        *   The "[Run Conversation]" button changes to "[Stop Conversation]" (or similar, indicating it's in progress).
        *   A global status indicator might appear: "Conversation 'Planet Explainer for Child v2' running..."
        *   The "Turn Sequence Display Area" (Area B) prepares to show live status updates.
        *   The "Conversation Log/Transcript View" (if visible) prepares for new entries.
        *   Conceptually, `ConversationOrchestrator.run_full_conversation(current_conversation_object)` is called.

### Step 3.2: Turn 1 Executes (Simulated)

*   **User Action:** (None - system is processing)
*   **System/UI Response:**
    1.  **Turn Sequence Display Area (Area B):**
        *   "Turn 1" card visually changes to "Executing..." (e.g., spinner icon, pulsing highlight). The view scrolls to ensure Turn 1 is visible.
    2.  **Conversation Log/Transcript View:**
        *   A new entry appears: "User (Turn 1 - Task): Ask the child which planet they would like to learn about first. Offer a few popular choices like Mars, Jupiter, or Saturn." (Or a summary).
    3.  **(Simulated Delay for `JulesExecutor.execute_conversation_turn`)**
    4.  **Turn 1 Completion:**
        *   `JulesExecutor` (stub) returns a dummy successful `AIResponse` for Turn 1. Example content: "Hello there, future space explorer! I can tell you all about Mars, Jupiter, or Saturn. Which one sounds most exciting to you right now?"
        *   `AIResponse.source_conversation_id` is set by the orchestrator.
        *   **Turn Sequence Display Area (Area B):** "Turn 1" card changes to "Completed" (e.g., green checkmark ✅).
        *   **Selected Turn Detail Panel (Area C):** If "Turn 1" was/is selected, its response area now displays:
            *   The `AIResponse.content` ("Hello there...").
            *   Rendered formatting, copy button.
            *   Conceptual response metadata.
            *   The "Feedback Collection UI" (for ratings, tags, etc.) for Turn 1's output.
        *   **Conversation Log/Transcript View:** A new entry appears: "Jules (Turn 1): Hello there, future space explorer! I can tell you all about Mars, Jupiter, or Saturn. Which one sounds most exciting to you right now?" (Visually distinct from user entries). Log auto-scrolls.

### Step 3.3: Turn 2 Executes (Simulated)

*   **User Action:** (None - system is processing)
*   **System/UI Response:**
    1.  **Turn Sequence Display Area (Area B):**
        *   "Turn 1" card remains "Completed."
        *   "Turn 2" card visually changes to "Executing...". The view scrolls to ensure Turn 2 is visible if needed.
    2.  **Conversation Log/Transcript View:**
        *   A new entry appears: "User (Turn 2 - Task): Explain the planet Jupiter in very simple terms for a 5-year-old. Use its Great Red Spot as part of an analogy. Keep it under 120 words."
    3.  **(Simulated Delay for `JulesExecutor.execute_conversation_turn`)**
    4.  **Turn 2 Completion:**
        *   `JulesExecutor` (stub) returns a dummy successful `AIResponse` for Turn 2. Example content: "Wow, Jupiter! It's a GIANT gas planet, like a huge striped bouncy ball in space! And see that big red spot? That's a superstorm, like a hurricane that's been spinning for hundreds of years – way bigger than Earth itself!"
        *   `AIResponse.source_conversation_id` is set.
        *   **Turn Sequence Display Area (Area B):** "Turn 2" card changes to "Completed" (✅).
        *   **Selected Turn Detail Panel (Area C):** If "Turn 2" is selected, its response area updates with Turn 2's `AIResponse.content`, metadata, and Feedback UI.
        *   **Conversation Log/Transcript View:** A new entry appears: "Jules (Turn 2): Wow, Jupiter! It's a GIANT gas planet..." Log auto-scrolls.

### Step 3.4: Conversation Run Finishes

*   **User Action:** (None - system is processing)
*   **System/UI Response:**
    1.  All turns in the sequence have been processed.
    2.  A global status message appears: "Conversation 'Planet Explainer for Child v2' run completed successfully."
    3.  The "[Stop Conversation]" button on the Main Actions Toolbar reverts to "[Run Conversation]" (or perhaps "[Re-run Conversation]").
    4.  The user is now free to review all turns, responses, and provide feedback.

---
*(End of Part 3. Next: Part 4: Reviewing Results and History.)*

---

## 7. Workflow Part 4: Reviewing Results, History, and Versions

This part details how the user reviews the outcomes of the executed conversation, interacts with the history, provides conceptual analytics feedback, and loads a previous version.

### Step 4.1: Reviewing a Specific Turn's Details

*   **User Action:** After the conversation run is complete (e.g., Version 2 of "Planet Explainer for Child"), the user clicks on the "Turn 1" card in the "Turn Sequence Display Area" (Area B).
*   **System/UI Response:**
    *   The "Selected Turn Detail Panel" (Area C) updates (or confirms its display) to show:
        *   The full `PromptObject` for Turn 1 (role, task, context, etc.) in the embedded editor section.
        *   The `AIResponse.content` received for Turn 1 ("Hello there, future space explorer!...") in the response display area within this panel.
        *   Associated metadata for Turn 1's response.
        *   The "Feedback Collection UI" for Turn 1's output is visible and interactive.

### Step 4.2: Interacting with the Conversation Log/Transcript View

*   **User Action:** Scrolls through the "Conversation Log/Transcript View" (detailed in `conversation_composer.md` Section VI.B.3).
*   **System/UI Response:**
    *   The user sees the complete, chronological dialogue:
        *   "User (Turn 1 - Task): Ask the child which planet..."
        *   "Jules (Turn 1): Hello there, future space explorer!..."
        *   "User (Turn 2 - Task): Explain the planet Jupiter..."
        *   "Jules (Turn 2): Wow, Jupiter! It's a GIANT gas planet..."
    *   Content is selectable and copyable. Formatted AI responses are rendered.

*   **User Action:** Clicks on the "User (Turn 2 - Task): Explain the planet Jupiter..." entry within the Conversation Log/Transcript View.
*   **System/UI Response:**
    *   The "Turn 2" card in the "Turn Sequence Display Area" (Area B) becomes highlighted/selected.
    *   The "Selected Turn Detail Panel" (Area C) updates to show all details for Turn 2, including its `PromptObject` and its specific `AIResponse` ("Wow, Jupiter!..."). The scroll position within Area C might focus on the start of Turn 2's details.

### Step 4.3: Providing Analytics Feedback (Conceptual)

*   **User Action:** While viewing Turn 2's details in the "Selected Turn Detail Panel" (Area C):
    1.  Clicks the "5 stars" for `output_rating`.
    2.  Adds custom tags like "very_clear", "age_appropriate" using the tag input in the Feedback Collection UI.
    3.  Checks the "Used in Final Work" checkbox (True).
    4.  Types in "User Qualitative Feedback" text area: "The analogy for Jupiter was excellent for a young child."
    5.  Clicks a "[Submit Feedback]" button within the Feedback Collection UI.
*   **System/UI Response:**
    *   The feedback UI might show a brief confirmation (e.g., "Feedback submitted for Turn 2!").
    *   Conceptually, an `AnalyticsEntry` object is created with this feedback and linked to `Conversation.conversation_id`, `PromptObject.prompt_id` (of Turn 2's prompt), `PromptObject.version` (of Turn 2's prompt), and `PromptTurn.turn_id` (of Turn 2). This entry is then (conceptually) sent to a backend analytics store.

### Step 4.4: Loading a Previous Version of the Conversation

*   **User Action:**
    1.  Decides they want to compare with or revert to Version 1 of this conversation.
    2.  Clicks the **"[Load Conversation]"** button on the Main Actions Toolbar.
    3.  In the load dialog, selects the base name "Planet Explainer for Child".
    4.  The UI shows available versions: "[1, 2] - Latest: 2". User selects "Version 1".
    5.  Clicks "Load" in the dialog.
*   **System/UI Response:**
    1.  (Optional: If current Version 2 has unsaved changes since its last *run* or explicit *save*, system might prompt "Discard unsaved changes to current view of Version 2 and load Version 1?"). Assume no intermediate unsaved changes for this step.
    2.  The system conceptually calls `ConversationManager.load_conversation("Planet Explainer for Child", version=1)`.
    3.  The entire Conversation Composer UI updates to reflect the state of "Planet Explainer for Child, Version 1":
        *   **Conversation Metadata Panel (II.A):** `title`, `description`, `tags` revert to V1 state. `Version` shows "1". `Last Modified At` shows V1's LMT.
        *   **Turn Sequence Display/Editor Area (II.B):** Turn cards for V1 are displayed. Turn 2's task will be about "Mars".
        *   **Selected Turn Detail Panel (II.C):** Cleared or shows details for the first turn of V1.
        *   **Conversation Log/Transcript View:** Cleared, as V1 has not been "run" in this session yet. (Alternatively, if run results were persisted with versions, it might show V1's last run results - for V1 paper prototype, assume it clears or shows "Not yet run for this version").
    4.  A confirmation message: "Conversation 'Planet Explainer for Child v1' loaded."

---
*End of Workflow: Full Conversation Lifecycle. End of Paper Prototype Document.*
*(Content for subsequent workflow steps will be added based on the plan.)*
