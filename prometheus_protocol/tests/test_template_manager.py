import unittest
import tempfile
import json
from pathlib import Path
import shutil # For cleaning up if setUp fails before self.temp_dir is assigned

from prometheus_protocol.core.template_manager import TemplateManager
from prometheus_protocol.core.prompt import PromptObject
from prometheus_protocol.core.exceptions import TemplateCorruptedError

class TestTemplateManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for templates before each test."""
        # In case setUp itself fails before self.temp_dir is assigned
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir_path = Path(self._temp_dir_obj.name)
        self.manager = TemplateManager(templates_dir=str(self.temp_dir_path))

        # Create a dummy prompt object for use in tests
        self.dummy_prompt_data = {
            "role": "Test Role",
            "context": "Test context for template",
            "task": "Test task",
            "constraints": ["Constraint A"],
            "examples": ["Example A"],
            "tags": ["test", "dummy"]
        }
        self.dummy_prompt = PromptObject(**self.dummy_prompt_data)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self._temp_dir_obj.cleanup()

    def test_save_template_creates_file(self):
        """Test that save_template creates a JSON file with correct content."""
        template_name = "my_test_template"
        self.manager.save_template(self.dummy_prompt, template_name)

        # Check if file exists (sanitized name)
        expected_file = self.temp_dir_path / "my_test_template.json"
        self.assertTrue(expected_file.exists())

        # Check content
        with expected_file.open('r', encoding='utf-8') as f:
            saved_data = json.load(f)

        # Compare all fields from dummy_prompt's to_dict()
        self.assertEqual(saved_data["role"], self.dummy_prompt_data["role"])
        self.assertEqual(saved_data["context"], self.dummy_prompt_data["context"])
        self.assertEqual(saved_data["task"], self.dummy_prompt_data["task"])
        self.assertEqual(saved_data["constraints"], self.dummy_prompt_data["constraints"])
        self.assertEqual(saved_data["examples"], self.dummy_prompt_data["examples"])
        self.assertEqual(saved_data["tags"], self.dummy_prompt_data["tags"])
        self.assertIn("prompt_id", saved_data) # Check metadata fields
        self.assertIn("version", saved_data)
        self.assertIn("created_at", saved_data)
        self.assertIn("last_modified_at", saved_data)

    def test_save_template_name_sanitization(self):
        """Test template name sanitization during save."""
        template_name = "My Test Template with Spaces & Chars!@#"
        self.manager.save_template(self.dummy_prompt, template_name)
        expected_file = self.temp_dir_path / "My_Test_Template_with_Spaces__Chars.json"
        self.assertTrue(expected_file.exists(), f"Expected file {expected_file} not found.")

    def test_save_template_empty_name_raises_value_error(self):
        """Test save_template raises ValueError for empty or whitespace name."""
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty."):
            self.manager.save_template(self.dummy_prompt, "")
        with self.assertRaisesRegex(ValueError, "Template name cannot be empty."):
            self.manager.save_template(self.dummy_prompt, "   ")

    def test_save_template_name_sanitizes_to_empty_raises_value_error(self):
        """Test save_template raises ValueError if name sanitizes to empty."""
        with self.assertRaisesRegex(ValueError, "Template name '!@#\$' sanitized to an empty string"):
            self.manager.save_template(self.dummy_prompt, "!@#$")

    def test_load_template_success(self):
        """Test loading an existing template successfully."""
        template_name = "load_me_template"
        self.manager.save_template(self.dummy_prompt, template_name)

        loaded_prompt = self.manager.load_template(template_name)
        self.assertIsInstance(loaded_prompt, PromptObject)
        self.assertEqual(loaded_prompt.role, self.dummy_prompt.role)
        self.assertEqual(loaded_prompt.context, self.dummy_prompt.context)
        # Compare other relevant fields as needed
        self.assertEqual(loaded_prompt.prompt_id, self.dummy_prompt.prompt_id)

    def test_load_template_not_found(self):
        """Test loading a non-existent template raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_template("non_existent_template")

    def test_load_template_corrupted_json(self):
        """Test loading a corrupted JSON file raises TemplateCorruptedError."""
        template_name = "corrupted_template"
        file_path = self.temp_dir_path / f"{template_name}.json"
        with file_path.open('w', encoding='utf-8') as f:
            f.write("{'invalid_json': ") # Write intentionally malformed JSON

        with self.assertRaisesRegex(TemplateCorruptedError, "corrupted (not valid JSON)"):
            self.manager.load_template(template_name)

    def test_load_template_mismatched_structure(self):
        """Test loading JSON with mismatched structure raises TemplateCorruptedError."""
        template_name = "mismatched_structure_template"
        file_path = self.temp_dir_path / f"{template_name}.json"
        # Save valid JSON, but not matching PromptObject structure for from_dict's needs
        # (e.g. 'role' might be expected by PromptObject.from_dict via data.get('role'))
        # If PromptObject.from_dict is very robust with .get() for all fields,
        # it might create an object with many None values.
        # This test depends on PromptObject.from_dict's strictness.
        # For now, let's assume PromptObject.from_dict might fail if critical fields are missing.
        # A more specific error from PromptObject.from_dict would be better.
        malformed_data = {"some_other_key": "value"}
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(malformed_data, f)

        with self.assertRaisesRegex(TemplateCorruptedError, "Error deserializing template"):
             self.manager.load_template(template_name)


    def test_list_templates_empty(self):
        """Test list_templates returns an empty list when no templates exist."""
        self.assertEqual(self.manager.list_templates(), [])

    def test_list_templates_with_items(self):
        """Test list_templates returns correct names after saving templates."""
        names = ["template_alpha", "template_beta_with space"]
        sanitized_names = ["template_alpha", "template_beta_with_space"] # Expected after sanitization

        for name in names:
            self.manager.save_template(self.dummy_prompt, name)

        listed_templates = self.manager.list_templates()
        self.assertCountEqual(listed_templates, sanitized_names) # Use assertCountEqual for order-agnostic comparison
        self.assertEqual(sorted(listed_templates), sorted(sanitized_names)) # Or check sorted lists

    def test_load_template_name_sanitization(self):
        """Test that load_template uses the same name sanitization as save_template."""
        original_name = "My Test Template with Spaces & Chars!@#"
        # This name will be sanitized to "My_Test_Template_with_Spaces__Chars.json" by save_template
        self.manager.save_template(self.dummy_prompt, original_name)

        # Attempt to load using the original, unsanitized name
        loaded_prompt = self.manager.load_template(original_name)
        self.assertIsNotNone(loaded_prompt)
        self.assertEqual(loaded_prompt.role, self.dummy_prompt.role)

if __name__ == '__main__':
    unittest.main()
