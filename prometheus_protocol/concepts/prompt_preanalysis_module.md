# Prometheus Protocol: Prompt Pre-analysis Module (Conceptual)

This document outlines conceptual ideas for a "Prompt Pre-analysis Module" within Prometheus Protocol. This module aims to provide users with proactive, automated feedback and estimations about their `PromptObject`s *before* execution with an AI model like "Jules," complementing the GIGO Guardrail and Risk Identifier.

## 1. Goals, Scope, and Types of Pre-analysis

### 1.1. Goals

The primary goals for the Prompt Pre-analysis Module are:

1.  **Proactive Guidance:** Offer users additional insights into their prompt's characteristics beyond structural correctness (GIGO) or potential safety/ethical risks (Risk Identifier).
2.  **Estimate Response Characteristics:** Provide very rough, heuristic-based estimations for aspects like potential token count of the prompt itself (relevant for AI model input limits).
3.  **Highlight Stylistic/Structural Considerations:** Check for elements that might affect AI comprehension, output clarity, or efficiency, but are not strictly errors.
4.  **Encourage Best Practices:** Subtly guide users towards prompt engineering techniques that are generally found to be effective.
5.  **Improve Prompt Refinement Efficiency:** Help users identify areas for potential improvement in their prompts before incurring the time or cost of actual AI execution.

### 1.2. Scope (V1 Concepts for this Document)

This initial conceptualization will focus on:

*   Defining a few distinct types of pre-analysis checks that can be performed primarily on the `PromptObject` data itself, without requiring external AI calls for the analysis.
*   Describing the conceptual logic or heuristics for these checks.
*   Proposing a data structure for the findings of these analyses.
*   Conceptualizing how these insights would be presented to the user within the `PromptObject` Editor UI.

**Out of Scope for this V1 Conceptualization:**

*   Complex Natural Language Processing (NLP) based analyses that would require their own sophisticated models (e.g., deep semantic analysis of task-example alignment, automated summarization of context to check for verbosity).
*   Direct prediction of AI output quality or specific content (this is the role of Jules, with feedback via Output Analytics).
*   Pre-analysis of multi-turn `Conversation` flows (V1 focuses on individual `PromptObject`s).

### 1.3. Types of Pre-analysis to Consider for V1 Detailing

For this V1 concept, we will focus on detailing the following types of pre-analysis checks:

1.  **Prompt Readability Score:**
    *   **Focus:** Assess the readability of user-generated text in fields like `PromptObject.task` and `PromptObject.context`.
    *   **Insight:** Helps users understand if their language is overly complex or simple for the intended AI interaction or for their own review.
2.  **Constraint Specificity/Actionability Check:**
    *   **Focus:** Analyze `PromptObject.constraints` for vague or non-actionable phrases.
    *   **Insight:** Guides users to write clearer, more effective constraints.
3.  **Estimated Input Token Count:**
    *   **Focus:** Provide a rough, heuristic-based estimate of the token count for the entire `PromptObject` content that would be sent to the AI.
    *   **Insight:** Helps users be mindful of potential input token limits of AI models.
4.  **(Optional V1.1) Example-Task Stylistic Consistency (High-Level):**
    *   **Focus:** A very basic check if the style of `PromptObject.examples` (e.g., prose, question/answer, code) seems to grossly mismatch the nature of the `PromptObject.task`.
    *   **Insight:** A gentle nudge if examples seem unrelated to the task's intent.

These checks aim to provide actionable, non-blocking suggestions to the user.

---

## 2. Specific Pre-analysis Checks (V1 Concepts)

This section details the conceptual logic and user feedback for the initial set of pre-analysis checks. These checks are designed to be heuristic-based and operate on the content of the `PromptObject`.

### 2.1. Prompt Readability Score

