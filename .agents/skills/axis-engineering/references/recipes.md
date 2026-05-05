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

## Prism Protocol Recipes

Use Prism for **modelling**: turning raw customer materials (SOWs, transcripts, samples) into a stable, reviewable outline of the system. Different problem from Triangle — Prism asks "which viewpoint are we missing?", not "which constraint do we sacrifice?".

**Phase 1 — Single-agent refraction (default mode):**

```
You are running the Prism Protocol on a modelling task.

INVOCATION:
  industry:    [e.g. insurance.mga]                    // dotted-path config
  stack:       [e.g. salesforce + mga-overlay + fsc]   // composed substrate
  materials:   [SOW, transcripts, samples, …]
  requirement: [the requirement statement]

AXES: Genba + MECE + Cynefin + Pre-mortem

REFRACTION (walk three lens-sets in order):
  1. Actor lenses — set is industry-specific (loaded from industry config).
     Each lens asks "what do I need from this system to do my job?"
     Cite source materials for every lens that fires. Honest "fires weakly"
     or "doesn't fire because [reason]" is signal, not failure — do not pad.
  2. Implementation lenses — substrate stdlib first, overlay pattern second,
     customer extension only with rationale.
  3. Lifecycle lenses — Day-1 launch, Year-3 maintenance, Year-5 schema-shift.

SEESAW (during refraction, watch for):
  - Actor-view ↔ model imbalance (stakeholder doesn't fit any model slot)
  - Model ↔ framework imbalance (model can't sit in stdlib + overlay)
  - Lifecycle imbalance (Day-1 model breaks under Year-3 / Year-5)
  Each imbalance is a ticket to log, not a problem to paper over.

OUTPUT (three distinct artefacts, not interleaved):
  1. Model fragment — objects, fields, relationships, status state machines
  2. Seesaw log — imbalances surfaced, with signal and forced action
  3. Open questions — real ambiguities, each with audience for resolution

STOP: Andon — halt if a requirement is genuinely contradictory across two
      actor lenses (requirements-level ambiguity; resolve before continuing).
```

**Phase 1b — Multi-agent refraction (high-stakes / ambiguous requirements):**

Run N=2 (or N=3) agents in parallel under context isolation. Each receives the identical Phase 1 prompt above — same protocol, same materials, same industry+stack, same requirement. Agents must not see each other's output.

```
You are Agent A (or B, or N) in a Prism Protocol multi-agent run.
[Identical Phase 1 prompt — see above]
You will not see other agents' output. Synthesis happens after all complete.
```

**Phase 2 — Synthesis (multi-agent only):**

```
AXES: MECE + First Principles
TARGET: N agent outputs (model fragments + seesaw logs + open questions)
TASK: Compare and synthesise. Do NOT pick a winner — the human decides.
STRUCTURE:
  - Convergence (multiple agents agreed — high confidence)
  - Divergence (genuine architectural choices the human must decide)
  - Unique catches (an edge case caught by only one agent)
  - Meta-findings (signals about the protocol's behaviour itself)
EVIDENCE: Cite each agent's output for every comparison point.
          Read all agent outputs in full before writing comparison.
STOP: Flag any case where two agents interpret the same requirement
      differently (requirements-level ambiguity, must be resolved).
```

**Empirical baseline:** N=2 blind runs on insurance.mga regulatory integration produced ~70% finding convergence with 3 architectural divergences and 4 unique edge-case catches per agent. If your synthesis reports >90% convergence, the requirement was overdetermined — default to single-agent next time.

## Seesaw Triggers (cross-cutting)

The Seesaw Principle is a **diagnostic that fires inside other protocols**, not a recipe of its own. When a 3-pole tension surfaces an imbalance during Triangle, Prism, or Two-Pass work, Seesaw fires.

**Subtypes (recognise and name):**

- **Test ↔ Design ↔ Implementation** — testing harness fights the design (e.g., test relies on accessibility-impaired selectors → fix the component, not the test).
- **Test ↔ Design ↔ Component** — test struggles → component-shape problem.
- **User ↔ Design ↔ UI** — UX struggles → design problem, not a UI patch.
- **Actor ↔ Model ↔ Framework** — modelling tension; the subtype that fires inside Prism's refraction.
- **Actor ↔ Design ↔ Implementation** — generalised form (any actor struggling with any implementation is signal to look at the design in the middle).

**Response (always the same):**

```
1. Stop. Name the subtype.
2. Log a ticket — what the imbalance is, which pole struggled, why.
3. Fix the middle pole (design / model). Do not work around at the easier pole.
4. Reference the commit that closes the ticket.
```

**Don't paper over.** Seesaw's discipline is that the visible struggle is *signal* about the upstream artefact, not a problem to suppress with a workaround.

## Selection Algorithm

If unsure which handles to pick:

1. **Size it first** — use Cynefin. Simple → Poka-yoke + YAGNI. Complex → full contract.
2. **Pick one disposition** — how should the agent think? (Genba for verification, Shoshin for fresh eyes, First Principles for deep analysis)
3. **Pick one lens** — what should it look for? (Fowler for smells, SOLID for structure, STRIDE for threats, Chaos Engineering for runtime failures)
4. **Pick one structure** — how should it report? (Pyramid for decisions, MECE for completeness, Five Whys for root cause)
5. **Add adversarial only if risk warrants it** — Pre-mortem for production risk, Red Team for security, Andon for stop-the-line urgency
