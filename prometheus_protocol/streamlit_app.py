import streamlit as st
import uuid
import json
from datetime import datetime, timezone # Ensure timezone is imported
import os
import sys
from typing import List, Dict, Any, Optional # Ensure all needed typing hints are imported

# --- Assume prometheus_protocol package is correctly installed or discoverable ---
# Add prometheus_protocol directory to path to allow import if running directly from the root
# where streamlit_app.py is located, and core etc. are in a subdirectory.
# This assumes streamlit_app.py is in the root of the project, and 'prometheus_protocol' is a package dir.
# If 'core' is directly under the root, the path setup might need adjustment.
# For the planned structure, 'prometheus_protocol' is the package.

# Get the directory of the current script (streamlit_app.py, which should be in the root)
# This path setup assumes that the `prometheus_protocol` directory (containing `core`, etc.)
# is a subdirectory in the same root directory as `streamlit_app.py`.
# If `streamlit_app.py` is *inside* a `prometheus_protocol` directory that also contains `core`,
# then direct relative imports like `from .core.prompt import PromptObject` would work,
# but the user specified placing it in the root.

# Let's assume the structure is:
# /project_root/
#   streamlit_app.py
#   /prometheus_protocol/  <- This is the package
#     __init__.py
#     /core/
#       prompt.py
#       ...
# To make this work, `project_root` needs to be in PYTHONPATH, or we adjust sys.path here.
# The user's original path setup was:
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir) # This would go one level ABOVE project_root if streamlit_app.py is in root.
# Let's adjust for streamlit_app.py in root, and package 'prometheus_protocol' also in root.

# If streamlit_app.py is in /project_root/ and the package is /project_root/prometheus_protocol/
# then the 'prometheus_protocol' package should be directly importable if /project_root/ is effectively the cwd
# or in PYTHONPATH.
# For robustness in typical execution (streamlit run streamlit_app.py from root):
# We need to ensure the 'prometheus_protocol' package can be found.
# Adding the current directory (which is project_root when running from there) to sys.path
# should make `import prometheus_protocol.core...` work.

sys.path.insert(0, os.getcwd()) # Add current working directory to path

# Import all core components
try:
    from prometheus_protocol.core.prompt import PromptObject
    from prometheus_protocol.core.conversation import Conversation, PromptTurn
    from prometheus_protocol.core.ai_response import AIResponse
    # Assuming validate_prompt is the main validation function from guardrails
    from prometheus_protocol.core.guardrails import validate_prompt
    from prometheus_protocol.core.risk_types import PotentialRisk, RiskLevel, RiskType # RiskType also needed
    from prometheus_protocol.core.risk_identifier import RiskIdentifier # Import the class
    from prometheus_protocol.core.template_manager import TemplateManager
    from prometheus_protocol.core.conversation_manager import ConversationManager
    from prometheus_protocol.core.jules_executor import JulesExecutor
    from prometheus_protocol.core.conversation_orchestrator import ConversationOrchestrator
    from prometheus_protocol.core.exceptions import (
        PromptValidationError, # Base for GIGO
        # Specific GIGO errors (if needed for more granular display, though validate_prompt raises PromptValidationError subclasses)
        UnresolvedPlaceholderError,
        RepetitiveListItemError,
        # Manager errors
        TemplateCorruptedError, # For TemplateManager
        ConversationCorruptedError # For ConversationManager
    )
    from prometheus_protocol.core.user_settings import UserSettings
    from prometheus_protocol.core.user_settings_manager import UserSettingsManager

    # Initialize managers and core components
    # These should be initialized once. Streamlit's execution model reruns the script,
    # so using @st.cache_resource or similar is best practice for expensive objects
    # or objects that need to maintain state across reruns IF that state isn't in st.session_state.
    # For file-based managers, re-initializing on each run is usually fine if paths are consistent.

    DEFAULT_USER_ID = "default_streamlit_user" # App-wide default user ID

    @st.cache_resource # Cache resource for managers & executors
    def get_core_components():
        base_data_path = "prometheus_protocol_data_streamlit" # Store data in a subfolder
        tm = TemplateManager(templates_dir=os.path.join(base_data_path, "templates"))
        cm = ConversationManager(conversations_dir=os.path.join(base_data_path, "conversations"))
        usm = UserSettingsManager(settings_base_dir=os.path.join(base_data_path, "user_settings"))

        # Load or create default user settings
        user_settings = usm.load_settings(DEFAULT_USER_ID)
        if user_settings is None:
            print(f"No settings found for {DEFAULT_USER_ID}, creating defaults.")
            user_settings = UserSettings(
                user_id=DEFAULT_USER_ID,
                default_jules_api_key="YOUR_HYPOTHETICAL_API_KEY", # Default placeholder
                default_jules_model="jules-xl-default-model",
                default_execution_settings={"temperature": 0.77, "max_tokens": 550},
                ui_theme="light",
                preferred_output_language="en-US",
                creative_catalyst_defaults={"RolePersonaGenerator_creativity": "balanced"}
            )
            try:
                usm.save_settings(user_settings)
                print(f"Default settings saved for {DEFAULT_USER_ID}")
            except Exception as e_usm_save:
                print(f"Error saving initial default user settings: {e_usm_save}")
                # Continue with in-memory default user_settings even if save fails

        je = JulesExecutor() # Our robust simulated executor
        # Initialize CO with the loaded/default user_settings. This instance might be replaced later if settings change.
        co = ConversationOrchestrator(jules_executor=je, user_settings=user_settings)
        ri = RiskIdentifier()
        return tm, cm, je, co, ri, usm, user_settings

    components_tuple = get_core_components()
    template_manager = components_tuple[0]
    conversation_manager = components_tuple[1]
    jules_executor_instance = components_tuple[2] # The cached one from get_core_components
    # CO will be re-initialized with session_state.user_settings later
    # conversation_orchestrator_instance initially from get_core_components
    risk_identifier = components_tuple[4]
    user_settings_manager = components_tuple[5]

    # Ensure st.session_state.user_settings exists and is current
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = components_tuple[6] # Initial load from get_core_components

    # Re-initialize ConversationOrchestrator with the potentially updated user_settings from session state
    # This is important if user settings are changed and need to be reflected immediately in new conversation runs.
    conversation_orchestrator_instance = ConversationOrchestrator(
        jules_executor=jules_executor_instance,
        user_settings=st.session_state.user_settings
    )