*   **Analysis Name:** `ReadabilityScoreCheck` (or similar internal name)
*   **Purpose:** To assess the readability of user-generated text in the `PromptObject.task` and `PromptObject.context` fields. This helps users understand if their language might be too complex or too simplistic for clear communication with the AI or for their own future reference.
*   **Conceptual Logic/Heuristics:**
    *   The system would apply one or more standard readability formulas (e.g., Flesch-Kincaid Reading Ease, Gunning Fog Index) to the text content of `prompt.task` and `prompt.context` separately.
    *   The raw scores from these formulas would be mapped to descriptive levels (e.g., "Very Easy to Read / Elementary School," "Easy to Read / Middle School," "Standard / High School," "Fairly Difficult / College," "Very Difficult / Graduate Level").
    *   The check might also consider sentence length and average word length as contributing factors.
*   **Output/Feedback to User (Example Messages):**
    *   "**Task Readability:** Fairly Difficult (College Level). Consider simplifying language if the AI struggles with nuance or if the prompt is for broader team use."
    *   "**Context Readability:** Easy to Read (Middle School Level). This is generally good for clear AI instructions."
    *   "**Suggestion (Task):** Average sentence length is high (25 words). Shorter sentences can improve clarity for some AI models."
    *   **Severity:** Typically "Info" or "Suggestion."

### 2.2. Constraint Specificity/Actionability Check

*   **Analysis Name:** `ConstraintActionabilityCheck`
*   **Purpose:** To analyze `PromptObject.constraints` for items that may be too vague, subjective, or non-actionable for an AI, guiding users to write clearer and more effective constraints.
*   **Conceptual Logic/Heuristics:**
    *   The system would scan each string in the `prompt.constraints` list.
    *   It would check against a predefined list of "vague phrases" or patterns (e.g., "make it good," "be interesting," "do your best," "ensure high quality," "be creative" without further qualification).
    *   It might also look for constraints that lack quantifiable measures where they might be expected (e.g., "make it short" vs. "limit to 100 words").
    *   It could also positively identify "actionable patterns" (e.g., "limit to X words," "use format Y," "include keywords A, B, C," "avoid topic Z").
*   **Output/Feedback to User (Example Messages):**
    *   "**Constraint Suggestion (Item 2: 'Make it much better'):** This constraint is vague. Consider specifying *how* the AI should make it better (e.g., 'Improve clarity,' 'Add more technical detail,' 'Use a more persuasive tone')."
    *   "**Constraint Info (Item 4: 'Keep it brief'):** This is somewhat vague. For more precise control, consider specifying a target length (e.g., 'Limit to approximately 50 words')."
    *   "**Constraint Strength:** X out of Y constraints appear highly actionable and specific." (A summary score).
    *   **Severity:** Typically "Suggestion" or "Info."

### 2.3. Estimated Input Token Count

*   **Analysis Name:** `InputTokenEstimator`
*   **Purpose:** To provide a rough, heuristic-based estimate of the number of tokens the entire `PromptObject` (key text fields) might consume when sent as input to an AI model. This helps users be mindful of potential input token limits of different models.
*   **Conceptual Logic/Heuristics:**
    1.  Concatenate the textual content from key fields of the `PromptObject`: `role`, `task`, `context`, and all items in `constraints` and `examples`.
    2.  Apply a character-based or word-based heuristic to estimate tokens. Examples:
        *   **Character-based:** Total characters / X (e.g., X might be 3 or 4, as a rough average for English).
        *   **Word-based:** Total words * Y (e.g., Y might be 1.3 to 1.5, as some words are multiple tokens).
    3.  The specific multipliers (X or Y) would be very approximate and might need to be tuned based on the typical tokenization behavior of the target AI (Jules).
    4.  The system should clearly state this is a rough estimate.
*   **Output/Feedback to User (Example Messages):**
    *   "**Estimated Input Tokens (Prompt Only):** ~180-220 tokens. (This is a rough estimate of your prompt's size for the AI. Actual token count by the AI model may vary.)"
    *   "**Info:** Your current prompt is estimated at ~X tokens. Some AI models have input limits around Y tokens. If your prompt is very long, consider summarizing some parts."
    *   **Severity:** "Info."

These V1 pre-analysis checks aim to provide non-blocking, helpful insights to the user before they commit to an AI execution call.

---

## 3. `PreanalysisFinding` Data Structure (Conceptual)

