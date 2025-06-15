# Prometheus Protocol: Creative Catalyst Modules Concepts

This document outlines conceptual ideas for "Creative Catalyst" modules within the Prometheus Protocol. These modules are designed to assist users in the ideation and creative formulation phases of prompt engineering.

## I. Overall Goals and Philosophy

### A. Goals

The primary goals for the Creative Catalyst Modules are:

1.  **Spark Creativity & Overcome Blocks:** Help users overcome the "blank page" challenge by providing inspiration and alternative perspectives when they are unsure how to start or refine a prompt component.
2.  **Enhance Prompt Quality & Nuance:** Encourage users to explore more diverse and effective options for prompt elements like roles, tasks, context, constraints, and examples, leading to richer and more nuanced prompts.
3.  **Increase Engagement & Exploration:** Make the prompt creation process itself more interactive, engaging, and exploratory, fostering a sense of partnership between the user and the AI assistance.
4.  **Augment Human Intent:** Leverage AI (conceptually) as a brainstorming partner to augment, not replace, the user's core intent and creativity.
5.  **Educate on Prompt Possibilities:** Subtly educate users on the art of the possible in prompt engineering by showcasing diverse approaches and component ideas.

### B. Guiding Philosophy

*   **Assistive, Not Prescriptive:** These modules provide suggestions and inspiration; the user always retains final control and makes the decisions. They are tools to broaden thinking, not automated prompt generators.
*   **Context-Aware (Conceptually):** Where possible, suggestions should ideally be relevant to the user's current task, topic, or the state of their `PromptObject` draft.
*   **Focus on "Kindling Spontaneous Spark":** The design should aim to trigger new ideas and connections in the user's mind.
*   **User-Centric:** The modules should be easy to access, understand, and use, seamlessly integrating into the prompt editing workflow.

---
*Next sections will detail specific module ideas, UI integration, and conceptual controls like "Creativity Level."*

## II. Specific Creative Catalyst Module Ideas (V1 Concepts)

The following are initial concepts for modules designed to assist users in crafting more effective and creative `PromptObject` components.

### A. Role Persona Generator

*   **Module Name:** Role Persona Generator
*   **Purpose:** To help users define or discover interesting and effective AI personas/roles beyond generic defaults, aligning the AI's voice and style with the task.
*   **Conceptual User Input:**
    *   Optional: Keywords related to the desired topic, domain, or task (e.g., "history," "coding," "customer service").
    *   Optional: Keywords related to desired tone or style (e.g., "formal," "witty," "patient," "skeptical").
    *   Optional: Selection of a general category (e.g., "Expert," "Entertainer," "Assistant," "Character").
*   **Conceptual Output/Interaction:**
    *   A list of suggested role descriptions (strings).
    *   Examples:
        *   Input: topic="science", tone="enthusiastic" -> Output: "A passionate science communicator, eager to explain complex topics simply," "An eccentric inventor bubbling with ideas," "A meticulous research scientist."
        *   Input: category="Character", tone="historical" -> Output: "A Roman Centurion describing daily life," "A Victorian-era detective solving a case," "A Renaissance artist discussing their craft."
    *   Users can click a suggestion to populate the `PromptObject.role` field.
*   **Link to "Kindle Spontaneous Spark":** Overcomes the difficulty of inventing a suitable persona from scratch; exposes users to diverse role options they might not have considered.

### B. Constraint Brainstormer

*   **Module Name:** Constraint Brainstormer
*   **Purpose:** To assist users in generating relevant and useful constraints that can guide the AI towards more precise, high-quality, or specific outputs.
*   **Conceptual User Input:**
    *   The current content of `PromptObject.task`.
    *   Optional: The current content of `PromptObject.context`.
    *   Optional: User selects a "Task Category" (e.g., "Summarization," "Creative Writing," "Code Generation," "Explanation," "Translation"). This could help narrow down relevant constraint types.
*   **Conceptual Output/Interaction:**
    *   A list of suggested constraint phrases or categories of constraints.
    *   Examples:
        *   Input: task="Summarize this article", category="Summarization" -> Output: "Max length: [X] words/sentences," "Focus on key findings," "Exclude historical background," "Target audience: [e.g., non-experts, executives]," "Output format: bullet points."
        *   Input: task="Write a short story", category="Creative Writing" -> Output: "Genre: [e.g., sci-fi, fantasy, horror]," "Include a specific theme: [e.g., redemption, betrayal]," "Main character must be [X]," "Setting: [e.g., futuristic city, ancient forest]," "Avoid clichés related to [Y]."
    *   Users can select one or more suggestions to add to their `PromptObject.constraints` list.
*   **Link to "Kindle Spontaneous Spark":** Helps users think about different dimensions of control over the AI's output, moving beyond obvious constraints. Highlights types of constraints effective for different tasks.

### C. Example Idea Suggester

