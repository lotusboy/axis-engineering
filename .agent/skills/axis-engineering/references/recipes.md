# Axis Engineering: Extended Recipe Catalog

## Light Touch

**Config change / field addition:**
```
Apply Poka-yoke and YAGNI.
```

## Code Review

**Standard code review:**
```
Approach with Shoshin and Genba. Apply Fowler's Refactoring Catalog.
Output using Pyramid Principle.
```

**Deep code review (two-pass):**

Pass 1 (Analytical):
```
AXES: Shoshin + Genba + Fowler's Catalog + SOLID
TARGET: [specific files]
STRUCTURE: Pyramid Principle
EVIDENCE: Every finding cites file:line
```

Pass 2 (Adversarial):
```
AXES: Chaos Engineering + Pre-mortem + Andon
TARGET: [same files as Pass 1 — do NOT read Pass 1 output]
STRUCTURE: BLUF with severity-ordered risks
EVIDENCE: Failure scenarios with triggering conditions
STOP: Andon — halt if data-loss or security vulnerability found
```

## Architecture Review

**Standard architecture review:**
```
Apply Cynefin to categorise, then DDD and Hexagonal Architecture for analysis.
Run a Pre-mortem before concluding.
```

**Solution design generation:**
```
AXES: Cynefin + First Principles + MECE + Pre-mortem
TARGET: [requirements document]
STRUCTURE: Pyramid Principle
EVIDENCE: Every design decision traces to requirement
ASSUMPTIONS: Ledger with Verified/Unknown for each assumption
```

## Security Review

**Standard security review:**
```
Red Team this using STRIDE. Apply Andon — stop on the first critical finding.
```

**Deep security review (four-pass):**
Run two-pass strategy twice with fresh sessions, then deduplicate.

## Bug Investigation

**Standard bug investigation:**
```
Genba mindset. Five Whys for root cause. First Principles if the Five Whys hit a dead end.
```

**Production incident:**
```
AXES: Genba + Five Whys + Andon
TARGET: Error logs, stack traces, relevant source files
STRUCTURE: Five Whys chain + BLUF recommendation
EVIDENCE: Log entries with timestamps, code snippets
STOP: Andon if data corruption or ongoing system damage
```

## Legacy Code

**Legacy code modification:**
```
Feathers' Legacy Code approach. Shoshin — read it fresh.
Kaizen — small safe changes only.
```

## Design Documentation

**Design doc review:**
```
Genba + MECE + Pre-mortem + Poka-yoke.
Verify claims against actual source. Check for completeness gaps.
Grade deliverable readiness.
```

**Documentation chain review:**
```
First Principles + Genba + MECE.
Trace each design decision to its source analysis doc.
Flag decisions without supporting evidence.
```

## Retrospectives

**Implementation retrospective:**
```
Genba + Pre-mortem + Five Whys.
Compare what was designed vs what was built.
Trace deviations to root causes. Assess whether the deviation was justified.
```

## Triangle Protocol Recipes

**Architecture with trade-offs:**

Agent TQ:
```
You are Agent TQ in the Triangle Protocol.
CONSTRAINT: Optimize Time + Quality, sacrifice Cost
[Task description]
OUTPUT: Architecture + Assumptions + Tradeoffs + Risks
```

Agent TC:
```
You are Agent TC in the Triangle Protocol.
CONSTRAINT: Optimize Time + Cost, sacrifice Quality
[Same task, fresh session — do NOT read TQ output]
OUTPUT: Architecture + Assumptions + Tradeoffs + Risks
```

Agent CQ:
```
You are Agent CQ in the Triangle Protocol.
CONSTRAINT: Optimize Cost + Quality, sacrifice Time
[Same task, fresh session — do NOT read TQ/TC outputs]
OUTPUT: Architecture + Assumptions + Tradeoffs + Risks
```

Synthesis:
```
AXES: Cynefin + MECE
TARGET: TQ output, TC output, CQ output
STRUCTURE: Convergences + Divergences + Blind Spots
EVIDENCE: Cite specific agent outputs for each finding
```

## Selection Algorithm

If unsure which handles to pick:

1. **Size it first** — use Cynefin. Simple → Poka-yoke + YAGNI. Complex → full contract.
2. **Pick one disposition** — how should the agent think? (Genba for verification, Shoshin for fresh eyes, First Principles for deep analysis)
3. **Pick one lens** — what should it look for? (Fowler for smells, SOLID for structure, STRIDE for threats, Chaos Engineering for runtime failures)
4. **Pick one structure** — how should it report? (Pyramid for decisions, MECE for completeness, Five Whys for root cause)
5. **Add adversarial only if risk warrants it** — Pre-mortem for production risk, Red Team for security, Andon for stop-the-line urgency
