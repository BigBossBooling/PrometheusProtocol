# DashAIBrowser - Prometheus Protocol Integration: Conceptual UI/UX & Test Scenario

This document outlines the conceptual User Interface (UI) and User Experience (UX) elements for integrating Prometheus Protocol's capabilities within DashAIBrowser. It also describes a conceptual end-to-end integration test scenario.

## I. Goal

To make Prometheus Protocol's prompt engineering and optimization features seamlessly accessible to DashAIBrowser users (for content creation and general interaction) and developers (for AI-powered development workflows).

## II. Conceptual UI/UX Elements

### A. AI-Assisted Content Creation (User-Facing)

This feature aims to help users generate or refine text content within DashAIBrowser using optimized prompts.

1.  **Activation Points:**
    *   **Context Menu:** Right-clicking in any editable text area (e.g., email composer, document editor, social media post field) presents an "AI Assist" or "Generate with Prometheus" option.
    *   **Floating Action Button (FAB) / Toolbar Icon:** A discreet, always-available (or contextually appearing) icon that, when clicked, opens an AI assistance panel.
    *   **Slash Commands:** Typing `/ai` or `/prometheus` in a text field could trigger a small input for a brief instruction.

2.  **AI Assistance Panel/Modal:**
    *   **Input Mode Selection:**
        *   **"Quick Generate":** User types a brief instruction or topic (e.g., "write a polite refusal email to a meeting invitation," "summarize this webpage for a tweet").
        *   **"Use Template":** User selects from a list of predefined or user-saved prompt templates relevant to the current context (e.g., "Email - Polite Decline," "Social - Event Announcement").
        *   **"Refine Selection":** User selects existing text, and the AI offers to rephrase, summarize, expand, or change its tone using Prometheus.
    *   **Key Inputs (dynamic based on mode):**
        *   **Brief Instruction Field:** For "Quick Generate."
        *   **Template Selector:** Dropdown or searchable list.
        *   **Core Variables:** Small input fields for essential variables required by the selected template (e.g., for an email template, "Recipient Name," "Meeting Subject"). Prometheus Protocol would define which variables are core.
        *   **Tone/Style Modifiers (Optional):** Simple dropdowns (e.g., Tone: Formal, Friendly, Concise). These map to `context_modifiers`.
    *   **Action Button:** "Generate," "Refine," "Suggest."
    *   **Output Display:**
        *   Shows the LLM-generated text.
        *   Option to "Insert" into the original text field, "Copy," or "Try Again" (potentially with slight variations or by adjusting inputs).
    *   **Implicit Feedback:** The act of inserting or copying could be positive feedback. Closing without using could be negative. Explicit feedback (see below) is also crucial.

### B. DevTools Prompt Engineering Panel (Developer-Facing)

A dedicated panel within DashAIBrowser's Developer Tools for more advanced prompt engineering and testing.

