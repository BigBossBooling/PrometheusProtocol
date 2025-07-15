# Build System Updates

This document describes the necessary changes to the `BUILD.gn` files to include the new Mojo interface and service updates for the AI-Enhanced Search & Discovery feature.

## dashai-browser/browser_core/services/ai_hooks/public/mojom/BUILD.gn

The `search_discovery.mojom` file needs to be added to the `sources` list in this file.

```
mojom("mojom") {
  sources = [
    "search_discovery.mojom",
  ]
}
```

## dashai-browser/asol/BUILD.gn

The `asol_service_impl` target needs to be updated to include the new `search_discovery.mojom` dependency.

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

A new `search_discovery_integration_test` target needs to be added to this file.

```
test("search_discovery_integration_test") {
  sources = [
    "search_discovery_integration_test.cc",
  ]

  deps = [
    "//dashai-browser/asol",
    "//dashai-browser/browser_core/services/ai_hooks/public/mojom",
    "//base",
    "//testing/gtest",
  ]
}
```
