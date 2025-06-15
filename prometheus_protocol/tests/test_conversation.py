import unittest
import uuid
from datetime import datetime, timezone # For timestamp comparisons
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.conversation import PromptTurn, Conversation

class TestPromptTurn(unittest.TestCase):

    def setUp(self):
        self.prompt_obj_data = {
            "role": "Test Role", "context": "Test Context", "task": "Test Task",
            "constraints": ["C1"], "examples": ["E1"]
        }
        self.prompt_obj = PromptObject(**self.prompt_obj_data)

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=2):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        # Handle 'Z' for UTC if Python version is older
        ts1_str_parsed = ts1_str.replace('Z', '+00:00') if 'Z' in ts1_str else ts1_str
        ts2_str_parsed = ts2_str.replace('Z', '+00:00') if 'Z' in ts2_str else ts2_str
        dt1 = datetime.fromisoformat(ts1_str_parsed)
        dt2 = datetime.fromisoformat(ts2_str_parsed)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    def test_prompt_turn_initialization_defaults(self):
        """Test PromptTurn initialization with default values."""
        turn = PromptTurn(prompt_object=self.prompt_obj)
        self.assertIsInstance(uuid.UUID(turn.turn_id), uuid.UUID) # Check valid UUID
        self.assertIsNone(turn.parent_turn_id)
        self.assertIsNone(turn.conditions)
        self.assertIsNone(turn.notes)
        self.assertEqual(turn.prompt_object, self.prompt_obj)

    def test_prompt_turn_initialization_with_values(self):
        """Test PromptTurn initialization with provided values."""
        custom_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        conditions = {"key": "value"}
        notes = "Test notes"
        turn = PromptTurn(
            turn_id=custom_id,
            prompt_object=self.prompt_obj,
            parent_turn_id=parent_id,
            conditions=conditions,
            notes=notes
        )
        self.assertEqual(turn.turn_id, custom_id)
        self.assertEqual(turn.parent_turn_id, parent_id)
        self.assertEqual(turn.conditions, conditions)
        self.assertEqual(turn.notes, notes)

    def test_prompt_turn_to_dict(self):
        """Test PromptTurn serialization to dictionary."""
        turn = PromptTurn(prompt_object=self.prompt_obj, notes="Serialization test")
        turn_dict = turn.to_dict()

        self.assertEqual(turn_dict["turn_id"], turn.turn_id)
        self.assertEqual(turn_dict["notes"], "Serialization test")
        self.assertIsInstance(turn_dict["prompt_object"], dict)
        self.assertEqual(turn_dict["prompt_object"]["role"], self.prompt_obj.role)

    def test_prompt_turn_from_dict(self):
        """Test PromptTurn deserialization from dictionary."""
        turn_data = {
            "turn_id": str(uuid.uuid4()),
            "prompt_object": self.prompt_obj.to_dict(),
            "parent_turn_id": str(uuid.uuid4()),
            "conditions": {"condition": True},
            "notes": "Deserialized notes"
        }
        turn = PromptTurn.from_dict(turn_data)
        self.assertEqual(turn.turn_id, turn_data["turn_id"])
        self.assertEqual(turn.notes, "Deserialized notes")
        self.assertIsInstance(turn.prompt_object, PromptObject)
        self.assertEqual(turn.prompt_object.role, self.prompt_obj.role)
        self.assertEqual(turn.parent_turn_id, turn_data["parent_turn_id"])

    def test_prompt_turn_from_dict_missing_prompt_object(self):
        """Test PromptTurn from_dict raises ValueError if prompt_object is missing."""
        turn_data = {"turn_id": str(uuid.uuid4()), "notes": "Test"}
        with self.assertRaisesRegex(ValueError, "Missing 'prompt_object' data"):
            PromptTurn.from_dict(turn_data)

    def test_prompt_turn_serialization_idempotency(self):
        """Test PromptTurn to_dict -> from_dict results in an equivalent object."""
        original_turn = PromptTurn(prompt_object=self.prompt_obj, notes="Idempotency")
        turn_dict = original_turn.to_dict()
        reconstructed_turn = PromptTurn.from_dict(turn_dict)
        self.assertEqual(reconstructed_turn.to_dict(), turn_dict)


