import unittest
import tempfile
import json
from pathlib import Path
import shutil # For cleaning up if setUp fails before self.temp_dir is assigned
import time # For ensuring timestamp differences

from prometheus_protocol.core.template_manager import TemplateManager
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.exceptions import TemplateCorruptedError

class TestTemplateManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for templates before each test."""
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir_path_str = str(self._temp_dir_obj.name) # Use this for base path
        self.manager = TemplateManager(data_storage_base_path=self.temp_dir_path_str)

        self.personal_user_id = "user_personal_test"
        self.workspace_id_alpha = "ws_alpha_space"
        self.workspace_id_beta = "ws_beta_space" # For testing empty context

        # Create a base dummy prompt object for use in tests.
        # Its version will be set/updated by save_template.
        self.dummy_prompt_content = {
            "role": "Test Role",
            "context": "Test context for template",
            "task": "Test task",
            "constraints": ["Constraint A"],
            "examples": ["Example A"],
            "tags": ["test", "dummy"]
        }
        # Create a new PromptObject for each test that needs to save it,
        # to avoid state modification issues across tests (e.g. version, timestamps).
        self.dummy_prompt = PromptObject(**self.dummy_prompt_content)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self._temp_dir_obj.cleanup()

    def assertAreTimestampsClose(self, ts1_str, ts2_str, tolerance_seconds=1):
        """Asserts that two ISO 8601 timestamp strings are close to each other."""
        # PromptObject uses 'Z' suffix, ensure comparison handles this.
        ts1_str_parsed = ts1_str.replace('Z', '+00:00')
        ts2_str_parsed = ts2_str.replace('Z', '+00:00')
        dt1 = datetime.fromisoformat(ts1_str_parsed)
        dt2 = datetime.fromisoformat(ts2_str_parsed)
        self.assertAlmostEqual(dt1.timestamp(), dt2.timestamp(), delta=tolerance_seconds)

    # --- Tests for save_template ---
    def test_save_template_new_and_incrementing_versions(self):
        """Test saving a new template creates v1, and subsequent saves increment version."""
        template_name = "version_test"

        # Initial prompt object for saving - Personal Context
        prompt_to_save_user = PromptObject(**self.dummy_prompt_content)
        original_lmat_user = prompt_to_save_user.last_modified_at
        time.sleep(0.001)
        saved_prompt_v1_user = self.manager.save_template(prompt_to_save_user, template_name, context_id=self.personal_user_id)
        self.assertEqual(saved_prompt_v1_user.version, 1)
        self.assertNotEqual(saved_prompt_v1_user.last_modified_at, original_lmat_user)

        user_context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        expected_file_v1_user = user_context_path / self.manager._construct_filename(template_name, 1)
        self.assertTrue(expected_file_v1_user.exists())

        # Save V2 in Personal Context
        time.sleep(0.001)
        saved_prompt_v2_user = self.manager.save_template(saved_prompt_v1_user, template_name, context_id=self.personal_user_id)
        self.assertEqual(saved_prompt_v2_user.version, 2)
        expected_file_v2_user = user_context_path / self.manager._construct_filename(template_name, 2)
        self.assertTrue(expected_file_v2_user.exists())

        # Save V1 in Workspace Alpha Context (Same template name, different context)
        prompt_to_save_ws = PromptObject(**self.dummy_prompt_content, task="Workspace Task")
        original_lmat_ws = prompt_to_save_ws.last_modified_at
        time.sleep(0.001)
        saved_prompt_v1_ws = self.manager.save_template(prompt_to_save_ws, template_name, context_id=self.workspace_id_alpha)
        self.assertEqual(saved_prompt_v1_ws.version, 1) # Independent versioning for this context
        self.assertNotEqual(saved_prompt_v1_ws.last_modified_at, original_lmat_ws)

        ws_alpha_context_path = self.manager._get_context_specific_templates_path(self.workspace_id_alpha)
        expected_file_v1_ws = ws_alpha_context_path / self.manager._construct_filename(template_name, 1)
        self.assertTrue(expected_file_v1_ws.exists())
        with expected_file_v1_ws.open('r') as f:
            ws_data = json.load(f)
            self.assertEqual(ws_data['task'], "Workspace Task")

        # Save V2 in Workspace Alpha Context
        time.sleep(0.001)
        saved_prompt_v2_ws = self.manager.save_template(saved_prompt_v1_ws, template_name, context_id=self.workspace_id_alpha)
        self.assertEqual(saved_prompt_v2_ws.version, 2)
        expected_file_v2_ws = ws_alpha_context_path / self.manager._construct_filename(template_name, 2)
        self.assertTrue(expected_file_v2_ws.exists())

        # Save a template with a different name in Workspace Alpha
        ws_template_other_name = "ws_other_template"
        prompt_to_save_ws_other = PromptObject(**self.dummy_prompt_content, task="Other WS Task")
        self.manager.save_template(prompt_to_save_ws_other, ws_template_other_name, context_id=self.workspace_id_alpha)
        expected_file_ws_other = ws_alpha_context_path / self.manager._construct_filename(ws_template_other_name, 1)
        self.assertTrue(expected_file_ws_other.exists())


    def test_save_template_name_sanitization(self):
        """Test template name sanitization during save, creating versioned file in a context."""
        template_name = "My Test Template with Spaces & Chars!@#"
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_to_save, template_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        expected_file = context_path / "My_Test_Template_with_Spaces__Chars_v1.json"
        self.assertTrue(expected_file.exists(), f"Expected file {expected_file} not found.")

    def test_save_template_empty_name_raises_value_error(self):
        """Test save_template raises ValueError for empty or whitespace name (context does not matter)."""
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty or just whitespace."):
            self.manager.save_template(prompt_to_save, "", context_id=self.personal_user_id)
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty or just whitespace."):
            self.manager.save_template(prompt_to_save, "   ", context_id=self.personal_user_id)

    def test_save_template_name_sanitizes_to_empty_raises_value_error(self):
        """Test save_template raises ValueError if name sanitizes to empty (context does not matter)."""
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        with self.assertRaisesRegex(ValueError, "Template name '!@#\$' sanitized to an empty string"):
            self.manager.save_template(prompt_to_save, "!@#$", context_id=self.personal_user_id)

    # --- Tests for load_template ---
    def test_load_template_latest_version_with_context(self):
        """Test loading the latest version from a specific context."""
        template_name = "load_latest_ctx"
        # Personal context
        p_v1_user = self._create_prompt_for_test("User v1")
        self.manager.save_template(p_v1_user, template_name, context_id=self.personal_user_id)
        time.sleep(0.001)
        p_v2_user = self._create_prompt_for_test("User v2")
        self.manager.save_template(p_v2_user, template_name, context_id=self.personal_user_id)
        # Workspace context (same name, different content)
        p_v1_ws = self._create_prompt_for_test("WS v1")
        self.manager.save_template(p_v1_ws, template_name, context_id=self.workspace_id_alpha)

        loaded_user = self.manager.load_template(template_name, context_id=self.personal_user_id)
        self.assertEqual(loaded_user.version, 2)
        self.assertEqual(loaded_user.task, "User v2")

        loaded_ws = self.manager.load_template(template_name, context_id=self.workspace_id_alpha)
        self.assertEqual(loaded_ws.version, 1)
        self.assertEqual(loaded_ws.task, "WS v1")

    def test_load_template_specific_version_with_context(self):
        """Test loading a specific version of a template from a specific context."""
        template_name = "load_specific_ctx"
        self.manager.save_template(self._create_prompt_for_test("User v1"), template_name, context_id=self.personal_user_id)
        time.sleep(0.001)
        self.manager.save_template(self._create_prompt_for_test("User v2"), template_name, context_id=self.personal_user_id)

        loaded_v1 = self.manager.load_template(template_name, version=1, context_id=self.personal_user_id)
        self.assertEqual(loaded_v1.version, 1)
        self.assertEqual(loaded_v1.task, "User v1")

        loaded_v2 = self.manager.load_template(template_name, version=2, context_id=self.personal_user_id)
        self.assertEqual(loaded_v2.version, 2)
        self.assertEqual(loaded_v2.task, "User v2")

    def test_load_template_no_versions_found_in_context(self):
        """Test FileNotFoundError when no versions exist for a template name in a context."""
        with self.assertRaisesRegex(FileNotFoundError, f"No versions found for template 'non_existent_ctx' in context '{self.workspace_id_beta}'"):
            self.manager.load_template("non_existent_ctx", context_id=self.workspace_id_beta)

    def test_load_template_specific_version_not_found_in_context(self):
        template_name = "specific_version_missing_ctx"
        self.manager.save_template(self._create_prompt_for_test("v1"), template_name, context_id=self.personal_user_id)
        with self.assertRaisesRegex(FileNotFoundError, f"Version 99 for template '{template_name}' not found in context '{self.personal_user_id}'"):
            self.manager.load_template(template_name, version=99, context_id=self.personal_user_id)

    def test_load_template_corrupted_json_in_context(self):
        template_name = "corrupted_template_ctx"
        self.manager.save_template(self._create_prompt_for_test("v1"), template_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        file_path = context_path / self.manager._construct_filename(template_name, 1)
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': ")

        with self.assertRaisesRegex(TemplateCorruptedError, f"Template file {file_path} in context '{self.personal_user_id}' is corrupted"):
            self.manager.load_template(template_name, version=1, context_id=self.personal_user_id)

    def test_load_template_mismatched_structure_in_context(self):
        template_name = "mismatched_template_ctx"
        self.manager.save_template(self._create_prompt_for_test("v1"), template_name, context_id=self.personal_user_id)

        context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        file_path = context_path / self.manager._construct_filename(template_name, 1)
        malformed_data = {"some_other_key": "value"}
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data, f)

        with self.assertRaisesRegex(TemplateCorruptedError, f"Error deserializing template {file_path} in context '{self.personal_user_id}'"):
             self.manager.load_template(template_name, version=1, context_id=self.personal_user_id)

    def test_load_template_name_sanitization_with_context(self):
        original_name = "My Context Load Test with Spaces & Chars!@#"
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_to_save, original_name, context_id=self.workspace_id_alpha)

        loaded_prompt = self.manager.load_template(original_name, context_id=self.workspace_id_alpha)
        self.assertIsNotNone(loaded_prompt)
        self.assertEqual(loaded_prompt.version, 1)

    # --- Tests for list_templates ---
    def test_list_templates_empty_directory_with_context(self):
        """Test list_templates returns an empty dict for an empty context directory."""
        self.assertEqual(self.manager.list_templates(context_id=self.workspace_id_beta), {})

    def test_list_templates_versioned_with_contexts(self):
        """Test list_templates correctly lists for different contexts."""
        # Personal context
        self.manager.save_template(self._create_prompt_for_test("User A1"), "templateA", context_id=self.personal_user_id)
        time.sleep(0.001)
        self.manager.save_template(self._create_prompt_for_test("User A2"), "templateA", context_id=self.personal_user_id)
        self.manager.save_template(self._create_prompt_for_test("User B1"), "templateB", context_id=self.personal_user_id)

        # Workspace Alpha context
        self.manager.save_template(self._create_prompt_for_test("WS_A A1"), "templateA", context_id=self.workspace_id_alpha)
        self.manager.save_template(self._create_prompt_for_test("WS_C C1"), "templateC", context_id=self.workspace_id_alpha)

        expected_user = {"templateA": [1, 2], "templateB": [1]}
        self.assertEqual(self.manager.list_templates(context_id=self.personal_user_id), expected_user)

        expected_ws_alpha = {"templateA": [1], "templateC": [1]}
        self.assertEqual(self.manager.list_templates(context_id=self.workspace_id_alpha), expected_ws_alpha)

        # Workspace Beta context (should be empty)
        self.assertEqual(self.manager.list_templates(context_id=self.workspace_id_beta), {})

        # Default context (None) should map to the default user personal space
        default_context_path = Path(self.temp_dir_path_str) / "user_personal_spaces" / "default_user_prompts" / "templates"
        default_context_path.mkdir(parents=True, exist_ok=True) # Ensure it exists for the test
        self.manager.save_template(self._create_prompt_for_test("Default D1"), "templateD", context_id=None)
        expected_default = {"templateD": [1]}
        self.assertEqual(self.manager.list_templates(context_id=None), expected_default)


    def test_list_templates_ignores_non_matching_files_in_context(self):
        """Test list_templates ignores non-matching files in a specific context."""
        context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        self.manager.save_template(self._create_prompt_for_test("Valid"), "valid_template", context_id=self.personal_user_id)

        (context_path / "non_versioned.json").touch()
        (context_path / "valid_template_vx.json").touch()
        (context_path / "another_v1.txt").touch()

        expected = {"valid_template": [1]}
        self.assertEqual(self.manager.list_templates(context_id=self.personal_user_id), expected)

    # --- Helper for delete tests ---
    # _create_prompt_for_test is already defined above

    # --- Tests for Delete Methods ---

    def test_delete_template_version_success_with_context(self):
        template_name = "delete_version_ctx_test"
        sanitized_name = self.manager._sanitize_base_name(template_name)

        self.manager.save_template(self._create_prompt_for_test("v1 user"), template_name, context_id=self.personal_user_id)
        self.manager.save_template(self._create_prompt_for_test("v2 user"), template_name, context_id=self.personal_user_id)
        self.manager.save_template(self._create_prompt_for_test("v1 ws"), template_name, context_id=self.workspace_id_alpha)

        user_context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        file_v1_user = user_context_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1_user.exists())

        delete_result = self.manager.delete_template_version(template_name, 1, context_id=self.personal_user_id)
        self.assertTrue(delete_result)
        self.assertFalse(file_v1_user.exists())

        file_v2_user = user_context_path / self.manager._construct_filename(sanitized_name, 2)
        self.assertTrue(file_v2_user.exists()) # v2 in user context should still exist

        ws_alpha_context_path = self.manager._get_context_specific_templates_path(self.workspace_id_alpha)
        file_v1_ws = ws_alpha_context_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1_ws.exists()) # v1 in workspace context should still exist

        listed_user = self.manager.list_templates(context_id=self.personal_user_id)
        self.assertEqual(listed_user.get(sanitized_name), [2])
        listed_ws = self.manager.list_templates(context_id=self.workspace_id_alpha)
        self.assertEqual(listed_ws.get(sanitized_name), [1])


    def test_delete_template_version_non_existent_version_with_context(self):
        template_name = "delete_non_existent_version_ctx"
        self.manager.save_template(self._create_prompt_for_test("v1"), template_name, context_id=self.personal_user_id)
        delete_result = self.manager.delete_template_version(template_name, 5, context_id=self.personal_user_id)
        self.assertFalse(delete_result)

    def test_delete_template_version_non_existent_template_name_with_context(self):
        delete_result = self.manager.delete_template_version("no_such_ctx", 1, context_id=self.personal_user_id)
        self.assertFalse(delete_result)

    def test_delete_template_all_versions_success_with_context(self):
        template_name = "delete_all_ctx_test"
        sanitized_name = self.manager._sanitize_base_name(template_name)

        # User personal context
        self.manager.save_template(self._create_prompt_for_test("v1 user"), template_name, context_id=self.personal_user_id)
        self.manager.save_template(self._create_prompt_for_test("v2 user"), template_name, context_id=self.personal_user_id)
        # Workspace Alpha context (same template name)
        self.manager.save_template(self._create_prompt_for_test("v1 ws_alpha"), template_name, context_id=self.workspace_id_alpha)
        # Workspace Alpha context (different template name)
        other_template_ws_alpha = "other_ws_alpha_template"
        sanitized_other_ws_alpha = self.manager._sanitize_base_name(other_template_ws_alpha)
        self.manager.save_template(self._create_prompt_for_test("other content"), other_template_ws_alpha, context_id=self.workspace_id_alpha)

        deleted_count_user = self.manager.delete_template_all_versions(template_name, context_id=self.personal_user_id)
        self.assertEqual(deleted_count_user, 2)

        user_context_path = self.manager._get_context_specific_templates_path(self.personal_user_id)
        self.assertFalse((user_context_path / self.manager._construct_filename(sanitized_name, 1)).exists())
        self.assertFalse((user_context_path / self.manager._construct_filename(sanitized_name, 2)).exists())

        listed_user = self.manager.list_templates(context_id=self.personal_user_id)
        self.assertNotIn(sanitized_name, listed_user)

        # Check workspace alpha context is untouched for 'template_name' and 'other_template_ws_alpha'
        ws_alpha_context_path = self.manager._get_context_specific_templates_path(self.workspace_id_alpha)
        self.assertTrue((ws_alpha_context_path / self.manager._construct_filename(sanitized_name, 1)).exists())
        self.assertTrue((ws_alpha_context_path / self.manager._construct_filename(sanitized_other_ws_alpha, 1)).exists())
        listed_ws_alpha = self.manager.list_templates(context_id=self.workspace_id_alpha)
        self.assertIn(sanitized_name, listed_ws_alpha)
        self.assertIn(sanitized_other_ws_alpha, listed_ws_alpha)


    def test_delete_template_all_versions_non_existent_template_name_with_context(self):
        deleted_count = self.manager.delete_template_all_versions("no_such_all_delete_ctx", context_id=self.personal_user_id)
        self.assertEqual(deleted_count, 0)


if __name__ == '__main__':
    unittest.main()
