# Prometheus Protocol: Centralized Configuration Management (Conceptual)

This document outlines conceptual strategies for managing system-wide configurations and default parameters for the Prometheus Protocol platform. This is distinct from user-specific settings (managed by `UserSettings`) and prompt-specific settings (managed in `PromptObject.settings`).

## 1. Goals, Scope, and Types of Configuration

### 1.1. Goals

The primary goals for conceptualizing a centralized configuration management system are:

1.  **Environment Flexibility:** Enable Prometheus Protocol to operate with different configurations across various deployment environments (e.g., development, testing, staging, production) without code changes.
2.  **Centralized Defaults:** Provide a clear, single source of truth for system-wide default behaviors and parameters that are not tied to individual users or prompts.
3.  **Maintainability:** Make it easier to update system parameters (e.g., default AI model, API endpoints, base data paths) without modifying core application code.
4.  **Clear Configuration Hierarchy:** Establish a well-defined order of precedence for how settings are applied (e.g., environment variables > config files > hardcoded fallbacks, which then serve as a base for UserSettings and PromptObject.settings).
5.  **Security Considerations:** Provide a conceptual place for managing sensitive information like system-level API keys (though actual secure storage mechanisms are a deeper topic).

### 1.2. Scope (V1 Concepts for this Document)

This initial conceptualization will focus on:

*   Identifying the **types of configurations** that would benefit from centralized management.
*   Proposing **strategies for loading and accessing** these configurations conceptually.
*   Defining the conceptual **structure of an application configuration object** (`AppConfig`).
*   Discussing how existing core components (`JulesExecutor`, Managers) would **conceptually interact** with such an `AppConfig`.
*   Outlining benefits and potential complexities.

**Out of Scope for this V1 Conceptualization:**

*   Actual implementation of configuration file parsers (e.g., for YAML, JSON, .env files).
*   Specific secure secret management solutions (e.g., HashiCorp Vault, cloud provider secret managers).
*   Detailed UI for managing these configurations (this would likely be an admin-level feature for deployed instances).

### 1.3. Types of Configuration to Consider

The following types of system-level configurations are relevant for Prometheus Protocol:

1.  **`JulesExecutor` System Defaults:**
    *   **`jules_api_endpoint` (str):** The base URL for the hypothetical Jules AI service.
    *   **`jules_system_api_key` (Optional[str]):** A system-wide API key for Jules, if applicable (can be overridden by `UserSettings.default_jules_api_key`).
    *   **`jules_default_model_id` (str):** The default AI model ID to be used if not specified by user or prompt settings.
    *   **`jules_default_execution_settings` (Dict[str, Any]):** System-wide default parameters for AI execution (e.g., `{"temperature": 0.6, "max_tokens": 750}`). These form the base of the settings hierarchy.

2.  **Data Storage Paths:**
    *   **`data_storage_base_path` (str):** The root directory for all application-generated data (templates, conversations, user settings files). This allows the entire data store to be relocated easily.
    *   (Derived paths like `templates_subdir`, `conversations_subdir`, `user_settings_subdir` could also be configurable or derived from this base).

3.  **Logging Configuration:**
    *   **`default_logging_level` (str):** System-wide default logging level (e.g., "INFO", "DEBUG", "WARNING").
    *   **(V2+) Per-module log levels.**

4.  **Feature Flags (Conceptual V2+):**
    *   **`feature_flags` (Dict[str, bool]):** A dictionary to enable/disable experimental or optional features without code changes (e.g., `{"enable_advanced_analytics_dashboard": false}`).

These configurations need to be loaded and made accessible to relevant parts of the application at runtime.

---

## 2. Configuration Loading Strategy (Conceptual)

To make system-wide configurations manageable and adaptable across different environments, a clear loading strategy is needed.

### 2.1. Potential Configuration Sources

Prometheus Protocol could conceptually draw its system-level configurations from one or more of the following sources, applied in a defined order of precedence:

