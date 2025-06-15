import unittest
import uuid # For generating test user_ids
from datetime import datetime, timezone
import time # For testing timestamp updates

from prometheus_protocol.core.user_settings import UserSettings

class TestUserSettings(unittest.TestCase):

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=2):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        ts1_str_parsed = ts1_str.replace('Z', '+00:00') if 'Z' in ts1_str else ts1_str
        ts2_str_parsed = ts2_str.replace('Z', '+00:00') if 'Z' in ts2_str else ts2_str
        dt1 = datetime.fromisoformat(ts1_str_parsed)
        dt2 = datetime.fromisoformat(ts2_str_parsed)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    def test_initialization_minimal(self):
        """Test UserSettings initialization with only user_id."""
        user_id = str(uuid.uuid4())
        settings = UserSettings(user_id=user_id)

        self.assertEqual(settings.user_id, user_id)
        self.assertIsNone(settings.default_jules_api_key)
        self.assertIsNone(settings.default_jules_model)
        self.assertEqual(settings.default_execution_settings, {}) # default_factory=dict
        self.assertIsNone(settings.ui_theme)
        self.assertIsNone(settings.preferred_output_language)
        self.assertEqual(settings.creative_catalyst_defaults, {}) # default_factory=dict
        self.assertIsNotNone(settings.last_updated_at)
        # Check timestamp is recent
        now_utc_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.assertAreTimestampsClose(settings.last_updated_at, now_utc_iso)

    def test_initialization_with_all_values(self):
        """Test UserSettings initialization with all fields provided."""
        user_id = str(uuid.uuid4())
        api_key = "test_key_123"
        model = "jules-xl-test"
        exec_settings = {"temperature": 0.9, "max_tokens": 700}
        theme = "dark"
        lang = "en-GB"
        catalyst_prefs = {"RolePersonaGenerator_creativity": "adventurous"}
        # Specific timestamp to test it's used if provided (though from_dict is more common for this)
        # For direct instantiation, last_updated_at will usually be auto-set by default_factory
        # So, we'll primarily test that it's set, and from_dict will test explicit setting.

        settings = UserSettings(
            user_id=user_id,
            default_jules_api_key=api_key,
            default_jules_model=model,
            default_execution_settings=exec_settings,
            ui_theme=theme,
            preferred_output_language=lang,
            creative_catalyst_defaults=catalyst_prefs
            # last_updated_at will be auto-set here
        )

        self.assertEqual(settings.user_id, user_id)
        self.assertEqual(settings.default_jules_api_key, api_key)
        self.assertEqual(settings.default_jules_model, model)
        self.assertEqual(settings.default_execution_settings, exec_settings)
        self.assertEqual(settings.ui_theme, theme)
        self.assertEqual(settings.preferred_output_language, lang)
        self.assertEqual(settings.creative_catalyst_defaults, catalyst_prefs)
        self.assertIsNotNone(settings.last_updated_at)


    def test_to_dict_serialization(self):
        """Test UserSettings serialization to dictionary."""
        user_id = str(uuid.uuid4())
        exec_settings = {"temperature": 0.5}
        catalyst_prefs = {"SomeModule_setting": "value"}

        settings = UserSettings(
            user_id=user_id,
            default_execution_settings=exec_settings,
            creative_catalyst_defaults=catalyst_prefs,
            ui_theme="light"
        )
        settings_dict = settings.to_dict()

        expected_keys = [
            "user_id", "default_jules_api_key", "default_jules_model",
            "default_execution_settings", "ui_theme", "preferred_output_language",
            "creative_catalyst_defaults", "last_updated_at"
        ]
        self.assertCountEqual(settings_dict.keys(), expected_keys) # Checks all keys are present

        self.assertEqual(settings_dict["user_id"], user_id)
        self.assertIsNone(settings_dict["default_jules_api_key"]) # Was not set
        self.assertEqual(settings_dict["default_execution_settings"], exec_settings)
        self.assertEqual(settings_dict["creative_catalyst_defaults"], catalyst_prefs)
        self.assertEqual(settings_dict["ui_theme"], "light")
        self.assertEqual(settings_dict["last_updated_at"], settings.last_updated_at)


    def test_from_dict_deserialization_full(self):
        """Test UserSettings deserialization from a full dictionary."""
        user_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        settings_data = {
            "user_id": user_id,
            "default_jules_api_key": "key_from_dict",
            "default_jules_model": "model_from_dict",
            "default_execution_settings": {"max_tokens": 200},
            "ui_theme": "dark_from_dict",
            "preferred_output_language": "de-DE",
            "creative_catalyst_defaults": {"TestModule_creativity": "low"},
            "last_updated_at": now_iso
        }
        settings = UserSettings.from_dict(settings_data)

        self.assertEqual(settings.user_id, user_id)
        self.assertEqual(settings.default_jules_api_key, "key_from_dict")
        self.assertEqual(settings.default_jules_model, "model_from_dict")
        self.assertEqual(settings.default_execution_settings, {"max_tokens": 200})
        self.assertEqual(settings.ui_theme, "dark_from_dict")
        self.assertEqual(settings.preferred_output_language, "de-DE")
        self.assertEqual(settings.creative_catalyst_defaults, {"TestModule_creativity": "low"})
        self.assertEqual(settings.last_updated_at, now_iso)

    def test_from_dict_deserialization_minimal(self):
        """Test UserSettings deserialization with minimal data (only user_id)."""
        user_id = str(uuid.uuid4())
        settings_data = {"user_id": user_id} # last_updated_at will be auto-set by from_dict

        settings = UserSettings.from_dict(settings_data)
        self.assertEqual(settings.user_id, user_id)
        self.assertIsNone(settings.default_jules_api_key)
        self.assertEqual(settings.default_execution_settings, {}) # Defaults to empty dict
        self.assertEqual(settings.creative_catalyst_defaults, {}) # Defaults to empty dict
        self.assertIsNotNone(settings.last_updated_at) # Should be set by from_dict's default

    def test_from_dict_missing_user_id_raises_error(self):
        """Test from_dict raises ValueError if user_id is missing."""
        settings_data = {"default_jules_api_key": "some_key"}
        with self.assertRaisesRegex(ValueError, "'user_id' is a required field"):
            UserSettings.from_dict(settings_data)

    def test_serialization_idempotency(self):
        """Test UserSettings to_dict -> from_dict results in an equivalent object dict."""
        user_id = str(uuid.uuid4())
        # Case 1: More fields populated
        settings1 = UserSettings(
            user_id=user_id,
            default_jules_model="model1",
            default_execution_settings={"temperature": 0.1},
            ui_theme="os_default"
        )
        dict1 = settings1.to_dict()
        reconstructed1 = UserSettings.from_dict(dict1)
        self.assertEqual(reconstructed1.to_dict(), dict1)

        # Case 2: Minimal fields (user_id only, others default)
        # Need to capture the auto-generated last_updated_at for fair comparison
        settings2_initial = UserSettings(user_id=str(uuid.uuid4()))
        dict2_initial_with_auto_ts = settings2_initial.to_dict() # This captures the auto TS

        reconstructed2 = UserSettings.from_dict(dict2_initial_with_auto_ts)
        self.assertEqual(reconstructed2.to_dict(), dict2_initial_with_auto_ts)


    def test_touch_method_updates_timestamp(self):
        """Test that touch() method updates last_updated_at."""
        user_id = str(uuid.uuid4())
        settings = UserSettings(user_id=user_id)
        original_lmt = settings.last_updated_at

        time.sleep(0.001) # Ensure time advances enough for typical timestamp precision
        settings.touch()

        self.assertNotEqual(settings.last_updated_at, original_lmt)
        now_utc_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.assertAreTimestampsClose(settings.last_updated_at, now_utc_iso)

if __name__ == '__main__':
    unittest.main()
