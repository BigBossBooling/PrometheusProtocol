# Prometheus Protocol: Output Analytics Concepts

This document outlines the conceptual framework for "Output Analytics" within the Prometheus Protocol. The aim is to provide users and the system itself with insights into the effectiveness and impact of AI-generated outputs derived from prompts and conversations.

## I. Goals of Output Analytics

The primary goals for implementing Output Analytics are:

1.  **Empower User Refinement:** Provide users with data-driven feedback on how their prompts and conversations perform, enabling them to iteratively improve their prompt engineering skills and achieve better outcomes.
2.  **Demonstrate Value and ROI:** Help users understand and quantify the value derived from well-crafted prompts (e.g., higher quality outputs, time saved, better engagement if external data were linkable).
3.  **Identify Effective Patterns:** Allow users (and potentially the system in aggregate, with privacy considerations) to discover which types of prompts, constraints, or conversational structures lead to the "highest statistically positive variable of best likely outcomes" for specific tasks or domains.
4.  **Facilitate A/B Testing:** Provide a framework for users to compare the performance of different versions of a prompt or conversation when targeting a specific goal.
5.  **Drive Platform Improvement:** Offer insights (potentially anonymized and aggregated) that can guide the future development and refinement of Prometheus Protocol itself.

## II. Scope for V1 Concepts

For this initial conceptualization (V1 Concepts), we will focus on:

1.  **User-Provided Feedback within Prometheus Protocol:** Defining mechanisms for users to directly rate and comment on the quality and usefulness of AI outputs generated via the platform.
2.  **Data Linkage:** Establishing a clear conceptual link between the analytics data and the specific `PromptObject` (including its version) or `Conversation` that was used to generate the output.
3.  **Core Metrics Definition:** Identifying a foundational set of metrics that can be collected based on user feedback.
4.  **Conceptual Data Storage:** Proposing a basic data structure for storing individual analytics entries.
5.  **Basic UI Ideas for Feedback Collection & Display:** Sketching out where users might provide feedback and how they might see analytics for their specific prompts/conversations.

**Out of Scope for V1 Concepts (Future Considerations):**

*   **Direct Integration with External Platform Metrics:** Real-time fetching of engagement data (likes, shares, conversions) from external platforms (e.g., social media, CRMs) is a V2+ concept due to API complexities.
*   **Advanced Statistical Analysis or Predictive Analytics:** Sophisticated data mining or predictive modeling based on analytics data.
*   **Automated Prompt Optimization Suggestions:** While analytics might inform users, the system automatically suggesting prompt changes based on performance data is a more advanced feature.
*   **Detailed Global Analytics Dashboard:** While we will touch on UI for individual items, a comprehensive, aggregated dashboard for all users/system-wide trends is a V2+ concept.

---
*Next sections will detail Key Metrics, Data Linkage, UI Concepts, and Implementation Considerations.*

## III. Key Metrics to Track (V1 Focus)

The following metrics are proposed for initial conceptualization, focusing on data that can be collected directly from user interactions within Prometheus Protocol or in direct relation to its usage.

### A. User Feedback Metrics (Internal)

These metrics rely on the user providing explicit feedback on the AI-generated output.

1.  **`output_rating` (Quantitative):**
    *   **Description:** Overall user satisfaction with the generated output.
    *   **Scale:** Integer, e.g., 1 (Very Poor) to 5 (Excellent).
    *   **Collection Point:** After an output is generated, UI prompts for a rating.

2.  **`output_clarity_rating` (Quantitative):**
    *   **Description:** User's assessment of how clear and understandable the output was.
    *   **Scale:** Integer, e.g., 1 (Very Unclear) to 5 (Very Clear).
    *   **Collection Point:** Alongside `output_rating`.

3.  **`output_relevance_rating` (Quantitative):**
    *   **Description:** User's assessment of how relevant the output was to the input prompt/task.
    *   **Scale:** Integer, e.g., 1 (Not Relevant) to 5 (Highly Relevant).
    *   **Collection Point:** Alongside `output_rating`.

4.  **`custom_tags` (Qualitative):**
    *   **Description:** User-defined tags to categorize the output or feedback.
    *   **Format:** List of strings.
    *   **Examples:** "accurate", "creative", "needs_revision", "off-topic", "too_long", "good_starting_point".
    *   **Collection Point:** Text input allowing multiple tags, alongside other feedback.

