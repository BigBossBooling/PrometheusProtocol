# Development Environment Setup

This document provides instructions for setting up the development environment for the Prometheus Protocol project.

## Prerequisites

- Go (version 1.18 or higher)
- Protocol Buffers (protoc)
- Git

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/prometheus-protocol.git
   ```

2. **Install Go:**

   Follow the official Go installation instructions for your operating system: [https://golang.org/doc/install](https://golang.org/doc/install)

3. **Install Protocol Buffers:**

   Follow the official Protocol Buffers installation instructions for your operating system: [https://grpc.io/docs/protoc-installation/](https://grpc.io/docs/protoc-installation/)

## IDE Configuration

We recommend using Visual Studio Code with the Go extension for development.

1. **Install Visual Studio Code:**

   [https://code.visualstudio.com/](https://code.visualstudio.com/)

2. **Install the Go extension:**

   [https://marketplace.visualstudio.com/items?itemName=golang.Go](https://marketplace.visualstudio.com/items?itemName=golang.Go)

## Building the Project

To build the project, run the following command from the root directory:

```bash
go build ./...
```

## Running Tests

To run the tests, run the following command from the root directory:

```bash
go test ./...
```