1.  **Environment Variables:**
    *   **Description:** Values set in the operating system's environment where the application is running.
    *   **Use Cases:** Ideal for deployment-specific settings (e.g., API endpoints for dev vs. prod), sensitive data like a system-level API key, or settings that need to be changed without altering packaged code/files.
    *   **Example:** `JULES_API_ENDPOINT="https_prod.jules.ai/v1"`, `PROMETHEUS_LOG_LEVEL="DEBUG"`.

2.  **Configuration Files:**
    *   **Description:** One or more files (e.g., `config.yaml`, `settings.json`, `.env` file) packaged with the application or placed in a known location.
    *   **Use Cases:** Suitable for storing a comprehensive set of default application parameters, less sensitive configurations, or settings that are less likely to change between minor deployments but might differ significantly from development defaults.
    *   **Example (`config.yaml`):**
        ```yaml
        jules_executor:
          default_model_id: "jules-xl-stable"
          default_settings:
            temperature: 0.65
            max_tokens: 800
        data_storage:
          base_path: "./app_data_prod"
        logging:
          default_level: "INFO"
        ```

3.  **Hardcoded Fallbacks (within code):**
    *   **Description:** Default values defined directly in the code (e.g., in the `AppConfig` dataclass definition or within components if `AppConfig` values are missing).
    *   **Use Cases:** To ensure the application can always run with a basic, sensible configuration even if no external configuration files or environment variables are provided. These should be considered the ultimate fallback.

### 2.2. Configuration Hierarchy / Precedence

A clear order of precedence is essential to determine which configuration source takes priority if a setting is defined in multiple places:

1.  **Environment Variables (Highest Precedence):** Values set as environment variables override all other sources.
2.  **Specific Configuration File(s) (Medium Precedence):** Values from explicitly loaded configuration files (e.g., `config.yaml`, `config.prod.yaml`) override hardcoded defaults. If multiple config files are supported (e.g., a base and an override), their loading order determines their relative precedence.
3.  **Hardcoded Dataclass Defaults (Lowest Precedence):** Default values defined directly within the conceptual `AppConfig` dataclass structure serve as the ultimate fallbacks if a setting is not found in any other source.

### 2.3. Access Mechanism for `AppConfig` (Conceptual)

Once the `AppConfig` object is fully populated at application startup (as described in Section 2.4), it needs to be accessible to various components of Prometheus Protocol.

1.  **Singleton `AppConfig` Instance:** The system will maintain a single, immutable instance of the `AppConfig` object throughout its runtime after initial loading.

2.  **Preferred Access Method: Dependency Injection:**
    *   **Concept:** The most robust and testable way for components to access configuration is through **Dependency Injection (DI)**. This means the `AppConfig` object (or relevant sub-sections/values from it) is explicitly passed to components that need it, typically via their constructors.
    *   **Benefits:**
        *   **Clear Dependencies:** Makes component dependencies on configuration explicit.
        *   **Testability:** Allows easy mocking or provision of specific configurations during unit testing by passing mock `AppConfig` objects.
        *   **Decoupling:** Components don't need to know *how* the configuration is loaded or where the global instance resides; they just receive what they need.

3.  **Alternative (Less Preferred): Global Accessor:**
    *   A global function (e.g., `get_app_config() -> AppConfig`) could provide access to the singleton `AppConfig` instance.
    *   **Drawbacks:** Can lead to hidden dependencies, make components harder to test in isolation, and behaves like a global variable.
    *   **V1 Stance:** While simpler for some scenarios, **Dependency Injection is the preferred conceptual approach** for Prometheus Protocol due to its benefits in maintainability and testability.

The choice of DI implies that the main application or service orchestrator, after loading `AppConfig`, would be responsible for instantiating key services (like `JulesExecutor`, `TemplateManager`, etc.) and passing the `AppConfig` (or relevant parts) to them.

### 2.4. Conceptual Loading Process Steps

The `AppConfig` object would be populated once at application startup by following these conceptual steps:

