# UI Concept: Main Dashboard

## 1. Overview

The Main Dashboard is the primary landing screen for users of Prometheus Protocol. It provides quick access to core functionalities, recent work, and navigation to different modules of the application. The design should be clean, intuitive, and prioritize common user workflows.

## 2. Layout

A responsive layout, potentially adapting from a three-column to a two-column or single-column stack on smaller screens.

*   **Persistent Navigation Panel (e.g., Left Sidebar or Top Navbar):** Contains primary navigation links.
*   **Main Content Area:** Divided into logical sections for actions and information.

## 3. Key Elements

### 3.1. Navigation Panel

*   **Links:**
    *   **Dashboard:** (Current view)
    *   **Prompt Editor:** Navigates to the interface for creating/editing single `PromptObject`s.
    *   **Conversation Composer:** Navigates to the interface for creating/editing multi-turn `Conversation`s.
    *   **Template Library:** Navigates to a browser for saved `PromptObject` templates.
    *   **Conversation Library:** Navigates to a browser for saved `Conversation` files.
    *   **Settings:** (Conceptual) For application or user preferences.
    *   **Help/Docs:** (Conceptual) Link to documentation.

### 3.2. Main Content Area

#### 3.2.1. Quick Actions & Search

*   **"Create New" Section:**
    *   Prominent button: **"+ New Prompt"** (navigates to Prompt Editor with a new, empty prompt).
    *   Prominent button: **"+ New Conversation"** (navigates to Conversation Composer with a new, empty conversation).
*   **Global Search Bar (Conceptual):**
    *   A search input field.
    *   Placeholder text: "Search templates and conversations..."
    *   Functionality: (Conceptual) Allows users to quickly find saved `PromptObject` templates and `Conversation` files by name, tags, or keywords in content.

#### 3.2.2. Recent Activity / Quick Access

This section helps users quickly resume their work.

*   **"Recent Templates" List:**
    *   Displays the names of the 3-5 most recently saved/accessed `PromptObject` templates.
    *   Each item is a link that, when clicked, loads the template into the Prompt Editor.
    *   Could show a small "last modified" timestamp next to each.
    *   Source: Data retrieved via `TemplateManager`.

*   **"Recent Conversations" List:**
    *   Displays the names/titles of the 3-5 most recently saved/accessed `Conversation` files.
    *   Each item is a link that, when clicked, loads the conversation into the Conversation Composer.
    *   Could show a small "last modified" timestamp next to each.
    *   Source: Data retrieved via `ConversationManager`.

### 3.3. Footer (Conceptual)

*   Displays application version information.
*   Copyright notice.
*   Link to "About Prometheus Protocol".

## 4. User Flow Examples

*   **Starting a new prompt:** User clicks "+ New Prompt" -> Navigates to Prompt Editor.
*   **Resuming work on a template:** User clicks a template name in "Recent Templates" -> Template loads in Prompt Editor.
*   **Finding an old conversation:** User types a keyword in the Global Search Bar -> Search results page/dropdown shows matching conversations -> User clicks a result to load it in Conversation Composer.

## 5. Design Principles Embodied

*   **KISS (Clarity & Accessibility):** Clear calls to action, easy navigation.
*   **KISS (Efficiency & Engagement):** Quick access to recent items and creation workflows.
