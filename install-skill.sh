#!/bin/bash
# Axis Engineering Skill Installer
# Usage: curl -sL https://raw.githubusercontent.com/lotusboy/axis-engineering/main/install-skill.sh | bash
# Usage (Claude Code): curl -sL .../install-skill.sh | bash -s -- --claude

set -e

REPO_URL="https://raw.githubusercontent.com/lotusboy/axis-engineering/main/.agents/skills/axis-engineering"
INSTALL_DIR=".agents/skills/axis-engineering"
CLAUDE_DIR=".claude/skills/axis-engineering"

# Detect Claude Code: --claude flag or CLAUDE_CODE_VERSION env var
INSTALL_FOR_CLAUDE=false
if [ "$1" = "--claude" ] || [ -n "$CLAUDE_CODE_VERSION" ]; then
  INSTALL_FOR_CLAUDE=true
fi

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

# Claude Code currently only scans .claude/skills/, not .agents/skills/
# Copy there if requested (other agents like Cursor/Windsurf already scan .agents/)
if [ "$INSTALL_FOR_CLAUDE" = true ]; then
  echo "Copying to .claude/skills/ for Claude Code..."
  mkdir -p "$CLAUDE_DIR"/{references,assets}
  cp "$INSTALL_DIR/SKILL.md" "$CLAUDE_DIR/SKILL.md"
  cp "$INSTALL_DIR/references/vocabulary.md" "$CLAUDE_DIR/references/vocabulary.md"
  cp "$INSTALL_DIR/references/recipes.md" "$CLAUDE_DIR/references/recipes.md"
  cp "$INSTALL_DIR/references/anti-patterns.md" "$CLAUDE_DIR/references/anti-patterns.md"
  cp "$INSTALL_DIR/assets/contract-template.md" "$CLAUDE_DIR/assets/contract-template.md"
fi

echo ""
echo "✅ Axis Engineering skill installed to $INSTALL_DIR/"
echo ""
echo "Detected by: Cursor, Windsurf/Cascade, OpenAI Codex, GitHub Copilot"

if [ "$INSTALL_FOR_CLAUDE" = true ]; then
  echo "Also copied to: $CLAUDE_DIR/ (Claude Code)"
else
  echo ""
  echo "⚠️  Claude Code users: run with --claude flag to also install to .claude/skills/"
  echo "   curl -sL .../install-skill.sh | bash -s -- --claude"
fi

echo ""
echo "Visit https://agentskills.io for more information on how agents use skills."