except ImportError as e:
    st.error(f"Critical Error: Failed to import Prometheus Protocol core modules: {e}")
    st.error("This application cannot run without these modules.")
    st.info(
        "Ensure the `prometheus_protocol` directory (containing `core`, `concepts`, etc.) "
        "is in the same directory as `streamlit_app.py`, or that the project root is in your PYTHONPATH. "
        "If running from the project root (where `streamlit_app.py` and the `prometheus_protocol` folder reside), "
        "this should generally work. "
        "You might need to install the package in editable mode: `pip install -e .` from the project root."
    )
    st.stop() # Stop execution if core components can't be loaded


# --- Helper Functions for UI ---
# Ensure PromptValidationError and its subclasses are imported if needed for type checking,
# though validate_prompt now returns List[PromptValidationError]
# from prometheus_protocol.core.exceptions import PromptValidationError

def display_gigo_feedback(prompt_object: PromptObject):
    """
    Validates the given PromptObject using core.guardrails.validate_prompt
    and displays all GIGO (Garbage In, Garbage Out) feedback in Streamlit.
    """
    if not isinstance(prompt_object, PromptObject):
        st.error("Invalid object passed to GIGO feedback display.")
        return

    validation_errors = validate_prompt(prompt_object) # This now returns a list

    if not validation_errors:
        st.success("GIGO Guardrail: All clear! ✅")
    else:
        st.error(f"GIGO Guardrail Alerts ({len(validation_errors)} found):")
        for error_instance in validation_errors:
            # The str(error_instance) should ideally contain the field information
            # due to the message formatting updates we made in validate_prompt.
            # Example: "Role: Must be a non-empty string."
            # Example: "Constraints (Item 1): Contains unresolved placeholder..."
            st.write(f"- 💔 **{error_instance.__class__.__name__}:** {str(error_instance)}")
            # If custom error objects consistently had an 'offending_field' attribute,
            # we could use it here for more structured display, e.g.:
            # field = getattr(error_instance, 'offending_field', 'N/A')
            # item_index = getattr(error_instance, 'item_index', None) # If we add item_index to exceptions
            # message = getattr(error_instance, 'message', str(error_instance))
            # st.write(f"- 💔 **{error_instance.__class__.__name__}** (Field: {field}" +
            #          (f", Item: {item_index+1}" if item_index is not None else "") +
            #          f"): {message}")
            # For now, relying on the error's __str__ representation which we updated to be informative.


def display_risk_feedback(prompt_object: PromptObject):
    # Takes PromptObject to call risk_identifier internally
    risks = risk_identifier.identify_risks(prompt_object) # Call the identifier
    if risks:
        st.warning("Potential Risks Identified by Prometheus Protocol:")
        for risk in risks:
            icon = "ℹ️" if risk.risk_level == RiskLevel.INFO else "⚠️" if risk.risk_level == RiskLevel.WARNING else "🚨"
            field_info = f"(Field: `{risk.offending_field}`)" if risk.offending_field else ""
            st.write(f"- {icon} **{risk.risk_type.value}:** {risk.message} {field_info}")
    else:
        st.info("Risk Identifier: No major risks detected. 👌")

def display_ai_response(ai_response: AIResponse, turn_index: Optional[int] = None):
    turn_label = f" (Turn {turn_index + 1})" if turn_index is not None else ""
    st.markdown(f"**--- AI Response{turn_label} ---**")
    if ai_response.was_successful and ai_response.content is not None:
        st.success("Generation Successful! ✨")
        # For now, display as markdown. Add toggle for raw/code later if needed.
        st.markdown(ai_response.content)
    elif ai_response.error_message:
        st.error(f"Generation FAILED! 💔 Error: {ai_response.error_message}")
    else:
        st.error("Generation FAILED! 💔 An unknown error occurred.")


    # Metadata Expander (simplified from user's code to avoid exclude_none error if not in to_dict)
    # Create a dict with only non-None values for cleaner display
    response_dict_for_display = {k: v for k, v in ai_response.to_dict().items() if v is not None}
    # Remove raw_jules_response from immediate display if too verbose, but keep in full dict
    display_subset = response_dict_for_display.copy()
    raw_response_to_expand = display_subset.pop("raw_jules_response", None)


    with st.expander(f"Response Metadata{turn_label}"):
        st.json(display_subset)
        if raw_response_to_expand:
            with st.expander(f"Raw Jules Response{turn_label} (Technical Detail)"):
                st.json(raw_response_to_expand)
    st.markdown("---")


# --- Page Layout ---
st.set_page_config(layout="wide", page_title="Prometheus Protocol - The Architect's Code")

# --- Session State Initialization (Crucial for Streamlit) ---
# General state
if 'menu_choice' not in st.session_state:
    st.session_state.menu_choice = "Dashboard"

# For Prompt Editor
if 'current_prompt_object' not in st.session_state: # Renamed from current_prompt for clarity
    st.session_state.current_prompt_object = None
if 'last_ai_response_single' not in st.session_state: # For single prompt executions
    st.session_state.last_ai_response_single = None
if 'save_template_name_input' not in st.session_state: # To hold text_input state for save
    st.session_state.save_template_name_input = ""


# For Conversation Composer
if 'current_conversation_object' not in st.session_state: # Renamed
    st.session_state.current_conversation_object = None
# 'editing_turn_index' was in user's code, but not used in this version yet.
# if 'editing_turn_index' not in st.session_state:
#     st.session_state.editing_turn_index = None
if 'conversation_run_results' not in st.session_state:
    st.session_state.conversation_run_results = None # Dict of {turn_id: AIResponse}
if 'save_conversation_name_input' not in st.session_state: # To hold text_input state for save
    st.session_state.save_conversation_name_input = ""


# --- Main Application ---
st.sidebar.title("Prometheus Protocol")
st.sidebar.markdown("### The Architect's Code for AI Mastery")

# Use st.session_state.menu_choice for persistence across reruns
navigation_options = ("Dashboard", "Prompt Editor", "Conversation Composer", "Template Library", "Conversation Library", "User Settings")
st.session_state.menu_choice = st.sidebar.radio(
    "Navigate Your Digital Ecosystem:",
    navigation_options,
    key='main_menu_selector',
    index=navigation_options.index(st.session_state.menu_choice if st.session_state.menu_choice in navigation_options else "Dashboard")
)
menu_choice = st.session_state.menu_choice


# --- Main Content Area ---
st.title(f"🚀 {menu_choice}")

