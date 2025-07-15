# Contributing to DashAIBrowser

We welcome contributions from the community. If you are interested in contributing to DashAIBrowser, please take a moment to review this document.

## Guiding Principles

*   **Expanded KISS (Keep It Simple, Stupid):** We believe in writing clear, concise, and maintainable code.
*   **Law of Constant Progression:** We believe in continuous improvement and iteration.
*   **Battle-Tested Mentality:** We believe in writing high-quality, well-tested code.

## Prerequisites

*   Git
*   Python
*   Node.js
*   Rust
*   A C++ toolchain that supports C++17
*   Chromium build dependencies
*   Docker

## Getting Started

1.  Clone the DashAIBrowser repository:

    ```
    git clone https://github.com/your-username/dashai-browser.git
    ```

2.  Set up the Chromium fork:

    *   Follow the instructions in the [Chromium documentation](https://www.chromium.org/developers/how-tos/get-the-code) to get the Chromium code and set up your build environment.

3.  Build the browser core:

    ```
    cd dashai-browser
    gn gen out/Default
    ninja -C out/Default
    ```

4.  Set up the ASOL components:

    *   The ASOL components are written in C++ and are built as part of the browser core.

## Contribution Workflow

1.  **Branching:** Create a new branch for your feature or bug fix.
2.  **TDD:** Write tests for your code.
3.  **Code Style:** Follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html).
4.  **Linting:** Run the linter to check your code for style errors.
5.  **Commit Messages:** Write clear and concise commit messages.
6.  **Pull Requests:** Open a pull request with your changes.

## Pull Request Process

1.  Ensure that your code is well-tested and that all tests pass.
2.  Ensure that your code follows the code style guide.
3.  Write a clear and concise pull request description.
4.  Request a review from one of the project maintainers.

## Code of Conduct

We follow the [QRASL Code of Conduct](https://www.qrasl.com/code-of-conduct).

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub.
