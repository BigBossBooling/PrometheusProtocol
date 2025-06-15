# Prometheus Protocol: Collaboration Features (V1 Concepts)

This document outlines initial conceptual ideas for collaboration features within the Prometheus Protocol, enabling multiple users to work together on prompt engineering projects.

## I. Goals of Collaboration Features (V1)

The primary goals for the initial version (V1) of collaboration features are:

1.  **Shared Access:** Enable multiple users to access and view common `PromptObject` templates and `Conversation` objects within a defined group or team context.
2.  **Controlled Contributions:** Allow designated users to edit and save new versions of these shared resources.
3.  **Basic Permission Model:** Introduce a simple role-based permission system to manage access and editing rights within a shared context.
4.  **Asynchronous Workflow:** Support asynchronous collaboration where users can work on shared resources independently, with versioning handling distinct contributions rather than real-time co-editing.
5.  **Foundation for Growth:** Lay the conceptual groundwork for more advanced collaboration features in future versions.

## II. Scope for V1 Concepts

The V1 conceptualization will focus on:

1.  **"Shared Workspaces" or "Teams":** A basic grouping mechanism for users and shared resources.
2.  **Resource Ownership:** Distinguishing between personal resources and those owned by/shared with a workspace.
3.  **Simple Roles/Permissions:** A minimal set of roles (e.g., Owner/Admin, Editor, Viewer) at the workspace level.
4.  **Sharing Mechanisms:** Conceptual ways to move or link personal resources to a shared workspace.
5.  **Impact on Resource Managers:** How `TemplateManager` and `ConversationManager` would conceptually need to be aware of workspaces and permissions (no code changes in this phase).
6.  **Handling Concurrent Edits (Asynchronously):** Leveraging the existing versioning system to manage contributions from multiple users working non-simultaneously on the same base template/conversation.

**Out of Scope for V1 Concepts (Future Considerations):**

*   **Real-time Co-editing:** Simultaneous editing of the same prompt by multiple users with live updates.
*   **Complex Version Merging/Branching:** Advanced Git-like merging of different versions or branches of a prompt/conversation. V1 will rely on linear version history with implicit branching if two users edit the same base version.
*   **Detailed Audit Trails:** Comprehensive logs of all changes made by all users to shared resources.
*   **Granular Per-Item Permissions:** Setting different permissions for specific templates or conversations within the same workspace. V1 assumes workspace-level roles.
*   **Project Management Features:** Task assignments, deadlines, review workflows, etc.
*   **In-app Notifications for All Changes:** While basic "newer version available" notifications might be considered, rich, real-time notifications for all collaborative activities are V2+.
*   **User Account Management System:** Detailed specification of user registration, profiles, etc., is assumed to be a prerequisite handled by a broader platform context if Prometheus Protocol is part of one. We will assume users have unique identifiers.

---
*Next sections will detail Shared Workspaces, Roles/Permissions, Sharing Mechanisms, Manager Impacts, Concurrent Edit Handling, and UI Implications.*

## III. "Shared Workspaces" / "Teams" Concept

To facilitate collaboration, Prometheus Protocol will introduce the concept of a "Shared Workspace" (or "Team Space"). This serves as a container for users and the `PromptObject` templates and `Conversation` objects they collaborate on.

### A. Workspace Characteristics

1.  **Entity:** A workspace is a distinct entity within Prometheus Protocol.
2.  **Naming:** Each workspace has a unique name (e.g., "Marketing Team Prompts," "Project Alpha Dialogues").
3.  **Membership:** Workspaces have a list of members (users). Each member is associated with a specific role within that workspace (see Section IV).
4.  **Resource Container:** A workspace "owns" or contains `PromptObject` templates and `Conversation` objects that are shared among its members. This is distinct from a user's personal, private resources.
5.  **Creation:**
    *   Any user can potentially create a new workspace, becoming its initial Owner/Admin.
    *   (V2 Consideration: System-level policies might restrict who can create workspaces, e.g., only users with a certain subscription level).

### B. Resource Ownership and Visibility

1.  **Personal Space:** By default, when a user creates a new `PromptObject` template or `Conversation`, it resides in their "personal space" and is private to them.
2.  **Workspace Space:** Resources (templates, conversations) can be explicitly moved or shared into a workspace. Once in a workspace:
    *   They are considered "owned" by the workspace entity itself, rather than an individual user (though an original creator might still be tracked via metadata like `PromptObject.created_by_user_id` - a new field to consider for `PromptObject`/`Conversation` if not implicitly handled by versioning/audit).
    *   Visibility and access are governed by workspace membership and roles.
