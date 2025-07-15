# DashAIBrowser: Build System Blueprint

## 1. Overview

This document outlines the conceptual `BUILD.gn` structure and necessary updates to compile the DashAIBrowser's AI Services Orchestration Layer (ASOL) and its integrated AI-powered features. It assumes a Chromium/Blink fork as the foundational browser core.

## 2. Core Principles

*   **Modularity:** Each major component (ASOL, Mojo interfaces, browser-side clients) is defined as a separate build target.
*   **Dependency Management:** `BUILD.gn` files explicitly define dependencies between targets.
*   **Automated Code Generation:** Protobuf and Mojo IDL files are automatically processed to generate C++ bindings.
*   **Scalability:** The structure supports adding new AI features and services incrementally.

## 3. Top-Level `BUILD.gn` Structure (Conceptual)

The main `BUILD.gn` files (e.g., `browser_core/BUILD.gn`, `asol/BUILD.gn`, `chrome/BUILD.gn`) will be updated to include the following conceptual targets:

```gn
# Example: browser_core/BUILD.gn (simplified)
# This file would include/import other BUILD.gn files for specific features.

import("//build/config/features.gni") # For feature flags
import("//build/config/compiler/compiler.gni") # For compiler settings

# Define a source_set for the ASOL service interface (Mojo IDL)
source_set("asol_mojo_interfaces") {
  sources = [
    "services/ai_hooks/public/mojom/asol_service.mojom",
    "services/ai_hooks/public/mojom/content_creation.mojom",
    "services/ai_hooks/public/mojom/search_discovery.mojom",
    "services/ai_hooks/public/mojom/adaptive_ui.mojom",
    "services/ai_hooks/public/mojom/collaborative_browsing.mojom",
    "services/ai_hooks/public/mojom/quantum_compute.mojom",
    "services/ai_hooks/public/mojom/neuromorphic_modes.mojom",
    "services/ai_hooks/public/mojom/content_curation.mojom",
    # Add other Mojo IDL files here
  ]
  # This generates C++ headers and source files for Mojo bindings
  # Actual Mojo rules are more complex and handled by Chromium's build system.
}

# Define a source_set for browser-side AI feature clients
source_set("ai_feature_clients") {
  sources = [
    "chrome/browser/ai_features/summary_service.cc",
    "chrome/browser/ai_features/content_creation_service.cc",
    "chrome/browser/ai_features/search_discovery_service.cc",
    "chrome/browser/ai_features/adaptive_ui_service.cc",
    "chrome/browser/ai_features/collaborative_browsing_service.cc",
    "chrome/browser/ai_features/quantum_compute_service.cc",
    "chrome/browser/ai_features/neuromorphic_modes_service.cc",
    "chrome/browser/ai_features/content_curation_service.cc",
    # Add other browser-side client .cc files
  ]
  public_deps = [
    ":asol_mojo_interfaces", # Depends on generated Mojo bindings
    "//base", # Common Chromium base library
    # Add other necessary Chromium dependencies
  ]
  # Other build configurations (e.g., visibility)
}

# Define a source_set for ASOL C++ implementation
source_set("asol_service_impl") {
  sources = [
    "asol/cpp/asol_service_impl.cc",
    # Add other ASOL core C++ files (e.g., prompt_generator_client.cc, echosphere_vcpu_interface.cc)
  ]
  public_deps = [
    ":asol_mojo_interfaces", # Depends on Mojo interfaces
    "//base",
    "//net", # For network operations
    # Add other necessary Chromium/ASOL dependencies
  ]
  # Other build configurations
}

# Define a source_set for ASOL tests
source_set("asol_tests") {
  testonly = true
  sources = [
    "asol/tests/asol_service_test.cc",
    "asol/tests/mock_echosphere_vcpu.h", # Mock implementation for testing
    # Add other ASOL test files
  ]
  deps = [
    ":asol_service_impl", # Depends on the ASOL implementation
    "//testing/gtest", # Google Test framework
    "//testing/gmock", # Google Mock framework
    # Add other test dependencies
  ]
}

# Define source_sets for browser-side integration tests
source_set("browser_ai_integration_tests") {
  testonly = true
  sources = [
    "browser_core/tests/summary_integration_test.cc",
    "browser_core/tests/content_creation_integration_test.cc",
    "browser_core/tests/search_discovery_integration_test.cc",
    "browser_core/tests/adaptive_ui_integration_test.cc",
    "browser_core/tests/collaborative_browsing_integration_test.cc",
    "browser_core/tests/quantum_compute_integration_test.cc",
    "browser_core/tests/neuromorphic_modes_integration_test.cc",
    "browser_core/tests/content_curation_integration_test.cc",
    # Add other browser-side integration test files
  ]
  deps = [
    ":ai_feature_clients", # Depends on browser-side clients
    ":asol_service_impl", # May depend on ASOL for full integration
    "//testing/gtest",
    "//testing/gmock",
    # Add other test dependencies
  ]
}
```

*   **Conceptual Build Commands:**
    *   To generate build files: `gn gen out/Default` (from Chromium root)
    *   To build all ASOL and AI features: `autoninja -C out/Default asol_service_impl asol_tests browser_ai_integration_tests ai_feature_clients` (conceptual targets)
