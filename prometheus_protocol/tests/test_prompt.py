import unittest
import uuid
from datetime import datetime, timezone
from prometheus_protocol.core.prompt import PromptObject

class TestPromptObject(unittest.TestCase):

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=1):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        # Python < 3.11 doesn't like 'Z' for UTC in fromisoformat
        ts1_str = ts1_str.replace('Z', '+00:00')
        ts2_str = ts2_str.replace('Z', '+00:00')
        dt1 = datetime.fromisoformat(ts1_str)
        dt2 = datetime.fromisoformat(ts2_str)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    def test_init_default_metadata(self):
        """Test PromptObject initialization with default metadata values."""
        prompt = PromptObject(role="Test Role", context="Test Context", task="Test Task",
                              constraints=["C1"], examples=["E1"])

        self.assertIsNotNone(prompt.prompt_id)
        try:
            uuid.UUID(prompt.prompt_id) # Check if it's a valid UUID
        except ValueError:
            self.fail("Default prompt_id is not a valid UUID.")

        self.assertEqual(prompt.version, 1)
        self.assertIsNotNone(prompt.created_at)
        self.assertIsNotNone(prompt.last_modified_at)
        self.assertAreTimestampsClose(prompt.created_at, prompt.last_modified_at)

        # Check created_at is close to now
        now_utc_iso = datetime.utcnow().isoformat() + 'Z'
        self.assertAreTimestampsClose(prompt.created_at, now_utc_iso)

        self.assertEqual(prompt.tags, [])

    def test_init_provided_metadata(self):
        """Test PromptObject initialization with provided metadata values."""
        custom_id = str(uuid.uuid4())
        custom_created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat() + 'Z'
        custom_modified_at = datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc).isoformat() + 'Z'

        prompt = PromptObject(
            role="Test Role", context="Test Context", task="Test Task",
            constraints=["C1"], examples=["E1"],
            prompt_id=custom_id,
            version=5,
            created_at=custom_created_at,
            last_modified_at=custom_modified_at,
            tags=["custom", "test"]
        )

        self.assertEqual(prompt.prompt_id, custom_id)
        self.assertEqual(prompt.version, 5)
        self.assertEqual(prompt.created_at, custom_created_at)
        self.assertEqual(prompt.last_modified_at, custom_modified_at)
        self.assertEqual(prompt.tags, ["custom", "test"])

    def test_to_dict_serialization(self):
        """Test the to_dict() method for correct serialization."""
        prompt = PromptObject(
            role="Serial Role", context="Serial Context", task="Serial Task",
            constraints=["SC1"], examples=["SE1"],
            version=2, tags=["serialization"]
        )
        prompt_dict = prompt.to_dict()

        expected_keys = [
            "role", "context", "task", "constraints", "examples",
            "prompt_id", "version", "created_at", "last_modified_at", "tags"
        ]
        self.assertCountEqual(prompt_dict.keys(), expected_keys) # Checks all keys are present

        self.assertEqual(prompt_dict["role"], "Serial Role")
        self.assertEqual(prompt_dict["context"], "Serial Context")
        self.assertEqual(prompt_dict["task"], "Serial Task")
        self.assertEqual(prompt_dict["constraints"], ["SC1"])
        self.assertEqual(prompt_dict["examples"], ["SE1"])
        self.assertEqual(prompt_dict["prompt_id"], prompt.prompt_id)
        self.assertEqual(prompt_dict["version"], 2)
        self.assertEqual(prompt_dict["created_at"], prompt.created_at)
        self.assertEqual(prompt_dict["last_modified_at"], prompt.last_modified_at)
        self.assertEqual(prompt_dict["tags"], ["serialization"])

    def test_from_dict_deserialization(self):
        """Test the from_dict() class method for correct deserialization."""
        original_prompt = PromptObject(
            role="Original Role", context="Original Context", task="Original Task",
            constraints=["OC1"], examples=["OE1"], tags=["original"]
        )
        prompt_data = original_prompt.to_dict()

        reconstructed_prompt = PromptObject.from_dict(prompt_data)

        self.assertIsInstance(reconstructed_prompt, PromptObject)
        self.assertEqual(reconstructed_prompt.role, original_prompt.role)
        self.assertEqual(reconstructed_prompt.context, original_prompt.context)
        self.assertEqual(reconstructed_prompt.task, original_prompt.task)
        self.assertEqual(reconstructed_prompt.constraints, original_prompt.constraints)
        self.assertEqual(reconstructed_prompt.examples, original_prompt.examples)
        self.assertEqual(reconstructed_prompt.prompt_id, original_prompt.prompt_id)
        self.assertEqual(reconstructed_prompt.version, original_prompt.version)
        self.assertEqual(reconstructed_prompt.created_at, original_prompt.created_at)
        self.assertEqual(reconstructed_prompt.last_modified_at, original_prompt.last_modified_at)
        self.assertEqual(reconstructed_prompt.tags, original_prompt.tags)

    def test_serialization_idempotency(self):
        """Test that serializing then deserializing results in an equivalent object dict."""
        prompt = PromptObject(
            role="Idempotent Role", context="Idempotent Context", task="Idempotent Task",
            constraints=["IC1"], examples=["IE1"], version=10, tags=["idempotency_check"]
        )

        # Get the dictionary representation of the original prompt
        original_dict = prompt.to_dict()

        # Create a new prompt object from this dictionary
        reconstructed_prompt = PromptObject.from_dict(original_dict)

        # Get the dictionary representation of the reconstructed prompt
        reconstructed_dict = reconstructed_prompt.to_dict()

        # Compare the two dictionaries
        self.assertEqual(original_dict, reconstructed_dict)

if __name__ == '__main__':
    unittest.main()