*   **Module Name:** Example Idea Suggester
*   **Purpose:** To help users formulate effective examples (input/output pairs or just output examples for V1) that can demonstrate the desired style, format, or content for the AI's response.
*   **Conceptual User Input:**
    *   The current content of `PromptObject.task`.
    *   Optional: The current content of `PromptObject.role`.
    *   Optional: The current content of `PromptObject.context`.
*   **Conceptual Output/Interaction:**
    *   Provides structural templates or conceptual ideas for examples.
    *   Examples:
        *   Input: task="Translate English to Spanish", role="Formal business translator" -> Output Suggestion: "Template: User: '[Common business phrase in English]' -> AI: '[Formal Spanish translation]'". Example fill: "User: 'Please find attached the report.' -> AI: 'Adjunto encontrará el informe.'"
        *   Input: task="Generate marketing slogans for a new coffee shop" -> Output Suggestion: "Focus on: [Key selling point, e.g., 'organic beans', 'cozy atmosphere', 'speedy service']. Example structure: '[Benefit-driven phrase] for [Target Audience]' or '[Catchy phrase] + [Shop Name]'."
    *   Users get ideas on *how* to structure examples, which they then fill in with specific content.
*   **Link to "Kindle Spontaneous Spark":** Many users struggle with what makes a "good" example. This module provides patterns and starting points, demystifying example creation.

### D. "What If?" Scenario Generator (for Context/Task)

*   **Module Name:** "What If?" Scenario Generator
*   **Purpose:** To encourage users to explore variations in their prompt's context or task parameters, potentially leading to more robust or creative prompts. Helps in considering edge cases or alternative framings.
*   **Conceptual User Input:**
    *   The current content of `PromptObject.context` or `PromptObject.task`.
*   **Conceptual Output/Interaction:**
    *   A list of "What if...?" questions or alternative scenario descriptions.
    *   Examples:
        *   Input: context="A customer is angry about a billing error." -> Output: "What if the customer is also a long-term VIP client?", "What if the billing error is very small vs. very large?", "What if the system for fixing errors is currently down?"
        *   Input: task="Explain photosynthesis to a child." -> Output: "What if the child is visually impaired (needs more auditory description)?", "What if you only have 30 seconds to explain it?", "What if you need to include a fun fact they'll remember?"
    *   These are not direct inputs to the prompt but serve as thought-starters for the user to refine their existing context or task, or to create new prompt variations.
*   **Link to "Kindle Spontaneous Spark":** Pushes users to think beyond their initial framing, consider different angles, and potentially create more versatile or targeted prompts.

---
*Next section: Conceptual UI Integration with PromptObject Editor.*

## III. Conceptual UI Integration with PromptObject Editor

To be effective, Creative Catalyst Modules should be easily accessible and seamlessly integrated into the user's workflow within the `PromptObject` Editor (as defined in `prometheus_protocol/ui_concepts/prompt_editor.md`).

### A. Access Points for Modules

Users could access Creative Catalyst Modules in a few ways:

1.  **Global "Creative Catalyst" Hub:**
    *   A dedicated button or icon (e.g., a lightbulb 💡, a magic wand ✨, or "Catalyst Hub") on the main Actions Panel or Toolbar of the `PromptObject` Editor.
    *   Clicking this button could open:
        *   A dropdown menu listing all available Creative Catalyst Modules (e.g., "Role Persona Generator," "Constraint Brainstormer").
        *   A dedicated sidebar or panel that slides out, providing access to all modules. This panel could have tabs or an accordion interface for different catalysts.

2.  **Contextual "Sparkle" Icons:**
    *   Small icons (e.g., a subtle sparkle ✨ or plus icon with a sparkle) placed directly next to or within specific `PromptObject` input fields where a catalyst might be particularly relevant.
    *   Examples:
        *   Next to the "Role" input field: Clicking it could directly open the "Role Persona Generator" suggestions.
        *   Next to the "Task" or "Context" text areas: Clicking could offer "What If? Scenario Generator" or context-relevant keyword expansion (a V2 module idea).
        *   Within the "Constraints" list editor (e.g., near the "Add Constraint" button): Clicking could open the "Constraint Brainstormer."
        *   Within the "Examples" list editor: Clicking could open the "Example Idea Suggester."
    *   This approach offers highly contextual assistance.

### B. Presentation of Suggestions

Once a module is activated and generates suggestions, they need to be presented clearly to the user:

1.  **Dropdown Lists:**
    *   For simple lists of suggestions (e.g., role names, constraint phrases), a dropdown appearing directly below or adjacent to the relevant input field can be effective.
    *   Each suggestion in the list should be easily clickable.

2.  **Dedicated Sidebar/Panel View:**
    *   If a global "Catalyst Hub" panel is used, suggestions from the selected module would populate this panel.
    *   This allows for richer display of suggestions, perhaps with more explanatory text for each.
    *   The panel could have a filter or search bar if a module generates many suggestions.

