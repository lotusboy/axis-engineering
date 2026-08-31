#!/bin/bash
# Axis Engineering Skill Installer
# Usage: curl -sL https://raw.githubusercontent.com/lotusboy/axis-engineering/main/install-skill.sh | bash
# Usage (Claude Code): curl -sL .../install-skill.sh | bash -s -- --claude

set -e

REPO_URL="https://raw.githubusercontent.com/lotusboy/axis-engineering/main/.agents/skills/axis-engineering"

# Detect Claude Code: --claude flag, or the CLAUDECODE env var it actually sets
# (CLAUDE_CODE_VERSION was never a real Claude Code env var - auto-detect was dead code)
INSTALL_FOR_CLAUDE=false
if [ "$1" = "--claude" ] || [ -n "$CLAUDECODE" ] || [ -n "$CLAUDE_CODE_VERSION" ]; then
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
mkdir -p "$TARGET_DIR"/{references,assets,scripts}

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
curl -fsSL "$REPO_URL/assets/review-schema.json" > "$TARGET_DIR/assets/review-schema.json"
curl -fsSL "$REPO_URL/assets/review-example.json" > "$TARGET_DIR/assets/review-example.json"
mkdir -p "$TARGET_DIR/assets/fixtures"
curl -fsSL "$REPO_URL/assets/fixtures/login.ts" > "$TARGET_DIR/assets/fixtures/login.ts"

# Download scripts
echo "Downloading scripts..."
curl -fsSL "$REPO_URL/scripts/axis-validate.py" > "$TARGET_DIR/scripts/axis-validate.py"
curl -fsSL "$REPO_URL/scripts/test_axis_validate.py" > "$TARGET_DIR/scripts/test_axis_validate.py"
curl -fsSL "$REPO_URL/scripts/requirements.txt" > "$TARGET_DIR/scripts/requirements.txt"

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
