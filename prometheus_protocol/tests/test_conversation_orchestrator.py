import unittest
from unittest.mock import MagicMock, call # Added call for checking call arguments
import uuid # For creating IDs for test objects
from typing import Optional # Added for _create_dummy_ai_response

from prometheus_protocol.core.conversation_orchestrator import ConversationOrchestrator
from prometheus_protocol.core.jules_executor import JulesExecutor
from prometheus_protocol.core.conversation import Conversation, PromptTurn
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.ai_response import AIResponse
from datetime import datetime, timezone # For creating AIResponse timestamps

class TestConversationOrchestrator(unittest.TestCase):

    def setUp(self):
        """Set up a mock JulesExecutor and ConversationOrchestrator for each test."""
        self.mock_jules_executor = MagicMock(spec=JulesExecutor)
        self.orchestrator = ConversationOrchestrator(jules_executor=self.mock_jules_executor)

    def _create_dummy_prompt_object(self, task_text: str, prompt_id=None, version=1) -> PromptObject:
        return PromptObject(
            prompt_id=prompt_id if prompt_id else str(uuid.uuid4()),
            version=version,
            role="Test Role",
            context="Test Context",
            task=task_text,
            constraints=[],
            examples=[]
        )

    def _create_dummy_prompt_turn(self, task_text: str, turn_id=None, prompt_id=None) -> PromptTurn:
        prompt = self._create_dummy_prompt_object(task_text, prompt_id=prompt_id)
        return PromptTurn(
            turn_id=turn_id if turn_id else str(uuid.uuid4()),
            prompt_object=prompt
        )

    def _create_dummy_ai_response(self, content: str, successful: bool = True, error_msg: str = None,
                                  prompt_id: str = "dummy_pid", version: int = 1, turn_id: Optional[str] = None) -> AIResponse:
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        return AIResponse(
            source_prompt_id=prompt_id,
            source_prompt_version=version,
            source_turn_id=turn_id,
            timestamp_request_sent=now,
            timestamp_response_received=now,
            content=content if successful else None,
            raw_jules_response={"simulated": True, "status": "success" if successful else "error"},
            was_successful=successful,
            error_message=error_msg
        )

    def test_run_full_conversation_all_success(self):
        """Test a conversation where all turns execute successfully."""
        turn1_id = str(uuid.uuid4())
        turn2_id = str(uuid.uuid4())

        turn1 = self._create_dummy_prompt_turn("Task for Turn 1", turn_id=turn1_id)
        turn2 = self._create_dummy_prompt_turn("Task for Turn 2", turn_id=turn2_id)

        conversation = Conversation(title="Test Success Convo", turns=[turn1, turn2])
        conversation_id = conversation.conversation_id

        # Configure mock executor to return successful responses
        response1_content = "AI Response to Turn 1"
        response2_content = "AI Response to Turn 2"

        # Use side_effect to return different AIResponse objects for sequential calls
        self.mock_jules_executor.execute_conversation_turn.side_effect = [
            self._create_dummy_ai_response(response1_content, prompt_id=turn1.prompt_object.prompt_id, version=turn1.prompt_object.version, turn_id=turn1.turn_id),
            self._create_dummy_ai_response(response2_content, prompt_id=turn2.prompt_object.prompt_id, version=turn2.prompt_object.version, turn_id=turn2.turn_id)
        ]

        turn_responses = self.orchestrator.run_full_conversation(conversation)

        self.assertEqual(self.mock_jules_executor.execute_conversation_turn.call_count, 2)
        self.assertIn(turn1_id, turn_responses)
        self.assertIn(turn2_id, turn_responses)

        # Check response for turn 1
        self.assertTrue(turn_responses[turn1_id].was_successful)
        self.assertEqual(turn_responses[turn1_id].content, response1_content)
        self.assertEqual(turn_responses[turn1_id].source_conversation_id, conversation_id)

        # Check response for turn 2
        self.assertTrue(turn_responses[turn2_id].was_successful)
        self.assertEqual(turn_responses[turn2_id].content, response2_content)
        self.assertEqual(turn_responses[turn2_id].source_conversation_id, conversation_id)

        # Check history passed to the second call
        history_for_turn2 = self.mock_jules_executor.execute_conversation_turn.call_args_list[1][0][1] # args[1] is current_conversation_history
        expected_history_for_turn2 = [
            {"speaker": "user", "text": "Task for Turn 1"},
            {"speaker": "ai", "text": response1_content}
        ]
        self.assertEqual(history_for_turn2, expected_history_for_turn2)


    def test_run_full_conversation_halts_on_error(self):
        """Test that conversation execution halts on the first error encountered."""
        turn1_id = str(uuid.uuid4())
        turn2_id = str(uuid.uuid4()) # Failing turn
        turn3_id = str(uuid.uuid4()) # Should not be executed

        turn1 = self._create_dummy_prompt_turn("Task for Turn 1", turn_id=turn1_id)
        turn2 = self._create_dummy_prompt_turn("Task for Turn 2 (will fail)", turn_id=turn2_id)
        turn3 = self._create_dummy_prompt_turn("Task for Turn 3", turn_id=turn3_id)

        conversation = Conversation(title="Test Error Halt Convo", turns=[turn1, turn2, turn3])
        conversation_id = conversation.conversation_id

        response1_content = "AI Response to Turn 1 (Success)"
        error_message_turn2 = "Simulated AI error on Turn 2"

        self.mock_jules_executor.execute_conversation_turn.side_effect = [
            self._create_dummy_ai_response(response1_content, prompt_id=turn1.prompt_object.prompt_id, version=turn1.prompt_object.version, turn_id=turn1.turn_id),
            self._create_dummy_ai_response(None, successful=False, error_msg=error_message_turn2, prompt_id=turn2.prompt_object.prompt_id, version=turn2.prompt_object.version, turn_id=turn2.turn_id)
        ]

        turn_responses = self.orchestrator.run_full_conversation(conversation)

        self.assertEqual(self.mock_jules_executor.execute_conversation_turn.call_count, 2) # Called for turn1 and turn2
        self.assertIn(turn1_id, turn_responses)
        self.assertIn(turn2_id, turn_responses)
        self.assertNotIn(turn3_id, turn_responses) # Turn 3 should not have been executed

        self.assertTrue(turn_responses[turn1_id].was_successful)
        self.assertEqual(turn_responses[turn1_id].source_conversation_id, conversation_id)

        self.assertFalse(turn_responses[turn2_id].was_successful)
        self.assertEqual(turn_responses[turn2_id].error_message, error_message_turn2)
        self.assertEqual(turn_responses[turn2_id].source_conversation_id, conversation_id)


    def test_run_full_conversation_empty_conversation(self):
        """Test running an empty conversation (no turns)."""
        conversation = Conversation(title="Empty Convo", turns=[])
        turn_responses = self.orchestrator.run_full_conversation(conversation)

        self.assertEqual(self.mock_jules_executor.execute_conversation_turn.call_count, 0)
        self.assertEqual(turn_responses, {})

    def test_run_full_conversation_history_builds_correctly_multiple_turns(self):
        """Test that conversation history is built and passed correctly over multiple turns."""
        turns_data = [("Task T1", "Resp T1"), ("Task T2", "Resp T2"), ("Task T3", "Resp T3")]
        turns = [self._create_dummy_prompt_turn(task, turn_id=f"tid_{i}") for i, (task, _) in enumerate(turns_data)]
        conversation = Conversation(title="History Test Convo", turns=turns)

        # Setup mock to return AIResponse based on input turn's task for easier checking
        def mock_exec_turn_side_effect(turn_obj, history_arg):
            # Find the response content for this task
            resp_content = ""
            for t_task, t_resp in turns_data:
                if t_task == turn_obj.prompt_object.task:
                    resp_content = t_resp
                    break
            return self._create_dummy_ai_response(
                resp_content,
                prompt_id=turn_obj.prompt_object.prompt_id,
                version=turn_obj.prompt_object.version,
                turn_id=turn_obj.turn_id
            )
        self.mock_jules_executor.execute_conversation_turn.side_effect = mock_exec_turn_side_effect

        self.orchestrator.run_full_conversation(conversation)

        self.assertEqual(self.mock_jules_executor.execute_conversation_turn.call_count, len(turns))

        # Check history passed to each call
        calls = self.mock_jules_executor.execute_conversation_turn.call_args_list

        # Call 1 (Turn 0)
        history_call1 = calls[0][0][1] # args[1] is current_conversation_history
        self.assertEqual(history_call1, [])

        # Call 2 (Turn 1)
        history_call2 = calls[1][0][1]
        expected_history_call2 = [
            {"speaker": "user", "text": "Task T1"}, {"speaker": "ai", "text": "Resp T1"}
        ]
        self.assertEqual(history_call2, expected_history_call2)

        # Call 3 (Turn 2)
        history_call3 = calls[2][0][1]
        expected_history_call3 = [
            {"speaker": "user", "text": "Task T1"}, {"speaker": "ai", "text": "Resp T1"},
            {"speaker": "user", "text": "Task T2"}, {"speaker": "ai", "text": "Resp T2"}
        ]
        self.assertEqual(history_call3, expected_history_call3)

if __name__ == '__main__':
    unittest.main()