if menu_choice == "Dashboard":
    st.header("Welcome to Your LaunchPad!")
    st.markdown("This is your command center for engineering precision into your AI interactions.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Start New:")
        if st.button("✨ New Single Prompt"): # Changed label for clarity
            # Create a new PromptObject with some defaults
            st.session_state.current_prompt_object = PromptObject(
                role="AI Assistant",
                task="Your task here...",
                context="Relevant context here..."
            )
            st.session_state.current_conversation_object = None # Clear conversation context
            st.session_state.conversation_run_results = None
            st.session_state.last_ai_response_single = None
            st.session_state.menu_choice = "Prompt Editor" # Switch view
            st.experimental_rerun()

        if st.button("💡 New Conversation"):
            st.session_state.current_conversation_object = Conversation(
                title="New Conversation",
                description="A multi-turn AI dialogue."
            )
            st.session_state.current_prompt_object = None # Clear single prompt context
            st.session_state.conversation_run_results = None
            st.session_state.last_ai_response_single = None
            st.session_state.menu_choice = "Conversation Composer" # Switch view
            st.experimental_rerun()

    with col2:
        st.subheader("Load Existing:")
        st.markdown("#### Recent Templates (Prompts):")
        try:
            templates_dict = template_manager.list_templates()
            if templates_dict:
                for i, (name, versions) in enumerate(list(templates_dict.items())[:3]): # Show top 3
                    latest_version = versions[-1]
                    if st.button(f"📄 Load Template: '{name}' (v{latest_version})", key=f"dash_load_template_{name}_{i}"):
                        st.session_state.current_prompt_object = template_manager.load_template(name, latest_version)
                        st.session_state.current_conversation_object = None
                        st.session_state.conversation_run_results = None
                        st.session_state.last_ai_response_single = None
                        st.session_state.menu_choice = "Prompt Editor"
                        st.experimental_rerun()
            else:
                st.info("No Prompt Templates saved yet.")
        except Exception as e:
            st.error(f"Could not load templates: {e}")


        st.markdown("#### Recent Conversations:")
        try:
            conversations_dict = conversation_manager.list_conversations()
            if conversations_dict:
                for i, (name, versions) in enumerate(list(conversations_dict.items())[:3]): # Show top 3
                    latest_version = versions[-1]
                    if st.button(f"💬 Load Conversation: '{name}' (v{latest_version})", key=f"dash_load_conv_{name}_{i}"):
                        st.session_state.current_conversation_object = conversation_manager.load_conversation(name, latest_version)
                        st.session_state.current_prompt_object = None
                        st.session_state.conversation_run_results = None
                        st.session_state.last_ai_response_single = None
                        st.session_state.menu_choice = "Conversation Composer"
                        st.experimental_rerun()
            else:
                st.info("No Conversations saved yet.")
        except Exception as e:
            st.error(f"Could not load conversations: {e}")


elif menu_choice == "Prompt Editor":
    st.header("Craft Your Intent: The Prompt Editor")

    if st.session_state.get('current_prompt_object') is None:
        st.info("No prompt loaded or created. Start by creating a 'New Single Prompt' from the Dashboard or loading from the Template Library.")
        if st.button("Go to Dashboard to Start"):
            st.session_state.menu_choice = "Dashboard"
            st.experimental_rerun()
        st.stop()

    prompt = st.session_state.current_prompt_object

    # --- Edit Fields ---
    prompt.role = st.text_input("Role", value=prompt.role, key="pe_role")
    prompt.context = st.text_area("Context", value=prompt.context, height=100, key="pe_context")
    prompt.task = st.text_area("Task", value=prompt.task, height=150, key="pe_task")

    # Constraints
    st.markdown("**Constraints (one per line):**")
    constraints_text = "\n".join(prompt.constraints)
    new_constraints_text = st.text_area("Constraints Text", value=constraints_text, height=100, label_visibility="collapsed", key="pe_constraints_text")
    if new_constraints_text != constraints_text:
        prompt.constraints = [c.strip() for c in new_constraints_text.split('\n') if c.strip()]

    # Examples
    st.markdown("**Examples (one per line):**")
    examples_text = "\n".join(prompt.examples)
    new_examples_text = st.text_area("Examples Text", value=examples_text, height=100, label_visibility="collapsed", key="pe_examples_text")
    if new_examples_text != examples_text:
        prompt.examples = [e.strip() for e in new_examples_text.split('\n') if e.strip()]

    # Tags
    st.markdown("**Tags (one per line):**")
    tags_text = "\n".join(prompt.tags)
    new_tags_text = st.text_area("Tags Text", value=tags_text, height=50, label_visibility="collapsed", key="pe_tags_text")
    if new_tags_text != tags_text:
        prompt.tags = [t.strip() for t in new_tags_text.split('\n') if t.strip()]

    # Settings (JSON editor)
    st.markdown("**Execution Settings (JSON format):**")
    current_settings_str = json.dumps(prompt.settings, indent=2) if prompt.settings is not None else "{}"
    new_settings_str = st.text_area("Settings JSON", value=current_settings_str, height=100, key="pe_settings_json")
    if new_settings_str != current_settings_str:
        try:
            prompt.settings = json.loads(new_settings_str)
        except json.JSONDecodeError:
            st.error("Invalid JSON in settings. Changes not applied.")
            # Keep old settings or set to {} or None? Let's keep old.
            # prompt.settings = None # Or {}

    # --- Actions ---
    st.markdown("---")
    col_action1, col_action2, col_action3 = st.columns(3)
    with col_action1:
        if st.button("💾 Save as Template", key="pe_save_template"):
            # Use a text input for template name that persists via session_state if button is pressed
            st.session_state.save_template_name_input = st.text_input(
                "Enter Template Name:",
                value=st.session_state.current_prompt_object.title if hasattr(st.session_state.current_prompt_object, 'title') and st.session_state.current_prompt_object.title else "My Prompt Template",
                key="pe_template_name_input_field"
            )
            if st.session_state.save_template_name_input: # Check if name is provided
                try:
                    # Pass a copy to avoid manager modifying the session state object directly before user confirms UI update
                    prompt_to_save = PromptObject(**st.session_state.current_prompt_object.to_dict())
                    saved_prompt = template_manager.save_template(prompt_to_save, st.session_state.save_template_name_input)
                    # Update session state with the potentially version-bumped prompt
                    st.session_state.current_prompt_object = saved_prompt
                    st.success(f"Template '{st.session_state.save_template_name_input}' saved as version {saved_prompt.version}!")
                    st.session_state.save_template_name_input = "" # Clear for next time
                    st.experimental_rerun() # Rerun to reflect changes and clear input
                except ValueError as e:
                    st.error(f"Error saving template: {e}")
                except IOError as e:
                    st.error(f"IOError saving template: {e}")
            else:
                st.warning("Template name cannot be empty to save.")


    with col_action2:
        if st.button("📂 Load from Library", key="pe_load_template"):
            st.session_state.menu_choice = "Template Library"
            st.experimental_rerun()

    with col_action3:
        if st.button("⚡ Run with Jules", key="pe_run_jules"):
            # Pre-execution GIGO check
            validation_errors_run = validate_prompt(prompt) # Get list of errors

            if validation_errors_run: # If list is not empty, there are errors
                st.error("Cannot run: Please fix GIGO Guardrail errors first!")
                # Call display_gigo_feedback which now handles list display correctly
                # No need to call display_gigo_feedback(prompt) here again if it's already displayed below.
                # The main display_gigo_feedback below the actions will show these.
                # However, for immediate feedback upon button click, this is okay.
                # Let's ensure the main display is sufficient.
                # The main display_gigo_feedback IS called below, so this specific call might be redundant
                # if the user can see the main feedback area.
                # For now, let's keep it to ensure error is prominent on "Run" action.
                # Re-displaying is fine.
                # To make it cleaner, we might just set a flag and let the main display handle it.
                # For this iteration, let's assume the immediate feedback here is desired.
                # No, let's remove this specific call display_gigo_feedback(prompt) here,
                # as the one in "Guidance & Diagnostics" section will show the errors.
                # The st.error message is sufficient here.
                pass # Errors will be shown by the general display_gigo_feedback below.
            else: # Proceed only if GIGO checks pass (list is empty)
                # Risk Check (conceptual - user proceeds after warning)
                risks = risk_identifier.identify_risks(prompt)
                proceed_after_risk_check = True # Assume proceed unless checkbox logic is added and unchecked
                if risks:
                    display_risk_feedback(prompt) # Display risks
                    # Example of how to make it conditional, though checkbox might be better in a modal
                    # if not st.checkbox("Acknowledge risks and proceed with run?", value=True, key="pe_proceed_risk"):
                    #     proceed_after_risk_check = False
                    # For now, let's assume risks are advisory and user implicitly proceeds

                if proceed_after_risk_check:
                    with st.spinner("Engaging Jules..."):
                        st.session_state.last_ai_response_single = jules_executor_instance.execute_prompt(
                            prompt,
                            user_settings=st.session_state.user_settings
                        )
                    st.experimental_rerun() # Rerun to display response below

    # --- Feedback Display Area ---
    st.markdown("---")
    st.subheader("Guidance & Diagnostics:")
    display_gigo_feedback(prompt) # Display GIGO feedback based on current state
    display_risk_feedback(prompt) # Display Risk feedback based on current state

    # --- Response Display Area ---
    if st.session_state.get('last_ai_response_single'):
        st.subheader("Jules's Response:")
        display_ai_response(st.session_state.last_ai_response_single)
        # Conceptual: Add Analytics Feedback UI here
        st.markdown("*(Conceptual: Analytics Feedback UI for this response would go here)*")