1.  **Step 1: Initialize with Hardcoded Defaults:**
    *   An instance of the `AppConfig` dataclass is created. Its attributes are initially populated with the hardcoded default values defined in the dataclass structure itself (as shown in Section 3's Python conceptual example).

2.  **Step 2: Load from Primary Configuration File (e.g., `config.default.yaml`):**
    *   The application attempts to find and load a primary configuration file (e.g., `config.default.yaml` or `settings.json`) from a predefined location (e.g., application root, a `/config` directory).
    *   If found and successfully parsed (YAML or JSON), the values from this file override the corresponding hardcoded defaults in the `AppConfig` instance.
    *   Nested structures in the file (like `jules_default_execution_settings` in the YAML example) would be mapped to the corresponding attributes in `AppConfig`.
    *   If the file is not found, this step is skipped (application proceeds with hardcoded defaults). If found but unparseable, a critical error should be raised, halting startup.

3.  **Step 3: (Optional) Load from Override Configuration File (e.g., `config.prod.yaml`, `config.local.yaml`):**
    *   The application could optionally look for an environment-specific or local override file (e.g., specified by an environment variable like `PROMETHEUS_CONFIG_OVERRIDE_PATH`, or a fixed name like `config.local.yaml` that is git-ignored).
    *   If found and parsed, values from this file override those already in the `AppConfig` instance (from Step 1 or 2). This allows for easy local overrides for development without modifying the default config file.

4.  **Step 4: Apply Environment Variable Overrides:**
    *   The application iterates through a predefined list of expected environment variables (e.g., `PROMETHEUS_JULES_API_ENDPOINT`, `PROMETHEUS_DATA_STORAGE_BASE_PATH`, `PROMETHEUS_LOGGING_DEFAULT_LEVEL`).
    *   For each recognized environment variable that is set:
        *   Its value is retrieved.
        *   The value is type-casted to the expected type of the corresponding `AppConfig` attribute (e.g., string to int for `max_tokens` if it were directly overridable, though complex dicts like `jules_default_execution_settings` are harder to override piece-meal this way and might require parsing a JSON string from an env var, or specific env vars for specific nested keys like `PROMETHEUS_JULES_SETTING_TEMPERATURE`).
        *   This type-casted value overrides the current value in the `AppConfig` instance.
    *   Environment variables have the highest precedence.

5.  **Step 5: Finalize and Use `AppConfig`:**
    *   The resulting `AppConfig` object is now considered final and immutable for the application's runtime.
    *   It is made available to other components (e.g., via dependency injection as discussed in Section 2.3).
    *   Key configuration values (excluding secrets) should be logged at startup for diagnostic purposes, indicating their source (e.g., "Loaded `jules_api_endpoint` from environment variable.").

This layered loading process provides a flexible and robust way to configure Prometheus Protocol for different environments and needs.

---

## 3. Conceptual `AppConfig` Object Structure and Examples

To hold the loaded system-wide configurations, a dedicated data structure is beneficial. This could be a dataclass or a Pydantic model for type safety and validation.

```python
# Conceptual Dataclass for AppConfig (illustrative, in markdown)
# from dataclasses import dataclass, field
# from typing import Optional, Dict, Any
#
# @dataclass
# class AppConfig:
#     jules_api_endpoint: str = "https_default.jules.api/v1_conceptual"
#     jules_system_api_key: Optional[str] = None
#     jules_default_model_id: str = "jules-xl-default-conceptual"
#     jules_default_execution_settings: Dict[str, Any] = field(default_factory=lambda: {"temperature": 0.6, "max_tokens": 750, "creativity_level_preference": "system_balanced"})
#     data_storage_base_path: str = "prometheus_protocol_data_v1"
#     templates_subdir: str = "templates"
#     conversations_subdir: str = "conversations"
#     user_settings_subdir: str = "user_settings" # For UserSettingsManager files
#     default_logging_level: str = "INFO"
#     # V2+ example: feature_flags: Dict[str, bool] = field(default_factory=dict)
```

**Key Considerations for `AppConfig`:**

*   **Immutability (Recommended):** Once loaded at startup, the `AppConfig` object should ideally be treated as immutable during the application's runtime to prevent unexpected changes in behavior. If configuration needs to be reloaded, it would typically require an application restart or a specific reload mechanism.
*   **Type Safety:** Using dataclasses or Pydantic models helps ensure that configuration values are of the expected types. Pydantic, for example, can perform validation during loading.
*   **Nested Structure (in files):** While the Python object might be flat or selectively nested for ease of use, configuration *files* (like YAML) often benefit from nested structures for organization (as shown in the examples below). The loading mechanism would handle mapping these nested file structures to the `AppConfig` object.
*   **Default Factories:** Using `default_factory` for mutable defaults like dictionaries is important to avoid all instances sharing the same dictionary if not overridden in the Python definition.
*   **Accessibility:** The loaded `AppConfig` instance needs to be made available to components that require it, often via dependency injection or a global access point.

This `AppConfig` structure would serve as the single source of truth for system-level settings after the initial loading and precedence logic (environment variables > config files > hardcoded defaults) has been applied.

### 3.1. Example YAML Configuration (`config.default.yaml`)

This file would provide base default configurations for the application.

```yaml
# Default System Configurations for Prometheus Protocol
# File: config.default.yaml

jules_api_endpoint: "https://api.google.jules_conceptual/v1"
# jules_system_api_key: null # Or omit if no system-wide key by default

jules_default_model_id: "jules-xl-general-v1"

jules_default_execution_settings:
  temperature: 0.65
  max_tokens: 800
  # Example of other potential default settings for Jules
  # top_p: 0.9
  # creativity_level_preference: "system_default_balanced"

data_storage:
  base_path: "./prometheus_data_storage" # Relative path example
  templates_subdir: "prompt_templates"
  conversations_subdir: "conversation_history"
  user_settings_subdir: "user_preferences"

logging:
  default_level: "INFO" # e.g., DEBUG, INFO, WARNING, ERROR

# feature_flags: # V2+
#   new_experimental_ui: false
```

### 3.2. Example `.env` File Format (for Overrides)

Environment variables can override values from YAML/JSON config files. They are typically prefixed.

```env
# Example .env file content
# These would override values from config.default.yaml

PROMETHEUS_JULES_API_ENDPOINT="https://prod.jules.api.google/v1"
PROMETHEUS_JULES_SYSTEM_API_KEY="prod_system_api_key_value_from_secret_store"

PROMETHEUS_JULES_DEFAULT_MODEL_ID="jules-xl-prod-optimized"

# Overriding nested settings via env vars can be tricky;
# often done for simple types or by expecting JSON strings for complex types.
# For simplicity, we might only override top-level or specific nested values.
# Example: Override only temperature from jules_default_execution_settings
# PROMETHEUS_JULES_DEFAULT_EXECUTION_SETTINGS_TEMPERATURE="0.72"
# (Requires config loader to handle such specific overrides, or expect full JSON string)
# PROMETHEUS_JULES_DEFAULT_EXECUTION_SETTINGS_JSON='{"temperature": 0.72, "max_tokens": 1000}'


PROMETHEUS_DATA_STORAGE_BASE_PATH="/var/prometheus_data_live"
PROMETHEUS_LOGGING_DEFAULT_LEVEL="WARNING"

# PROMETHEUS_FEATURE_FLAGS_NEW_EXPERIMENTAL_UI="true" # V2+
```
Note on overriding nested structures: Directly overriding deeply nested dictionary values (like individual items within `jules_default_execution_settings`) with environment variables can be complex. Common strategies include using a specific naming convention for environment variables (e.g., `PROMETHEUS_JULES_DEFAULT_EXECUTION_SETTINGS__TEMPERATURE=0.72` with double underscore for nesting) that the configuration loader can parse, or expecting the entire nested structure as a JSON string in a single environment variable (e.g., `PROMETHEUS_JULES_DEFAULT_EXECUTION_SETTINGS_JSON='{...}'`).

---

## 4. Component Integration with `AppConfig` (Conceptual)

This section outlines how core components of Prometheus Protocol would conceptually be initialized with and utilize the `AppConfig` object, primarily through Dependency Injection.

*   **`JulesExecutor`**:
    *   **`__init__(self, app_config: AppConfig, user_provided_api_key: Optional[str] = None)`:** The executor would be initialized with the global `AppConfig`. It might also accept a `user_provided_api_key` which, if present and valid (e.g., from `UserSettings`), would take precedence over `app_config.jules_system_api_key` or the executor's own placeholder.
    *   It would store and use:
        *   `self.endpoint_url = app_config.jules_api_endpoint`
        *   `self.system_api_key = app_config.jules_system_api_key` (This is the baseline key from system config)
        *   `self.base_default_settings = app_config.jules_default_execution_settings` (These are the system-level defaults)
    *   The settings hierarchy in `_prepare_jules_request_payload` then becomes: `PromptObject.settings` > `UserSettings.default_execution_settings` > `self.base_default_settings` (from `AppConfig`). The API key logic in `_prepare_jules_request_payload` would first consider `UserSettings.default_jules_api_key`, then `self.system_api_key` (from `AppConfig`), and finally any built-in placeholder in `JulesExecutor` itself if others are not provided.

*   **`TemplateManager`**:
    *   **`__init__(self, app_config: AppConfig)`:**
    *   Its `self.templates_dir_path` would be initialized as:
        `Path(app_config.data_storage_base_path) / app_config.templates_subdir`.
    *   This removes the hardcoded default path from the manager's constructor, making its data location entirely dependent on the application configuration.

*   **`ConversationManager`**:
    *   **`__init__(self, app_config: AppConfig)`:**
    *   Its `self.conversations_dir_path` would be initialized as:
        `Path(app_config.data_storage_base_path) / app_config.conversations_subdir`.

*   **`UserSettingsManager`**:
    *   **`__init__(self, app_config: AppConfig)`:**
    *   Its `self.settings_base_dir_path` would be initialized as:
        `Path(app_config.data_storage_base_path) / app_config.user_settings_subdir`.

*   **Other Core Components (e.g., `RiskIdentifier`, `ConversationOrchestrator`):**
    *   These might not directly need `AppConfig` if their dependencies (like `JulesExecutor`) are already configured. However, if they develop behaviors that need system-wide defaults not specific to other components, they too could accept `AppConfig`.

This approach ensures that components receive their necessary configurations upon instantiation, promoting cleaner design and better testability. The main application orchestrator (e.g., `streamlit_app.py`'s `get_core_components` or a future main application runner) would be responsible for loading `AppConfig` and injecting it into these components.

---

## 5. Configuration Validation (Conceptual)

Once the `AppConfig` object is populated from various sources (hardcoded defaults, files, environment variables), it's crucial to validate its contents before the application proceeds with full initialization and use by other components. This ensures the system starts in a known, valid state.

### 5.1. Importance of Validation

*   **Prevent Startup Failures:** Invalid or missing critical configurations (e.g., a malformed API endpoint, an non-existent essential data path if not creatable) can lead to immediate runtime errors or unpredictable behavior.
*   **Early Error Detection:** Catching configuration issues at startup is preferable to encountering them during runtime operations, which can be harder to debug and affect user experience.
*   **System Stability:** Ensures that components relying on `AppConfig` receive valid and expected types of data.

### 5.2. What to Validate (Examples)

Validation logic would depend on the specific fields in `AppConfig`:

*   **Required Fields:** Ensure that fields without hardcoded defaults and not provided by any loaded source (if they are essential for operation) are flagged (e.g., `jules_api_endpoint` might be considered critical).
*   **Data Types:** If configurations are loaded from sources like environment variables (which are strings) or loosely typed files, ensure they are correctly cast to their expected Python types (e.g., integers for `max_tokens`, booleans for feature flags). Dataclasses or Pydantic-like models for `AppConfig` can handle much of this automatically.
*   **Format/Value Constraints:**
    *   Validate URL formats (e.g., for `jules_api_endpoint`).
    *   Check if numerical values are within sensible ranges (e.g., `temperature` between 0.0 and 1.0, or a V2 range like 0.0-2.0).
    *   Ensure specified paths (like `data_storage_base_path`) are valid, and check if they exist. If they don't exist, the system might attempt to create them (as managers currently do for their subdirs), but the base path itself might need to be writable.
    *   Validate enum-like string values against a list of allowed options (e.g., `default_logging_level` must be one of "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").

### 5.3. Validation Mechanism (Conceptual)

*   **Within `AppConfig` (if using Pydantic/attrs):** If `AppConfig` were implemented using a library like Pydantic, or `attrs` with validators, much of the type and value validation could be defined directly within the class structure and would run automatically upon instantiation and population.
*   **Dedicated Validation Function:** A separate `validate_app_config(config: AppConfig) -> List[ConfigError]` function could be called immediately after the `AppConfig` object is populated. This function would perform all custom checks and return a list of errors.
*   **Application Startup Behavior:**
    *   If validation fails (i.e., the list of errors is not empty), the application should:
        *   Log the configuration errors clearly.
        *   Refuse to start up fully, exiting with a critical error message indicating configuration problems. This "fail fast" approach prevents runtime issues due to bad config.

By implementing configuration validation, Prometheus Protocol can ensure a more robust and predictable startup and operational lifecycle.

---

## 6. Benefits and Trade-offs of Centralized Configuration

Adopting a centralized configuration management approach, as conceptualized in this document, offers significant advantages but also introduces considerations that need to be managed.

### 6.1. Benefits

1.  **Improved Maintainability:**
    *   System-wide defaults and environment-specific parameters are managed in one or a few well-defined places (config files, environment variables) rather than being scattered as hardcoded values throughout the codebase. This makes updates easier and reduces the risk of inconsistencies.
2.  **Enhanced Flexibility Across Environments:**
    *   Different configurations for development, testing, staging, and production environments can be managed without code changes, simply by using different config files or environment variable sets. This is crucial for robust deployment pipelines.
3.  **Clear Separation of Concerns:**
    *   Configuration (which often changes based on deployment environment or operational needs) is separated from application logic (which changes based on feature development).
4.  **Simplified Management of Defaults:**
    *   Provides a clear hierarchy (Env Vars > Config Files > Hardcoded `AppConfig` Defaults) for how system-level default behaviors are determined and overridden.
5.  **Increased Security (Potential for Sensitive Data):**
    *   While this document doesn't detail secure secret management, a centralized configuration system provides a *place* where strategies for handling sensitive data (like system API keys) can be implemented (e.g., loading from environment variables which can be injected by secure deployment systems, or integrating with secret managers in V2+). It avoids hardcoding secrets in source code.
6.  **Better Testability of Components:**
    *   When components receive their configurations via Dependency Injection (e.g., an `AppConfig` object passed to their constructor), they can be easily tested with different mock configurations in unit tests.
7.  **Consistency for System Operations:**
    *   Operations teams can manage and understand system behavior more easily by referring to a centralized configuration.

### 6.2. Trade-offs and Potential Complexities

1.  **Initial Setup Complexity:**
    *   Implementing the config loading logic (parsing files, handling environment variables, managing precedence, validating configurations) adds some initial development overhead compared to just using hardcoded values.
2.  **Configuration Availability at Startup:**
    *   The `AppConfig` object must be fully populated and validated very early in the application's startup sequence, as many core components will depend on it. This requires careful sequencing of initialization logic.
3.  **Accessibility of Configuration:**
    *   If using a singleton `AppConfig` with a global accessor (the less preferred method), it can introduce global state, making it harder to reason about component dependencies and to test components in complete isolation. Dependency Injection mitigates this but requires passing the config object through call chains or to constructors.
4.  **Management of Configuration Files:**
    *   Ensuring the correct configuration files are deployed to the correct environments and that they are kept in sync with application expectations (e.g., new required config fields) requires good deployment and version control practices for the config files themselves.
5.  **Complexity of Overriding Nested Structures:**
    *   As noted in Section 3.2 (Example `.env` File Format), overriding deeply nested configuration structures purely with environment variables can be cumbersome or require conventions like using JSON strings in environment variables. This needs careful design if extensive overriding of nested structures is a common requirement.

Despite these complexities, the benefits of a well-designed centralized configuration management system generally outweigh the trade-offs for applications intended to be maintainable, flexible across environments, and scalable.

---
*(Content for Section 7 Conclusion next.)*
