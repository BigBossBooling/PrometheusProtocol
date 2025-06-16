from typing import List, Dict, Any, Optional # Any might be useful if PromptTurn.conditions become complex

from prometheus_protocol.core.jules_executor import JulesExecutor
from prometheus_protocol.core.conversation import Conversation, PromptTurn # Conversation might be used by a higher-level orchestrator
from prometheus_protocol.core.ai_response import AIResponse
from prometheus_protocol.core.user_settings import UserSettings

class ConversationOrchestrator:
    """
    Manages the execution of a multi-turn Conversation.

    It iterates through the turns of a Conversation, calls the JulesExecutor
    for each turn, manages conversation history, and collects AIResponses.
    For V1, it assumes a linear execution of turns and halts on the first error.
    """

    def __init__(self, jules_executor: JulesExecutor, user_settings: Optional[UserSettings] = None):
        """
        Initializes the ConversationOrchestrator.

        Args:
            jules_executor (JulesExecutor): An instance of JulesExecutor to be used
                                            for making (conceptual) calls to the AI engine.
            user_settings (Optional[UserSettings], optional): User-specific settings
                                                              to be passed to JulesExecutor.
                                                              Defaults to None.
        """
        if not isinstance(jules_executor, JulesExecutor):
            raise TypeError("jules_executor must be an instance of JulesExecutor")
        self.jules_executor = jules_executor
        self.user_settings = user_settings # Can be None

    def run_full_conversation(self, conversation: Conversation) -> Dict[str, AIResponse]:
        """
        Executes all turns in the given Conversation sequentially.

        Manages conversation history between turns. If a turn results in an error
        (AIResponse.was_successful is False), the conversation execution halts,
        and responses collected up to that point are returned.

        Args:
            conversation (Conversation): The Conversation object to execute.

        Returns:
            Dict[str, AIResponse]: A dictionary mapping each executed turn's ID (turn_id)
                                   to its corresponding AIResponse object.
        """
        if not isinstance(conversation, Conversation):
            raise TypeError("Input must be a Conversation object.")

        current_conversation_history: List[Dict[str, str]] = []
        turn_responses: Dict[str, AIResponse] = {}

        print(f"ORCHESTRATOR: Starting conversation (ID: {conversation.conversation_id}, Title: '{conversation.title}').")

        for turn in conversation.turns:
            print(f"ORCHESTRATOR: Processing Turn ID {turn.turn_id} (Task: '{turn.prompt_object.task[:50]}...').")

            # V1: No conditional logic for skipping turns based on turn.conditions yet.
            # This would be a V2 feature, checking conditions against previous turn_responses.

            ai_response = self.jules_executor.execute_conversation_turn(
                turn,
                current_conversation_history,
                user_settings=self.user_settings
            )

            # Populate source_conversation_id in the AIResponse
            ai_response.source_conversation_id = conversation.conversation_id

            turn_responses[turn.turn_id] = ai_response

            if ai_response.was_successful and ai_response.content is not None:
                # Add user's part of the current turn to history
                current_conversation_history.append({
                    "speaker": "user",
                    "text": turn.prompt_object.task
                })
                # Add AI's successful response to history
                current_conversation_history.append({
                    "speaker": "ai",
                    "text": ai_response.content
                })
            else:
                # Error occurred on this turn, halt conversation
                print(f"ORCHESTRATOR: CONVERSATION HALTED due to error on Turn ID {turn.turn_id}.")
                if ai_response.error_message:
                    print(f"ORCHESTRATOR: Error details: {ai_response.error_message}")
                break  # Stop processing further turns

        print(f"ORCHESTRATOR: Conversation (ID: {conversation.conversation_id}) processing finished. {len(turn_responses)} turns executed.")
        return turn_responses