elif menu_choice == "Conversation Composer":
    st.header("Orchestrate Dialogues: The Conversation Composer")

    if st.session_state.get('current_conversation_object') is None:
        st.info("No conversation loaded or created. Start by creating a 'New Conversation' from the Dashboard or loading from the Conversation Library.")
        if st.button("Go to Dashboard to Start"):
            st.session_state.menu_choice = "Dashboard"
            st.experimental_rerun()
        st.stop()

    convo = st.session_state.current_conversation_object

    # --- Conversation Metadata ---
    st.subheader("Conversation Details:")
    convo.title = st.text_input("Title", value=convo.title, key="cc_title")
    convo.description = st.text_area("Description", value=convo.description if convo.description else "", height=75, key="cc_description")

    conv_tags_text = "\n".join(convo.tags)
    new_conv_tags_text = st.text_area("Conversation Tags (one per line)", value=conv_tags_text, height=50, key="cc_tags_text")
    if new_conv_tags_text != conv_tags_text:
        convo.tags = [t.strip() for t in new_conv_tags_text.split('\n') if t.strip()]

    st.caption(f"ID: {convo.conversation_id} | Version: {convo.version} | Created: {convo.created_at} | Modified: {convo.last_modified_at}")
    st.markdown("---")

    # --- Turns Editor ---
    st.subheader("Dialogue Turns:")
    if not convo.turns:
        st.markdown("_No turns yet. Click 'Add Turn' to begin building your conversation._")

    for i, turn_obj in enumerate(convo.turns):
        turn_key_prefix = f"cc_turn_{i}_{turn_obj.turn_id[:8]}" # Unique key prefix for widgets in this turn

        with st.container(): # Use container for better layout of each turn
            st.markdown(f"**Turn {i+1}** (ID: `{turn_obj.turn_id[:8]}`)")
            cols_turn_edit_delete = st.columns([0.9, 0.1])
            with cols_turn_edit_delete[0]:
                with st.expander(f"Edit Turn {i+1}: '{turn_obj.prompt_object.task[:40].strip()}...'", expanded=False): # Start collapsed
                    st.markdown(f"**Editing Prompt for Turn {i+1}:**")
                    turn_obj.prompt_object.role = st.text_input("Role", value=turn_obj.prompt_object.role, key=f"{turn_key_prefix}_role")
                    turn_obj.prompt_object.context = st.text_area("Context", value=turn_obj.prompt_object.context, height=70, key=f"{turn_key_prefix}_context")
                    turn_obj.prompt_object.task = st.text_area("Task", value=turn_obj.prompt_object.task, height=100, key=f"{turn_key_prefix}_task")

                    # Constraints for this turn's prompt
                    turn_constraints_text = "\n".join(turn_obj.prompt_object.constraints)
                    new_turn_constraints_text = st.text_area("Constraints", value=turn_constraints_text, height=70, label_visibility="collapsed", key=f"{turn_key_prefix}_constraints")
                    if new_turn_constraints_text != turn_constraints_text:
                        turn_obj.prompt_object.constraints = [c.strip() for c in new_turn_constraints_text.split('\n') if c.strip()]

                    # Examples for this turn's prompt
                    turn_examples_text = "\n".join(turn_obj.prompt_object.examples)
                    new_turn_examples_text = st.text_area("Examples", value=turn_examples_text, height=70, label_visibility="collapsed", key=f"{turn_key_prefix}_examples")
                    if new_turn_examples_text != turn_examples_text:
                        turn_obj.prompt_object.examples = [e.strip() for e in new_turn_examples_text.split('\n') if e.strip()]

                    # Tags for this turn's prompt
                    turn_tags_text = "\n".join(turn_obj.prompt_object.tags)
                    new_turn_tags_text = st.text_area("Prompt Tags", value=turn_tags_text, height=50, label_visibility="collapsed", key=f"{turn_key_prefix}_ptags")
                    if new_turn_tags_text != turn_tags_text:
                        turn_obj.prompt_object.tags = [t.strip() for t in new_turn_tags_text.split('\n') if t.strip()]

                    # Settings for this turn's prompt
                    st.markdown("**Prompt Settings (JSON):**")
                    turn_settings_str = json.dumps(turn_obj.prompt_object.settings, indent=2) if turn_obj.prompt_object.settings is not None else "{}"
                    new_turn_settings_str = st.text_area("Settings JSON", value=turn_settings_str, height=70, key=f"{turn_key_prefix}_psettings")
                    if new_turn_settings_str != turn_settings_str:
                        try:
                            turn_obj.prompt_object.settings = json.loads(new_turn_settings_str)
                        except json.JSONDecodeError:
                            st.error(f"Invalid JSON in settings for Turn {i+1}. Changes not applied.")

                    # Turn Notes
                    turn_obj.notes = st.text_area("Turn Notes", value=turn_obj.notes if turn_obj.notes else "", height=70, key=f"{turn_key_prefix}_notes")

                    # GIGO and Risk for this turn's prompt
                    st.markdown("**Turn Prompt Guidance:**")
                    display_gigo_feedback(turn_obj.prompt_object)
                    display_risk_feedback(turn_obj.prompt_object)

            with cols_turn_edit_delete[1]: # Delete button column
                if st.button(f"🗑️", key=f"{turn_key_prefix}_delete", help=f"Delete Turn {i+1}"):
                    # Confirmation could be added here
                    st.session_state.current_conversation_object.turns.pop(i)
                    st.experimental_rerun()
            st.markdown("---") # Separator for each turn


    if st.button("➕ Add Turn to Conversation", key="cc_add_turn"):
        new_prompt = PromptObject(role="User", task="New task for this turn...", context="Context for new turn...")
        new_turn = PromptTurn(prompt_object=new_prompt)
        if convo.turns: # Set parent_turn_id if not the first turn
            new_turn.parent_turn_id = convo.turns[-1].turn_id
        st.session_state.current_conversation_object.turns.append(new_turn)
        st.experimental_rerun()

    # --- Conversation Actions ---
    st.markdown("---")
    st.subheader("Manage & Execute Conversation:")
    col_conv_act1, col_conv_act2, col_conv_act3 = st.columns(3)
    with col_conv_act1:
        if st.button("💾 Save Conversation", key="cc_save_conversation"):
            st.session_state.save_conversation_name_input = st.text_input(
                "Enter Conversation Name:",
                value=st.session_state.current_conversation_object.title,
                key="cc_conversation_name_input_field"
            )
            if st.session_state.save_conversation_name_input:
                try:
                    # Pass a copy for saving
                    convo_to_save = Conversation(**st.session_state.current_conversation_object.to_dict())
                    saved_convo = conversation_manager.save_conversation(convo_to_save, st.session_state.save_conversation_name_input)
                    st.session_state.current_conversation_object = saved_convo # Update with new version/LMT
                    st.success(f"Conversation '{st.session_state.save_conversation_name_input}' saved as version {saved_convo.version}!")
                    st.session_state.save_conversation_name_input = ""
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(f"Error saving conversation: {e}")
                except IOError as e:
                    st.error(f"IOError saving conversation: {e}")
            else:
                st.warning("Conversation name cannot be empty to save.")


    with col_conv_act2:
        if st.button("📂 Load from Library", key="cc_load_conversation"):
            st.session_state.menu_choice = "Conversation Library"
            st.experimental_rerun()

    with col_conv_act3:
        if st.button("🚀 Run Full Conversation", key="cc_run_conversation"):
            # Pre-execution GIGO check for all turns
            all_turns_valid = True
            first_error_turn_idx = -1
            first_error_detail = ""

            for turn_idx, turn_obj_check in enumerate(convo.turns):
                turn_validation_errors = validate_prompt(turn_obj_check.prompt_object)
                if turn_validation_errors:
                    all_turns_valid = False
                    first_error_turn_idx = turn_idx
                    # Take the first error from that turn's list for the summary message
                    first_error_detail = f"{turn_validation_errors[0].__class__.__name__}: {str(turn_validation_errors[0])}"
                    break

            if not all_turns_valid:
                st.error(f"Cannot run: GIGO Error in Turn {first_error_turn_idx+1} ('{convo.turns[first_error_turn_idx].prompt_object.task[:30]}...'): {first_error_detail}")
                # Errors for specific turn will be displayed within the turn's expander.
            else: # Proceed if all turns are valid
                # Conceptual Risk Check for all turns (simplified: proceed if any risks)
                all_risks_flat = []
                for turn_obj_check in convo.turns:
                    all_risks_flat.extend(risk_identifier.identify_risks(turn_obj_check.prompt_object))

                proceed_with_risks = True # Default to true if no explicit checkbox for now
                if all_risks_flat:
                    st.warning("Potential risks identified in one or more turns. Review them in each turn's editor section or the main prompt editor if this is a single prompt.")
                    # This simple checkbox is just an example. A modal might be better.
                    # if not st.checkbox("Acknowledge risks and proceed with run?", value=True, key="cc_proceed_risk_run_global"):
                    #     proceed_with_risks = False

                if proceed_with_risks:
                    with st.spinner("Orchestrating dialogue with Jules... This may take a moment."):
                        # Pass a copy to the orchestrator to avoid modifications to session state object during run
                        convo_to_run = Conversation(**st.session_state.current_conversation_object.to_dict())
                        # Use the orchestrator instance that has the latest user_settings
                        st.session_state.conversation_run_results = conversation_orchestrator_instance.run_full_conversation(convo_to_run)
                    st.experimental_rerun() # Rerun to show results

    # --- Conversation Log / Run Results ---
    if st.session_state.get('conversation_run_results'):
        st.markdown("---")
        st.subheader("Conversation Run Log & Results:")

        run_results = st.session_state.conversation_run_results
        current_log_history_display = []

        for turn_idx, turn_in_convo in enumerate(convo.turns): # Iterate through original turns to ensure order
            turn_id = turn_in_convo.turn_id
            ai_resp_for_turn = run_results.get(turn_id)

            # User's part of the turn
            current_log_history_display.append({
                "speaker": "user",
                "turn_label": f"Turn {turn_idx + 1}",
                "task": turn_in_convo.prompt_object.task,
                "role": turn_in_convo.prompt_object.role # For context
            })

            if ai_resp_for_turn:
                # AI's part of the turn
                if ai_resp_for_turn.was_successful and ai_resp_for_turn.content is not None:
                    current_log_history_display.append({
                        "speaker": "ai",
                        "turn_label": f"Turn {turn_idx + 1}",
                        "text": ai_resp_for_turn.content
                    })
                else:
                    error_display_text = f"Error: {ai_resp_for_turn.error_message if ai_resp_for_turn.error_message else 'Unknown error.'}"
                    current_log_history_display.append({
                        "speaker": "ai_error",
                        "turn_label": f"Turn {turn_idx + 1}",
                        "text": error_display_text
                    })
                    # If conversation halts, no more turns are processed by orchestrator
                    if turn_id in run_results and not ai_resp_for_turn.was_successful:
                         st.error(f"Conversation halted at Turn {turn_idx+1} due to an error.")
                         break
            else:
                # This turn was not executed (e.g., due to prior error)
                current_log_history_display.append({
                    "speaker": "system_info",
                    "turn_label": f"Turn {turn_idx+1}",
                    "text": "This turn was not executed."
                })
                break # Stop displaying further turns if one wasn't found in results (implies halt)

        # Display the constructed log
        for msg in current_log_history_display:
            if msg["speaker"] == "user":
                st.markdown(f"**You ({msg['turn_label']}, Role: {msg['role']}):**\n\n{msg['task']}")
            elif msg["speaker"] == "ai":
                st.markdown(f"**Jules ({msg['turn_label']}):**\n\n{msg['text']}")
            elif msg["speaker"] == "ai_error":
                st.error(f"**Jules ({msg['turn_label']} - ERROR):**\n\n{msg['text']}")
            elif msg["speaker"] == "system_info":
                st.info(f"**System ({msg['turn_label']}):** {msg['text']}")
            st.markdown("---")


        with st.expander("View Full Turn AIResponse Objects (Technical Detail)"):
            # Prepare for JSON display, converting AIResponse objects
            serializable_results = {}
            for t_id, response_obj in run_results.items():
                if isinstance(response_obj, AIResponse):
                    serializable_results[t_id] = response_obj.to_dict()
                else: # Should not happen
                    serializable_results[t_id] = str(response_obj)
            st.json(serializable_results)

        st.markdown("*(Conceptual: Analytics Feedback UI for each turn's response would go here or be linked from here)*")