5.  **`regeneration_count` (Quantitative):**
    *   **Description:** Number of times the user re-ran the same (or very similar) prompt to get a satisfactory output for a specific intent.
    *   **Format:** Integer.
    *   **Collection Point (Conceptual):** The system might infer this if a user modifies a prompt slightly and regenerates, or explicitly asks "Did this output meet your needs, or do you need to try again?". For V1, this might be a user-reported field: "How many attempts did this take?".

6.  **`used_in_final_work` (Boolean):** (Renamed from "used_in_production" for broader applicability)
    *   **Description:** User indicates if the generated output was directly useful or incorporated into their final work/product.
    *   **Format:** Boolean (True/False).
    *   **Collection Point:** A checkbox or simple Yes/No question alongside other feedback.

7.  **`user_qualitative_feedback` (Qualitative - to be detailed in `AnalyticsEntry`):**
    *   **Description:** Free-text comments from the user about the output's quality, issues, or specific aspects they liked/disliked.
    *   **Format:** String.
    *   **Collection Point:** A text area for comments.

### B. A/B Testing Support (Conceptual Linkage)

While full A/B testing execution is complex, the analytics system should be designed to support it conceptually.

1.  **`ab_test_id` (Identifier):**
    *   **Description:** An identifier to group multiple prompt versions that are being tested against each other.
    *   **Collection:** If a user initiates an A/B test (future UI feature), this ID is associated with the `AnalyticsEntry` for outputs from each version.
2.  **`prompt_variant_id` (Identifier):**
    *   **Description:** Identifies which specific variant (e.g., "A" or "B", or the `prompt_id:version`) an `AnalyticsEntry` belongs to within an `ab_test_id`.
    *   **Collection:** Associated with the `AnalyticsEntry`.
3.  **Goal Metric for A/B Test:**
    *   **Description:** When setting up an A/B test, the user would define what primary metric (e.g., `output_rating`, `used_in_final_work`) they are using to compare variants.
    *   **Collection:** Part of the A/B test setup (future UI feature).

### C. Prompt/Conversation Performance Metrics (Derived)

These are not directly collected but calculated from the raw `AnalyticsEntry` data. The UI might display these.

1.  **Average Ratings:** For a specific `PromptObject` (template) or `Conversation`, calculate average `output_rating`, `clarity_rating`, `relevance_rating` over time or across many uses.
2.  **Feedback Tag Frequency:** Most common `custom_tags` applied to outputs from a specific prompt/conversation.
3.  **Success Rate:** Percentage of times `used_in_final_work` was true for outputs from a specific prompt/conversation.
4.  **Average Regeneration Count:** For a specific prompt/conversation.

---
*Next section: Data Linkage and `AnalyticsEntry` Dataclass.*

## IV. Data Linkage and `AnalyticsEntry` Dataclass

To make analytics useful, each piece of feedback or metric needs to be clearly associated with the specific prompt or conversation that led to the AI-generated output.

### A. Core Linkage Identifiers

Each analytics entry must store identifiers to link back to its source:

*   **`source_prompt_id` (str):** The `prompt_id` of the `PromptObject` used. This is crucial for tracking the performance of individual prompt templates or specific prompt instances.
*   **`source_prompt_version` (int):** The `version` of the `PromptObject` used. This allows for tracking performance across different iterations of a prompt.
*   **`source_conversation_id` (Optional[str]):** If the prompt was part of a `Conversation`, this stores the `conversation_id`. This helps analyze the effectiveness of entire dialogue flows or specific turns within them.
*   **`source_turn_id` (Optional[str]):** If part of a conversation, this could store the specific `turn_id` within that conversation the feedback pertains to. (V1.1 consideration, might be too granular for V1, could be part of `metrics` dict if needed).

### B. Conceptual `AnalyticsEntry` Dataclass

The following dataclass structure is proposed for storing individual analytics records. This would typically reside in a new Python file (e.g., `prometheus_protocol/core/analytics_entry.py`) if implemented, but is presented here for conceptual clarity.