3.  **Access Control:** Users who are members of a workspace can see and interact with the resources it contains according to their assigned role within that workspace. Users not part of the workspace cannot access its resources.

### C. Number of Workspaces

*   A user might be a member of multiple workspaces.
*   A user still has their own "personal space" for private work.
*   The UI will need a clear way for users to switch between their personal space and any workspaces they are part of (see Section VIII on UI Implications).

This workspace model provides a basic but effective way to group users and resources for collaborative prompt engineering efforts.

---
*Next section: Basic User Roles and Permissions within a Workspace.*

## IV. Basic User Roles and Permissions (V1)

Within a Shared Workspace, a simple role-based permission system will govern what actions members can perform on the workspace's resources (`PromptObject` templates and `Conversation` objects). For V1, these roles are assigned at the workspace level and apply to all resources contained within that workspace.

### A. Defined Roles

1.  **Workspace Owner / Admin:**
    *   **Capabilities:**
        *   Full control over all resources within the workspace (create, view, edit, delete, save new versions).
        *   Manage workspace settings (e.g., rename workspace, delete workspace - V2).
        *   Manage workspace members:
            *   Invite new members.
            *   Remove existing members.
            *   Change the roles of existing members (e.g., promote an Editor to Admin, demote an Editor to Viewer).
    *   **Assignment:** Typically, the creator of a workspace becomes its initial Owner/Admin. Multiple Owners/Admins might be possible.

2.  **Workspace Editor:**
    *   **Capabilities:**
        *   Create new `PromptObject` templates and `Conversation` objects within the workspace.
        *   View all resources within the workspace and their different versions.
        *   Edit existing resources (which, with versioning, means creating a new version based on their edits when saving).
        *   Delete resources from the workspace (subject to confirmation, and perhaps a soft-delete/trash V2 feature).
    *   **Limitations:** Cannot manage workspace settings or members.

3.  **Workspace Viewer:**
    *   **Capabilities:**
        *   View all resources within the workspace and their different versions.
        *   "Duplicate" or "Copy to Personal Space": Can take a copy of a workspace resource to their personal space, where they would then have full editing rights over that copy. The original workspace resource remains untouched by this action.
    *   **Limitations:** Cannot create, edit, or delete resources directly within the workspace. Cannot save new versions of existing workspace resources.

### B. Permission Application

*   **Workspace Scope:** In V1, a user's role is assigned for the entire workspace. This role dictates their permissions for all templates and conversations within that workspace.
*   **No Per-Item Granularity (V1):** We will not implement finer-grained permissions on individual templates or conversations within a workspace for V1 (e.g., this template is read-only for Editor X, but editable for Editor Y).
*   **Personal Space:** These roles do not apply to a user's personal space, where they always have full owner-like control over their own private resources.

### C. Default Role for New Members

*   When inviting a new member to a workspace, the Owner/Admin would assign them one of the defined roles (Editor or Viewer, typically not another Owner/Admin directly unless intended).
*   A default role (e.g., "Viewer") might be pre-selected during the invitation process.

This simple RBAC model provides a balance between collaborative access and controlled contribution for V1. More granular controls can be a future enhancement.

---
*Next section: Conceptualize Sharing Mechanisms.*

## V. Conceptual Sharing Mechanisms (V1)

This section outlines how users can share their personal resources (`PromptObject` templates, `Conversation` objects) with a Shared Workspace and how members are managed within a workspace.

### A. Sharing Personal Resources with a Workspace

Users need a way to contribute their individual work to a collaborative environment.

1.  **Action: "Move to Workspace" or "Share with Workspace"**
    *   **UI Context:** When viewing a list of their personal templates or conversations, or when editing a specific personal item, a user would have an option like "[Move to Workspace...]" or "[Share with Workspace...]" (perhaps in a context menu or an action button).
    *   **Process:**
        1.  User selects this action.
        2.  A dialog appears listing all workspaces where the user has "Editor" or "Owner/Admin" permissions (as only these roles can typically add content).
        3.  User selects the target workspace.
        4.  Upon confirmation:
            *   The resource (template or conversation) is conceptually moved or copied from the user's personal space to the selected workspace.
            *   **Ownership Change:** The resource is now "owned" by the workspace. The original creator might still be tracked via metadata (e.g., a `created_by_user_id` field on the `PromptObject`/`Conversation` or its first version).
            *   **Visibility/Permissions:** The resource immediately becomes subject to the target workspace's member roles and permissions.
            *   (V1.1 Consideration: "Move" implies removal from personal space, "Share/Copy" implies the original stays personal and a copy goes to workspace. For V1, "Move" is simpler to manage to avoid desynchronized copies, but "Copy to Workspace" might be safer if users want to keep a personal master). Let's assume **"Move to Workspace"** as the primary V1 mechanism for simplicity, clearly indicating a change of ownership context.

