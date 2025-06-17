# Prometheus Protocol: System State & Context Management (Conceptual)

This document outlines conceptual approaches for managing system state and user context within the Prometheus Protocol application, primarily focusing on how the user interface (e.g., the Streamlit prototype) would maintain and react to this state.

## 1. Goals, Scope, and Key Context Types

### 1.1. Goals

The primary goals for conceptualizing System State & Context Management are:

1.  **UI Cohesion:** Ensure different parts of the user interface (editors, libraries, dashboard) present consistent information and controls based on the user's current focus and operational context (e.g., active workspace, selected item).
2.  **Data Flow Clarity:** Define how contextual information (like current user ID or active workspace ID) is made available to backend managers when they are invoked by UI actions (e.g., for saving or loading resources to the correct location).
3.  **User Experience:** Enable a smooth user experience where the application "remembers" the user's current selections and navigates logically.
4.  **Foundation for Collaboration:** Provide the state management primitives necessary for future multi-user collaboration features (e.g., knowing which workspace's resources to display).

### 1.2. Scope (V1 Concepts for this Document)

This initial conceptualization will focus on:

*   Identifying the **key types of state and context variables** needed for a single-user experience that is "workspace-aware" (i.e., can differentiate between a personal space and a conceptual shared workspace, even if V1 collaboration logic isn't fully implemented).
*   Describing how this state is **initialized, updated by user actions, and persisted** across interactions, primarily within the context of a Streamlit-like UI architecture (using `st.session_state`).
*   Outlining how different UI views and (conceptually) backend managers would **consume and react** to this context.
*   Identifying challenges and considerations for state management.

**Out of Scope for this V1 Conceptualization:**

*   Real-time state synchronization mechanisms for multi-user, simultaneous collaboration (this is a V2+ collaboration feature).
*   Complex URL routing for deep-linking into specific application states (Streamlit has limitations here, so `session_state` is the primary focus for V1 state).
*   Implementation of actual user authentication or a full-fledged user account system (we assume a `current_user_id` is conceptually available).

### 1.3. Key Context Types (Managed in `st.session_state` for Streamlit UI)

The following are key pieces of state/context that need to be managed:

1.  **`current_user_id` (str):**
    *   **Description:** The identifier for the currently (conceptually) logged-in user. For the V1 Streamlit prototype, this might be a hardcoded default (e.g., "default_streamlit_user").
    *   **Impacts:** Determines personal space for resources, user settings loading.

2.  **`active_workspace_id` (Optional[str]):**
    *   **Description:** The identifier of the currently active shared workspace. If `None`, the user is operating in their "Personal Space."
    *   **Impacts:** Filters resource listings in libraries (templates, conversations) to show items belonging to this workspace or the personal space. Influences save location for new shared resources.

3.  **`current_ui_page` (str; Enum-like):**
    *   **Description:** The main page or view the user is currently interacting with (e.g., "Dashboard", "PromptEditor", "ConversationComposer", "TemplateLibrary", "ConversationLibrary", "UserSettings").
    *   **Impacts:** Controls which primary UI section is rendered. (Already used in `streamlit_app.py` as `st.session_state.menu_choice`).

4.  **`current_editing_item_type` (Optional[Literal["PromptObject", "Conversation"]]):**
    *   **Description:** Indicates whether the user is currently focused on editing a `PromptObject` or a `Conversation`. `None` if no specific item is being edited (e.g., on Dashboard or in Libraries).
    *   **Impacts:** Helps determine which editor UI to display and what kind of "save" or "run" operations are relevant.

5.  **`current_editing_item_ref` (Optional[Any]):** (Name TBD, was `current_editing_item_id/version` before)
    *   **Description:** A reference to the actual in-memory object being edited if an item is loaded. For new items, this might be `None` until first save.
        *   In Streamlit, this is often handled by having specific session state variables like `st.session_state.current_prompt_object` or `st.session_state.current_conversation_object`.
    *   **Structure could be:** A dictionary like `{"id": "uuid", "version": 2, "object_instance": <the_actual_object>}` or simply relying on dedicated session state vars.
    *   **Impacts:** Provides the data for editor UIs. Tracks which specific item (and version) is active.

6.  **`active_turn_id_in_composer` (Optional[str]):**
    *   **Description:** When in the "ConversationComposer" and a specific turn is selected for detailed editing, this holds the `turn_id` of that active turn.
    *   **Impacts:** Determines which turn's details (PromptObject editor, notes, AIResponse) are shown in the "Selected Turn Detail Panel."

7.  **`ui_flags` (Optional[Dict[str, bool]]):**
    *   **Description:** For managing transient UI states, like the visibility of confirmation dialogs (e.g., `{"confirm_delete_tpl_X_vY": True}`).
    *   **Impacts:** Controls display of temporary UI elements. (Already used in `streamlit_app.py` for delete confirmations).

These context types, primarily managed within `st.session_state` in the Streamlit prototype, form the basis for a responsive and context-aware user interface.

---

## 2. State Initialization, Lifecycle, and Persistence (Conceptual for Streamlit)

Effective state management requires a clear understanding of how state variables are initialized, how their values change throughout the application lifecycle (typically driven by user interactions), and how this state is maintained across interactions within the Streamlit environment.

### 2.1. State Initialization

*   **On Application Start:** When the Streamlit application (`streamlit_app.py`) first starts for a user session:
    *   Key state variables in `st.session_state` must be initialized if they don't already exist. This is typically done at the beginning of the script.
    *   **`current_user_id`:** Initialized to a default value for the V1 prototype (e.g., `"default_streamlit_user"`). In a full system, this would be set after user authentication.
    *   **`active_workspace_id`:** Initialized to `None`, signifying the user starts in their "Personal Space."
    *   **`current_ui_page`:** Initialized to the default landing page (e.g., `"Dashboard"`). (This is `st.session_state.menu_choice` in `streamlit_app.py`).
    *   **`current_editing_item_type`:** Initialized to `None`.
    *   **`current_editing_item_ref`:** Initialized to `None` (or specific session state variables like `st.session_state.current_prompt_object` and `st.session_state.current_conversation_object` are initialized to `None`).
    *   **`active_turn_id_in_composer`:** Initialized to `None`.
    *   **`ui_flags`:** Not typically pre-initialized globally; specific flags are set/unset as needed by UI interactions (e.g., for delete confirmations).

### 2.2. State Lifecycle and Updates

*   **User-Driven Changes:** The values of these context variables change primarily based on user actions within the UI.
    *   Navigating the sidebar menu updates `current_ui_page`.
    *   Clicking "[New Prompt]" sets `current_editing_item_type` to "PromptObject" and populates `st.session_state.current_prompt_object` with a new instance. It also clears any active conversation context.
    *   Clicking "[New Conversation]" sets `current_editing_item_type` to "Conversation" and populates `st.session_state.current_conversation_object`. It clears any active single prompt context.
    *   Loading a template or conversation from a library updates `current_editing_item_type` and the relevant object in `st.session_state` (`current_prompt_object` or `current_conversation_object`).
    *   (Conceptual V1.x/V2) Selecting a workspace from a workspace switcher UI would update `active_workspace_id`.
    *   Selecting a turn in the Conversation Composer updates `active_turn_id_in_composer`.
    *   Actions like initiating a delete operation set specific `ui_flags`.
*   **System-Driven Changes (Indirect):** Some state might change as a result of system operations. For example, after saving a new version of a `PromptObject`, its `version` attribute (and thus the `current_editing_item_ref`'s data) is updated.

### 2.3. State Persistence (Streamlit Context)

*   **`st.session_state`:** In the context of the Streamlit prototype (`streamlit_app.py`), `st.session_state` is the **primary mechanism for persisting state across user interactions and script reruns within a single user session.**
    *   All key context variables listed in Section 1.3 are stored as attributes of `st.session_state`.
    *   When a user interacts with a widget (e.g., clicks a button, changes a text input), Streamlit typically reruns the script. Values stored in `st.session_state` are preserved across these reruns, allowing the UI to reflect the current context.
*   **No Long-Term Server-Side State (for UI Context):** Beyond the current session, this UI state is not automatically persisted on a server (unless explicitly saved, e.g., `UserSettings` are saved to files by `UserSettingsManager`). If the user closes their browser tab and starts a new session, `st.session_state` is reinitialized (unless Streamlit introduces features for session resumption from server-side storage, which is beyond our V1).
*   **Data Persistence vs. UI State Persistence:**
    *   It's important to distinguish between the persistence of UI *context* (e.g., what item is being edited) and the persistence of *data* (e.g., `PromptObject` templates saved as JSON files).
    *   `UserSettingsManager`, `TemplateManager`, `ConversationManager` handle data persistence to the file system.
    *   `st.session_state` handles the UI's memory of the current operational context for the active user session.

### 2.4. Resetting or Clearing Context

*   **Explicit Actions:**
    *   Clicking "[New Prompt]" or "[New Conversation]" explicitly clears the other editing context (e.g., `current_conversation_object` is set to `None` when a new prompt is started).
    *   Navigating away from an editor to a library view might clear the `current_editing_item_ref` if the item wasn't saved (or prompt the user to save "dirty" state - see Challenges).
*   **Session End:** As mentioned, `st.session_state` is typically cleared when the user session truly ends (e.g., browser tab closed for a sufficient duration, or server restarts if not deployed with session persistence).

Understanding this lifecycle is key to designing predictable and intuitive UI flows, especially in Streamlit's execution model.

---

## 3. Component Interaction with Context

The managed state and context variables are crucial for orchestrating the behavior of different UI views and for ensuring that backend operations (like saving and loading) occur in the correct user or workspace scope.

### 3.1. UI Views (`streamlit_app.py` as Primary Example)

The Streamlit UI (`streamlit_app.py`) heavily relies on `st.session_state` to manage and react to context:

1.  **Navigation and View Rendering:**
    *   `st.session_state.current_ui_page` (e.g., "Dashboard", "PromptEditor") directly controls which main section of the UI is rendered. Changing this variable (e.g., via sidebar navigation) causes Streamlit to display the corresponding page.

2.  **Editor Content Loading:**
    *   The "PromptEditor" loads its content based on `st.session_state.current_prompt_object`.
    *   The "ConversationComposer" loads its content based on `st.session_state.current_conversation_object`.
    *   These session state objects are populated when a user creates a "New" item or "Loads" an existing item from a library. The IDs and types of these items are implicitly part of the `current_editing_item_ref` context.

3.  **Library Views (Template & Conversation Libraries):**
    *   **Conceptual Requirement:** To support personal vs. workspace resources, the library views would need to display items based on the `active_workspace_id` (if set) or the `current_user_id` (if `active_workspace_id` is `None`, indicating "Personal Space").
    *   **Current `streamlit_app.py` V1 Implementation:** The managers (`template_manager`, `conversation_manager`) are initialized once by `@st.cache_resource` with fixed base paths (`prometheus_protocol_data_streamlit/templates` and `.../conversations`). This means the current V1 UI prototype *does not yet differentiate* between personal and workspace data; it shows everything within those fixed paths.
    *   **Future Interaction Model (Post V1 Collaboration Concepts):**
        *   When `active_workspace_id` changes, the manager instances might need to be re-initialized or have their target paths updated to point to the correct workspace-specific or user-specific directory (e.g., `data_root/workspaces/{workspace_id}/templates` vs. `data_root/users/{user_id}/personal/templates`).
        *   Alternatively, manager methods (`list_templates`, `load_template`, etc.) would need to accept a `context_id` (user or workspace) to construct paths internally. This is further discussed under "Backend Managers."

4.  **Action Enablement/Disability:**
    *   (Conceptual, especially for Collaboration V2+) UI controls (e.g., "Save," "Delete," "Add Turn") could be enabled or disabled based on the user's role within an `active_workspace_id` and their permissions for the `current_editing_item_ref`.

### 3.2. Backend Managers (Conceptual Invocation & Contextualization)

While the current Python implementations of `TemplateManager`, `ConversationManager`, and `UserSettingsManager` are initialized with a single base path, a fully context-aware system (especially for collaboration and multi-user scenarios) would require them to operate on context-specific data locations.

1.  **Path Scoping Challenge with Current Singleton Managers:**
    *   The `@st.cache_resource` decorator in `streamlit_app.py` creates singleton instances of managers. If their base paths are fixed at initialization, they cannot dynamically switch between, for example, `user_A/personal/templates`, `user_B/personal/templates`, or `workspace_X/templates` without re-initialization or internal changes.

2.  **Conceptual Solutions for Contextual Manager Operations:**

    *   **Option A: Context-Specific Manager Instantiation (UI Layer Responsibility):**
        *   The UI layer (e.g., `streamlit_app.py`), upon detecting a change in `active_workspace_id` or `current_user_id`, would be responsible for creating or retrieving a manager instance configured for that specific context's data path.
        *   This might mean `st.cache_resource` would need to be parameterized or bypassed for managers if their context changes frequently within a session. Or, a dictionary of manager instances (keyed by context ID) could be cached.
        *   Example: `current_manager = get_template_manager_for_context(st.session_state.active_workspace_id or st.session_state.current_user_id)`

    *   **Implemented Approach: Context ID Passed to Manager Methods:**
        *   This approach has been implemented for `TemplateManager` and `ConversationManager`.
        *   Their public methods (e.g., `save_template`, `load_template`, `list_templates`, `delete_template_version`, `delete_template_all_versions`, and their `ConversationManager` equivalents) now accept an optional `context_id: Optional[str]` parameter.
        *   Their `__init__` methods have been modified to accept a `data_storage_base_path` (conceptually from `AppConfig`).
        *   Internal private helper methods (e.g., `_get_context_specific_templates_path` and `_get_context_specific_conversations_path`) use the `data_storage_base_path` and the provided `context_id` to dynamically construct the correct file paths for operations (e.g., `base_path/user_personal_spaces/[user_id]/[asset_type]/` or `base_path/workspaces/[ws_id]/[asset_type]/`).
        *   This implementation allows manager instances (which can still be singletons like those cached in `streamlit_app.py`) to operate across different user or workspace contexts by specifying the target context in each method call.

    *   **Option C: Hybrid (Managers take base path, UI provides full path for operations):**
        *   This is less clean and not recommended.

    **Implemented Direction:** This implemented approach for `TemplateManager` and `ConversationManager` provides flexibility and aligns well with future scalability needs. For the V1 Streamlit app, these managers are now used with a default `context_id` ensuring the backend logic is context-aware even if the UI doesn't yet fully expose context switching.

3.  **`UserSettingsManager`:**
    *   This manager is inherently user-specific. Its `_get_user_settings_filepath(user_id)` already uses the `user_id` to scope paths, so it's naturally context-aware for its specific purpose.

The interaction between UI-managed context and backend manager operations is crucial for correctly scoping data access and storage, especially as features like collaboration are built out.

---

## 4. Challenges and Considerations for State Management

While using `st.session_state` provides a straightforward way to manage UI context in the V1 Streamlit prototype, several challenges and considerations arise, especially when looking towards more complex features and scalability.

1.  **URL Non-Addressability of State (Streamlit Limitation):**
    *   **Challenge:** Streamlit's `session_state` is not typically reflected in or driven by URL query parameters by default. This means users cannot easily bookmark or share a link to a specific state of the application (e.g., a particular prompt being edited in a specific workspace).
    *   **Consideration:** For V1, this is a known limitation of using basic Streamlit for rapid prototyping. V2+ or alternative web frameworks might offer better URL routing for deep linking and state sharing. Some Streamlit components or upcoming features might offer partial solutions.

2.  **"Dirty" State Management / Unsaved Changes:**
    *   **Challenge:** If a user edits a `PromptObject` or `Conversation` (modifying the in-memory object stored in `st.session_state`) and then tries to navigate away (e.g., load another item, switch pages, select a different workspace) without explicitly saving, their changes could be lost or they might inadvertently overwrite something else if not handled carefully.
    *   **Consideration:**
        *   The UI needs a clear "dirty" indicator (e.g., an asterisk `*` next to the item's title/version).
        *   Before navigating away from an editor with unsaved changes, a confirmation dialog ("You have unsaved changes. Save now? Discard? Cancel?") is crucial.
        *   This adds complexity to navigation and action button logic in `streamlit_app.py`.

3.  **Scalability of `st.session_state`:**
    *   **Challenge:** While convenient, storing many large objects (e.g., multiple complex `Conversation` objects with full `AIResponse` histories for each turn, if the user navigates through many) directly in `st.session_state` could potentially impact performance or memory usage in the browser/server for that session.
    *   **Consideration:** For V1, this is likely acceptable. For V2+, strategies might include:
        *   Only keeping essential IDs or summaries in `st.session_state` and reloading full objects from managers as needed (though this might affect UI responsiveness).
        *   More aggressive clearing of inactive objects from `session_state`.

4.  **Manager Contextualization Implementation:**
    *   **Challenge:** As discussed in Section 3.2, making the singleton file managers (`TemplateManager`, `ConversationManager`) truly context-aware (personal vs. specific workspace) requires either re-instantiation with new paths or modifying their methods to accept `context_id` parameters.
    *   **Consideration:** The "Context ID passed to manager methods" (Option B) is preferred conceptually for scalability but represents a significant refactoring of all manager methods (`save`, `load`, `list`, `delete`) and their internal path logic. This needs careful planning when V1 Collaboration concepts are implemented.

5.  **Complexity with Real-Time Collaboration (V2+):**
    *   **Challenge:** The current `st.session_state` model is for a single user's session. Real-time multi-user collaboration (e.g., two users editing the same prompt simultaneously) would require a completely different, server-backed state synchronization mechanism (e.g., WebSockets, operational transforms, or a collaborative backend datastore).
    *   **Consideration:** This is a V2+ architectural shift and is explicitly out of scope for V1 state management concepts.

6.  **Testing UI State Logic:**
    *   **Challenge:** Testing Streamlit applications, especially those heavily reliant on `st.session_state` for complex workflows, can be non-trivial. Unit testing core Python logic is straightforward, but end-to-end UI state flow testing often requires specialized tools or frameworks (e.g., Selenium, Playwright) or very careful manual testing.
    *   **Consideration:** For V1, manual workflow testing based on paper prototypes and the Streamlit app itself will be key. Automated UI testing is a V2+ consideration.

Addressing these challenges thoughtfully will be important as Prometheus Protocol evolves from a V1 prototype into a more feature-rich and robust application.

---

## 5. Conclusion (System State & Context Management Concepts)

This document has outlined the core concepts for managing system state and user context within Prometheus Protocol, primarily focusing on the needs of a V1 Streamlit-based user interface that is aware of users and (conceptual) workspaces.

Key aspects covered include:
*   The types of context variables essential for tracking user focus (e.g., `current_user_id`, `active_workspace_id`, `current_ui_page`, `current_editing_item_ref`).
*   The lifecycle of this state within Streamlit's `st.session_state` (initialization, updates via user action, persistence within a session).
*   How UI views would react to this context to display relevant information and controls.
*   The significant conceptual implication that backend managers (`TemplateManager`, `ConversationManager`) would need to evolve to accept a `context_id` to operate on specific user or workspace data paths, moving away from fixed directory initializations for true multi-context support.
*   Challenges such as URL addressability, "dirty" state management, and manager contextualization.

While the V1 Streamlit prototype (`streamlit_app.py`) currently uses a simplified approach with global managers operating on default paths, this conceptual framework for state and context management provides a crucial blueprint for future development, especially as Prometheus Protocol evolves towards more robust collaboration features and potentially different UI architectures. It highlights the need for a clear strategy to ensure data is scoped correctly and the user experience remains coherent across various operational contexts.

---
*End of System State & Context Management (Conceptual) document.*
