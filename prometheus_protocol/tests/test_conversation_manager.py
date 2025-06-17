import unittest
import tempfile
import json
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone
import time

from prometheus_protocol.core.conversation_manager import ConversationManager
from prometheus_protocol.core.conversation import Conversation, PromptTurn
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.exceptions import ConversationCorruptedError

class TestConversationManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for conversations before each test."""
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir_path_str = str(self._temp_dir_obj.name)
        self.manager = ConversationManager(data_storage_base_path=self.temp_dir_path_str) # Updated

        self.personal_user_id = "test_user_conv_personal"
        self.workspace_id_alpha = "ws_conv_alpha_space"
        self.workspace_id_beta = "ws_conv_beta_space" # For testing an empty context

        # Base objects for creating conversations easily
        self.base_prompt_content = {
            "role": "Test Role", "context": "Test Context",
            "constraints": ["C1"], "examples": ["E1"]
        }

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self._temp_dir_obj.cleanup()

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=2):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        ts1_str_parsed = ts1_str.replace('Z', '+00:00') if 'Z' in ts1_str else ts1_str
        ts2_str_parsed = ts2_str.replace('Z', '+00:00') if 'Z' in ts2_str else ts2_str
        dt1 = datetime.fromisoformat(ts1_str_parsed)
        dt2 = datetime.fromisoformat(ts2_str_parsed)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    def _create_dummy_prompt_object(self, task_text: str) -> PromptObject:
        # Uses self.base_prompt_content but overrides task
        content = {**self.base_prompt_content, "task": task_text}
        return PromptObject(**content)

    def _create_dummy_prompt_turn(self, task_text_for_prompt: str) -> PromptTurn:
        prompt_obj = self._create_dummy_prompt_object(task_text_for_prompt)
        return PromptTurn(prompt_object=prompt_obj)

    def _create_conversation_for_test(self, title_suffix="", task_for_turn1="Task 1", initial_version=1):
        """Helper to create a fresh Conversation object for testing save.
           The 'initial_version' is what the object has BEFORE save_conversation modifies it.
           save_conversation will determine the actual saved version number based on files on disk.
        """
        turn1 = self._create_dummy_prompt_turn(task_for_turn1)
        return Conversation(
            title=f"Test Conversation {title_suffix}",
            turns=[turn1],
            tags=["test_tag"],
            version=initial_version
        )

    # --- Tests for save_conversation (with versioning) ---
    def test_save_conversation_new_and_incrementing_versions(self):
        """Test saving a new convo creates v1, and subsequent saves increment version."""
        convo_name = "versioned_convo"

        # Personal Context
        convo1_user = self._create_conversation_for_test("V1_User", task_for_turn1="User Task V1")
        self.manager.save_conversation(convo1_user, convo_name, context_id=self.personal_user_id)
        user_context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        expected_file_v1_user = user_context_path / self.manager._construct_filename(convo_name, 1)
        self.assertTrue(expected_file_v1_user.exists())
        with expected_file_v1_user.open('r') as f:
            data_v1_user = json.load(f)
        self.assertEqual(data_v1_user['version'], 1)
        self.assertEqual(data_v1_user['title'], "Test Conversation V1_User")

        # Personal Context - Version 2
        convo2_user = self._create_conversation_for_test("V2_User", task_for_turn1="User Task V2")
        self.manager.save_conversation(convo2_user, convo_name, context_id=self.personal_user_id)
        expected_file_v2_user = user_context_path / self.manager._construct_filename(convo_name, 2)
        self.assertTrue(expected_file_v2_user.exists())

        # Workspace Alpha Context - Version 1 (Same base name)
        convo1_ws_alpha = self._create_conversation_for_test("V1_WS_Alpha", task_for_turn1="WS Alpha Task V1")
        self.manager.save_conversation(convo1_ws_alpha, convo_name, context_id=self.workspace_id_alpha)
        ws_alpha_context_path = self.manager._get_context_specific_conversations_path(self.workspace_id_alpha)
        expected_file_v1_ws_alpha = ws_alpha_context_path / self.manager._construct_filename(convo_name, 1)
        self.assertTrue(expected_file_v1_ws_alpha.exists())
        with expected_file_v1_ws_alpha.open('r') as f:
            data_v1_ws_alpha = json.load(f)
        self.assertEqual(data_v1_ws_alpha['version'], 1)
        self.assertEqual(data_v1_ws_alpha['title'], "Test Conversation V1_WS_Alpha")

        # Workspace Alpha Context - Different base name
        other_convo_name_ws = "other_ws_convo"
        convo_other_ws = self._create_conversation_for_test("Other_WS", task_for_turn1="Other WS Task")
        self.manager.save_conversation(convo_other_ws, other_convo_name_ws, context_id=self.workspace_id_alpha)
        expected_file_other_ws = ws_alpha_context_path / self.manager._construct_filename(other_convo_name_ws, 1)
        self.assertTrue(expected_file_other_ws.exists())


    def test_save_conversation_name_sanitization(self):
        convo_name = "My Test Convo with Spaces & Chars!@#"
        sanitized_base_name = "My_Test_Convo_with_Spaces__Chars"
        convo_to_save = self._create_conversation_for_test("Sanitize")
        self.manager.save_conversation(convo_to_save, convo_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        expected_file_name = self.manager._construct_filename(sanitized_base_name, 1)
        expected_file_path = context_path / expected_file_name
        self.assertTrue(expected_file_path.exists())

    def test_save_conversation_empty_name_raises_value_error(self):
        convo_to_save = self._create_conversation_for_test("EmptyName")
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty or just whitespace."):
            self.manager.save_conversation(convo_to_save, "", context_id=self.personal_user_id)
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty or just whitespace."):
            self.manager.save_conversation(convo_to_save, "   ", context_id=self.personal_user_id)

    def test_save_conversation_type_error(self):
        with self.assertRaises(TypeError):
            self.manager.save_conversation({"title": "fake"}, "wont_save", context_id=self.personal_user_id)


    def test_load_conversation_latest_version_with_context(self):
        convo_name = "load_latest_convo_ctx"
        self.manager.save_conversation(self._create_conversation_for_test("v1", task_for_turn1="User V1"), convo_name, context_id=self.personal_user_id)
        time.sleep(0.001)
        self.manager.save_conversation(self._create_conversation_for_test("v2", task_for_turn1="User V2"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("ws_v1", task_for_turn1="WS V1"), convo_name, context_id=self.workspace_id_alpha)

        loaded_user = self.manager.load_conversation(convo_name, context_id=self.personal_user_id)
        self.assertEqual(loaded_user.version, 2)
        self.assertEqual(loaded_user.turns[0].prompt_object.task, "User V2")

        loaded_ws = self.manager.load_conversation(convo_name, context_id=self.workspace_id_alpha)
        self.assertEqual(loaded_ws.version, 1)
        self.assertEqual(loaded_ws.turns[0].prompt_object.task, "WS V1")

    def test_load_conversation_specific_version_with_context(self):
        convo_name = "load_specific_convo_ctx"
        self.manager.save_conversation(self._create_conversation_for_test("v1", task_for_turn1="User V1"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("v2", task_for_turn1="User V2"), convo_name, context_id=self.personal_user_id)

        loaded_v1 = self.manager.load_conversation(convo_name, version=1, context_id=self.personal_user_id)
        self.assertEqual(loaded_v1.version, 1)
        self.assertEqual(loaded_v1.turns[0].prompt_object.task, "User V1")

        loaded_v2 = self.manager.load_conversation(convo_name, version=2, context_id=self.personal_user_id)
        self.assertEqual(loaded_v2.version, 2)
        self.assertEqual(loaded_v2.turns[0].prompt_object.task, "User V2")

        # Try to load from wrong context
        with self.assertRaisesRegex(FileNotFoundError, f"Version 1 for conversation '{convo_name}' not found in context '{self.workspace_id_alpha}'"):
            self.manager.load_conversation(convo_name, version=1, context_id=self.workspace_id_alpha)


    def test_load_conversation_specific_version_not_found_in_context(self):
        convo_name = "specific_version_missing_convo_ctx"
        self.manager.save_conversation(self._create_conversation_for_test("v1"), convo_name, context_id=self.personal_user_id)
        with self.assertRaisesRegex(FileNotFoundError, f"Version 2 for conversation '{convo_name}' not found in context '{self.personal_user_id}'"):
            self.manager.load_conversation(convo_name, version=2, context_id=self.personal_user_id)

    def test_load_conversation_no_versions_found_in_context(self):
        with self.assertRaisesRegex(FileNotFoundError, f"No versions found for conversation 'no_such_convo_ctx' in context '{self.workspace_id_beta}'"):
            self.manager.load_conversation("no_such_convo_ctx", context_id=self.workspace_id_beta)

    def test_load_conversation_corrupted_json_in_context(self):
        convo_name = "corrupted_convo_json_ctx"
        self.manager.save_conversation(self._create_conversation_for_test("Corrupt"), convo_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        file_path = context_path / self.manager._construct_filename(convo_name, 1)
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': this_is_not_valid,}")

        with self.assertRaisesRegex(ConversationCorruptedError, f"Corrupted conversation file .* in context '{self.personal_user_id}'"):
            self.manager.load_conversation(convo_name, version=1, context_id=self.personal_user_id)

    def test_load_conversation_version_mismatch_warning_in_context(self):
        convo_name = "version_mismatch_convo_ctx"
        convo_to_save = self._create_conversation_for_test("Mismatch Test")
        self.manager.save_conversation(convo_to_save, convo_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        file_path = context_path / self.manager._construct_filename(convo_name, 1)
        with file_path.open('r', encoding='utf-8') as f: data = json.load(f)
        data['version'] = 99
        with file_path.open('w', encoding='utf-8') as f: json.dump(data, f, indent=4)

        loaded_convo = self.manager.load_conversation(convo_name, version=1, context_id=self.personal_user_id)
        self.assertEqual(loaded_convo.version, 99)


    def test_list_conversations_empty_directory_with_context(self):
        self.assertEqual(self.manager.list_conversations(context_id=self.workspace_id_beta), {})

    def test_list_conversations_versioned_with_contexts(self):
        # Personal context
        self.manager.save_conversation(self._create_conversation_for_test("A1_user"), "convoA", context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("A2_user"), "convoA", context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("B1_user"), "convoB", context_id=self.personal_user_id)

        # Workspace Alpha context
        self.manager.save_conversation(self._create_conversation_for_test("A1_ws"), "convoA", context_id=self.workspace_id_alpha)
        self.manager.save_conversation(self._create_conversation_for_test("C1_ws"), "convoC", context_id=self.workspace_id_alpha)

        expected_user = {"convoA": [1, 2], "convoB": [1]}
        self.assertEqual(self.manager.list_conversations(context_id=self.personal_user_id), expected_user)

        expected_ws_alpha = {"convoA": [1], "convoC": [1]}
        self.assertEqual(self.manager.list_conversations(context_id=self.workspace_id_alpha), expected_ws_alpha)

        self.assertEqual(self.manager.list_conversations(context_id=self.workspace_id_beta), {})

        # Default context (None)
        self.manager.save_conversation(self._create_conversation_for_test("D1_default"), "convoD", context_id=None)
        expected_default = {"convoD": [1]}
        self.assertEqual(self.manager.list_conversations(context_id=None), expected_default)


    def test_list_conversations_ignores_non_matching_files_in_context(self):
        context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("Valid"), "valid_convo", context_id=self.personal_user_id)

        (context_path / "non_versioned.json").touch()
        (context_path / "valid_convo_vx.json").touch()
        (context_path / "another_v1.txt").touch()

        expected = {"valid_convo": [1]}
        self.assertEqual(self.manager.list_conversations(context_id=self.personal_user_id), expected)

    # --- Tests for Delete Methods (Context-Aware) ---

    def test_delete_conversation_version_success_with_context(self):
        convo_name = "delete_version_ctx_convo"
        sanitized_name = self.manager._sanitize_base_name(convo_name)

        self.manager.save_conversation(self._create_conversation_for_test("v1_user"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("v2_user"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("v1_ws"), convo_name, context_id=self.workspace_id_alpha)

        user_context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        file_v1_user = user_context_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1_user.exists())

        delete_result = self.manager.delete_conversation_version(convo_name, 1, context_id=self.personal_user_id)
        self.assertTrue(delete_result)
        self.assertFalse(file_v1_user.exists())

        file_v2_user = user_context_path / self.manager._construct_filename(sanitized_name, 2)
        self.assertTrue(file_v2_user.exists())

        ws_alpha_context_path = self.manager._get_context_specific_conversations_path(self.workspace_id_alpha)
        file_v1_ws = ws_alpha_context_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1_ws.exists())

        listed_user = self.manager.list_conversations(context_id=self.personal_user_id)
        self.assertEqual(listed_user.get(sanitized_name), [2])
        listed_ws = self.manager.list_conversations(context_id=self.workspace_id_alpha)
        self.assertEqual(listed_ws.get(sanitized_name), [1])

    def test_delete_conversation_version_non_existent_version_with_context(self):
        convo_name = "del_non_exist_ver_ctx_convo"
        self.manager.save_conversation(self._create_conversation_for_test("v1"), convo_name, context_id=self.personal_user_id)
        delete_result = self.manager.delete_conversation_version(convo_name, 5, context_id=self.personal_user_id)
        self.assertFalse(delete_result)

    def test_delete_conversation_version_non_existent_name_with_context(self):
        delete_result = self.manager.delete_conversation_version("no_such_convo_ctx", 1, context_id=self.personal_user_id)
        self.assertFalse(delete_result)

    def test_delete_conversation_all_versions_success_with_context(self):
        convo_name = "del_all_ctx_convo"
        sanitized_name = self.manager._sanitize_base_name(convo_name)

        self.manager.save_conversation(self._create_conversation_for_test("v1_user"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("v2_user"), convo_name, context_id=self.personal_user_id)
        self.manager.save_conversation(self._create_conversation_for_test("v1_ws_alpha"), convo_name, context_id=self.workspace_id_alpha)
        other_convo_ws_alpha = "other_ws_alpha_convo"
        sanitized_other_ws_alpha = self.manager._sanitize_base_name(other_convo_ws_alpha)
        self.manager.save_conversation(self._create_conversation_for_test("other_ws"), other_convo_ws_alpha, context_id=self.workspace_id_alpha)

        deleted_count_user = self.manager.delete_conversation_all_versions(convo_name, context_id=self.personal_user_id)
        self.assertEqual(deleted_count_user, 2)

        user_context_path = self.manager._get_context_specific_conversations_path(self.personal_user_id)
        self.assertFalse((user_context_path / self.manager._construct_filename(sanitized_name, 1)).exists())
        self.assertFalse((user_context_path / self.manager._construct_filename(sanitized_name, 2)).exists())

        listed_user = self.manager.list_conversations(context_id=self.personal_user_id)
        self.assertNotIn(sanitized_name, listed_user)

        ws_alpha_context_path = self.manager._get_context_specific_conversations_path(self.workspace_id_alpha)
        self.assertTrue((ws_alpha_context_path / self.manager._construct_filename(sanitized_name, 1)).exists())
        self.assertTrue((ws_alpha_context_path / self.manager._construct_filename(sanitized_other_ws_alpha, 1)).exists())
        listed_ws_alpha = self.manager.list_conversations(context_id=self.workspace_id_alpha)
        self.assertIn(sanitized_name, listed_ws_alpha)
        self.assertIn(sanitized_other_ws_alpha, listed_ws_alpha)

    def test_delete_conversation_all_versions_non_existent_name_with_context(self):
        deleted_count = self.manager.delete_conversation_all_versions("no_such_all_del_ctx_convo", context_id=self.personal_user_id)
        self.assertEqual(deleted_count, 0)


if __name__ == '__main__':
    unittest.main()
