#!/bin/bash
# Axis Engineering Skill Installer
# Usage: curl -sL https://raw.githubusercontent.com/lotusboy/axis-engineering/main/install-skill.sh | bash

set -e

REPO_URL="https://raw.githubusercontent.com/lotusboy/axis-engineering/main/.agent/skills/axis-engineering"
INSTALL_DIR=".agent/skills/axis-engineering"

echo "Installing Axis Engineering Agent Skill..."

# Create directory structure
mkdir -p "$INSTALL_DIR"/{references,assets}

# Download core skill file
echo "Downloading SKILL.md..."
curl -fsSL "$REPO_URL/SKILL.md" > "$INSTALL_DIR/SKILL.md"

# Download reference files
echo "Downloading reference files..."
curl -fsSL "$REPO_URL/references/vocabulary.md" > "$INSTALL_DIR/references/vocabulary.md"
curl -fsSL "$REPO_URL/references/recipes.md" > "$INSTALL_DIR/references/recipes.md"
curl -fsSL "$REPO_URL/references/anti-patterns.md" > "$INSTALL_DIR/references/anti-patterns.md"

# Download assets
echo "Downloading assets..."
curl -fsSL "$REPO_URL/assets/contract-template.md" > "$INSTALL_DIR/assets/contract-template.md"

echo ""
echo "✅ Axis Engineering skill installed to $INSTALL_DIR/"
echo ""
echo "The skill is now available to agents that support the Agent Skills format."
echo "Visit https://agentskills.io for more information on how agents use skills."
