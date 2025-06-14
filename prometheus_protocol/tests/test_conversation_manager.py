import unittest
import tempfile
import json
from pathlib import Path
import shutil # For cleaning up if setUp fails
from datetime import datetime, timezone # For checking timestamps

from prometheus_protocol.core.conversation_manager import ConversationManager
from prometheus_protocol.core.conversation import Conversation, PromptTurn
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.exceptions import ConversationCorruptedError

class TestConversationManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for conversations before each test."""
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self._temp_dir_obj.name)
        self.manager = ConversationManager(conversations_dir=str(self.temp_dir_path))

        # Create dummy objects for use in tests
        self.prompt_obj1 = PromptObject(role="R1", context="C1", task="T1", constraints=[], examples=[])
        self.turn1 = PromptTurn(prompt_object=self.prompt_obj1, notes="Turn 1")

        self.prompt_obj2 = PromptObject(role="R2", context="C2", task="T2", constraints=[], examples=[])
        self.turn2 = PromptTurn(prompt_object=self.prompt_obj2, notes="Turn 2", parent_turn_id=self.turn1.turn_id)

        self.dummy_conversation_data = {
            "title": "Test Conversation Title",
            "description": "A conversation for testing.",
            "turns": [self.turn1, self.turn2],
            "tags": ["test", "manager"]
        }
        # Create a fully fledged Conversation object
        self.dummy_conversation = Conversation(**self.dummy_conversation_data)

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

    def test_save_conversation_creates_file_and_updates_timestamp(self):
        """Test save_conversation creates a file and updates last_modified_at."""
        convo_name = "my_test_convo"
        original_lmt = self.dummy_conversation.last_modified_at

        # Ensure some time might pass if system clock resolution is low
        # Alternatively, set last_modified_at to a known past time before saving
        # For this test, we rely on touch() making it different from initial creation time
        # if saved quickly after creation. A more robust way is to set it manually to an older date.
        # self.dummy_conversation.last_modified_at = "2000-01-01T00:00:00Z"
        # original_lmt = self.dummy_conversation.last_modified_at

        import time
        time.sleep(0.001) # Introduce small delay to ensure timestamp can change

        self.manager.save_conversation(self.dummy_conversation, convo_name)

        expected_file = self.temp_dir_path / "my_test_convo.json"
        self.assertTrue(expected_file.exists())

        with expected_file.open('r', encoding='utf-8') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["title"], self.dummy_conversation_data["title"])
        self.assertEqual(len(saved_data["turns"]), 2)
        self.assertEqual(saved_data["turns"][0]["notes"], self.turn1.notes)
        self.assertNotEqual(saved_data["last_modified_at"], original_lmt, "last_modified_at was not updated.")
        self.assertAreTimestampsClose(saved_data["last_modified_at"], datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


    def test_save_conversation_name_sanitization(self):
        """Test conversation name sanitization during save."""
        convo_name = "My Test Convo with Spaces & Chars!@#"
        self.manager.save_conversation(self.dummy_conversation, convo_name)
        expected_file = self.temp_dir_path / "My_Test_Convo_with_Spaces__Chars.json"
        self.assertTrue(expected_file.exists(), f"Expected file {expected_file} not found.")

    def test_save_conversation_empty_name_raises_value_error(self):
        """Test save_conversation raises ValueError for empty or whitespace name."""
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty."):
            self.manager.save_conversation(self.dummy_conversation, "")
        with self.assertRaisesRegex(ValueError, "Conversation name cannot be empty."):
            self.manager.save_conversation(self.dummy_conversation, "   ")

    def test_save_conversation_name_sanitizes_to_empty_raises_value_error(self):
        """Test save_conversation raises ValueError if name sanitizes to empty."""
        with self.assertRaisesRegex(ValueError, "Conversation name '!@#\$' sanitized to an empty string"):
            self.manager.save_conversation(self.dummy_conversation, "!@#$")

    def test_load_conversation_success(self):
        """Test loading an existing conversation successfully."""
        convo_name = "load_me_convo"
        self.manager.save_conversation(self.dummy_conversation, convo_name)

        loaded_convo = self.manager.load_conversation(convo_name)
        self.assertIsInstance(loaded_convo, Conversation)
        self.assertEqual(loaded_convo.title, self.dummy_conversation.title)
        self.assertEqual(len(loaded_convo.turns), len(self.dummy_conversation.turns))
        self.assertEqual(loaded_convo.turns[0].notes, self.dummy_conversation.turns[0].notes)
        self.assertEqual(loaded_convo.conversation_id, self.dummy_conversation.conversation_id)

    def test_load_conversation_not_found(self):
        """Test loading a non-existent conversation raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_conversation("non_existent_convo")

    def test_load_conversation_corrupted_json(self):
        """Test loading a corrupted JSON file raises ConversationCorruptedError."""
        convo_name = "corrupted_convo"
        file_path = self.temp_dir_path / f"{convo_name}.json"
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': ") # Intentionally malformed JSON

        with self.assertRaisesRegex(ConversationCorruptedError, "corrupted (not valid JSON)"):
            self.manager.load_conversation(convo_name)

    def test_load_conversation_mismatched_structure(self):
        """Test loading JSON with mismatched structure raises ConversationCorruptedError."""
        convo_name = "mismatched_structure_convo"
        file_path = self.temp_dir_path / f"{convo_name}.json"
        malformed_data = {"some_other_key": "value_without_title_or_turns"} # Missing required fields for Conversation.from_dict
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data, f)

        # This relies on Conversation.from_dict raising an error (e.g. TypeError or KeyError)
        # if critical fields like 'title' or 'turns' are missing and not handled by defaults in from_dict.
        # The default for title in from_dict makes it more resilient.
        # Let's test a case where a turn is malformed.
        malformed_data_with_bad_turn = {
            "title": "Test",
            "turns": [{"not_a_prompt_object": "bad"}]
        }
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data_with_bad_turn, f)

        with self.assertRaisesRegex(ConversationCorruptedError, "Error deserializing conversation"):
             self.manager.load_conversation(convo_name)


    def test_list_conversations_empty(self):
        """Test list_conversations returns an empty list when no conversations exist."""
        self.assertEqual(self.manager.list_conversations(), [])

    def test_list_conversations_with_items(self):
        """Test list_conversations returns correct names after saving conversations."""
        names = ["convo_alpha", "convo_beta with space"]
        # Expected names after default sanitization by save_conversation
        sanitized_names = ["convo_alpha", "convo_beta_with_space"]

        for name in names:
            # Create a new Conversation instance for each save to avoid modifying the same object's LMT
            current_convo = Conversation(title=f"Title for {name}", turns=[self.turn1])
            self.manager.save_conversation(current_convo, name)

        listed_conversations = self.manager.list_conversations()
        # Sort both lists before comparing to ensure order doesn't affect test outcome
        self.assertCountEqual(listed_conversations, sanitized_names)
        self.assertEqual(sorted(listed_conversations), sorted(sanitized_names))


    def test_load_conversation_name_sanitization(self):
        """Test that load_conversation uses the same name sanitization as save_conversation."""
        original_name = "My Test Convo with Spaces & Chars!@#"
        self.manager.save_conversation(self.dummy_conversation, original_name)

        loaded_convo = self.manager.load_conversation(original_name) # Try loading with original name
        self.assertIsNotNone(loaded_convo)
        self.assertEqual(loaded_convo.title, self.dummy_conversation.title)

if __name__ == '__main__':
    unittest.main()