To provide a consistent and structured way for the Prompt Pre-analysis Module to report its findings, a dedicated data structure is needed. This structure would encapsulate the details of each individual insight or suggestion generated by the various pre-analysis checks.

We propose a conceptual Python dataclass named `PreanalysisFinding`:

```python
# Conceptual Dataclass for PreanalysisFinding
# To be defined in a Python file if/when implemented, e.g., prometheus_protocol/core/preanalysis_types.py
#
# from dataclasses import dataclass, field
# from typing import Optional, Dict, Any, Literal # Literal for severity

# @dataclass
# class PreanalysisFinding:
#     """
#     Represents a single finding or suggestion from a pre-analysis check.
#     """
#     check_name: str
#     # Unique identifier for the specific check that generated this finding.
#     # e.g., "ReadabilityScore_Task", "ConstraintActionability_Item_2", "TokenEstimator_Input"

#     severity: Literal["Info", "Suggestion", "Warning"]
#     # The severity level of the finding. Differs from GIGO (errors) and Risk (potential harms).
#     # - Info: General information or observation (e.g., token count).
#     # - Suggestion: A recommendation for improvement that isn't critical (e.g., rephrasing a vague constraint).
#     # - Warning: Highlights an issue that might significantly impact clarity or AI performance,
#     #            though not a blocking error (e.g., extremely poor readability).

#     message: str
#     # The user-facing message describing the finding and offering advice.
#     # e.g., "Task Readability: College Level. Consider simplifying."
#     # e.g., "Constraint 'Make it engaging' is vague. Consider specifying how."

#     details: Optional[Dict[str, Any]] = None
#     # Optional dictionary for any additional structured data related to the finding.
#     # e.g., {"score": 75.0, "level_description": "8th Grade"} for readability.
#     # e.g., {"offending_constraint_text": "make it better", "suggested_alternatives": ["improve clarity", "add detail"]}
#     # e.g., {"estimated_tokens": 180, "estimation_method": "char_based_div_4"}

#     ui_target_field: Optional[str] = None
#     # An optional string indicating which part of the PromptObject UI this finding most directly relates to.
#     # This can help the UI to highlight the relevant field or link the finding to it.
#     # e.g., "task", "context", "constraints[2]" (referring to the 3rd constraint), "examples[0]".

#     def __str__(self) -> str:
#         return f"[{self.severity}] {self.check_name}: {self.message}"

```

**Field Explanations:**

*   **`check_name` (str):** A unique string identifying the specific analysis check that produced this finding (e.g., "ReadabilityScore_Task", "ConstraintActionability_Item_2", "InputTokenEstimator"). This helps in categorizing or filtering findings.
*   **`severity` (Literal["Info", "Suggestion", "Warning"]):**
    *   **Info:** Provides general information or observations (e.g., token count, basic readability score). Typically non-critical.
    *   **Suggestion:** Offers recommendations for improvement that are not critical but could enhance the prompt (e.g., rephrasing a vague constraint, minor readability improvements).
    *   **Warning:** Highlights an issue that might significantly impact clarity, AI comprehension, or efficiency, though it's not a blocking GIGO error (e.g., extremely poor readability, many vague constraints).
    This severity scale is distinct from GIGO `PromptValidationError` (which are errors) and `RiskLevel` (which pertains to safety/ethical/effectiveness risks).
*   **`message` (str):** The primary user-facing message that explains the finding and offers actionable advice.
*   **`details` (Optional[Dict[str, Any]]):** A flexible dictionary to store any additional structured data relevant to the finding, such as specific scores, problematic text snippets, or even suggested alternative phrasings.
*   **`ui_target_field` (Optional[str]):** An optional identifier that the UI can use to link the finding back to a specific input field or element in the `PromptObject` editor (e.g., "task", "context", "constraints[2]"). This can enable features like highlighting the relevant field when a finding is selected.

A conceptual Prompt Pre-analysis Module or function would then return a `List[PreanalysisFinding]` for a given `PromptObject`.

---

## 4. Conceptual UI Integration with `PromptObject` Editor

The insights generated by the Prompt Pre-analysis Module should be presented to the user in a clear, non-intrusive, and actionable manner within the `PromptObject` Editor UI (as defined in `prometheus_protocol/ui_concepts/prompt_editor.md`).

