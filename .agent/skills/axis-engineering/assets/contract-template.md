# Axis Contract Template

Copy and customize this template for any non-trivial task:

---

## Standard Contract

```
AXES:         [2-3 named handles from recipes]
TARGET:       [specific artifacts — files, endpoints, docs]
STRUCTURE:    [output format — Pyramid, MECE, BLUF]
EVIDENCE:     [every finding must cite file:line; critical findings include verbatim snippet]
ASSUMPTIONS:  [maintain a Verified/Unknown ledger of all assumptions made]
STOP:         [Andon — halt and flag on data-loss or security vulnerability]
```

---

## Example: Code Review Contract

```
AXES:         Shoshin + Genba + Fowler's Catalog + Pyramid Principle
TARGET:       src/services/*.ts, tests/services/*.test.ts
STRUCTURE:    Pyramid Principle (verdict first, then severity-ordered findings)
EVIDENCE:     Every finding must cite file:line. Every claim verified by grep/read.
              Critical findings must include a verbatim snippet (≤25 words) from source.
ASSUMPTIONS:  List every assumption. Mark each Verified (with evidence) or Unknown
              (with proposed verification step). Include at end of review.
STOP:         Andon — halt and flag if you find a data-loss or security vulnerability.
```

---

## Example: Architecture Review Contract

```
AXES:         Cynefin + DDD + Hexagonal + Pre-mortem
TARGET:       docs/architecture/*.md, src/domain/**/*, src/infrastructure/**/*
STRUCTURE:    MECE (bounded contexts, then ports/adapters, then failure modes)
EVIDENCE:     Every architectural claim maps to code location or documented decision.
              Every Pre-mortem scenario includes triggering condition and impact.
ASSUMPTIONS:  Ledger tracking: domain boundaries, technology choices, scale assumptions.
STOP:         Andon on unresolvable security or data integrity issues.
```

---

## Example: Security Review Contract

```
AXES:         Red Team + STRIDE + Andon
TARGET:       src/auth/**/*, src/api/**/*, config/security*
STRUCTURE:    STRIDE categories (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation)
EVIDENCE:     Every threat includes exploitation steps and concrete code location.
              Risk severity with CVSS-style score (Critical/High/Medium/Low).
ASSUMPTIONS:  Trust boundaries, threat actor capabilities, mitigations in place.
STOP:         Immediate Andon on Critical severity findings.
```

---

## Example: Bug Investigation Contract

```
AXES:         Genba + Five Whys + First Principles
TARGET:       Error logs, stack traces, relevant source files, related issues
STRUCTURE:   Five Whys chain leading to BLUF fix recommendation
EVIDENCE:    Log entries with timestamps. Code snippets showing error path.
             Root cause verified by reproduction or code analysis.
ASSUMPTIONS:  Error conditions, user impact scope, reproduction steps.
STOP:         Andon if data corruption or ongoing system damage detected.
```

---

## Contract Checklist

- [ ] AXES: 2-3 handles across different axes?
- [ ] TARGET: Specific artifacts identified?
- [ ] STRUCTURE: Output format specified?
- [ ] EVIDENCE: Proof-of-work rules defined?
- [ ] ASSUMPTIONS: Verification ledger included?
- [ ] STOP: Escalation condition clear?