class TestConversation(unittest.TestCase):

    def setUp(self):
        self.prompt_obj1 = PromptObject(role="Role1", context="Ctx1", task="Task1", constraints=[], examples=[])
        self.prompt_obj2 = PromptObject(role="Role2", context="Ctx2", task="Task2", constraints=[], examples=[])
        self.turn1 = PromptTurn(prompt_object=self.prompt_obj1, notes="Turn 1 notes")
        self.turn2 = PromptTurn(prompt_object=self.prompt_obj2, notes="Turn 2 notes", parent_turn_id=self.turn1.turn_id)

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=2):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        ts1_str_parsed = ts1_str.replace('Z', '+00:00') if 'Z' in ts1_str else ts1_str
        ts2_str_parsed = ts2_str.replace('Z', '+00:00') if 'Z' in ts2_str else ts2_str
        dt1 = datetime.fromisoformat(ts1_str_parsed)
        dt2 = datetime.fromisoformat(ts2_str_parsed)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    def test_conversation_initialization_defaults(self):
        """Test Conversation initialization with default values."""
        convo = Conversation(title="Test Convo")
        self.assertIsInstance(uuid.UUID(convo.conversation_id), uuid.UUID)
        self.assertEqual(convo.title, "Test Convo")
        self.assertIsNone(convo.description)
        self.assertEqual(convo.turns, [])
        self.assertIsNotNone(convo.created_at)
        self.assertIsNotNone(convo.last_modified_at)
        self.assertAreTimestampsClose(convo.created_at, convo.last_modified_at)
        # Check created_at is close to now
        now_utc_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.assertAreTimestampsClose(convo.created_at, now_utc_iso)
        self.assertEqual(convo.tags, [])
        self.assertEqual(convo.version, 1, "Default version should be 1")

    def test_conversation_initialization_with_values(self):
        """Test Conversation initialization with provided values."""
        custom_id = str(uuid.uuid4())
        created = datetime(2023,1,1,10,0,0, tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
        modified = datetime(2023,1,1,11,0,0, tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')

        convo = Conversation(
            conversation_id=custom_id,
            title="Full Convo",
            version=5,
            description="A detailed test conversation.",
            turns=[self.turn1, self.turn2],
            created_at=created,
            last_modified_at=modified,
            tags=["test", "full"]
        )
        self.assertEqual(convo.conversation_id, custom_id)
        self.assertEqual(convo.title, "Full Convo")
        self.assertEqual(convo.version, 5, "Version not set as provided")
        self.assertEqual(convo.description, "A detailed test conversation.")
        self.assertEqual(len(convo.turns), 2)
        self.assertEqual(convo.turns[0].notes, "Turn 1 notes")
        self.assertEqual(convo.created_at, created)
        self.assertEqual(convo.last_modified_at, modified)
        self.assertEqual(convo.tags, ["test", "full"])

    def test_conversation_to_dict(self):
        """Test Conversation serialization to dictionary."""
        convo = Conversation(title="Dict Convo", turns=[self.turn1], version=3)
        convo_dict = convo.to_dict()

        self.assertEqual(convo_dict["conversation_id"], convo.conversation_id)
        self.assertEqual(convo_dict["version"], convo.version)
        self.assertEqual(convo_dict["title"], "Dict Convo")
        self.assertEqual(len(convo_dict["turns"]), 1)
        self.assertEqual(convo_dict["turns"][0]["notes"], self.turn1.notes)
        self.assertEqual(convo_dict["tags"], []) # Default empty list

    def test_conversation_from_dict(self):
        """Test Conversation deserialization from dictionary."""
        convo_data = {
            "conversation_id": str(uuid.uuid4()),
            "title": "Loaded Convo",
            "description": "Loaded from dict.",
            "turns": [self.turn1.to_dict(), self.turn2.to_dict()],
            "version": 10,
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "last_modified_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "tags": ["loaded"]
        }
        convo = Conversation.from_dict(convo_data)
        self.assertEqual(convo.title, "Loaded Convo")
        self.assertEqual(len(convo.turns), 2)
        self.assertIsInstance(convo.turns[0], PromptTurn)
        self.assertEqual(convo.turns[0].notes, self.turn1.notes)
        self.assertEqual(convo.tags, ["loaded"])
        self.assertEqual(convo.version, 10)

    def test_conversation_from_dict_defaults(self):
        """Test Conversation from_dict with missing optional fields."""
        minimal_data = {
            "conversation_id": str(uuid.uuid4()),
            # title is missing, should default in from_dict
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "last_modified_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        convo = Conversation.from_dict(minimal_data)
        self.assertEqual(convo.title, "Untitled Conversation") # Default from from_dict
        self.assertEqual(convo.description, None)
        self.assertEqual(convo.turns, [])
        self.assertEqual(convo.tags, [])
        self.assertEqual(convo.version, 1) # Add this for missing version in data


    def test_conversation_serialization_idempotency(self):
        """Test Conversation to_dict -> from_dict results in an equivalent object dict."""
        original_convo_v_explicit = Conversation(title="Idempotent Convo Explicit Version", turns=[self.turn1], tags=["idem_explicit"], version=7)
        dict_v_explicit = original_convo_v_explicit.to_dict()
        reconstructed_v_explicit = Conversation.from_dict(dict_v_explicit)
        self.assertEqual(reconstructed_v_explicit.to_dict(), dict_v_explicit)

        # Test with default version (implicitly 1)
        original_convo_v_default = Conversation(title="Idempotent Convo Default Version", turns=[self.turn2], tags=["idem_default"])
        # version will be 1 by default
        dict_v_default = original_convo_v_default.to_dict()
        reconstructed_v_default = Conversation.from_dict(dict_v_default)
        self.assertEqual(reconstructed_v_default.to_dict(), dict_v_default)
        self.assertEqual(reconstructed_v_default.version, 1)

    def test_conversation_touch_method(self):
        """Test that touch() method updates last_modified_at."""
        convo = Conversation(title="Timestamp Test")
        original_lmt = convo.last_modified_at
        # Ensure some time passes; direct time mocking is more robust but complex for this stage
        # For now, a small sleep or just calling it should usually result in a different microsecond at least
        import time
        time.sleep(0.001) # Small delay
        convo.touch()
        self.assertNotEqual(convo.last_modified_at, original_lmt)
        self.assertAreTimestampsClose(convo.last_modified_at, datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


if __name__ == '__main__':
    unittest.main()