### B. Managing Workspace Membership

Workspace Owners/Admins are responsible for managing who has access to the workspace.

1.  **Inviting New Members:**
    *   **UI Context:** Within a workspace settings view (accessible to Owners/Admins).
    *   **Process:**
        1.  Owner/Admin enters the identifier of the user to invite (e.g., username or email, assuming a user system exists).
        2.  Owner/Admin assigns a role (Editor or Viewer) to the invitee for this workspace.
        3.  System (conceptually) sends an invitation.
        4.  Invited user receives a notification and can accept or decline.
        5.  Upon acceptance, the user is added to the workspace's member list with the assigned role.

2.  **Removing Members:**
    *   **UI Context:** Workspace settings view (Owners/Admins only).
    *   **Process:** Owner/Admin selects a member and chooses to "Remove from Workspace."
    *   **Effect:** The user loses access to the workspace and its resources (unless they have other means of access, e.g., via another team they are part of that also has some link to these resources - out of scope for V1).

3.  **Changing Member Roles:**
    *   **UI Context:** Workspace settings view (Owners/Admins only).
    *   **Process:** Owner/Admin selects a member and can change their assigned role (e.g., Viewer to Editor, Editor to Viewer).
    *   **Effect:** The member's permissions within the workspace are updated immediately.

These mechanisms provide the basic framework for populating workspaces with shared content and managing their collaborative user base.

---
*Next section: Discuss Impact on Existing Managers.*

## VI. Impact on Existing Managers (`TemplateManager`, `ConversationManager`)

Introducing Shared Workspaces and resource ownership will conceptually impact how `TemplateManager` and `ConversationManager` operate. While full implementation details are beyond V1 concepts for collaboration itself, we need to consider these impacts.

### A. Awareness of Context (Personal vs. Workspace)

*   Both managers currently operate on a single directory (`templates/`, `conversations/`). In a collaborative model, this single directory might need to represent the user's "current context" (either their personal space or an active workspace).
*   Alternatively, the directory structure itself might need to be partitioned (e.g., `user_personal_space/user_xyz/templates/`, `workspaces/workspace_abc/templates/`). This has implications for file paths.

### B. Potential Modifications to Manager Methods (Conceptual)

Let's consider `TemplateManager` as an example; similar changes would apply to `ConversationManager`.

1.  **`__init__(self, base_dir_for_user_or_workspace: str)`:**
    *   The constructor might need to be initialized with a path that points to the *specific context* it's managing (e.g., `TemplateManager(templates_dir="path/to/workspace_xyz/templates")` or `TemplateManager(templates_dir="path/to/user_abc/personal/templates")`).
    *   A higher-level part of the application would decide which path to pass based on the user's currently selected workspace/personal space.

