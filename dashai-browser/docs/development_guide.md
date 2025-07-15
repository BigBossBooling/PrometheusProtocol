# Development Guide

This document provides a guide for developers who want to contribute to DashAIBrowser.

## Getting Started

To get started with DashAIBrowser, you will need to have the following installed:

*   A C++ compiler that supports C++17.
*   The `gn` build tool.
*   The `ninja` build tool.

Once you have these tools installed, you can clone the DashAIBrowser repository and build the project.

```
git clone https://github.com/your-username/dashai-browser.git
cd dashai-browser
gn gen out/Default
ninja -C out/Default
```

## Building the C++ Components

The C++ components of DashAIBrowser are built using the `gn` and `ninja` build tools. The build system is configured using `BUILD.gn` files. You can find more information about the build system in the `docs/build_system_blueprint.md` file.

## Contributing

We welcome contributions from the community. If you are interested in contributing to DashAIBrowser, please see our Contribution Guide for more information.

## Code Style

We follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html).

## Testing

We use the Google Test framework for testing. You can run the tests by running the following command:

```
ninja -C out/Default tests
```

## Debugging

You can debug the browser by running the following command:

```
gdb --args out/Default/dash_ai_browser
```
