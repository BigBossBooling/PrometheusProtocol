import unittest
import tempfile
import json
from pathlib import Path
import uuid # For generating test user_ids
from datetime import datetime, timezone # For checking timestamps
import time # For testing timestamp updates

from prometheus_protocol.core.user_settings_manager import UserSettingsManager
from prometheus_protocol.core.user_settings import UserSettings
from prometheus_protocol.core.exceptions import UserSettingsCorruptedError

class TestUserSettingsManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for settings files before each test."""
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir_path_str = str(self._temp_dir_obj.name) # UserSettingsManager takes str
        self.manager = UserSettingsManager(settings_base_dir=self.temp_dir_path_str)
        self.test_user_id = str(uuid.uuid4())

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

    def test_get_user_settings_filepath_valid_id(self):
        """Test _get_user_settings_filepath with a valid user_id."""
        expected_path = Path(self.temp_dir_path_str) / f"settings_{self.test_user_id}.json"
        self.assertEqual(self.manager._get_user_settings_filepath(self.test_user_id), expected_path)

    def test_get_user_settings_filepath_invalid_id(self):
        """Test _get_user_settings_filepath raises ValueError for invalid user_id."""
        with self.assertRaises(ValueError):
            self.manager._get_user_settings_filepath("") # Empty user_id
        with self.assertRaises(ValueError):
            self.manager._get_user_settings_filepath(None) # None user_id

    def test_save_settings_creates_file_and_returns_updated_settings(self):
        """Test save_settings creates a file with correct content and returns updated UserSettings."""
        settings_to_save = UserSettings(user_id=self.test_user_id, ui_theme="dark")
        original_lmt = settings_to_save.last_updated_at

        time.sleep(0.001) # Ensure time advances for LMT check

        returned_settings = self.manager.save_settings(settings_to_save)

        # Check returned object
        self.assertIsInstance(returned_settings, UserSettings)
        self.assertEqual(returned_settings.user_id, self.test_user_id)
        self.assertNotEqual(returned_settings.last_updated_at, original_lmt)
        self.assertEqual(returned_settings.ui_theme, "dark")
        # Also check original object was modified if it's the same instance
        self.assertEqual(settings_to_save.last_updated_at, returned_settings.last_updated_at)


        expected_file = self.manager._get_user_settings_filepath(self.test_user_id)
        self.assertTrue(expected_file.exists())

        with expected_file.open('r', encoding='utf-8') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["user_id"], self.test_user_id)
        self.assertEqual(saved_data["ui_theme"], "dark")
        self.assertEqual(saved_data["last_updated_at"], returned_settings.last_updated_at)
        self.assertAreTimestampsClose(saved_data["last_updated_at"], datetime.now(timezone.utc).isoformat())

    def test_save_settings_overwrites_existing(self):
        """Test that saving settings for an existing user overwrites the file."""
        # First save
        settings_v1 = UserSettings(user_id=self.test_user_id, ui_theme="light")
        self.manager.save_settings(settings_v1)

        # Second save with different data
        time.sleep(0.001)
        settings_v2 = UserSettings(user_id=self.test_user_id, ui_theme="dark", default_jules_model="model-x")
        original_lmt_v2 = settings_v2.last_updated_at # LMT before save

        returned_settings_v2 = self.manager.save_settings(settings_v2)

        self.assertEqual(returned_settings_v2.ui_theme, "dark")
        self.assertEqual(returned_settings_v2.default_jules_model, "model-x")
        self.assertNotEqual(returned_settings_v2.last_updated_at, original_lmt_v2)

        expected_file = self.manager._get_user_settings_filepath(self.test_user_id)
        with expected_file.open('r', encoding='utf-8') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["ui_theme"], "dark")
        self.assertEqual(saved_data["default_jules_model"], "model-x")
        self.assertEqual(saved_data["last_updated_at"], returned_settings_v2.last_updated_at)

    def test_save_settings_type_error(self):
        """Test save_settings raises TypeError for invalid input type."""
        with self.assertRaises(TypeError):
            self.manager.save_settings({"user_id": "fake"}) # Not a UserSettings instance

    def test_load_settings_success(self):
        """Test loading existing settings successfully."""
        settings_to_save = UserSettings(
            user_id=self.test_user_id,
            ui_theme="matrix",
            default_execution_settings={"temperature": 0.88}
        )
        self.manager.save_settings(settings_to_save) # Save it first

        loaded_settings = self.manager.load_settings(self.test_user_id)
        self.assertIsNotNone(loaded_settings)
        self.assertIsInstance(loaded_settings, UserSettings)
        self.assertEqual(loaded_settings.user_id, self.test_user_id)
        self.assertEqual(loaded_settings.ui_theme, "matrix")
        self.assertEqual(loaded_settings.default_execution_settings, {"temperature": 0.88})
        self.assertEqual(loaded_settings.last_updated_at, settings_to_save.last_updated_at) # LMT from saved file

    def test_load_settings_non_existent_user(self):
        """Test loading settings for a user_id with no file returns None."""
        loaded_settings = self.manager.load_settings("non_existent_user_id")
        self.assertIsNone(loaded_settings)

    def test_load_settings_corrupted_json(self):
        """Test loading a corrupted (invalid JSON) settings file raises UserSettingsCorruptedError."""
        file_path = self.manager._get_user_settings_filepath(self.test_user_id)
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': this_is_not_valid,}") # Malformed JSON

        with self.assertRaisesRegex(UserSettingsCorruptedError, "Corrupted settings file.*invalid JSON"):
            self.manager.load_settings(self.test_user_id)

    def test_load_settings_missing_userid_in_file_content(self):
        """Test loading a JSON file missing the user_id key raises UserSettingsCorruptedError."""
        file_path = self.manager._get_user_settings_filepath(self.test_user_id)
        # Valid JSON, but UserSettings.from_dict will raise ValueError as user_id is mandatory
        malformed_data = {"ui_theme": "test"}
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data, f)

        with self.assertRaisesRegex(UserSettingsCorruptedError, "Invalid data structure or missing required fields"):
            self.manager.load_settings(self.test_user_id)

    def test_load_settings_userid_mismatch_in_file(self):
        """Test loading a file where user_id in content mismatches filename's user_id."""
        file_path = self.manager._get_user_settings_filepath(self.test_user_id)
        mismatched_data = {
            "user_id": "another_user_id_in_content",
            "ui_theme": "test"
            # last_updated_at will be set by from_dict if not present
        }
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(mismatched_data, f)

        with self.assertRaisesRegex(UserSettingsCorruptedError, "User ID mismatch in settings file"):
            self.manager.load_settings(self.test_user_id)


if __name__ == '__main__':
    unittest.main()