### 4.1. Triggering Pre-analysis

Pre-analysis could be triggered in a few ways:

1.  **On-Demand Button:**
    *   An explicitly labeled button in the `PromptObject` Editor's Actions Panel, e.g., **"[Analyze Prompt Quality]"** or **"[Get Pre-analysis Insights]"**.
    *   This gives the user direct control over when to run these checks.
2.  **Automatic (Debounced, Optional):**
    *   Potentially, analyses could run automatically in the background as the user types or after they pause editing a field (with a debounce mechanism to avoid excessive processing).
    *   This provides more real-time feedback but needs to be performant and not overly distracting. For V1 concepts, on-demand might be simpler to start with.
3.  **Before Execution (Optional):**
    *   As part of the pre-flight checks when the user clicks "[Execute with Jules]", after GIGO validation and Risk Identification, pre-analysis findings could be presented as a final set of suggestions.

**V1 Recommendation:** Start with an **on-demand "[Analyze Prompt Quality]" button** for clarity and user control.

### 4.2. Displaying `PreanalysisFinding` Results

Once a `List[PreanalysisFinding]` is generated, the results need to be displayed:

1.  **Dedicated "Prompt Analysis Insights" Panel/Section:**
    *   Similar to how GIGO errors and Risks are potentially displayed, a new collapsible panel or tab within the `PromptObject` Editor (e.g., labeled "Analysis Insights" or "Quality Suggestions").
    *   If no findings, it shows a message like "No specific pre-analysis insights at this time."
    *   If findings exist, they are listed, each formatted according to its `PreanalysisFinding` attributes.

2.  **Formatting Each Finding:**
    *   **Icon/Color by `severity`:**
        *   `Info`: e.g., Blue information icon (💡 or ℹ️).
        *   `Suggestion`: e.g., Lightbulb icon (💡) or a distinct color like purple/green.
        *   `Warning` (for pre-analysis): e.g., Yellow triangle (⚠️) - distinct from GIGO's red errors or Risk's potential red criticals.
    *   **`check_name` or User-Friendly Title:** Display a readable title for the check (e.g., "Readability Analysis for Task," "Constraint Actionability").
    *   **`message`:** The main user-facing advice.
    *   **`details`:** If present, could be revealed via a small "show details" toggle or on hover.
    *   **Link to Field:** If `ui_target_field` is populated (e.g., "constraints[2]"), clicking the finding in the list should ideally:
        *   Scroll the editor to the relevant field.
        *   Briefly highlight the field.
        *   Focus the cursor there if it's an input field.

3.  **Non-Blocking Nature:**
    *   It should be emphasized in the UI that these pre-analysis findings are generally informational or suggestions, not blocking errors like GIGO issues. Users can choose to act on them or ignore them.

### 4.3. Example Display of a Finding

```
[Analysis Insights Panel]

💡 **Constraint Suggestion** (Constraint: 'Make it much better')
   This constraint is vague. Consider specifying *how* the AI should make it better
   (e.g., 'Improve clarity,' 'Add more technical detail,' 'Use a more persuasive tone').
   [Show Details...]
   ---
ℹ️ **Estimated Input Tokens (Prompt Only)**
   ~180-220 tokens. (This is a rough estimate... Actual token count may vary.)
   ---
⚠️ **Task Readability Warning**
   Fairly Difficult (College Level). Consider simplifying language if the AI struggles
   with nuance or if the prompt is for broader team use.
   (Offending Field: Task) [Jump to Task]
```

This UI integration aims to make the pre-analysis insights easily digestible and actionable for the user, helping them refine their prompts proactively.

---

## 5. Relationship to GIGO Guardrail and Risk Identifier

The Prompt Pre-analysis Module is designed to complement, not replace, the existing `GIGO Guardrail` and `RiskIdentifier` components. Each system serves a distinct but related purpose in guiding the user towards creating high-quality, effective, and responsible prompts.

