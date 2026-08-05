#!/usr/bin/env bash
# Build the AgentCore Runtime deployment package (ARM64, Python 3.11).
# The package includes the runtime dependencies + the travel_agent.py entrypoint.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/agent_files"
BUILD_DIR="$AGENT_DIR/deployment_package"
ZIP_PATH="$AGENT_DIR/deployment_package.zip"

echo "→ Cleaning previous build"
rm -rf "$BUILD_DIR" "$ZIP_PATH"
mkdir -p "$BUILD_DIR"

echo "→ Installing dependencies for ARM64 / Python 3.11"
uv pip install \
  --python-platform aarch64-manylinux2014 \
  --python-version 3.11 \
  --target="$BUILD_DIR" \
  --only-binary=:all: \
  -r "$AGENT_DIR/requirements.txt"

echo "→ Copying agent source"
cp "$AGENT_DIR/travel_agent.py" "$BUILD_DIR/"

echo "→ Zipping deployment package"
cd "$BUILD_DIR"
zip -qr "$ZIP_PATH" .
echo "→ Done: $ZIP_PATH"
