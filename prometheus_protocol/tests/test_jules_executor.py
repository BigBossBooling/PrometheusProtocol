import unittest
import uuid # For checking client_request_id format
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.conversation import PromptTurn
from prometheus_protocol.core.ai_response import AIResponse
from prometheus_protocol.core.jules_executor import JulesExecutor

class TestJulesExecutor(unittest.TestCase):

    def setUp(self):
        """Set up a JulesExecutor instance before each test."""
        self.executor = JulesExecutor(api_key="test_api_key")
        self.prompt_content = { # Reusable content for creating PromptObjects
            "role": "Test Role",
            "context": "Test Context",
            "task": "Test Task",
            "constraints": ["Constraint 1"],
            "examples": ["Example 1"],
            "tags": ["test"]
        }

    def create_prompt_object(self, task_override=None, context_override=None) -> PromptObject:
        """Helper to create a fresh PromptObject instance."""
        content = self.prompt_content.copy()
        if task_override:
            content["task"] = task_override
        if context_override:
            content["context"] = context_override
        return PromptObject(**content)

    def test_prepare_jules_request_payload_basic(self):
        """Test _prepare_jules_request_payload with a basic prompt."""
        prompt = self.create_prompt_object()
        payload = self.executor._prepare_jules_request_payload(prompt)

        self.assertEqual(payload["api_key"], "test_api_key")
        self.assertTrue(isinstance(uuid.UUID(payload["request_id_client"]), uuid.UUID)) # Valid UUID

        prompt_payload = payload["prompt_payload"]
        self.assertEqual(prompt_payload["role"], prompt.role)
        self.assertEqual(prompt_payload["task_description"], prompt.task)
        self.assertEqual(prompt_payload["context_data"], prompt.context)
        self.assertEqual(prompt_payload["constraints_list"], prompt.constraints)
        self.assertEqual(prompt_payload["examples_list"], prompt.examples)
        self.assertIn("temperature", prompt_payload["settings"])
        self.assertNotIn("conversation_history", payload)

    def test_prepare_jules_request_payload_with_history(self):
        """Test _prepare_jules_request_payload with conversation history."""
        prompt = self.create_prompt_object()
        history = [{"speaker": "user", "text": "Hello"}]
        payload = self.executor._prepare_jules_request_payload(prompt, history=history)

        self.assertIn("conversation_history", payload)
        self.assertEqual(payload["conversation_history"], history)

    # --- Tests for execute_prompt dynamic responses ---
    def test_execute_prompt_default_success(self):
        prompt = self.create_prompt_object(task_override="A normal task.")
        response = self.executor.execute_prompt(prompt)
        self.assertTrue(response.was_successful)
        self.assertIn("Simulated successful response to task: 'A normal task.'", response.content)
        self.assertIsNone(response.error_message)
        self.assertEqual(response.source_prompt_id, prompt.prompt_id)
        self.assertEqual(response.source_prompt_version, prompt.version)

    def test_execute_prompt_simulated_content_policy_error(self):
        prompt = self.create_prompt_object(task_override="error_test:content_policy trigger")
        response = self.executor.execute_prompt(prompt)
        self.assertFalse(response.was_successful)
        self.assertIsNone(response.content)
        self.assertIn("Simulated content policy violation", response.error_message)
        self.assertEqual(response.raw_jules_response["error"]["code"], "JULES_ERR_CONTENT_POLICY_VIOLATION")

    def test_execute_prompt_simulated_overload_error(self):
        prompt = self.create_prompt_object(task_override="error_test:overload trigger")
        response = self.executor.execute_prompt(prompt)
        self.assertFalse(response.was_successful)
        self.assertIn("Simulated model overload", response.error_message)
        self.assertEqual(response.raw_jules_response["error"]["code"], "JULES_ERR_MODEL_OVERLOADED")

    def test_execute_prompt_simulated_auth_error(self):
        prompt = self.create_prompt_object(task_override="error_test:auth trigger")
        response = self.executor.execute_prompt(prompt)
        self.assertFalse(response.was_successful)
        self.assertIn("Simulated authentication failure", response.error_message)
        self.assertEqual(response.raw_jules_response["error"]["code"], "AUTH_FAILURE")
        self.assertIsNone(response.jules_request_id_jules) # Specific check for auth error simulation
        self.assertIsNone(response.jules_request_id_client)


    def test_execute_prompt_short_task_advisory(self):
        prompt = self.create_prompt_object(task_override="Hi") # Less than 3 words
        response = self.executor.execute_prompt(prompt)
        self.assertTrue(response.was_successful)
        self.assertIn("Task 'Hi' is very short. For a better simulated response, please elaborate", response.content)

    # --- Tests for execute_conversation_turn dynamic responses ---
    def test_execute_conversation_turn_default_success_no_history(self):
        prompt = self.create_prompt_object(task_override="First turn task")
        # Ensure prompt_object is a new instance for the turn
        turn_prompt_object = PromptObject(role=prompt.role, context=prompt.context, task=prompt.task, constraints=prompt.constraints, examples=prompt.examples)
        turn = PromptTurn(prompt_object=turn_prompt_object)
        response = self.executor.execute_conversation_turn(turn, [])

        self.assertTrue(response.was_successful)
        # The content check needs to be more specific to what execute_conversation_turn generates
        self.assertIn(f"Simulated response to turn: '{turn_prompt_object.task}'. History length: 0.", response.content)
        self.assertEqual(response.source_turn_id, turn.turn_id)
        self.assertEqual(response.source_prompt_id, turn_prompt_object.prompt_id)


    def test_execute_conversation_turn_default_success_with_history(self):
        prompt = self.create_prompt_object(task_override="Follow-up task")
        turn_prompt_object = PromptObject(role=prompt.role, context=prompt.context, task=prompt.task, constraints=prompt.constraints, examples=prompt.examples)
        turn = PromptTurn(prompt_object=turn_prompt_object)
        history = [{"speaker": "user", "text": "Previous user query"}, {"speaker": "ai", "text": "Previous AI answer"}]
        response = self.executor.execute_conversation_turn(turn, history)

        self.assertTrue(response.was_successful)
        self.assertIn(f"Simulated response to turn: '{turn_prompt_object.task}'", response.content)
        self.assertIn(f"History length: {len(history)}", response.content)
        # The dummy response includes the last user message from history if history is not empty.
        # In this case, history[-1] is the AI's response, history[-2] is the user's.
        # The execute_conversation_turn current logic is: `current_conversation_history[-1]['text'][:30]`
        # This means it would take the last item, which could be AI or user.
        # For this test, let's make history such that the last item is what we expect to be summarized.
        # Or, more simply, check that *some* part of the history content is acknowledged.
        # The current dummy response logic is: sim_content += f" Last user msg: '{current_conversation_history[-1]['text'][:30]}...'"
        # So it will take the last message, regardless of speaker.
        self.assertIn(f"Last user msg: '{history[-1]['text'][:30]}...", response.content)


    def test_execute_conversation_turn_simulated_content_policy_error(self):
        prompt = self.create_prompt_object(task_override="error_test:content_policy in conversation")
        turn_prompt_object = PromptObject(role=prompt.role, context=prompt.context, task=prompt.task, constraints=prompt.constraints, examples=prompt.examples)
        turn = PromptTurn(prompt_object=turn_prompt_object)
        response = self.executor.execute_conversation_turn(turn, [])

        self.assertFalse(response.was_successful)
        self.assertIn(f"Simulated content policy violation for turn '{turn.turn_id}'", response.error_message)
        self.assertEqual(response.raw_jules_response["error"]["code"], "JULES_ERR_CONTENT_POLICY_VIOLATION")

    def test_execute_conversation_turn_simulated_overload_error(self):
        prompt = self.create_prompt_object(task_override="error_test:overload in conversation")
        turn_prompt_object = PromptObject(role=prompt.role, context=prompt.context, task=prompt.task, constraints=prompt.constraints, examples=prompt.examples)
        turn = PromptTurn(prompt_object=turn_prompt_object)
        response = self.executor.execute_conversation_turn(turn, [])

        self.assertFalse(response.was_successful)
        self.assertIn(f"Simulated model overload for turn '{turn.turn_id}'", response.error_message)
        self.assertEqual(response.raw_jules_response["error"]["code"], "JULES_ERR_MODEL_OVERLOADED")

if __name__ == '__main__':
    unittest.main()
