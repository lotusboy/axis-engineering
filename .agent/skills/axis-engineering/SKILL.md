---
name: axis-engineering
description: AI Operating System with 33 behavior handles for critical thinking. Use when performing code review, architecture review, bug investigation, security review, or any task requiring structured reasoning.
license: CC-BY-4.0
compatibility: Designed for Claude Code, Cascade/Windsurf, Cursor, and similar agentic tools
metadata:
  author: Steven Loftus
  version: "2.0.0"
tags: [framework, thinking, methodology, genba, pre-mortem, stride]
---

# Axis Engineering

> Created by **Steven Loftus** (2026) — Licensed under [CC BY 4.0](LICENSE)

Axis Engineering is a prompt methodology that changes *how* AI thinks, not just *what* it outputs.

It does this by applying a small number of named "behavior handles" (e.g. Genba, Pre-mortem, MECE) that act as high-density tokens, activating existing reasoning patterns inside the model's training data.

## Quick Start

```
Approach with Genba and Chaos Engineering.
Cite file:line for every finding.
Before approving, run a Pre-mortem.
```

**Rule of thumb:** Pick 2–3 handles across different axes.

## The Five Axes

| Axis | Question | Example Handles |
|------|----------|-----------------|
| **Dispositional** | How should it think? | Genba, Shoshin, First Principles |
| **Structural** | How should it report? | MECE, Pyramid Principle, Five Whys |
| **Pattern-oriented** | What should it recognise? | SOLID, Fowler's Catalog, DDD |
| **Adversarial** | What should it try to break? | Chaos Engineering, Pre-mortem, STRIDE |
| **Contextual** | How big is this problem? | Cynefin, YAGNI, Poka-yoke |

See `references/vocabulary.md` for the full 33-handle reference.

## Recipes (Handle Combinations)

| Task | Handles |
|------|---------|
| Config change | Poka-yoke + YAGNI |
| Code review | Shoshin + Genba + Fowler's + Pyramid |
| Architecture review | Cynefin + DDD + Hexagonal + Pre-mortem |
| Security review | Red Team + STRIDE + Andon |
| Bug investigation | Genba + Five Whys + First Principles |

## The Axis Contract Template

Use this for any non-trivial task:

```
AXES:         [2-3 named handles from recipes above]
TARGET:       [specific artifacts — files, endpoints, docs]
STRUCTURE:    [output format — Pyramid, MECE, BLUF]
EVIDENCE:     [every finding must cite file:line]
ASSUMPTIONS:  [maintain a Verified/Unknown ledger]
STOP:         [Andon — halt on data-loss or security vuln]
```

## Execution Strategies

| Strategy | When to use | Findings |
|----------|-------------|----------|
| Single pass, no contract | Routine code review | ~12 |
| Single pass, with contract | Feature review | ~14-19 |
| Two-pass, fresh sessions | Pre-production audit | **~30** |
| Triangle Protocol | Architecture tradeoffs | 3 designs + synthesis |

**Key finding:** The Axis Contract increases evidence density by 70%. Always use it for anything above routine.

See `references/experiments.md` for full data from 9 controlled reviews and 20 real-world applications.

## Why This Works

LLMs don't "understand" Genba. They activate **co-occurrence clusters**. When you say "Genba mindset", the model activates verification language, ground-truth checking, artifact-first reasoning — because those tokens are statistically correlated in training data.

You're leveraging the model's latent structure, not teaching it something new. That's why compressed terms work better than verbose instructions.

## Anti-patterns

- **Over-stacking:** Using 5+ handles in one prompt causes superficial application
- **Wrong hammer:** Using DDD for a checkbox field (use Cynefin to size first)
- **Keyword cargo-culting:** Name-dropping handles without evidence
- **Verification theatre:** Saying "I checked" without citing file:line

See `references/anti-patterns.md` for full details.

## Composition with Other Skills

Axis Engineering is designed to be **composed into** other skills rather than being technology-specific.

Example: A `bug-fixing` skill would reference Axis handles:
```
Step 1: Apply Genba to read error logs and source
Step 2: Apply Five Whys to trace root cause  
Step 3: Apply Poka-yoke to design the fix
```

This keeps Axis pure (cognitive framework) while domain skills handle technology specifics.

## Known Limitations

1. **Model specificity:** Tested primarily on Claude. Cross-model transfer predicted but unverified.
2. **Context window decay:** Handle effects weaken over long conversations. Re-anchor periodically.
3. **No automated contract validation:** Manual verification currently required.
4. **English-centric:** Handle effectiveness depends on English training data density.

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | Core skill — quick start, recipes, contract (this file) |
| `references/vocabulary.md` | Full 33-handle reference with Evidence/Domain fields |
| `references/recipes.md` | Extended recipe catalog |
| `references/anti-patterns.md` | Detailed anti-patterns and mitigations |
| `assets/contract-template.md` | Copy-paste contract template |

## Installation

Copy this skill to your project's `.agent/skills/` folder:

```bash
mkdir -p .agent/skills/axis-engineering
curl -L https://raw.githubusercontent.com/lotusboy/axis-engineering/main/.agent/skills/axis-engineering/SKILL.md > .agent/skills/axis-engineering/SKILL.md
```

Or use as a git submodule:
```bash
git submodule add https://github.com/lotusboy/axis-engineering.git .agent/skills/axis-engineering
```

## Provenance & Legal

Original synthesis by Steven Loftus (2026). Licensed under CC BY 4.0.

Third-party frameworks (Toyota Production System, McKinsey, etc.) remain property of their originators, used under fair use for educational purposes.