3.  **Modal Dialogs:**
    *   For modules that require more focused interaction or present complex options (though less ideal for quick brainstorming), a modal dialog could be used.
    *   Example: A "Constraint Brainstormer" might first ask for a "Task Category" in a modal before showing tailored suggestions.

### C. Applying Suggestions to the `PromptObject`

1.  **Direct Insertion:**
    *   Clicking a single text suggestion (e.g., a role name from "Role Persona Generator," a constraint phrase from "Constraint Brainstormer") should directly populate the corresponding `PromptObject` field.
    *   If the field already has content, the module could either replace it (with user confirmation, perhaps) or append to it (e.g., for list-based fields like `constraints`).

2.  **Adding to List Fields:**
    *   For suggestions meant for `constraints` or `examples`, clicking a suggestion should add it as a new item in the respective list editor.
    *   If a module provides multiple suggestions (e.g., "Constraint Brainstormer" offers 3 relevant constraints), the UI might allow the user to check/select multiple suggestions and then click an "Add Selected to [Constraints/Examples]" button.

3.  **Copy to Clipboard:**
    *   Each suggestion could also have a "copy" icon, allowing the user to copy the text and paste it manually if they prefer.

4.  **No Direct Application (for some modules):**
    *   Modules like the "'What If?' Scenario Generator" might not result in direct text insertion. Their output (probing questions, alternative scenarios) is meant to stimulate the user's own thinking, leading them to manually edit their prompt. The UI for these would simply display the generated questions/scenarios.

---
*Next section: Conceptual "Creativity Level" Control.*

## IV. "Creativity Level" / "Temperature" Control (Conceptual)

To give users more control over the nature of suggestions provided by certain Creative Catalyst Modules, a "Creativity Level" (akin to "temperature" in some generative AI models) could be introduced. This would allow users to guide whether they receive more conventional, standard suggestions or more novel, unconventional, "out-of-the-box" ideas.

### A. Modules Potentially Using This Control

This control would be most relevant for modules where the *variety* or *novelty* of output is a key aspect, such as:

*   **Role Persona Generator:** Low level might suggest common roles (e.g., "Expert," "Assistant"), while a high level might suggest more eccentric or highly specific personas ("A time-traveling botanist from the Victorian era with a penchant for puns").
*   **"What If?" Scenario Generator:** Low level might generate common variations, while a high level could produce more surreal or abstract scenarios.
*   **Example Idea Suggester (Potentially):** Could influence the creativity or unusualness of the example structures or content ideas.
*   Modules like "Constraint Brainstormer" might be less affected by a "creativity" control and more by task type or direct keyword input, though a "specificity vs. generality" control could be analogous for some constraint types.

### B. Conceptual UI for "Creativity Level" Control

1.  **Placement:**
    *   If a module is activated via a dedicated panel or modal, the control could be a prominent element within that module's UI.
    *   If suggestions appear in a simple dropdown, accessing this control might require an "Advanced Options" toggle or a settings icon associated with the catalyst.

2.  **Visual Representation:**
    *   **Slider:** A horizontal slider labeled "Creativity Level" or "Novelty," ranging from "Conventional" to "Adventurous" (or "Focused" to "Exploratory").
    *   **Segmented Control/Buttons:** Discrete options like [Standard] - [Balanced] - [Inventive].
    *   **Metaphorical Visual:** As mentioned in the original vision, a "thermostat" icon or a "spark" intensity visual could intuitively represent this. For example, a thermometer graphic that fills up, or a spark icon that grows larger/more animated.

### C. Impact on Suggestions

*   **Low Setting (e.g., "Conventional," "Focused," Low Temperature):**
    *   The module would prioritize suggestions that are more common, widely applicable, safer, or directly related to the core input.
    *   Useful for users seeking standard solutions or needing to refine a well-understood prompt.
*   **Medium Setting (e.g., "Balanced"):**
    *   A mix of standard and slightly more creative ideas.
*   **High Setting (e.g., "Adventurous," "Exploratory," High Temperature):**
    *   The module would generate more unusual, novel, or unexpected suggestions.
    *   Could lead to highly innovative prompts but might also produce less directly applicable ideas.
    *   Useful for brainstorming, breaking creative ruts, or when seeking a truly unique angle.

### D. User Experience Considerations

*   **Default Setting:** A balanced default (e.g., medium creativity) would likely be best. This default could itself be a global system default, then overridden by a user's preference stored in `UserSettings.creative_catalyst_defaults` (e.g., `creative_catalyst_defaults['RolePersonaGenerator_creativity'] = 'adventurous'`), and finally, the UI control would allow session-specific overrides.
*   **Clarity:** The UI should make it clear what the control does and how it might affect the suggestions. Tooltips or brief explanatory text could be helpful.
*   **Persistence (Optional):** The system could remember a user's preferred creativity level for certain modules across sessions.

This "Creativity Level" control would add another layer of user empowerment, allowing them to tailor the Creative Catalyst Modules' assistance to their specific needs and creative goals.

---
*End of Creative Catalyst Modules Concepts document.*
