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
        self.assertIsNone(prompt.created_by_user_id, "Default created_by_user_id should be None")
        self.assertIsNone(prompt.settings, "Default settings should be None")

    def test_init_provided_metadata(self):
        """Test PromptObject initialization with provided metadata values."""
        custom_id = str(uuid.uuid4())
        custom_created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat() + 'Z'
        custom_modified_at = datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc).isoformat() + 'Z'
        custom_user_id = "user_test_123"
        sample_settings = {"temperature": 0.8, "max_tokens": 1000}

        prompt = PromptObject(
            role="Test Role", context="Test Context", task="Test Task",
            constraints=["C1"], examples=["E1"],
            prompt_id=custom_id,
            version=5,
            created_at=custom_created_at,
            last_modified_at=custom_modified_at,
            tags=["custom", "test"],
            created_by_user_id=custom_user_id,
            settings=sample_settings
        )

        self.assertEqual(prompt.prompt_id, custom_id)
        self.assertEqual(prompt.version, 5)
        self.assertEqual(prompt.created_at, custom_created_at)
        self.assertEqual(prompt.last_modified_at, custom_modified_at)
        self.assertEqual(prompt.tags, ["custom", "test"])
        self.assertEqual(prompt.created_by_user_id, custom_user_id, "created_by_user_id not set as provided")
        self.assertEqual(prompt.settings, sample_settings, "settings not set as provided")

    def test_to_dict_serialization(self):
        """Test the to_dict() method for correct serialization."""
        sample_settings_for_dict_test = {"temperature": 0.75}
        prompt = PromptObject(
            role="Serial Role", context="Serial Context", task="Serial Task",
            constraints=["SC1"], examples=["SE1"],
            version=2, tags=["serialization"],
            created_by_user_id="user_serializer_test",
            settings=sample_settings_for_dict_test
        )
        prompt_dict = prompt.to_dict()

        expected_keys = [
            "role", "context", "task", "constraints", "examples",
            "prompt_id", "version", "created_at", "last_modified_at", "tags",
            "created_by_user_id", "settings"
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
        self.assertEqual(prompt_dict["created_by_user_id"], "user_serializer_test")
        self.assertEqual(prompt_dict["settings"], sample_settings_for_dict_test)

    def test_to_dict_serialization_with_none_user_id(self):
        """Test to_dict() when created_by_user_id is None."""
        prompt = PromptObject(
            role="Test Role", context="Test Context", task="Test Task",
            constraints=[], examples=[],
            created_by_user_id=None
        )
        prompt_dict = prompt.to_dict()
        self.assertIsNone(prompt_dict["created_by_user_id"])
        self.assertIn("created_by_user_id", prompt_dict.keys())

    def test_to_dict_serialization_with_none_settings(self):
        """Test to_dict() when settings is None."""
        prompt = PromptObject(
            role="Test Role", context="Test Context", task="Test Task",
            constraints=[], examples=[],
            settings=None
        )
        prompt_dict = prompt.to_dict()
        self.assertIsNone(prompt_dict["settings"])
        self.assertIn("settings", prompt_dict.keys()) # Ensure key is still present

    def test_from_dict_deserialization(self):
        """Test the from_dict() class method for correct deserialization."""
        original_prompt = PromptObject(
            role="Original Role", context="Original Context", task="Original Task",
            constraints=["OC1"], examples=["OE1"], tags=["original"],
            created_by_user_id="user_deserial_test",
            settings={"temperature": 0.9, "max_tokens": 150}
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
        self.assertEqual(reconstructed_prompt.created_by_user_id, "user_deserial_test")
        self.assertEqual(reconstructed_prompt.settings, {"temperature": 0.9, "max_tokens": 150})

    def test_from_dict_deserialization_missing_or_none_user_id(self):
        """Test from_dict() when created_by_user_id is missing or None in data."""
        # Case 1: created_by_user_id is missing from data
        minimal_data_missing_user_id = {
            "role": "R", "context": "C", "task": "T",
            "constraints": [], "examples": [],
            "prompt_id": str(uuid.uuid4()), "version": 1,
            "created_at": "2023-01-01T00:00:00Z", "last_modified_at": "2023-01-01T00:00:00Z",
            "tags": []
        }
        prompt1 = PromptObject.from_dict(minimal_data_missing_user_id)
        self.assertIsNone(prompt1.created_by_user_id)

        # Case 2: created_by_user_id is explicitly None in data
        minimal_data_none_user_id = minimal_data_missing_user_id.copy()
        minimal_data_none_user_id["created_by_user_id"] = None
        prompt2 = PromptObject.from_dict(minimal_data_none_user_id)
        self.assertIsNone(prompt2.created_by_user_id)

    def test_from_dict_deserialization_missing_or_none_settings(self):
        """Test from_dict() when settings is missing or None in data."""
        # Case 1: settings is missing from data
        minimal_data_missing_settings = {
            "role": "R", "context": "C", "task": "T",
            "constraints": [], "examples": [],
            "prompt_id": str(uuid.uuid4()), "version": 1,
            "created_at": "2023-01-01T00:00:00Z", "last_modified_at": "2023-01-01T00:00:00Z",
            "tags": [], "created_by_user_id": None
            # settings field is omitted
        }
        prompt1 = PromptObject.from_dict(minimal_data_missing_settings)
        self.assertIsNone(prompt1.settings)

        # Case 2: settings is explicitly None in data
        minimal_data_none_settings = minimal_data_missing_settings.copy()
        minimal_data_none_settings["settings"] = None
        prompt2 = PromptObject.from_dict(minimal_data_none_settings)
        self.assertIsNone(prompt2.settings)

    def test_serialization_idempotency(self):
        """Test that serializing then deserializing results in an equivalent object dict."""
        prompt_with_user = PromptObject(
            role="Idempotent Role", context="Idempotent Context", task="Idempotent Task",
            constraints=["IC1"], examples=["IE1"], version=10, tags=["idempotency_check"],
            created_by_user_id="user_idem_test"
        )
        original_dict_with = prompt_with_user.to_dict()
        reconstructed_prompt_with = PromptObject.from_dict(original_dict_with)
        self.assertEqual(reconstructed_prompt_with.to_dict(), original_dict_with)

        prompt_without_user = PromptObject(
            role="Idempotent Role", context="Idempotent Context", task="Idempotent Task",
            constraints=["IC1"], examples=["IE1"], version=10, tags=["idempotency_check"],
            created_by_user_id=None # Explicitly None
        )
        original_dict_without = prompt_without_user.to_dict()
        reconstructed_prompt_without = PromptObject.from_dict(original_dict_without)
        self.assertEqual(reconstructed_prompt_without.to_dict(), original_dict_without)

        # Test with settings populated
        prompt_with_settings = PromptObject(
            role="Idempotent Role", context="Idempotent Context", task="Idempotent Task",
            constraints=["IC1"], examples=["IE1"], version=10, tags=["idempotency_check"],
            created_by_user_id="user_idem_test",
            settings={"temperature": 0.88}
        )
        original_dict_with_settings = prompt_with_settings.to_dict()
        reconstructed_prompt_with_settings = PromptObject.from_dict(original_dict_with_settings)
        self.assertEqual(reconstructed_prompt_with_settings.to_dict(), original_dict_with_settings)

        # Test with settings as None (covered by prompt_without_user if it has settings=None, or add another case)
        prompt_with_none_settings = PromptObject(
            role="Idempotent Role", context="Idempotent Context", task="Idempotent Task",
            constraints=["IC1"], examples=["IE1"], version=10, tags=["idempotency_check"],
            created_by_user_id=None,
            settings=None # Explicitly None
        )
        original_dict_none_settings = prompt_with_none_settings.to_dict()
        reconstructed_prompt_none_settings = PromptObject.from_dict(original_dict_none_settings)
        self.assertEqual(reconstructed_prompt_none_settings.to_dict(), original_dict_none_settings)

if __name__ == '__main__':
    unittest.main()
