# Build System Updates for Neuromorphic Efficiency Modes

This document describes the necessary changes to the `BUILD.gn` files to include the new Mojo interface and service updates for the Neuromorphic Efficiency Modes feature.

## dashai-browser/browser_core/services/ai_hooks/public/mojom/BUILD.gn

The `neuromorphic_modes.mojom` file needs to be added to the `sources` list in this file.

```
mojom("mojom") {
  sources = [
    "adaptive_ui.mojom",
    "collaborative_browsing.mojom",
    "neuromorphic_modes.mojom",
    "quantum_compute.mojom",
    "search_discovery.mojom",
  ]
}
```

## dashai-browser/asol/BUILD.gn

The `asol` target needs to be updated to include the new `neuromorphic_modes.mojom` dependency.

```
source_set("asol") {
  sources = [
    "cpp/asol_service_impl.cc",
    "cpp/asol_service_impl.h",
  ]

  deps = [
    "//dashai-browser/asol/protos",
    "//dashai-browser/browser_core/services/ai_hooks/public/mojom",
  ]
}
```

## dashai-browser/browser_core/tests/BUILD.gn

A new `neuromorphic_modes_integration_test` target needs to be added to this file.

```
test("neuromorphic_modes_integration_test") {
  sources = [
    "neuromorphic_modes_integration_test.cc",
  ]

  deps = [
    "//dashai-browser/asol",
    "//dashai-browser/browser_core/services/ai_hooks/public/mojom",
    "//base",
    "//testing/gtest",
  ]
}
```