elif menu_choice == "Template Library":
    st.header("Your Vault of Prompts: Template Library")
    st.markdown("Explore, load, and manage your saved PromptObject templates.")
    try:
        templates = template_manager.list_templates() # Returns Dict[str, List[int]]
        search_term_template = st.text_input("Search templates by name:", key="search_template_lib")

        if not templates:
            st.info("No Prompt Templates saved yet. Head to the 'Prompt Editor' to create one!")
        else:
            for base_name, versions in sorted(templates.items()):
                if search_term_template.lower() not in base_name.lower():
                    continue

                st.markdown(f"#### Template: **{base_name}**")
                latest_version = versions[-1]

                # --- Display and Load Buttons ---
                col_display1, col_display2 = st.columns([0.7, 0.3])
                with col_display1:
                    version_tags = [f"v{v}" for v in reversed(versions)]
                    st.write(f"Available Versions: {', '.join(version_tags)}")

                with col_display2: # Load Latest Button
                    if st.button(f"📂 Load Latest (v{latest_version})", key=f"tpl_load_latest_{base_name}"):
                        try:
                            st.session_state.current_prompt_object = template_manager.load_template(base_name, latest_version)
                            st.session_state.menu_choice = "Prompt Editor"
                            st.session_state.current_conversation_object = None
                            st.session_state.conversation_run_results = None
                            st.session_state.last_ai_response_single = None
                            st.experimental_rerun()
                        except FileNotFoundError:
                            st.error(f"Template '{base_name}' v{latest_version} not found. It might have been deleted.")
                        except TemplateCorruptedError as e:
                            st.error(f"Could not load template '{base_name}' v{latest_version}: {e}")

                # --- Load Specific Version ---
                if len(versions) > 1:
                    cols_specific_load = st.columns([0.7, 0.3])
                    with cols_specific_load[0]:
                        sorted_versions_for_select = sorted(versions, reverse=True)
                        version_to_load_specific = st.selectbox(
                            "Load specific version:",
                            options=sorted_versions_for_select,
                            format_func=lambda x: f"v{x}",
                            key=f"tpl_select_version_{base_name}"
                        )
                    with cols_specific_load[1]:
                        if st.button(f"📂 Load v{version_to_load_specific}", key=f"tpl_load_specific_{base_name}_{version_to_load_specific}"):
                            try:
                                st.session_state.current_prompt_object = template_manager.load_template(base_name, version_to_load_specific)
                                st.session_state.menu_choice = "Prompt Editor"
                                st.session_state.current_conversation_object = None
                                st.session_state.conversation_run_results = None
                                st.session_state.last_ai_response_single = None
                                st.experimental_rerun()
                            except FileNotFoundError:
                                 st.error(f"Template '{base_name}' v{version_to_load_specific} not found.")
                            except TemplateCorruptedError as e:
                                 st.error(f"Could not load template '{base_name}' v{version_to_load_specific}: {e}")

                st.markdown("---")

                # --- Delete Actions for this base_name ---
                st.write("**Delete Options:**")
                # Calculate number of columns needed: one for each version + one for "Delete All"
                # Max columns for Streamlit is typically around 10-12 for readability. If more versions, might need different UI.
                num_delete_cols = min(len(versions) + 1, 10)
                cols_delete_actions = st.columns(num_delete_cols)

                # "Delete All Versions" button
                with cols_delete_actions[0]:
                    delete_all_key = f"confirm_delete_all_tpl_{base_name}"
                    if st.button(f"🗑️ All ({len(versions)})", key=f"btn_del_all_tpl_{base_name}", help=f"Delete all versions of '{base_name}'"):
                        st.session_state[delete_all_key] = True

                    if st.session_state.get(delete_all_key):
                        st.warning(f"**Confirm:** Delete all {len(versions)} versions of '{base_name}'?")
                        col_confirm_all1, col_confirm_all2 = st.columns(2)
                        with col_confirm_all1:
                            if st.button("YES, DELETE ALL", key=f"yes_del_all_tpl_{base_name}", type="primary"):
                                deleted_count = template_manager.delete_template_all_versions(base_name)
                                st.success(f"Deleted {deleted_count} version(s) of '{base_name}'.")
                                del st.session_state[delete_all_key]
                                st.experimental_rerun()
                        with col_confirm_all2:
                            if st.button("NO, CANCEL", key=f"no_del_all_tpl_{base_name}"):
                                del st.session_state[delete_all_key]
                                st.experimental_rerun()

                # "Delete Specific Version" buttons
                # Display buttons for up to (num_delete_cols - 1) individual versions
                versions_to_display_delete = list(reversed(versions))[:num_delete_cols-1]

                for idx, version_num in enumerate(versions_to_display_delete):
                    with cols_delete_actions[idx + 1]:
                        delete_specific_key = f"confirm_delete_tpl_{base_name}_v{version_num}"
                        if st.button(f"🗑️ v{version_num}", key=f"btn_del_tpl_{base_name}_v{version_num}", help=f"Delete version {version_num} of '{base_name}'"):
                            st.session_state[delete_specific_key] = True

                        if st.session_state.get(delete_specific_key):
                            st.warning(f"**Confirm:** Delete '{base_name}' v{version_num}?")
                            col_confirm_spec1, col_confirm_spec2 = st.columns(2)
                            with col_confirm_spec1:
                                if st.button(f"YES, DELETE v{version_num}", key=f"yes_del_tpl_{base_name}_v{version_num}", type="primary"):
                                    deleted = template_manager.delete_template_version(base_name, version_num)
                                    if deleted:
                                        st.success(f"Template '{base_name}' version {version_num} deleted.")
                                    else:
                                        st.error(f"Failed to delete '{base_name}' version {version_num} (it may have already been deleted).")
                                    del st.session_state[delete_specific_key]
                                    st.experimental_rerun()
                            with col_confirm_spec2:
                                if st.button(f"NO, CANCEL v{version_num}", key=f"no_del_tpl_{base_name}_v{version_num}"):
                                    del st.session_state[delete_specific_key]
                                    st.experimental_rerun()

                st.markdown("---") # End of section for this base_name

    except Exception as e:
        st.error(f"Error loading template library: {e}")


