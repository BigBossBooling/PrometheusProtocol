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
        self.temp_dir_path = Path(self._temp_dir_obj.name)
        self.manager = TemplateManager(templates_dir=str(self.temp_dir_path))

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

        # Initial prompt object for saving
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        original_lmat = prompt_to_save.last_modified_at
        time.sleep(0.001) # ensure time progresses for LMAT check

        # Save V1
        saved_prompt_v1 = self.manager.save_template(prompt_to_save, template_name)
        self.assertEqual(saved_prompt_v1.version, 1, "Version should be 1 for the first save.")
        self.assertEqual(prompt_to_save.version, 1, "Original prompt object version should be updated to 1.")
        self.assertNotEqual(saved_prompt_v1.last_modified_at, original_lmat, "LMAT should update on save V1.")

        expected_file_v1 = self.temp_dir_path / "version_test_v1.json"
        self.assertTrue(expected_file_v1.exists(), "Version 1 file was not created.")
        with expected_file_v1.open('r', encoding='utf-8') as f:
            data_v1 = json.load(f)
        self.assertEqual(data_v1['version'], 1)
        self.assertEqual(data_v1['prompt_id'], saved_prompt_v1.prompt_id)
        self.assertEqual(data_v1['last_modified_at'], saved_prompt_v1.last_modified_at)

        # Save V2 (using the object returned and modified by the first save)
        time.sleep(0.001) # ensure time progresses
        original_lmat_v2 = saved_prompt_v1.last_modified_at

        saved_prompt_v2 = self.manager.save_template(saved_prompt_v1, template_name)
        self.assertEqual(saved_prompt_v2.version, 2, "Version should be 2 for the second save.")
        self.assertEqual(saved_prompt_v1.version, 2, "Original prompt object for V2 save should be updated to 2.")
        self.assertNotEqual(saved_prompt_v2.last_modified_at, original_lmat_v2, "LMAT should update on save V2.")

        expected_file_v2 = self.temp_dir_path / "version_test_v2.json"
        self.assertTrue(expected_file_v2.exists(), "Version 2 file was not created.")
        with expected_file_v2.open('r', encoding='utf-8') as f:
            data_v2 = json.load(f)
        self.assertEqual(data_v2['version'], 2)
        self.assertEqual(data_v2['prompt_id'], saved_prompt_v2.prompt_id) # ID should remain the same
        self.assertEqual(data_v2['last_modified_at'], saved_prompt_v2.last_modified_at)

        # Check that an independent save of a new prompt with same name also gets next version
        fresh_prompt = PromptObject(**self.dummy_prompt_content)
        saved_prompt_v3 = self.manager.save_template(fresh_prompt, template_name)
        self.assertEqual(saved_prompt_v3.version, 3)


    def test_save_template_name_sanitization(self):
        """Test template name sanitization during save, creating versioned file."""
        template_name = "My Test Template with Spaces & Chars!@#"
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_to_save, template_name)
        expected_file = self.temp_dir_path / "My_Test_Template_with_Spaces__Chars_v1.json"
        self.assertTrue(expected_file.exists(), f"Expected file {expected_file} not found.")

    def test_save_template_empty_name_raises_value_error(self):
        """Test save_template raises ValueError for empty or whitespace name."""
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty or just whitespace."):
            self.manager.save_template(prompt_to_save, "")
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty or just whitespace."):
            self.manager.save_template(prompt_to_save, "   ")

    def test_save_template_name_sanitizes_to_empty_raises_value_error(self):
        """Test save_template raises ValueError if name sanitizes to empty."""
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        with self.assertRaisesRegex(ValueError, "Template name '!@#\$' sanitized to an empty string"):
            self.manager.save_template(prompt_to_save, "!@#$")

    # --- Tests for load_template ---
    def test_load_template_latest_version(self):
        """Test loading the latest version when no specific version is requested."""
        template_name = "load_latest_test"
        prompt_v1 = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_v1, template_name) # Saves as v1
        time.sleep(0.001)
        prompt_v2 = PromptObject(**self.dummy_prompt_content, context="Context V2") # Make it different
        self.manager.save_template(prompt_v2, template_name) # Saves as v2
        time.sleep(0.001)
        prompt_v3 = PromptObject(**self.dummy_prompt_content, context="Context V3")
        self.manager.save_template(prompt_v3, template_name) # Saves as v3

        loaded_prompt = self.manager.load_template(template_name) # Should load v3
        self.assertEqual(loaded_prompt.version, 3)
        self.assertEqual(loaded_prompt.context, "Context V3")

    def test_load_template_specific_version(self):
        """Test loading a specific version of a template."""
        template_name = "load_specific_test"
        prompt_v1_orig = PromptObject(**self.dummy_prompt_content, context="Context V1")
        self.manager.save_template(prompt_v1_orig, template_name) # v1
        time.sleep(0.001)
        prompt_v2_orig = PromptObject(**self.dummy_prompt_content, context="Context V2")
        self.manager.save_template(prompt_v2_orig, template_name) # v2

        loaded_prompt_v1 = self.manager.load_template(template_name, version=1)
        self.assertEqual(loaded_prompt_v1.version, 1)
        self.assertEqual(loaded_prompt_v1.context, "Context V1")

        loaded_prompt_v2 = self.manager.load_template(template_name, version=2)
        self.assertEqual(loaded_prompt_v2.version, 2)
        self.assertEqual(loaded_prompt_v2.context, "Context V2")

    def test_load_template_no_versions_found(self):
        """Test FileNotFoundError when no versions exist for a template name."""
        with self.assertRaisesRegex(FileNotFoundError, "No versions found for template 'non_existent'"):
            self.manager.load_template("non_existent")

    def test_load_template_specific_version_not_found(self):
        """Test FileNotFoundError when a specific, non-existent version is requested."""
        template_name = "specific_version_missing"
        prompt_v1 = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_v1, template_name) # Save v1

        with self.assertRaisesRegex(FileNotFoundError, f"Version 99 for template '{template_name}' not found"):
            self.manager.load_template(template_name, version=99)

    def test_load_template_corrupted_json(self):
        """Test TemplateCorruptedError for malformed JSON."""
        template_name = "corrupted_template"
        prompt_v1 = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_v1, template_name) # v1

        file_path = self.temp_dir_path / f"{template_name}_v1.json"
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': ")

        with self.assertRaisesRegex(TemplateCorruptedError, "corrupted (not valid JSON)"):
            self.manager.load_template(template_name, version=1)

    def test_load_template_mismatched_structure(self):
        """Test TemplateCorruptedError for JSON not matching PromptObject structure."""
        template_name = "mismatched_template"
        prompt_v1 = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_v1, template_name) # v1

        file_path = self.temp_dir_path / f"{template_name}_v1.json"
        malformed_data = {"some_other_key": "value"} # Missing required PromptObject fields
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data, f)

        with self.assertRaisesRegex(TemplateCorruptedError, "Error deserializing template"):
             self.manager.load_template(template_name, version=1)

    def test_load_template_name_sanitization(self):
        """Test load_template uses name sanitization to find files."""
        original_name = "My Load Test with Spaces & Chars!@#"
        sanitized_base = "My_Load_Test_with_Spaces__Chars"
        prompt_to_save = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_to_save, original_name) # Saves as _v1.json

        loaded_prompt = self.manager.load_template(original_name) # Load latest (v1)
        self.assertIsNotNone(loaded_prompt)
        self.assertEqual(loaded_prompt.version, 1)
        self.assertEqual(loaded_prompt.role, self.dummy_prompt_content["role"])

    # --- Tests for list_templates ---
    def test_list_templates_empty_directory(self):
        """Test list_templates returns an empty dict for an empty directory."""
        self.assertEqual(self.manager.list_templates(), {})

    def test_list_templates_versioned(self):
        """Test list_templates returns a dict with base names and sorted version lists."""
        prompt_a = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt_a, "templateA") # v1
        time.sleep(0.001)
        self.manager.save_template(prompt_a, "templateA") # v2 (prompt_a is now v2)
        time.sleep(0.001)

        prompt_b_content = {**self.dummy_prompt_content, "role": "RoleB"}
        prompt_b = PromptObject(**prompt_b_content)
        self.manager.save_template(prompt_b, "Template B with space") # v1
        time.sleep(0.001)

        prompt_c_content = {**self.dummy_prompt_content, "role": "RoleC"}
        prompt_c = PromptObject(**prompt_c_content)
        self.manager.save_template(prompt_c, "templateA") # v3 of templateA (prompt_c is now v3)

        expected = {
            "templateA": [1, 2, 3],
            "Template_B_with_space": [1]
        }
        self.assertEqual(self.manager.list_templates(), expected)

    def test_list_templates_ignores_non_matching_files(self):
        """Test list_templates ignores files not matching the version pattern."""
        # Save a valid versioned template
        prompt = PromptObject(**self.dummy_prompt_content)
        self.manager.save_template(prompt, "valid_template") # valid_template_v1.json

        # Create some non-matching files
        (self.temp_dir_path / "non_versioned.json").touch()
        (self.temp_dir_path / "valid_template_vx.json").touch() # Invalid version char
        (self.temp_dir_path / "another_v1.txt").touch() # Not json
        (self.temp_dir_path / "prefix_valid_template_v1.json").touch() # Wrong prefix

        expected = {"valid_template": [1]}
        self.assertEqual(self.manager.list_templates(), expected)

    # --- Helper for delete tests ---
    def _create_prompt_for_test(self, task_text: str, initial_version=1) -> PromptObject:
        # Using a copy of dummy_prompt_content to avoid modifying class-level dict
        content = self.dummy_prompt_content.copy()
        content["task"] = task_text
        # version in PromptObject is for its own state, save_template determines file version
        return PromptObject(**content, version=initial_version)

    # --- Tests for Delete Methods ---

    def test_delete_template_version_success(self):
        """Test deleting a specific version of a template successfully."""
        template_name = "delete_version_test"
        sanitized_name = self.manager._sanitize_base_name(template_name)
        # Save a few versions
        p1 = self._create_prompt_for_test("v1 content")
        self.manager.save_template(p1, template_name) # Saves as v1
        p2 = self._create_prompt_for_test("v2 content")
        self.manager.save_template(p2, template_name) # Saves as v2

        # Ensure v1 file exists
        file_v1 = self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1.exists())

        # Delete version 1
        delete_result = self.manager.delete_template_version(template_name, 1)
        self.assertTrue(delete_result, "delete_template_version should return True on success.")
        self.assertFalse(file_v1.exists(), "Version 1 file should be deleted.")

        # Check that version 2 still exists
        file_v2 = self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 2)
        self.assertTrue(file_v2.exists(), "Version 2 file should still exist.")

        # Check list_templates reflects the change
        listed_templates = self.manager.list_templates()
        self.assertIn(sanitized_name, listed_templates)
        self.assertEqual(listed_templates[sanitized_name], [2]) # Only v2 should remain

    def test_delete_template_version_non_existent_version(self):
        """Test deleting a non-existent version of a template."""
        template_name = "delete_non_existent_version"
        sanitized_name = self.manager._sanitize_base_name(template_name)
        p1 = self._create_prompt_for_test("v1 content")
        self.manager.save_template(p1, template_name) # Only v1 exists

        delete_result = self.manager.delete_template_version(template_name, 5) # Try to delete v5
        self.assertFalse(delete_result, "delete_template_version should return False for non-existent version.")

        # Ensure v1 still exists
        file_v1 = self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 1)
        self.assertTrue(file_v1.exists())

    def test_delete_template_version_non_existent_template_name(self):
        """Test deleting a version from a non-existent template base name."""
        delete_result = self.manager.delete_template_version("no_such_template_ever", 1)
        self.assertFalse(delete_result, "delete_template_version should return False for non-existent template name.")

    def test_delete_template_all_versions_success(self):
        """Test deleting all versions of a template successfully."""
        template_name = "delete_all_test"
        sanitized_name = self.manager._sanitize_base_name(template_name)
        # Save multiple versions
        p1 = self._create_prompt_for_test("v1")
        self.manager.save_template(p1, template_name) # v1
        p2 = self._create_prompt_for_test("v2")
        self.manager.save_template(p2, template_name) # v2
        p3 = self._create_prompt_for_test("v3")
        self.manager.save_template(p3, template_name) # v3

        # Save another template to ensure it's not affected
        other_template_name = "other_template"
        sanitized_other_name = self.manager._sanitize_base_name(other_template_name)
        p_other = self._create_prompt_for_test("other content")
        self.manager.save_template(p_other, other_template_name) # v1 of other_template

        deleted_count = self.manager.delete_template_all_versions(template_name)
        self.assertEqual(deleted_count, 3, "Should report 3 versions deleted.")

        # Verify all files for 'delete_all_test' are gone
        self.assertFalse((self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 1)).exists())
        self.assertFalse((self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 2)).exists())
        self.assertFalse((self.manager.templates_dir_path / self.manager._construct_filename(sanitized_name, 3)).exists())

        # Verify list_templates reflects the removal
        listed_templates = self.manager.list_templates()
        self.assertNotIn(sanitized_name, listed_templates)

        # Verify other template still exists
        self.assertIn(sanitized_other_name, listed_templates)
        self.assertTrue((self.manager.templates_dir_path / self.manager._construct_filename(sanitized_other_name, 1)).exists())

    def test_delete_template_all_versions_non_existent_template_name(self):
        """Test deleting all versions for a non-existent template base name."""
        deleted_count = self.manager.delete_template_all_versions("no_such_template_for_all_delete")
        self.assertEqual(deleted_count, 0, "Should report 0 versions deleted for non-existent template.")


if __name__ == '__main__':
    unittest.main()
