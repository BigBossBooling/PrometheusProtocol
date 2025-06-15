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
        self.manager = ConversationManager(conversations_dir=self.temp_dir_path_str)
        self.test_user_id = str(uuid.uuid4()) # Though not directly used by ConversationManager

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

        # First save
        convo1_to_save = self._create_conversation_for_test("V1", task_for_turn1="Task V1", initial_version=5) # initial_version on obj is ignored by save
        original_lmt1 = convo1_to_save.last_modified_at
        time.sleep(0.001)

        returned_convo1 = self.manager.save_conversation(convo1_to_save, convo_name)

        self.assertEqual(returned_convo1.version, 1, "Returned convo version should be 1 for first save.")
        self.assertEqual(convo1_to_save.version, 1, "Original convo object version should be updated to 1.")
        self.assertNotEqual(returned_convo1.last_modified_at, original_lmt1, "LMT should update on save V1.")

        expected_file_v1_name = self.manager._construct_filename(convo_name, 1)
        expected_file_v1_path = self.manager.conversations_dir_path / expected_file_v1_name
        self.assertTrue(expected_file_v1_path.exists(), f"{expected_file_v1_name} was not created.")

        with expected_file_v1_path.open('r') as f:
            data_v1 = json.load(f)
        self.assertEqual(data_v1['version'], 1)
        self.assertEqual(data_v1['last_modified_at'], returned_convo1.last_modified_at)
        self.assertEqual(data_v1['title'], "Test Conversation V1")

        # Second save (same conversation name)
        convo2_to_save = self._create_conversation_for_test("V2", task_for_turn1="Task V2 Content", initial_version=10)
        original_lmt2 = convo2_to_save.last_modified_at
        time.sleep(0.001)

        returned_convo2 = self.manager.save_conversation(convo2_to_save, convo_name)

        self.assertEqual(returned_convo2.version, 2, "Returned convo version should be 2 for second save.")
        self.assertEqual(convo2_to_save.version, 2, "Original convo object for V2 save should be updated to 2.")
        self.assertNotEqual(returned_convo2.last_modified_at, original_lmt2, "LMT should update on save V2.")

        expected_file_v2_name = self.manager._construct_filename(convo_name, 2)
        expected_file_v2_path = self.manager.conversations_dir_path / expected_file_v2_name
        self.assertTrue(expected_file_v2_path.exists(), f"{expected_file_v2_name} was not created.")

        with expected_file_v2_path.open('r') as f:
            data_v2 = json.load(f)
        self.assertEqual(data_v2['version'], 2)
        self.assertEqual(data_v2['last_modified_at'], returned_convo2.last_modified_at)
        self.assertEqual(data_v2['turns'][0]['prompt_object']['task'], "Task V2 Content")

    def test_save_conversation_name_sanitization(self):
        """Test conversation name sanitization during save, creating versioned file."""
        convo_name = "My Test Convo with Spaces & Chars!@#"
        sanitized_base_name = "My_Test_Convo_with_Spaces__Chars"
        convo_to_save = self._create_conversation_for_test("Sanitize")

        self.manager.save_conversation(convo_to_save, convo_name)

        expected_file_name = self.manager._construct_filename(sanitized_base_name, 1)
        expected_file_path = self.manager.conversations_dir_path / expected_file_name
        self.assertTrue(expected_file_path.exists(), f"Expected file {expected_file_path} not found.")

    def test_save_conversation_empty_name_raises_value_error(self):
        """Test save_conversation raises ValueError for empty or whitespace name."""
        convo_to_save = self._create_conversation_for_test("EmptyName")
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty or just whitespace."):
            self.manager.save_conversation(convo_to_save, "")
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty or just whitespace."):
            self.manager.save_conversation(convo_to_save, "   ")

    def test_save_conversation_type_error(self):
        """Test save_conversation raises TypeError for invalid input type."""
        with self.assertRaises(TypeError):
            self.manager.save_conversation({"title": "fake"}, "wont_save")


    # --- Tests for load_conversation (with versioning) ---
    def test_load_conversation_latest_version(self):
        """Test loading the latest version when no specific version is requested."""
        convo_name = "load_latest_convo"
        c1 = self._create_conversation_for_test("v1", task_for_turn1="Content v1")
        self.manager.save_conversation(c1, convo_name) # Saves as v1
        time.sleep(0.001)
        c2 = self._create_conversation_for_test("v2", task_for_turn1="Content v2")
        self.manager.save_conversation(c2, convo_name) # Saves as v2
        time.sleep(0.001)
        c3 = self._create_conversation_for_test("v3", task_for_turn1="Content v3")
        self.manager.save_conversation(c3, convo_name) # Saves as v3

        loaded_convo = self.manager.load_conversation(convo_name)
        self.assertIsNotNone(loaded_convo)
        self.assertEqual(loaded_convo.version, 3)
        self.assertEqual(loaded_convo.turns[0].prompt_object.task, "Content v3")

    def test_load_conversation_specific_version(self):
        """Test loading a specific version of a conversation."""
        convo_name = "load_specific_convo"
        c1 = self._create_conversation_for_test("v1", task_for_turn1="Content v1")
        self.manager.save_conversation(c1, convo_name) # v1
        time.sleep(0.001)
        c2 = self._create_conversation_for_test("v2", task_for_turn1="Content v2")
        self.manager.save_conversation(c2, convo_name) # v2

        loaded_v1 = self.manager.load_conversation(convo_name, version=1)
        self.assertIsNotNone(loaded_v1)
        self.assertEqual(loaded_v1.version, 1)
        self.assertEqual(loaded_v1.turns[0].prompt_object.task, "Content v1")

        loaded_v2 = self.manager.load_conversation(convo_name, version=2)
        self.assertIsNotNone(loaded_v2)
        self.assertEqual(loaded_v2.version, 2)
        self.assertEqual(loaded_v2.turns[0].prompt_object.task, "Content v2")

    def test_load_conversation_specific_version_not_found(self):
        """Test FileNotFoundError when a specific, non-existent version is requested."""
        convo_name = "specific_version_missing_convo"
        c1 = self._create_conversation_for_test("v1")
        self.manager.save_conversation(c1, convo_name) # Only v1 exists
        with self.assertRaisesRegex(FileNotFoundError, f"Version 2 for conversation '{convo_name}' not found"):
            self.manager.load_conversation(convo_name, version=2)

    def test_load_conversation_no_versions_found(self):
        """Test FileNotFoundError when no versions exist for a conversation name."""
        with self.assertRaisesRegex(FileNotFoundError, "No versions found for conversation 'no_such_convo'"):
            self.manager.load_conversation("no_such_convo")

    def test_load_conversation_corrupted_json(self):
        """Test ConversationCorruptedError for malformed JSON."""
        convo_name = "corrupted_convo_json"
        c1 = self._create_conversation_for_test("Corrupt")
        self.manager.save_conversation(c1, convo_name) # v1

        file_path = self.manager.conversations_dir_path / self.manager._construct_filename(convo_name, 1)
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': this_is_not_valid,}")

        with self.assertRaisesRegex(ConversationCorruptedError, "Corrupted conversation file.*invalid JSON"):
            self.manager.load_conversation(convo_name, version=1)

    def test_load_conversation_version_mismatch_warning(self):
        """Test warning for version mismatch between filename and content (though content wins)."""
        convo_name = "version_mismatch_convo"
        convo_to_save = self._create_conversation_for_test("Mismatch Test") # Will be saved as v1
        self.manager.save_conversation(convo_to_save, convo_name) # Filename is _v1.json

        # Manually corrupt the file content to have a different version
        file_path = self.manager.conversations_dir_path / self.manager._construct_filename(convo_name, 1)
        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        data['version'] = 99 # Change version in content
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        # Expect a print warning, but load should succeed based on content's version
        # This test is more about observing the print for now, actual behavior might be stricter in future
        loaded_convo = self.manager.load_conversation(convo_name, version=1) # Load by filename version
        self.assertEqual(loaded_convo.version, 99) # Version from content


    # --- Tests for list_conversations (with versioning) ---
    def test_list_conversations_empty_directory(self):
        """Test list_conversations returns an empty dict for an empty directory."""
        self.assertEqual(self.manager.list_conversations(), {})

    def test_list_conversations_versioned(self):
        """Test list_conversations returns a dict with base names and sorted version lists."""
        # Save convoA v1, v2, v3
        self.manager.save_conversation(self._create_conversation_for_test("A1"), "convoA")
        time.sleep(0.001)
        self.manager.save_conversation(self._create_conversation_for_test("A2"), "convoA")
        time.sleep(0.001)
        self.manager.save_conversation(self._create_conversation_for_test("A3"), "convoA")

        # Save convoB v1
        time.sleep(0.001)
        self.manager.save_conversation(self._create_conversation_for_test("B1"), "convoB")

        # Save convo_with_space v1
        time.sleep(0.001)
        self.manager.save_conversation(self._create_conversation_for_test("S1"), "convo with space")

        expected_list = {
            "convoA": [1, 2, 3],
            "convoB": [1],
            "convo_with_space": [1]
        }
        actual_list = self.manager.list_conversations()
        self.assertEqual(actual_list, expected_list)

    def test_list_conversations_ignores_non_matching_files(self):
        """Test list_conversations ignores files not matching the version pattern."""
        self.manager.save_conversation(self._create_conversation_for_test("Valid"), "valid_convo")

        # Create some non-matching files
        (self.manager.conversations_dir_path / "non_versioned.json").touch()
        (self.manager.conversations_dir_path / "valid_convo_vx.json").touch()
        (self.manager.conversations_dir_path / "another_v1.txt").touch()
        (self.manager.conversations_dir_path / "prefix_valid_convo_v1.json").touch()

        expected = {"valid_convo": [1]}
        self.assertEqual(self.manager.list_conversations(), expected)

if __name__ == '__main__':
    unittest.main()
