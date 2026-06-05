# Axis Engineering — Automated Contract Validation

> A deterministic linter that converts the Axis Contract from a prompt instruction (soft) into an enforced invariant (hard).
>
> See also: [main methodology](README.md) | [vocabulary](vocabulary-quick-ref.md) | [two-pass strategy](two-pass-strategy.md)

---

## The Problem

The Axis Contract is a powerful prompt discipline, but it relies on the AI self-reporting compliance. Nothing prevents an AI from claiming "all citations verified" when they aren't, or firing a handle name without any supporting finding. The contract is a soft constraint — you trust the output rather than verifying it.

`axis-validate` makes the contract mechanical: a deterministic Python linter that reads a structured review document and enforces the contract's rules with real exit codes.

---

## What It Validates

Seven checks run against every review document:

| # | Check | What it enforces |
|---|-------|-----------------|
| 1 | **Schema version** | Document declares a supported `schema_version` |
| 2 | **Schema conformance** | Document shape matches `review-schema.json` (requires `jsonschema`) |
| 3 | **Citation coverage** | Every `defect` and `fact` finding has ≥1 `file:line` citation |
| 4 | **Citation resolution** | Every cited file exists; every cited line number is in range |
| 5 | **Handle firing** | Every handle named in `contract.axes` owns ≥1 finding |
| 6 | **Ledger integrity** | `assumptions` array is present |
| 7 | **Andon rule** | Critical/high `data-loss` or `security` defects have `stop_triggered: true` |

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | All checks passed — contract is conformant |
| `1` | Hard failure — citation dead, handle unfired, Andon violated |
| `2` | Advisory — schema shape unenforced (install `jsonschema` or pass `--require-schema`) |

---

## Setup

```bash
# From the skill directory
pip install -r scripts/requirements.txt   # installs jsonschema for full enforcement
```

Without `jsonschema`, schema shape checks (check 2) degrade to advisory (exit 2). All other checks run regardless.

---

## Usage

```bash
# From the skill directory (.agents/skills/axis-engineering/ or ~/.claude/skills/axis-engineering/)
python scripts/axis-validate.py <review.json> --repo-path <path-to-repo>

# With strict schema enforcement (recommended for CI)
python scripts/axis-validate.py <review.json> --repo-path <path-to-repo> --require-schema

# Validate the shipped example (run from skill dir)
python scripts/axis-validate.py assets/review-example.json --repo-path . --require-schema
```

`--repo-path` is the root against which citation file paths are resolved. For validating a review of your own codebase, pass the path to that repo.

---

## Output

```
axis-validate: Contract Conformance Report
==========================================

Overall: 7/7 checks passed

  schema_version:    Schema version: 1.0.0 ✓
  schema_conformance: Schema conformance: valid ✓
  citations:         Citation coverage: 3/3 ✓
  resolution:        Citation resolution: 6/6 ✓
  handles:           Handle firing: SOLID, STRIDE, YAGNI ✓
  ledger:            Ledger integrity: 1 unknown, 2 verified, 0 refuted ✓
  andon:             Andon rule: All critical/high security/data-loss defects have stop_triggered ✓

All checks passed. Contract is conformant.
```

Failures report the specific finding IDs and violations, not just a pass/fail count.

---

## Review Document Format

Reviews must be valid JSON conforming to `assets/review-schema.json`. The required top-level fields:

```json
{
  "schema_version": "1.0.0",
  "contract": {
    "axes": ["SOLID", "STRIDE"],
    "structure": "Pyramid",
    "stop": "Andon"
  },
  "bluf": "One-sentence verdict.",
  "findings": [
    {
      "id": "F1",
      "handle": "SOLID",
      "severity": "critical",
      "type": "defect",
      "category": "security",
      "claim": "Specific, grounded claim.",
      "citations": [{"file": "src/auth.ts", "line": 42}],
      "stop_triggered": true
    }
  ],
  "assumptions": [
    {"statement": "...", "status": "verified", "evidence": "..."}
  ]
}
```

**Key rules:**
- `type` must be one of: `defect`, `recommendation`, `fact`, `absence`
- `defect` and `fact` findings **must** have citations
- Always set `category` on findings — omitting it triggers conservative Andon treatment (any `critical`/`high` defect without a category is treated as Andon-relevant)
- `stop_triggered: true` is required for `critical` or `high` `security`/`data-loss` defects when `contract.stop` is `"Andon"`

See `assets/review-example.json` for a complete worked example.

---

## CI Integration

Add to your CI pipeline to gate merges on contract conformance:

```yaml
- run: pip install -r .agents/skills/axis-engineering/scripts/requirements.txt
- run: |
    python .agents/skills/axis-engineering/scripts/axis-validate.py \
      review.json \
      --repo-path . \
      --require-schema
```

The `axis-validate-ci.yml` workflow in this repo runs the full regression suite (with and without `jsonschema`) on every push and PR.

---

## Regression Tests

```bash
# Run from repo root with jsonschema installed (full suite — 9 tests)
python .agents/skills/axis-engineering/scripts/test_axis_validate.py

# Without jsonschema — baseline tests skip, tests 8-9 still run
python .agents/skills/axis-engineering/scripts/test_axis_validate.py
```

Both must exit 0. The suite is the safety net for the validator — do not merge changes to `axis-validate.py` without running it.
