#!/bin/bash
# Axis Engineering Skill Installer
# Usage: curl -sL https://raw.githubusercontent.com/lotusboy/axis-engineering/main/install-skill.sh | bash
# Usage (Claude Code): curl -sL .../install-skill.sh | bash -s -- --claude

set -e

REPO_URL="https://raw.githubusercontent.com/lotusboy/axis-engineering/main/.agents/skills/axis-engineering"

# Detect Claude Code: --claude flag or CLAUDE_CODE_VERSION env var
INSTALL_FOR_CLAUDE=false
if [ "$1" = "--claude" ] || [ -n "$CLAUDE_CODE_VERSION" ]; then
  INSTALL_FOR_CLAUDE=true
fi

if [ "$INSTALL_FOR_CLAUDE" = true ]; then
  TARGET_DIR=".claude/skills/axis-engineering"
  echo "Installing Axis Engineering Agent Skill for Claude Code..."
else
  TARGET_DIR=".agents/skills/axis-engineering"
  echo "Installing Axis Engineering Agent Skill..."
fi

# Create directory structure
mkdir -p "$TARGET_DIR"/{references,assets}

# Download core skill file
echo "Downloading SKILL.md..."
curl -fsSL "$REPO_URL/SKILL.md" > "$TARGET_DIR/SKILL.md"

# Download reference files
echo "Downloading reference files..."
curl -fsSL "$REPO_URL/references/vocabulary.md" > "$TARGET_DIR/references/vocabulary.md"
curl -fsSL "$REPO_URL/references/recipes.md" > "$TARGET_DIR/references/recipes.md"
curl -fsSL "$REPO_URL/references/anti-patterns.md" > "$TARGET_DIR/references/anti-patterns.md"

# Download assets
echo "Downloading assets..."
curl -fsSL "$REPO_URL/assets/contract-template.md" > "$TARGET_DIR/assets/contract-template.md"

echo ""
echo "✅ Axis Engineering skill installed to $TARGET_DIR/"
echo ""

if [ "$INSTALL_FOR_CLAUDE" = true ]; then
  echo "Detected by: Claude Code"
else
  echo "Detected by: Cursor, Windsurf/Cascade, OpenAI Codex, GitHub Copilot"
  echo ""
  echo "⚠️  Claude Code users: run with --claude flag to install to .claude/skills/"
  echo "   curl -sL .../install-skill.sh | bash -s -- --claude"
fi

echo ""
echo "Visit https://agentskills.io for more information on how agents use skills."