elif menu_choice == "Conversation Library":
    st.header("Your Dialogue Vault: Conversation Library")
    st.markdown("Manage and load your saved multi-turn conversations.")
    try:
        conversations = conversation_manager.list_conversations()
        search_term_conv = st.text_input("Search conversations by name:", key="search_conv_lib")

        if not conversations:
            st.info("No Conversations saved yet. Head to the 'Conversation Composer' to engineer a new dialogue!")
        else:
            for base_name, versions in sorted(conversations.items()):
                if search_term_conv.lower() not in base_name.lower():
                    continue

                st.markdown(f"#### Conversation: **{base_name}**")
                latest_version = versions[-1]

                # --- Display and Load Buttons ---
                col_display1_c, col_display2_c = st.columns([0.7, 0.3])
                with col_display1_c:
                    version_tags_c = [f"v{v}" for v in reversed(versions)]
                    st.write(f"Available Versions: {', '.join(version_tags_c)}")

                with col_display2_c: # Load Latest Button
                    if st.button(f"📂 Load Latest (v{latest_version})", key=f"cnv_load_latest_{base_name}"):
                        try:
                            st.session_state.current_conversation_object = conversation_manager.load_conversation(base_name, latest_version)
                            st.session_state.menu_choice = "Conversation Composer"
                            st.session_state.current_prompt_object = None
                            st.session_state.conversation_run_results = None
                            st.session_state.last_ai_response_single = None
                            st.experimental_rerun()
                        except FileNotFoundError:
                            st.error(f"Conversation '{base_name}' v{latest_version} not found. It might have been deleted.")
                        except ConversationCorruptedError as e:
                            st.error(f"Could not load conversation '{base_name}' v{latest_version}: {e}")

                # --- Load Specific Version ---
                if len(versions) > 1:
                    cols_specific_load_c = st.columns([0.7, 0.3])
                    with cols_specific_load_c[0]:
                        sorted_versions_for_select_c = sorted(versions, reverse=True)
                        version_to_load_c = st.selectbox(
                            "Load specific version:",
                            options=sorted_versions_for_select_c,
                            format_func=lambda x: f"v{x}",
                            key=f"cnv_select_version_{base_name}"
                        )
                    with cols_specific_load_c[1]:
                        if st.button(f"📂 Load v{version_to_load_c}", key=f"cnv_load_specific_{base_name}_{version_to_load_c}"):
                            try:
                                st.session_state.current_conversation_object = conversation_manager.load_conversation(base_name, version_to_load_c)
                                st.session_state.menu_choice = "Conversation Composer"
                                st.session_state.current_prompt_object = None
                                st.session_state.conversation_run_results = None
                                st.session_state.last_ai_response_single = None
                                st.experimental_rerun()
                            except FileNotFoundError:
                                 st.error(f"Conversation '{base_name}' v{version_to_load_c} not found.")
                            except ConversationCorruptedError as e:
                                 st.error(f"Could not load conversation '{base_name}' v{version_to_load_c}: {e}")

                st.markdown("---")

                # --- Delete Actions for this base_name ---
                st.write("**Delete Options:**")
                max_specific_delete_buttons_c = 3
                versions_for_quick_delete_c = list(reversed(versions))[:max_specific_delete_buttons_c]

                num_delete_cols_c = 1 + min(len(versions), max_specific_delete_buttons_c)
                cols_delete_actions_c = st.columns(num_delete_cols_c)

                with cols_delete_actions_c[0]:
                    delete_all_key_c = f"confirm_delete_all_cnv_{base_name}"
                    if st.button(f"🗑️ All ({len(versions)})", key=f"btn_del_all_cnv_{base_name}", help=f"Delete all versions of conversation '{base_name}'"):
                        st.session_state[delete_all_key_c] = True

                    if st.session_state.get(delete_all_key_c):
                        st.warning(f"**Confirm:** Delete all {len(versions)} versions of conversation '{base_name}'?")
                        col_confirm_all_c, col_cancel_all_c = st.columns(2)
                        with col_confirm_all_c:
                            if st.button("YES, DELETE ALL", key=f"yes_del_all_cnv_{base_name}", type="primary"):
                                deleted_count = conversation_manager.delete_conversation_all_versions(base_name)
                                st.success(f"Deleted {deleted_count} version(s) of conversation '{base_name}'.")
                                del st.session_state[delete_all_key_c]
                                st.experimental_rerun()
                        with col_cancel_all_c:
                            if st.button("NO, CANCEL", key=f"no_del_all_cnv_{base_name}"):
                                del st.session_state[delete_all_key_c]
                                st.experimental_rerun()

                for idx, version_num in enumerate(versions_for_quick_delete_c):
                    if idx + 1 < num_delete_cols_c:
                        with cols_delete_actions_c[idx + 1]:
                            delete_specific_key_c = f"confirm_delete_cnv_{base_name}_v{version_num}"
                            if st.button(f"🗑️ Del v{version_num}", key=f"btn_del_cnv_{base_name}_v{version_num}", help=f"Delete version {version_num} of conversation '{base_name}'"):
                                st.session_state[delete_specific_key_c] = True

                            if st.session_state.get(delete_specific_key_c):
                                st.warning(f"**Confirm:** Delete conversation '{base_name}' version {version_num}?")
                                col_confirm_spec_c, col_cancel_spec_c = st.columns(2)
                                with col_confirm_spec_c:
                                    if st.button(f"YES, DELETE v{version_num}", key=f"yes_del_cnv_{base_name}_v{version_num}", type="primary"):
                                        deleted = conversation_manager.delete_conversation_version(base_name, version_num)
                                        if deleted:
                                            st.success(f"Conversation '{base_name}' version {version_num} deleted.")
                                        else:
                                            st.error(f"Failed to delete conversation '{base_name}' version {version_num} (it may have already been deleted).")
                                        del st.session_state[delete_specific_key_c]
                                        st.experimental_rerun()
                                with col_cancel_spec_c:
                                    if st.button(f"NO, CANCEL v{version_num}", key=f"no_del_cnv_{base_name}_v{version_num}"):
                                        del st.session_state[delete_specific_key_c]
                                        st.experimental_rerun()

                st.markdown("---")
    except Exception as e:
        st.error(f"Error loading conversation library: {e}")