1.  **Panel Layout:**
    *   **Template Management Area:**
        *   Select/Load existing Prometheus prompt templates (from a shared library or user's local/cloud storage).
        *   View/Edit template YAML/JSON directly.
        *   Save new or modified templates.
    *   **Input Configuration Area:**
        *   **Dynamic Variables:** Key-value input fields based on the selected template's `input_variables` schema.
        *   **Context Modifiers:** Key-value input fields or structured inputs for `persona`, `tone`, `style`, etc., based on `context_modifiers_schema`.
        *   **Original Prompt Text (for optimization):** A field to paste or type raw text that the user wants to optimize into a structured prompt or use as a base for optimization.
    *   **Control Area:**
        *   **"Generate Prompt" Button:** Calls ASOL's `GenerateOptimizedPrompt` with `apply_optimization: false` (or based on a toggle).
        *   **"Generate & Optimize Prompt" Button:** Calls `GenerateOptimizedPrompt` with `apply_optimization: true`.
        *   **"Simulate LLM Call" Button (Conceptual):** Sends the generated prompt to a (configurable or mock) LLM endpoint and displays the response.
    *   **Display Areas:**
        *   **Constructed Prompt View:** Shows the final prompt string (or message list) that would be sent to the LLM.
        *   **LLM Response View:** Displays the (simulated or actual) LLM response.
        *   **Optimization Feedback View:** Shows feedback history or scores related to the current template/prompt.
    *   **Feedback Submission:** UI elements to submit `PromptFeedbackRequest` data based on the (simulated) LLM response.

### C. Universal Feedback Mechanism

Discreet and easy ways for users to provide feedback on AI-generated content or suggestions.

1.  **Inline Feedback:**
    *   **Thumbs Up/Down:** Appears next to AI-generated content (e.g., inserted text, a suggested rephrasing).
    *   **Quick Rating (e.g., 1-5 stars):** Optional, could appear on hover or after interaction.
2.  **"Report Issue" / "Provide Detailed Feedback" Option:**
    *   Opens a small modal where users can provide:
        *   A qualitative score (if not already given).
        *   Indicate if the task was successful.
        *   Add a free-text comment.
3.  **Data Collection:** All feedback actions would trigger a `SubmitPromptFeedback` call to ASOL, including relevant IDs (`prompt_instance_id`, `template_id_used`) and the feedback data.

## III. Conceptual End-to-End Integration Test Scenario

This scenario outlines the data flow from DashAIBrowser to ASOL (and conceptually to Prometheus Protocol).

1.  **Setup:**
    *   DashAIBrowser is running.
    *   ASOL gRPC service stub (`AsolServiceImpl`) is running and accessible to DashAIBrowser.
    *   Prometheus Protocol (conceptual backend) is implicitly "connected" to ASOL for this test.
    *   A sample prompt template (e.g., "summarize_webpage") is known to both DashAIBrowser (e.g., selectable in DevTools panel) and conceptually by Prometheus Protocol.

2.  **User Action (Content Creation - Summarization):**
    *   User navigates to a webpage in DashAIBrowser.
    *   User activates the "AI Assist" feature (e.g., clicks a toolbar button).
    *   In the AI Assist Panel, user selects "Summarize this page." This implicitly selects the "summarize_webpage" template.
    *   The panel might automatically populate a `dynamic_variable` like `webpage_content_summary` (e.g., a condensed text version of the current page).
    *   User sets `context_modifiers` like `tone: "concise"`.
    *   User clicks "Generate Summary."

3.  **DashAIBrowser Frontend to ASOL (Request):**
    *   DashAIBrowser's frontend (Mojo/JavaScript) constructs a `PromptGenerationRequest` object:
        *   `template_id: "summarize_webpage_v1"`
        *   `dynamic_variables: {"webpage_content_summary": "<condensed text of page>"}`
        *   `context_modifiers: {"tone": "concise"}`
        *   `apply_optimization: true` (user might have a toggle, or it's default for this feature)
    *   The frontend makes a gRPC call to the `AsolService.GenerateOptimizedPrompt` RPC endpoint exposed by ASOL.

4.  **ASOL Service Stub Processing:**
    *   `AsolServiceImpl::GenerateOptimizedPrompt` method in `asol_service_impl.cc` receives the request.
    *   The stub logs: "Received GenerateOptimizedPrompt for template_id: summarize_webpage_v1, apply_optimization: true."
    *   **Conceptual Interaction with Prometheus Protocol:** The stub would normally forward this request to the actual Prometheus Protocol backend. The backend would:
        *   Use `FeedbackCollector` to get history for "summarize_webpage_v1".
        *   Use `OptimizationAgent` to potentially refine "summarize_webpage_v1" based on history.
        *   Use `PromptGenerator` with the (possibly optimized) template and provided variables/modifiers to construct the final LLM prompt string.
    *   **Stub Response:** The ASOL stub crafts a dummy `PromptGenerationResponse`:
        *   `final_prompt_string: "Summarize for me: <condensed text of page>. Make it concise. (ASOL Stub - Optimized)"`
        *   `generated_by_template_id: "summarize_webpage_v1_opt_stub_XYZ"`
        *   `error_message: ""`
    *   The stub returns this response to DashAIBrowser.

5.  **DashAIBrowser Frontend (Response Handling):**
    *   The frontend receives the `PromptGenerationResponse`.
    *   It displays `final_prompt_string` in the AI Assist Panel.
    *   (If this were a real LLM call, this string would be sent to an LLM, and the LLM's actual summary would be displayed).

6.  **User Provides Feedback:**
    *   User sees the (dummy) summary. Let's say they click "Thumbs Up" (which translates to a high `user_satisfaction_score` and `response_quality_score`).
    *   The frontend needs to have stored a `prompt_instance_id` associated with the interaction that led to this displayed summary.

7.  **DashAIBrowser Frontend to ASOL (Feedback):**
    *   Frontend constructs `PromptFeedbackRequest`:
        *   `prompt_instance_id: "<unique_id_for_this_interaction>"`
        *   `template_id_used: "summarize_webpage_v1_opt_stub_XYZ"` (from the response)
        *   `response_quality_score: 0.9`
        *   `user_satisfaction_score: 1.0`
        *   `task_success_status: true`
    *   Frontend makes a gRPC call to `AsolService.SubmitPromptFeedback`.

8.  **ASOL Service Stub Processing (Feedback):**
    *   `AsolServiceImpl::SubmitPromptFeedback` receives the request.
    *   Logs: "Received SubmitPromptFeedback for instance <unique_id_for_this_interaction>, score: 0.9."
    *   **Conceptual Interaction:** Would forward to Prometheus Protocol's `FeedbackCollector`.
    *   **Stub Response:** Crafts `PromptFeedbackResponse`:
        *   `feedback_acknowledged: true`
        *   `message: "Feedback received by ASOL stub."`
    *   Returns response to DashAIBrowser.

9.  **DashAIBrowser Frontend (Feedback Ack):**
    *   Frontend receives acknowledgment. UI might show a small "Feedback sent" notification.

This scenario validates the defined gRPC interface and the basic request/response flow between DashAIBrowser and a conceptual ASOL backend that interfaces with Prometheus Protocol. The stubs allow for frontend development and testing of the UI/UX elements even before the full Prometheus Protocol backend is connected to ASOL.

## IV. Feature: AI-Powered Summarization & Content Digest

This section details the UI/UX for an on-demand content summarization feature, leveraging ASOL and the conceptual EchoSphere AI-vCPU.

### A. Activation Points & UI

1.  **"Sparkle" Icon in Address Bar (Omnibox):**
    *   A discreet "✨" (Sparkle) icon appears in the address bar when a page with summarizable content is loaded (e.g., articles, long documents).
    *   **Interaction:**
        *   Clicking the Sparkle icon opens a small popover/dropdown directly beneath it.
        *   The popover shows:
            *   "Generate Summary" button.
            *   Options for summary length: "Short," "Medium," "Detailed" (maps to `SummaryLengthPreference`). Default could be "Medium."
            *   A "Settings" cog for advanced options (e.g., target audience - conceptual for later).
    *   **Alternative:** The icon could directly trigger a "Medium" summary, with options available post-generation.

2.  **Context Menu Integration:**
    *   **Page Summary:** Right-clicking anywhere on a webpage shows a "DashAI: Summarize Page" option.
    *   **Selected Text Summary:** If text is selected on the page, right-clicking shows "DashAI: Summarize Selected Text."
    *   **Interaction:** Selecting these options could either:
        *   Immediately generate a summary with default options and display it (see Display Methods).
        *   Open the same Sparkle icon popover with pre-filled context (page vs. selection).

3.  **Dedicated "Digest" Panel/Sidebar:**
    *   A toggleable sidebar or a dedicated panel (perhaps part of a larger "AI Tools" panel).
    *   **Content:**
        *   "Summarize Current Page" button.
        *   If text is selected on the page: "Summarize Selection" button appears.
        *   Input field: "Summarize specific URL or text..." (user can paste content).
        *   Display area for the generated summary.
        *   History of recent summaries.
        *   Controls for summary length and other options.

### B. Summary Display Methods

1.  **Popover/Notification:**
    *   For quick summaries (e.g., triggered from address bar icon with default settings).
    *   A non-intrusive popover or a rich notification displays the summary.
    *   Actions: "Copy Summary," "View Full Digest" (opens the Digest Panel), "Refine" (opens options to regenerate).

2.  **Digest Panel/Sidebar:**
    *   The primary display area for summaries, especially detailed ones or when multiple summaries are generated.
    *   Displays the summary text.
    *   Source indication (e.g., "Summary of [Page Title/URL/Selection Snippet]").
    *   Actions: "Copy," "Save to Notes," "Share," "Regenerate with different options."
    *   Feedback mechanism (thumbs up/down, rating) for the summary quality.

### C. Interaction Flow Example (Address Bar Icon)

1.  User loads an article page. The "✨" icon appears in the address bar.
2.  User clicks the "✨" icon.
3.  A small popover appears:
    *   Title: "AI Page Digest"
    *   Buttons: "Short Summary" | "Medium Summary" | "Detailed Summary"
    *   (Optional) Cog icon for "More Options."
4.  User clicks "Medium Summary."
    *   **Browser-Side Action (Conceptual `SummaryService`):**
        *   A browser component (e.g., an action handler for the UI) gets the current page's main content (e.g., using a conceptual `PageContentExtractor`).
        *   It calls `SummaryService::GetSummary(page_content, {length_preference: MEDIUM}, callback)`.
    *   **Mojo IPC (Browser to ASOL):**
        *   `SummaryService` uses its Mojo remote to call `ContentAnalyzer::RequestSummary(page_content, options)` which crosses the process boundary to ASOL.
    *   **ASOL - Mojo Service Implementation (`ContentAnalyzerImpl` - Conceptual):**
        *   The `ContentAnalyzerImpl::RequestSummary` method in ASOL is invoked.
        *   It constructs a `PageSummaryRequest` gRPC message (if calling its own gRPC service) or directly constructs an `AiTaskRequest`.
        *   **Decision from plan:** ASOL's `GetPageSummary` gRPC service will be called. So, `ContentAnalyzerImpl` makes a local gRPC call to `AsolServiceImpl::GetPageSummary`.
    *   **ASOL - `AsolServiceImpl::GetPageSummary` (gRPC method):**
        *   Receives `PageSummaryRequest`.
        *   Constructs `core::ConceptualAiTaskRequest` with `task_type: "SUMMARIZE_TEXT"`, `input_data` containing `page_content` and `length_preference`.
        *   Calls `vcpu_interface_->SubmitTask(ai_task_request)`.
    *   **EchoSphere AI-vCPU (Mocked):**
        *   The `MockEchoSphereVCPU::SubmitTask` is called.
        *   It's configured for this test to expect a "SUMMARIZE_TEXT" task.
        *   It returns a predefined `core::ConceptualAiTaskResponse` with `success: true` and `output_data["summary_text"] = "This is a mocked summary of the page content."`.
    *   **ASOL - `AsolServiceImpl::GetPageSummary` (Response Handling):**
        *   Receives the `AiTaskResponse` from the vCPU.
        *   Extracts the summary and populates a `ConceptualPageSummaryResponse` (gRPC response type).
        *   Returns this to its caller (`ContentAnalyzerImpl`).
    *   **ASOL - Mojo Service Implementation (`ContentAnalyzerImpl` - Callback):**
        *   Receives the `PageSummaryResponse`.
        *   Invokes the Mojo callback provided by `SummaryService` with `(summary_text, error_message)`.
    *   **Browser-Side Action (`SummaryService` Callback):**
        *   The callback in `SummaryService` is executed.
        *   It receives "This is a mocked summary of the page content." and an empty error string.
7.  **Displaying the Summary:**
        *   `SummaryService` (or its caller) updates the browser UI (e.g., Digest Panel, popover) with the received summary.
    *   **Feedback (Separate Flow):** User can provide feedback on the summary, triggering the `SubmitPromptFeedback` flow detailed previously.

This detailed scenario validates the entire conceptual pipeline from browser UI interaction, through Mojo IPC, ASOL's gRPC service handling, delegation to the (mocked) AI-vCPU, and the response path back to the UI.
