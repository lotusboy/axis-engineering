# Axis Engineering — Quick Reference

> Each behavior handle has five fields: **Name**, **One-liner** (unpack), **Evidence** (what proves it was applied), **Domain** (where it's most effective), **Avoid** (common misapplication).

## Axis 1: Dispositional (How to Think)

| Handle | One-liner | Evidence | Domain | Avoid |
|--------|-----------|----------|--------|-------|
| Genba | Go to the source — verify, don't assume | File:line citations, grep results, "I read X and found Y" | any | Trivial config changes (overkill — verifying a boolean flip wastes cycles) |
| Seven Factors | Mindful, investigative, energetic, engaged, calm, focused, unbiased | Balanced assessment (praise + critique), deep traces, no rushed conclusions | code, architecture | Quick fixes, trivial tasks (overkill) |
| Kaizen | Small improvements, not big rewrites | Targeted fixes, no unnecessary refactoring proposed | code, ops | Architecture reviews (suppresses necessary big changes) |
| Shoshin | Beginner's mind — read it fresh | Fresh observations not anchored on prior reviews, "I noticed X" language | code, architecture | Iterative work on same file (you *should* carry context between edits) |
| First Principles | Decompose to fundamentals | "Why does this exist?" questioning, derivation from base constraints | architecture, planning | Bug fixes (too slow for urgent issues) |
| Wabi-sabi | Accept imperfection — working code has value | Explicit "this is fine because..." for working but imperfect code | code | Security reviews (imperfection is not acceptable there) |
| Wu Wei | Don't force it — find the natural path | Framework-aligned solutions, no fighting the platform | code, architecture | Urgent bug fixes (sometimes you must force a workaround) |

## Axis 2: Structural (How to Output)

| Handle | One-liner | Evidence | Domain | Avoid |
|--------|-----------|----------|--------|-------|
| MECE | No overlaps, no gaps | Categories don't overlap, every finding is placed exactly once | any | Adversarial passes (causes axis leakage — fills cells instead of following threads) |
| Pyramid Principle | Answer first, detail below | Verdict in first sentence of each section | any | Exploratory research (you don't know the answer yet) |
| Eisenhower Matrix | Urgent × Important quadrants | 2×2 categorisation with clear placement rationale | planning, ops | Code reviews (forced quadrant placement is unnatural) |
| BLUF | Bottom line up front | First sentence is the conclusion | any | Exploratory research (same as Pyramid — premature conclusions) |
| Five Whys | Chain root cause analysis | Explicit causal chain (≥3 levels deep) | code, ops | Architecture reviews (wrong tool — use Pre-mortem instead) |

## Axis 3: Pattern-Oriented (What to Recognise)

| Handle | One-liner | Evidence | Domain | Avoid |
|--------|-----------|----------|--------|-------|
| Gang of Four | 23 design patterns | Named patterns identified with rationale | code, architecture | Simple scripts, config changes |
| Fowler's Catalog | Code smells → named refactorings | Named smells (Feature Envy, Long Method, etc.) with locations | code | Architecture reviews (wrong level of abstraction) |
| SOLID | Five OO design principles | Each violation mapped to specific principle (S/O/L/I/D) | code | Non-OO code, declarative metadata |
| DDD | Think in business domains, not tables | Bounded contexts identified, ubiquitous language used | architecture | Bug fixes, small features |
| Feathers' Legacy Code | Safe refactoring of untested code | Characterisation tests proposed, seams identified | code | Greenfield code (no legacy to protect) |
| Kent Beck's Four Rules | Tests, intention, no duplication, minimal | Four rules applied in priority order | code | Prototype/spike code (rules suppress necessary experimentation) |
| Hexagonal | Ports and adapters, depend inward | Dependency direction analysed, infrastructure vs domain boundaries | architecture | Small utilities, single-class changes |
| 12-Factor | Config/env/stateless/disposable | Factor-by-factor assessment where relevant | ops, architecture | Pure business logic reviews |

## Axis 4: Adversarial (What to Break)

| Handle | One-liner | Evidence | Domain | Avoid |
|--------|-----------|----------|--------|-------|
| Red Team | Think like an attacker | Attack vectors described with exploitation steps | security | Non-security contexts without explicit scoping |
| Pre-mortem | It already failed — why? | "Assume this failed in production. Here is why." | any | Low-risk changes (hallucinated risk — see anti-patterns) |
| STRIDE | Six threat categories | Findings categorised by S/T/R/I/D/E | security | Non-security reviews (forced categories produce noise) |
| Muda | Find the seven wastes | Named wastes (dead code, overprocessing, etc.) with locations | code, ops | Greenfield code (nothing to waste yet) |
| Andon | Stop the line on first defect | Critical findings flagged with STOP/HALT language | any | Planning phases (premature stop signals) |
| Devil's Advocate | Argue against even if you agree | Counterarguments to proposed solution | planning, architecture | Already-decided work (demoralising — argue *before* the decision, not after) |
| Chaos Engineering | Inject failures deliberately | "What if X is null? Empty? Down? Timeout?" with traced consequences | code, ops | Design reviews (no code to trace yet) |

## Axis 5: Contextual (How to Size It)

| Handle | One-liner | Evidence | Domain | Avoid |
|--------|-----------|----------|--------|-------|
| Cynefin | Simple / Complicated / Complex / Chaotic | Problem explicitly categorised with approach matched to category | any | Rapid iteration (categorisation overhead slows tight loops) |
| Poka-yoke | **Preventative:** make the wrong thing impossible | Guards/constraints identified or proposed, not just warnings | code, ops | Exploratory prototyping (over-constraining kills experimentation) |
| Jidoka | Quality at the source | Quality checks at point of creation, not as afterthought | code, ops | Spike/throwaway code (quality gates slow learning) |
| YAGNI | Don't build what's not needed | Scope limited to what's asked, speculative features rejected | code, planning | Architecture reviews (sometimes you DO need it) |
| Occam's Razor | Simplest solution wins | Simpler alternative chosen over more complex one with justification | any | Genuinely complex domains (dismisses real complexity as "must be simpler") |
| Theory of Constraints | Find the bottleneck first | Bottleneck identified before optimising elsewhere | ops, architecture | Code reviews (no system-level bottleneck to find) |

## Recipes

```
Config change:       Poka-yoke + YAGNI
Code review:         Shoshin + Genba + Fowler's Catalog + Pyramid Principle
Architecture:        Cynefin + DDD + Hexagonal + Pre-mortem
Security:            Red Team + STRIDE + Andon
Bug investigation:   Genba + Five Whys + First Principles
Legacy modification: Feathers' Legacy Code + Shoshin + Kaizen
Design doc review:   Genba + MECE + Pre-mortem + Poka-yoke
Doc chain review:    First Principles + Genba + MECE
Retrospective:       Genba + Pre-mortem + Five Whys
Design generation:   Cynefin + First Principles + MECE + Pre-mortem
Performance:         Theory of Constraints + Genba + Muda
```

## Axis Contract Template

```
AXES:         [2-3 named handles]
TARGET:       [specific artifacts — files, endpoints, docs]
STRUCTURE:    [output format handle]
EVIDENCE:     [proof-of-work rules from the Evidence column above]
              Critical findings must include verbatim snippet (≤25 words) from source.
ASSUMPTIONS:  [maintain a Verified/Unknown ledger of all assumptions made]
STOP:         [when to halt or escalate]
```