elif menu_choice == "User Settings":
    st.header("Your Personal Preferences: User Settings")

    if 'user_settings' not in st.session_state or st.session_state.user_settings is None:
        st.error("User settings not loaded. Please restart or check configuration.")
        st.stop()

    st.markdown(f"Editing settings for User ID: `{st.session_state.user_settings.user_id}`")

    us = st.session_state.user_settings # Get current settings from session state

    # Display current settings (some as editable, some as st.write for complex dicts)
    new_api_key = st.text_input(
        "Jules API Key (conceptual)",
        value=us.default_jules_api_key if us.default_jules_api_key else "",
        type="password",
        help="This is stored locally in a JSON file for this demo."
    )
    new_model = st.text_input("Default Jules Model", value=us.default_jules_model if us.default_jules_model else "")

    current_theme_index = 0 # Default to light
    theme_options = ["light", "dark", "system_default"]
    if us.ui_theme and us.ui_theme in theme_options:
        current_theme_index = theme_options.index(us.ui_theme)
    new_theme = st.selectbox("UI Theme", theme_options, index=current_theme_index)

    new_lang = st.text_input("Preferred Output Language (e.g., en-US)", value=us.preferred_output_language if us.preferred_output_language else "")

    st.markdown("**Default Execution Settings (JSON):**")
    exec_settings_str = json.dumps(us.default_execution_settings, indent=2) if us.default_execution_settings else "{}"
    new_exec_settings_str = st.text_area("Default Execution Settings JSON", value=exec_settings_str, height=150)

    st.markdown("**Creative Catalyst Defaults (JSON):**")
    catalyst_defaults_str = json.dumps(us.creative_catalyst_defaults, indent=2) if us.creative_catalyst_defaults else "{}"
    new_catalyst_defaults_str = st.text_area("Creative Catalyst Defaults JSON", value=catalyst_defaults_str, height=100)

    if st.button("Save User Settings"):
        # Update the session state object
        us.default_jules_api_key = new_api_key if new_api_key else None
        us.default_jules_model = new_model if new_model else None
        us.ui_theme = new_theme
        us.preferred_output_language = new_lang if new_lang else None

        try:
            us.default_execution_settings = json.loads(new_exec_settings_str)
        except json.JSONDecodeError:
            st.error("Invalid JSON for Default Execution Settings. Not saved.")

        try:
            us.creative_catalyst_defaults = json.loads(new_catalyst_defaults_str)
        except json.JSONDecodeError:
            st.error("Invalid JSON for Creative Catalyst Defaults. Not saved.")

        us.touch() # Update last_updated_at

        try:
            user_settings_manager.save_settings(us)
            st.success("User settings saved successfully!")
            st.session_state.user_settings = us # Ensure session state has the saved version

            # Re-initialize ConversationOrchestrator with new settings
            # This is important because CO might hold a reference to the old settings object
            # or its behavior might depend on settings at init time.
            # For this app, we create a new CO instance with new settings.
            # Note: jules_executor_instance is cached and its internal state isn't changed by UserSettings directly,
            # UserSettings are passed to its methods.
            st.session_state.conversation_orchestrator_instance = ConversationOrchestrator(
                jules_executor=jules_executor_instance, # The globally cached JE
                user_settings=st.session_state.user_settings # The updated user settings
            )
            st.experimental_rerun()
        except Exception as e_save_us:
            st.error(f"Error saving user settings: {e_save_us}")

    st.markdown("---")
    with st.expander("Current UserSettings Object (Raw Data)"):
        st.json(us.to_dict())


# --- Footer (Conceptual) ---
st.sidebar.markdown("---")
st.sidebar.info(f"Prometheus Protocol (Conceptual UI) - © {datetime.now(timezone.utc).year} Josephis K. Wade") # Use timezone.utc
st.sidebar.caption("The Architect's Code for AI Mastery.")