2.  **`save_template(self, prompt: PromptObject, template_name: str) -> PromptObject`:**
    *   **Permissions Check (Conceptual):** Before saving, the manager (or a layer above it) would need to verify if the current user has "Editor" or "Owner/Admin" rights in the current context (if it's a workspace). If not, the save operation should be denied.
    *   **Ownership Metadata (Conceptual):** When a new template (version 1) is saved, metadata about its owner context (e.g., `workspace_id` or `user_id` for personal space) should be stored, perhaps within the JSON file itself or in a separate manifest/database. For V1 of collaboration concepts, the file path (e.g., being in `workspaces/workspace_abc/`) might implicitly define this.

3.  **`load_template(self, template_name: str, version: Optional[int] = None) -> PromptObject`:**
    *   **Permissions Check (Conceptual):** Needs to ensure the user has at least "Viewer" rights for the context (workspace) from which the template is being loaded.
    *   It would operate on the `templates_dir_path` set during initialization, which points to the correct user/workspace context.

4.  **`list_templates(self) -> Dict[str, List[int]]`:**
    *   Would list templates only from the `templates_dir_path` it was initialized with (i.e., within the current user/workspace context).
    *   No explicit filtering logic needed inside `list_templates` itself if the `templates_dir_path` already points to the correctly scoped directory.

5.  **`delete_template_version` (If implemented):**
    *   Would also require "Editor" or "Owner/Admin" permission checks for the context.

### C. Data Storage Implications

*   **File System Approach (Current Model):**
    *   If we stick to a pure file system approach, the top-level directory structure becomes critical. Example:
        ```
        prometheus_data/
        ├── user_personal_spaces/
        │   └── user_id_123/
        │       ├── templates/
        │       │   └── my_personal_prompt_v1.json
        │       └── conversations/
        │           └── my_chat_v1.json
        └── workspaces/
            └── workspace_id_abc/
                ├── templates/
                │   └── shared_team_prompt_v1.json
                │   └── shared_team_prompt_v2.json
                └── conversations/
                    └── project_dialogue_v1.json
        ```
    *   The `TemplateManager` or `ConversationManager` would then be instantiated pointing to the relevant subdirectory.
*   **Database Approach (V2+):**
    *   A database could store prompts and conversations along with `owner_user_id` and `workspace_id` columns. Managers would then query based on these IDs and user permissions. This is more robust for complex queries and permissions but is a larger architectural shift. For V1 concepts, acknowledging the file system implications is sufficient.

### D. No Direct Code Changes to Managers in This Conceptual Phase

It's important to reiterate that these are *conceptual impacts*. We are not changing the Python code of `TemplateManager` or `ConversationManager` as part of *conceptualizing collaboration features*. This discussion informs future implementation phases if collaboration is pursued.

The current implementation of these managers is context-agnostic (they work on the directory they are given). A higher-level application layer would be responsible for instantiating them with the correct directory path based on the active user and their selected workspace/personal space context.

---
*Next section: Address Concurrent Edits (V1 Asynchronous Approach).*

## VII. Handling Concurrent Edits (V1 Asynchronous Approach)

With multiple users potentially accessing and editing shared resources in a workspace, a strategy for handling "concurrent" edits is needed. For V1, Prometheus Protocol will support an **asynchronous collaboration model**, meaning users are not co-editing in real-time. The existing versioning system of `TemplateManager` (and a similar system for `ConversationManager`) is key to managing this.

### A. Scenario

Consider the following common scenario:

1.  **User A** opens "SharedTemplateX" (which is currently at version 1 - `SharedTemplateX_v1.json`) from a workspace. Their editor now has the content of v1 in memory.
2.  **User B** also opens "SharedTemplateX" (v1) from the same workspace. Their editor also has v1 content in memory.
3.  **User B** makes changes and saves their work.
    *   The `TemplateManager.save_template(prompt_object_from_B, "SharedTemplateX")` method is called.
    *   It detects that `_v1.json` exists, finds it's the highest version.
    *   It increments the version for User B's prompt object to 2.
    *   It saves User B's work as `SharedTemplateX_v2.json`.
    *   User B's editor now reflects that they are working on/just saved v2.
4.  **User A** (who still has their modified version of the original v1 content in their editor) then saves their work.
    *   `TemplateManager.save_template(prompt_object_from_A, "SharedTemplateX")` is called.

### B. V1 Resolution: Leveraging Automatic Versioning

Prometheus Protocol's `TemplateManager.save_template` method (as designed in the "Prompt Versioning" feature) inherently handles this scenario by always creating a new, incremented version based on the *current highest version number on disk for that base name*.

1.  **User A's Save Action:**
    *   When `TemplateManager.save_template(prompt_object_from_A, "SharedTemplateX")` is called:
        *   It calls `_sanitize_base_name("SharedTemplateX")` -> `"SharedTemplateX"`.
        *   It calls `_get_highest_version("SharedTemplateX")`. At this point, `SharedTemplateX_v2.json` exists on disk (from User B's save), so this returns `2`.
        *   `new_version` is calculated as `2 + 1 = 3`.
        *   The `prompt_object_from_A` (which User A was editing, possibly based on their initial load of v1) has its `version` attribute updated to `3`.
        *   `prompt_object_from_A.touch()` updates its `last_modified_at`.
        *   The content from `prompt_object_from_A` is saved as `SharedTemplateX_v3.json`.
        *   The updated `prompt_object_from_A` (now with `version = 3`) is returned.

2.  **Result: Implicit Branching / Divergence**
    *   The file system now contains:
        *   `SharedTemplateX_v1.json` (original)
        *   `SharedTemplateX_v2.json` (User B's changes, based on v1)
        *   `SharedTemplateX_v3.json` (User A's changes, also based on v1 but saved later as a new version).
    *   This creates an implicit divergence or branch in the history:
        ```
          v1
         /  \
        v2   v3
        (B)  (A)
        ```
    *   This is a simple and robust way to ensure no work is lost in an asynchronous V1 model.

### C. User Interface Notifications (Conceptual)

While the backend handles this without data loss, the UI should provide some awareness:

1.  **On Load (Stale Copy Check - V1.1/V2):**
    *   When User A initially loads `SharedTemplateX_v1.json`, the system could note its version.
    *   If User B saves `_v2.json` while User A is still editing their copy of v1, User A's editor *could* (as a V1.1 or V2 enhancement) receive a subtle notification: "A newer version (v2) of 'SharedTemplateX' has been saved by another user. You are currently editing based on v1." This is non-blocking.
    *   **For V1 core functionality, this notification can be deferred.** The save will still work correctly as described above.

2.  **On Save (When Divergence Occurs):**
    *   When User A saves and `SharedTemplateX_v3.json` is created (because v2 already existed), the UI should clearly inform User A:
        *   "Your changes to 'SharedTemplateX' have been saved as new version 3."
        *   "Note: Version 2 was created by another user while you were editing. You may want to review version 2 to see if any changes need to be manually reconciled with your version 3."
    *   This makes the user aware of the divergence.

### D. No Automatic Merging in V1

*   Prometheus Protocol V1 will **not** attempt to automatically merge changes from divergent versions (e.g., v2 and v3 in the scenario).
*   Manual Reconciliation: If users need to combine changes from different "branches" (like v2 and v3), they would need to:
    1.  Load v2.
    2.  Load v3 (perhaps in a separate editor instance or one after the other).
    3.  Manually compare and consolidate the desired changes into a new `PromptObject`.
    4.  Save this consolidated version, which would then become `SharedTemplateX_v4.json`.

This V1 approach prioritizes simplicity and data integrity by leveraging the existing "always save as new version" logic. It avoids the complexities of three-way merges or operational transforms needed for more sophisticated conflict resolution or real-time collaboration.

---
*Next section: Outline UI Concept Implications.*

## VIII. UI Concept Implications for Collaboration (V1)

Introducing collaboration features, even in their V1 asynchronous form, will necessitate several additions and modifications to the Prometheus Protocol user interface. These are high-level considerations that would need further detailing in UI-specific design documents (like `prompt_editor.md` or `conversation_composer.md`, or a new `workspace_ui.md`).

1.  **Workspace Navigation / Context Switching:**
    *   **UI Element:** A clear mechanism for the user to see their current context (e.g., "My Personal Space," "Marketing Team Workspace") and to switch between their personal space and any workspaces they are a member of.
    *   **Location:** Could be a prominent dropdown in a main header/navigation bar, or a dedicated section in a sidebar.
    *   **Impact:** Lists of templates (`TemplateManager.list_templates()`) and conversations (`ConversationManager.list_conversations()`) would dynamically update to reflect the selected context.

2.  **Resource Ownership and Sharing Indicators:**
    *   **UI Element:** When viewing lists of templates or conversations, or when editing an item, there should be clear visual indicators of:
        *   **Ownership:** "Owner: You (Personal)" vs. "Workspace: Marketing Team."
        *   **Permissions:** Subtle cues about the user's current permissions for an item in a workspace (e.g., "View Only" badge if they are a Viewer, edit controls disabled).
    *   **Sharing Actions:** Context menus or action buttons for personal items like "[Move to Workspace...]" or "[Share with Workspace...]" (name TBD).

3.  **Workspace Management UI (for Workspace Owners/Admins):**
    *   **Access:** A dedicated "Workspace Settings" or "Manage Workspace" area, accessible only to Owners/Admins of the currently active workspace.
    *   **Functionality:**
        *   View list of current workspace members and their roles.
        *   Invite new members (input for user identifier, role assignment dropdown).
        *   Change roles of existing members.
        *   Remove members from the workspace.
        *   (V2+) Edit workspace name, description, or delete the workspace.

4.  **Notifications for Collaborative Activity (Simple V1):**
    *   **"Newer Version Available":** As discussed in Section VII.C, if a user has a template/conversation open (e.g., `_v1`) and another user saves a newer version (`_v2`), a non-intrusive notification could appear in the editor: "Heads up: A newer version (v2) of this item is available. Your current changes, if saved, will create version 3."
    *   **Save Confirmation with Version Context:** When saving a shared item that results in a new version due to concurrent edits (e.g., user saves v3 because v2 was just created), the confirmation message should be clear: "Saved as version 3. Note: Version 2 was recently created by another user."

5.  **Invitations/Notifications Area (Global UI):**
    *   A general notifications area in the application (e.g., a bell icon) where users can see:
        *   Invitations to join new workspaces (with Accept/Decline actions).
        *   (V2+) Other relevant notifications about shared resource updates.

These UI implications aim to make the V1 collaboration features understandable and usable, providing necessary context and controls without overwhelming the user with the complexities of a full real-time system.

---
*End of Collaboration Features (V1 Concepts) document.*