```python
# Conceptual Dataclass (for output_analytics.md)
# from dataclasses import dataclass
# from typing import Optional, Dict, List, Union, Any # Union might be needed for metrics
# from datetime import datetime # Or just use strings for ISO timestamps

# @dataclass
# class AnalyticsEntry:
#     """Represents a single analytics record for an AI-generated output."""
#     entry_id: str # Auto-generated UUID for this analytics entry
#     source_prompt_id: str # ID of the PromptObject
#     source_prompt_version: int # Version of the PromptObject
#
#     source_conversation_id: Optional[str] = None # ID of the Conversation, if applicable
#     # source_turn_id: Optional[str] = None # Specific turn ID, if applicable (V1.1+)
#
#     generated_at_timestamp: str # ISO 8601 UTC: When the AI output was generated
#     analytics_recorded_at_timestamp: str # ISO 8601 UTC: When this feedback/metric was logged
#
#     # Stores the actual metric values collected, based on III.A and III.B
#     metrics: Dict[str, Union[int, float, str, bool, List[str]]]
#     # Example:
#     # {
#     #     "output_rating": 5,
#     #     "output_clarity_rating": 4,
#     #     "custom_tags": ["helpful", "accurate"],
#     #     "used_in_final_work": True,
#     #     "regeneration_count": 0,
#     #     "ab_test_id": "test001", # if part of an A/B test
#     #     "prompt_variant_id": "prompt_abc:3" # if part of an A/B test
#     # }
#
#     output_preview_snippet: Optional[str] = None # e.g., first 200-500 chars of the AI output
#     user_qualitative_feedback: Optional[str] = None # Free-text user notes about the output
#
#     # user_id: Optional[str] = None # For multi-user systems, to segment analytics (V2+)

```

**Field Explanations for `AnalyticsEntry`:**

*   `entry_id`: Unique identifier for the analytics log itself.
*   `source_prompt_id`, `source_prompt_version`, `source_conversation_id`: Link back to the Prometheus Protocol objects.
*   `generated_at_timestamp`: Records when the AI output (that this feedback pertains to) was originally generated. This helps correlate feedback with specific generation events.
*   `analytics_recorded_at_timestamp`: Records when *this specific feedback* was logged by the user or system.
*   `metrics`: A flexible dictionary to store the various key-value metrics defined in Section III (e.g., ratings, boolean flags, A/B test info). Using `Union` in the type hint allows for different metric value types.
*   `output_preview_snippet`: Storing a small part of the actual AI output can be invaluable for qualitatively understanding the feedback within context, without needing to store entire (potentially very large) outputs.
*   `user_qualitative_feedback`: For any free-text notes the user provides about the output.
*   `user_id` (Commented out for V1): In a multi-user system, this would be essential for per-user analytics.

This structure aims to be comprehensive enough for V1 needs and extensible for future metric types.

---
*Next section: Conceptual UI for Displaying Analytics.*

## V. Conceptual UI for Displaying Analytics (V1 Focus)

The primary goal for V1 UI concepts is to make analytics accessible and actionable at the level of individual prompts or conversations. A global, aggregated dashboard is a V2+ consideration.

### A. Analytics Display for Individual Prompts/Conversations

1.  **Access Point:**
    *   When viewing a saved `PromptObject` template (e.g., in a Template Management view) or a saved `Conversation` (e.g., in a Conversation Management view), there should be an "Analytics" tab or a dedicated section.
    *   This section becomes populated once analytics data exists for that specific prompt/conversation ID and version(s).

2.  **Content of the Analytics View (for a specific Prompt/Conversation):**

    *   **Summary Statistics (Header Area):**
        *   Displays key derived metrics (see Section III.C) for the selected item.
        *   Example for a `PromptObject` template:
            *   "Total Times Used: 25"
            *   "Average Output Rating: 4.2 / 5.0 (based on 18 ratings)"
            *   "Average Clarity: 4.5 / 5.0"
            *   "Average Relevance: 4.3 / 5.0"
            *   "Marked 'Used in Final Work': 70% of rated instances"
            *   "Common Feedback Tags: 'creative' (10), 'accurate' (8), 'too_short' (3)"
        *   If multiple versions of a `PromptObject` template exist, there could be a dropdown to filter analytics by version or view "All Versions."

    *   **Individual Feedback Log / `AnalyticsEntry` List:**
        *   A chronological or sortable list of individual `AnalyticsEntry` records associated with this prompt/conversation.
        *   **Each Log Item Display:**
            *   `analytics_recorded_at_timestamp` (e.g., "Feedback on Nov 3, 2023")
            *   `output_preview_snippet` (clickable to see more if stored, or just the snippet).
            *   Key metrics from the `metrics` dict (e.g., "Rating: 5/5, Clarity: 4/5, Used: Yes").
            *   `custom_tags` applied to this specific output.
            *   `user_qualitative_feedback` (if any).
            *   (If applicable) Link to `source_prompt_version` if viewing "All Versions" for a template.
            *   (If applicable) Link to `source_turn_id` if viewing analytics for a whole `Conversation`.

    *   **Visualizations (Simple V1):**
        *   Basic charts could enhance understanding.
        *   Example: A bar chart showing the distribution of `output_rating` (how many 1-star, 2-star, ..., 5-star ratings).
        *   Example: A pie chart for `custom_tags` frequency.