*   **`GIGO Guardrail (`validate_prompt`)`:**
    *   **Focus:** Ensures fundamental structural correctness, completeness, and syntactic validity of a `PromptObject`.
    *   **Nature of Feedback:** Identifies objective errors that *must* be fixed for the prompt to be considered well-formed and processable by the system or reliably by an AI.
    *   **Severity:** Errors (blocking, typically prevents saving a template as "final" or executing a prompt until resolved).
    *   **Examples:** Empty required fields, incorrect data types for list items, unresolved placeholders that would break processing.
    *   **Interaction with Pre-analysis:** GIGO checks would generally run *before* or *alongside* more nuanced pre-analysis. A prompt failing GIGO checks might not even be suitable for some pre-analysis checks.

*   **`RiskIdentifier`:**
    *   **Focus:** Identifies potential semantic, ethical, safety, or effectiveness risks in the prompt's content or intended use that could lead to problematic, biased, harmful, or simply very poor AI outputs.
    *   **Nature of Feedback:** Advisory warnings or informational alerts about potential negative outcomes or areas requiring careful consideration.
    *   **Severity:** Information, Warnings, potentially Critical (though these usually advise strong caution rather than being hard blocks like GIGO errors).
    *   **Examples:** Prompts dealing with sensitive topics without disclaimers, overly broad tasks prone to hallucination, potential for generating biased content based on phrasing.
    *   **Interaction with Pre-analysis:** Risk identification is also a form of pre-analysis but focuses on a different class of issues. `PotentialRisk` findings would be displayed alongside or in conjunction with `PreanalysisFinding`s, but visually and semantically distinct due to their different implications.

*   **Prompt Pre-analysis Module (This Concept):**
    *   **Focus:** Provides heuristic-based insights, estimations, and stylistic suggestions to improve a prompt's potential clarity, efficiency, or to help the user be more mindful of certain prompt characteristics (like estimated token count or readability).
    *   **Nature of Feedback:** Primarily informational and suggestive, aimed at polish and optimization rather than critical error correction or risk mitigation.
    *   **Severity:** Info, Suggestions, occasionally soft Warnings (e.g., for very poor readability that might hinder AI understanding). These are generally non-blocking.
    *   **Examples:** Readability scores, constraint actionability suggestions, input token estimations, stylistic consistency checks (V1.1).
    *   **Interaction with GIGO/Risk:** Runs on GIGO-valid prompts. Its findings offer a layer of refinement *on top of* basic correctness and risk awareness. For example, a prompt might be GIGO-valid and have no identified Risks, but pre-analysis could still suggest its `context` field is "Hard to Read."

**Synergistic Goal:**

Together, these three layers of guidance (GIGO, Risk ID, Pre-analysis) create a comprehensive feedback system:
1.  **GIGO:** Is the prompt correctly formed? (Must-fix errors)
2.  **Risk ID:** Is the prompt potentially problematic in its intent or likely output? (Advisory warnings)
3.  **Pre-analysis:** Can the prompt be further polished or optimized for clarity, efficiency, or estimated impact? (Informational insights and suggestions)

This multi-layered approach helps users progressively refine their prompts, addressing different facets of prompt quality and responsibility. The UI should clearly distinguish feedback from these three sources to help the user prioritize and understand the nature of the guidance.

---

## 6. Conclusion (Prompt Pre-analysis Module Concepts)

The conceptual Prompt Pre-analysis Module outlined in this document aims to provide an additional layer of proactive guidance to Prometheus Protocol users, complementing the existing GIGO Guardrail and Risk Identifier. By offering heuristic-based insights into prompt readability, constraint actionability, and estimated input token counts, this module can help users further polish their `PromptObject`s for clarity, efficiency, and awareness of potential AI model limitations *before* execution.

The defined `PreanalysisFinding` data structure provides a standardized way to communicate these non-blocking, advisory findings, and the UI integration concepts focus on presenting this information actionably within the `PromptObject` Editor.

While the V1 concepts focus on a few core heuristic checks, this module has the potential for future expansion with more sophisticated analyses as Prometheus Protocol evolves. Its primary goal is to empower users to become more effective and mindful prompt engineers through accessible, pre-emptive feedback.

---
*End of Prompt Pre-analysis Module (Conceptual) document.*