### B. UI for A/B Testing Analytics (Conceptual)

*   If an `ab_test_id` is associated with `AnalyticsEntry` records:
    *   A separate view or a filtered view within the prompt's analytics could compare performance.
    *   Side-by-side display of key metrics (especially the user-defined `goal_metric_for_ab_test`) for `prompt_variant_id` "A" vs. "B".
    *   Example: "Variant A: Avg Rating 4.5 | Variant B: Avg Rating 3.8".

### C. Feedback Collection UI (Brief Mention - Links to other UI areas)

*   While not the focus of *displaying* analytics, it's important to consider *where* users provide this feedback.
*   **Post-Generation Feedback Form:** After an AI output is generated (in either the PromptObject Editor testing area or a Conversation execution view):
    *   A small, non-intrusive form or set of controls appears near the output.
    *   Allows users to quickly provide ratings (1-5 stars for different categories).
    *   Input for `custom_tags`.
    *   Checkbox for `used_in_final_work`.
    *   Text area for `user_qualitative_feedback`.
    *   A "Submit Feedback" button.
*   This feedback would then create an `AnalyticsEntry` linked to the relevant prompt/conversation.

This UI aims to make the collected data transparent and useful for users to understand how their prompts are performing and how they might improve them.

---
*Next section: Implementation Considerations (Hypothetical).*

## VI. Implementation Considerations (Hypothetical)

While this document focuses on the *concept* of Output Analytics, a brief consideration of implementation aspects is useful for completeness. A real implementation would require careful design of backend systems.

1.  **Data Storage:**
    *   A dedicated database would be necessary to store `AnalyticsEntry` records. This could be:
        *   A relational database (e.g., PostgreSQL, MySQL) for structured data and querying capabilities.
        *   A NoSQL database (e.g., MongoDB, Elasticsearch) if the `metrics` dictionary is highly variable or if text search on `output_preview_snippet` or `user_qualitative_feedback` is a priority. Elasticsearch could also power aggregations for dashboards.
    *   The volume of data could grow significantly, so scalability of the database solution would be a concern.

2.  **Feedback Collection Mechanism:**
    *   **API Endpoint:** A backend API endpoint would be needed to receive `AnalyticsEntry` data payloads from the client-side UI (where users submit their feedback).
    *   **Client-Side Logic:** The UI where AI output is displayed would need JavaScript logic to capture user feedback from the form elements and send it to this API endpoint.

3.  **Data Aggregation and Querying:**
    *   To display summary statistics and derived metrics (as described in Section V.A and potentially for a V2+ global dashboard), backend processes or efficient database queries would be needed to aggregate data (e.g., calculate average ratings, count tag frequencies).
    *   This might involve periodic batch processing or real-time aggregation capabilities depending on the chosen database and desired freshness of analytics.

4.  **Asynchronous Processing:**
    *   Submitting analytics data should ideally not block the user's main workflow. Sending data to the backend API should be asynchronous.

5.  **Privacy and Data Security:**
    *   **User-Specific Data:** If `user_id` is implemented, ensure that users can only see analytics related to their own prompts/outputs, unless data is explicitly shared or aggregated anonymously.
    *   **Anonymization for Global Trends:** If system-wide analytics are ever considered (V2+), data must be anonymized and aggregated to protect individual user privacy and the content of their prompts/outputs.
    *   **Sensitive Information in Snippets:** `output_preview_snippet` and `user_qualitative_feedback` could inadvertently contain sensitive information. Policies and potentially filtering mechanisms might be needed if this data is reviewed or used more broadly. For V1, it's primarily for the user's own review.

6.  **Versioning and Evolution:**
    *   The structure of `AnalyticsEntry` and the types of metrics collected may evolve. The backend and database schema should be designed with some flexibility in mind (e.g., using JSONB fields for `metrics` in PostgreSQL).

These considerations highlight that a full-fledged analytics system is a significant undertaking. The V1 concepts in this document aim to lay the groundwork for what data to collect and why, which is the first step towards such a system.

---
*End of Output Analytics Concepts document.*
