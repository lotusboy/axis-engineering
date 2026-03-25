# Axis Engineering — Triangle Protocol

> **Domain-specific companions:** [Salesforce](salesforce-triangle.md) — output skeleton, contracts, and divergence patterns for the platform.
> See also: [main methodology](README.md) | [vocabulary](vocabulary-quick-ref.md) | [two-pass strategy](two-pass-strategy.md)

## The Problem

Axis Engineering is strong at **reviewing** — looking back at existing artifacts. It's weaker at **looking forward** — generating architectures, designs, and plans. This asymmetry exists because LLMs are autoregressive: they commit to the first plausible path and then elaborate on it. Within the first few sentences of a design output, the model is locked into an architecture. Asking "now give me alternatives" produces variations anchored to the first choice, not genuinely independent options.

The single-pass design generation experiment (Ping Vision) demonstrated ~90% architectural match from requirements alone — impressive, but it produced **one design**. The 4 gaps (missing output processor batch, missing NC indirection, missing separate schedulers, missing date sync trigger) weren't wrong — they were **different tradeoff decisions** that were never surfaced as explicit choices because the agent never explored them.

Human engineers know this instinctively: you sketch at least 3 options before committing. The Triangle Protocol brings that discipline to AI-assisted design.

## The Iron Triangle as a Forcing Function

The Iron Triangle (Time, Cost, Quality) is a universal project management constraint. The real insight isn't that you pick one — it's that you **pick two and the third suffers**. Nobody walks into a room and says "I only care about quality." They say "I want it right and I want it fast — we'll pay whatever it takes." That's a real engineering position. A single corner is a caricature.

Three pairs, three sacrifices:

| Agent | Optimises | Sacrifices | Engineering Voice | Pair-Specific Handles |
|-------|-----------|------------|-------------------|---------------------|
| **TQ** | Time + Quality | Cost | "Ship it fast and ship it right — we'll absorb the expense" | First Principles, Pre-mortem |
| **TC** | Time + Cost | Quality | "Ship it fast and ship it cheap — accept the tech debt" | YAGNI, Theory of Constraints |
| **CQ** | Cost + Quality | Time | "Build it right and build it to last — take as long as it needs" | Muda, Kent Beck's Four Rules |

The handle assignments are initial pairings validated in a single experiment (N=1). They produced genuine divergence on that test case, but different handle assignments may work better for different problem domains. The constraint pairing (TQ/TC/CQ) is the load-bearing mechanism — the handles amplify it but aren't the only valid combination.

Each pair produces a **viable, shippable design** — not a thought experiment. The sacrifice is what creates divergence:

- **TQ sacrifices Cost** → may over-engineer with more moving parts, higher ops burden, but it ships fast and works correctly
- **TC sacrifices Quality** → may under-spec edge cases, accumulate tech debt, but it ships fast and stays cheap
- **CQ sacrifices Time** → may over-design upfront, take longer to first delivery, but it's maintainable and robust

These aren't labels — they're **different handle cocktails** that produce different designs because they activate different knowledge clusters in the model's training data. And because each agent optimises for *two* constraints, every design is viable enough to actually ship — the question is which tradeoff the team prefers.

## How It Works

### Phase 1: Diverge (3 Parallel Agents)

Three agents run independently, each in a **fresh context** with no visibility of the others. Each receives the same requirements but a different Axis Contract weighted by its triangle pair.

All agents share a **baseline** of `Cynefin + MECE` — Cynefin prevents misjudging complexity domains (applying YAGNI to a Complex problem), and MECE forces completeness checking so no agent silently drops requirements. Each agent adds 2 pair-specific handles, keeping the total at 4 (within the tested sweet spot — see Anti-patterns § Over-stacking in the README).

**Isolation principle:** Agents must not know that other agents exist or what constraints they're operating under. Each agent believes it is producing the only design. This prevents differentiation-seeking behavior (trying to be "different" rather than genuinely good under its constraint).

All agents use a **common output skeleton** to make synthesis structurally tractable:

```
OUTPUT SKELETON:
  1. Executive Summary (Pyramid Principle — answer first, ≤10 lines)
  2. Cynefin Assessment (Simple / Complicated / Complex domains)
  3. Data Model (entities, schemas, relationships — adapt to your domain)
  4. Configuration (environment-specific settings, credentials, feature flags)
  5. Component Inventory (modules/classes/services with responsibilities)
  6. Key Design Decisions (each citing requirement + constraint influence)
  7. What This Design Sacrifices (explicit acknowledgment of the tradeoff)
  8. Components Considered and Rejected (what was NOT built, and why)
  9. Work Estimate (component count, approximate complexity per component)
  10. Assumption Ledger
```

**Adapt sections 3-5 for your domain.** The skeleton above is intentionally generic. A Salesforce project might have "Custom Objects / CMDT / Apex Classes" — see `salesforce-triangle.md` for the full Salesforce-specific skeleton and ready-to-use contracts. A React frontend might have "State Management / API Contracts / Component Tree." A data pipeline might have "Schema / DAG / Storage Layer." What matters is that all three agents use the **same** skeleton — the synthesis agent depends on structural alignment for MECE comparison. Define the skeleton before running agents.

Section 7 is critical — forcing each agent to explicitly name its sacrifice gives the synthesis agent a direct comparison point and prevents agents from quietly minimising their tradeoff. Section 8 is valuable when present — CQ's Muda handle naturally produces it, but requiring it from all agents gives the synthesis richer comparison material.

#### Agent TQ — Time + Quality (sacrifice Cost)

```
AXES:         Cynefin + MECE + First Principles + Pre-mortem
TARGET:       [requirements document]
CONSTRAINT:   Optimise for TIME and QUALITY. Ship fast and ship correctly.
              Accept higher operational cost, more infrastructure, larger team burden
              if it means delivering a robust solution sooner.
              Your sacrifice (Cost) is a deprioritisation, not an elimination.
              Ask: "What's the best architecture if we can throw resources at it?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the common output skeleton (sections 1-10).
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Time+Quality priority influenced it.
              If a choice would be the same regardless of constraint, say so.
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
STOP:         Andon — halt if a design choice creates a single point of failure
              or violates a hard constraint.
```

**Observed tendency:** Well-separated modules with clear responsibilities, comprehensive error handling, but potentially more moving parts than necessary. May produce separate components for each concern, extensive config surface. Ships fast because it doesn't agonise over simplification — it builds the "right" thing and accepts the ops burden. First Principles drives decomposition; Pre-mortem catches failure modes that would delay delivery if discovered later. (In the Ping experiment, TQ produced 10 functional classes + 4 schedulers — the most components of any agent.)

#### Agent TC — Time + Cost (sacrifice Quality)

```
AXES:         Cynefin + MECE + YAGNI + Theory of Constraints
TARGET:       [requirements document]
CONSTRAINT:   Optimise for TIME and COST. Ship fast and ship cheap.
              Accept reduced robustness, less test coverage, thinner error handling
              if it reduces delivery time and operational surface.
              Your sacrifice (Quality) is a deprioritisation, not an elimination.
              Ask: "What is the minimum viable architecture?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the common output skeleton (sections 1-10).
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Time+Cost priority influenced it.
              Every simplification must state what quality it sacrifices and why that's acceptable.
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
STOP:         Andon — halt if a simplification would violate a hard constraint
              or make the system unshippable.
```

**Observed tendency:** Fewer modules, combined responsibilities where safe, direct implementations over abstractions, minimal configuration surface. May merge processing logic into a single component, skip edge-case handling for unlikely scenarios, reduce config to essentials. The MVP — gets to market but may need hardening later. YAGNI strips non-essential components; Theory of Constraints focuses effort on the bottleneck. (In the Ping experiment, TC produced 5 classes with a single consolidated processing pipeline — the leanest of any agent.)

#### Agent CQ — Cost + Quality (sacrifice Time)

```
AXES:         Cynefin + MECE + Muda + Kent Beck's Four Rules
TARGET:       [requirements document]
CONSTRAINT:   Optimise for COST and QUALITY. Build it right and build it to last.
              Accept longer delivery timeline if it means lower TCO, cleaner architecture,
              and less cognitive load for the team maintaining it over 2+ years.
              Your sacrifice (Time) is a deprioritisation, not an elimination.
              Ask: "What will a new developer understand in 6 months?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the common output skeleton (sections 1-10).
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Cost+Quality priority influenced it.
              Every component must justify its existence — if it's waste (Muda), cut it.
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
STOP:         Andon — halt if a design choice introduces unnecessary operational fragility
              or maintenance burden.
```

**Observed tendency:** Clean architecture with minimal dependencies, explicit over implicit, boring technology choices. Tends to land between TQ and TC in component count, but this is emergent — not guaranteed. Muda eliminates unnecessary components; Kent Beck's Four Rules (passes tests, reveals intention, no duplication, fewest elements) drives toward the simplest correct design. The "do it once, do it right" approach. (In the Ping experiment, CQ produced 7 functional classes — between TC's 5 and TQ's 10 — with the most thorough "Components NOT Built" justification section.)

### Phase 2: Synthesize (1 Agent, Fresh Context)

A fourth agent receives all three design outputs. It does **not** pick a winner. Its job is structured comparison.

```
AXES:         Cynefin + MECE + First Principles
TARGET:       Agent TQ output, Agent TC output, Agent CQ output
TASK:         Compare and synthesize three architecture proposals.
              Do NOT pick a winner — the human decides.
              Do not use language like "best", "recommended", "preferred",
              or conditional recommendations like "lean toward" or "consider choosing".
              Present options with tradeoffs only. Every comparison must state
              what is gained AND what is lost.
STRUCTURE:    MECE (no overlaps, no gaps in comparison)
OUTPUT:
  0. EXECUTIVE SUMMARY — 10 lines max. How many convergence points, how many
     divergence points, and the single highest-stakes tradeoff the human must decide.
  1. CONVERGENCE — Where all three agents independently made the same choice.
     (High-confidence decisions — likely correct regardless of constraint priority.)
  2. DIVERGENCE — Where agents made different choices, with each agent's rationale.
     (Genuine tradeoff zones requiring human judgment.)
  3. TRADEOFF MATRIX — For each divergence point: what you gain, what you lose,
     under each constraint pair.
  4. EFFORT COMPARISON — For each design: component count, estimated complexity
     (Simple/Medium/Complex per component), and relative implementation size.
     Normalise estimates to a common unit (hours or days) for direct comparison.
     (Drawn from each agent's Section 9: Work Estimate.)
  5. HYBRID OPPORTUNITIES — Combinations that take the best of each
     (e.g., TQ's architecture with TC's simpler data layer).
     Effort estimates for hybrids should use ranges (e.g., "60-75 hours")
     to reflect the uncertainty of combining approaches.
  6. RISK REGISTER — Pre-mortem for each hybrid: what fails if this combination
     doesn't hold together?
  7. BLIND SPOTS — Requirements from the input document that no agent addressed,
     or that all three agents handled identically without justification.
     Priority-rank each blind spot:
       P0 = blocks architecture choice (e.g., requirements contradiction)
       P1 = must resolve before sprint planning
       P2 = can resolve during or after implementation
     (These may indicate ambiguous requirements that need human clarification.)
  8. NEXT STEPS — Sequence the decisions the human needs to make.
     State prerequisites ("resolve blind spot X before choosing Y").
     Do NOT recommend which option to choose — only state the order of decisions
     and what information is needed for each.
EVIDENCE:     Every comparison point must cite the specific section from each agent's output.
              Read all three designs in full before writing any comparison.
STOP:         Flag any case where an agent's output contradicts the requirements.
              Flag any case where two agents interpret the same requirement differently —
              this indicates a requirements ambiguity that must be resolved before design.
```

### Phase 3: Decide (Human)

The synthesis output is a **decision aid**, not a decision. The human reviews:

1. **P0 blind spots first** — resolve any requirements contradictions or ambiguities before making architecture decisions. When agents interpret the same requirement differently, that's a signal the requirement needs clarification, not that one agent is wrong.
2. **Convergence points** — adopt these with confidence (all three agents agree)
3. **Divergence points** — make explicit tradeoff decisions based on project priorities
4. **Hybrid options** — consider cherry-picking across designs where compatible

This is the step that single-agent design generation skips entirely. The human gets to see the solution space, not just one point in it.

### Phase 3b: AI-Augmented Selection (Optional)

The synthesis output is structured data: convergence points, divergence points with tradeoffs, hybrid options with effort ranges, and prioritised blind spots. This structure makes it consumable not just by humans but by a subsequent AI agent fed **real project constraints**.

```
AXES:         First Principles + MECE
TARGET:       Synthesis output (from Phase 2)
CONSTRAINTS:  Real project parameters:
              - Timeline: [actual deadline or sprint boundary]
              - Budget: [actual hours/headcount available]
              - Quality floor: [actual non-negotiable requirements — SLAs, compliance, etc.]
TASK:         Given the synthesis and these constraints, recommend which design
              (or hybrid) best fits. For each recommendation, state:
              1. Which constraint drove the choice
              2. What is sacrificed and whether the sacrifice is acceptable
                 given the stated constraints
              3. What changes if any constraint shifts (sensitivity analysis)
EVIDENCE:     Every recommendation must trace back to a specific divergence point
              or hybrid option in the synthesis output.
STOP:         Flag if the stated constraints are contradictory
              (e.g., timeline requires TC's approach but quality floor requires CQ's).
```

This turns the protocol from a **decision aid** into an **end-to-end pipeline**: requirements → 3 designs → synthesis → constraint-informed recommendation → human approval. The human still has final say, but the decision is now grounded in actual project parameters rather than gut feel.

**When to use Phase 3b:**
- The tradeoffs are well-understood but the constraint data is complex (e.g., partial team availability, phased budget, multiple deadlines)
- The decision-maker wants a starting recommendation to react to rather than a blank canvas
- The project has quantified constraints that an AI can reason about (hours, headcount, SLA numbers)

**When to skip Phase 3b:**
- The tradeoffs involve organisational or political factors that aren't captured in T/C/Q numbers
- The decision-maker prefers to work directly from the synthesis
- The constraints are obvious enough that the recommendation would be trivial

### Phase 4: Retrospective (Optional)

After the human decides, record:
- Which convergence/divergence points influenced the decision
- Whether any finding would have been missed by a single-agent run
- Whether the protocol was overkill (>90% convergence means the problem was overdetermined)

This feedback loop is what turns the protocol from a one-off exercise into a calibrated tool. Without it, teams cannot judge when to use the protocol vs single-pass generation.

## Output Structure

```
testing/triangle-[project]-agent-tq.md     ← Time + Quality design (sacrifice Cost)
testing/triangle-[project]-agent-tc.md     ← Time + Cost design (sacrifice Quality)
testing/triangle-[project]-agent-cq.md     ← Cost + Quality design (sacrifice Time)
testing/triangle-[project]-synthesis.md    ← Comparison, hybrids, and blind spots
```

## Why Three Agents, Not Three Prompts

Asking one agent to "give me 3 options" in a single context produces anchored variations:

```
# What actually happens with "give me 3 options":
Option 1: [genuine first-instinct design]
Option 2: [Option 1 with minor changes — anchored]
Option 3: [Option 1 with different minor changes — still anchored]
```

Separate agents with separate contexts produce genuinely independent exploration because:

1. **No shared token history** — Agent CQ cannot be anchored by what Agent TQ generated
2. **Different handle cocktails** — each agent's Axis handles activate different knowledge clusters
3. **Different constraint pairing** — "fast and correct" vs "fast and cheap" vs "correct and cheap" produces fundamentally different first tokens, which cascade through the entire generation
4. **Viable by construction** — because each agent optimises for *two* constraints, every design is shippable, not a thought experiment. The question is which tradeoff the team prefers

This is the same principle as the two-pass strategy (fresh context beats continued context), extended from review to generation.

## Relationship to Existing Strategies

The Triangle Protocol is a **meta-layer** that sits above the existing Axis Engineering toolkit:

```
┌─────────────────────────────────────────────┐
│              Triangle Protocol              │  ← NEW: explores the solution space
│         (3 agents + synthesis)              │
├─────────────────────────────────────────────┤
│           Axis Contracts + Handles          │  ← Each agent uses these internally
├─────────────────────────────────────────────┤
│         Two-Pass Strategy (optional)        │  ← Can review each agent's output
├─────────────────────────────────────────────┤
│              Single-Pass Recipes            │  ← The building blocks
└─────────────────────────────────────────────┘
```

Each triangle agent runs Axis Engineering internally — selecting handles, following contracts, producing evidence. The triangle doesn't replace the methodology; it orchestrates multiple instances of it under different constraints.

### Combining with Two-Pass

For high-stakes architecture decisions, you can run a two-pass review on each agent's output before synthesis:

1. **Triangle Phase 1:** 3 agents generate designs (3 outputs)
2. **Two-pass review:** Each design is reviewed independently — analytical pass then adversarial pass (6 review agents, each reviewing one design against the requirements, not cross-reviewing other agents' designs)
3. **Triangle Phase 2:** Synthesis agent receives designs + their reviews (informed comparison)

This is expensive (10 agent invocations) but appropriate for foundational architecture that will live for years.

### End-to-End Pipeline

The maximum configuration runs the full pipeline:

1. **Phase 1:** 3 agents generate designs
2. **Two-pass review:** 6 review agents (optional)
3. **Phase 2:** Synthesis agent
4. **Phase 3b:** AI selection agent with real T/C/Q constraints (optional)
5. **Phase 3/4:** Human decision + retrospective

This is 11 agent invocations at maximum. In practice, most projects will run Phases 1 → 2 → 3 (4 agents) and use Phase 3b only when the constraint data is complex enough to warrant it.

## When to Use

The Cynefin domain is the strongest signal:

```
Is this a Complex domain problem (right architecture unclear upfront,
  multiple viable approaches with genuine tradeoffs)?
    → Triangle Protocol

Is this a Complicated domain problem (architecture is known/deterministic,
  e.g., trigger + callout, field mapping, integration wiring)?
    → Single-pass design generation (Cynefin + First Principles + MECE + Pre-mortem)

Is this a review of an existing design?
  → Two-pass strategy or single-pass with contract
```

**Rule of thumb:** If the "right" architecture depends on which tradeoff you're willing to accept, use the Triangle Protocol. If the architecture follows deterministically from the requirements, use single-pass — the Triangle Protocol will produce 3 near-identical designs and waste tokens.

The 3-4x token cost and 1-2 hour human review time means the protocol should be reserved for decisions that persist. A cancellation flow with three genuinely different architectural approaches (hook vs toggle vs flow override) is worth exploring. A CRUD integration with a known pattern is not.

## Expected Benefits

1. **Requirements ambiguity detection** — when agents interpret the same requirement differently, that's a signal the requirement is ambiguous. A single agent silently picks one interpretation; three agents surface the disagreement. In the Ping experiment, the synthesis agent flagged a requirements contradiction (whether "Cleared" was an outbound status change) that would have been discovered during implementation otherwise.
2. **Solution space exploration** — the human sees 3 genuinely different architectures, not 1
3. **Explicit tradeoffs** — divergence points become visible decisions, not silent omissions
4. **Convergence signal** — when all 3 agents independently reach the same conclusion, that's strong evidence it's correct
5. **Anchoring prevention** — fresh contexts prevent the "first idea" lock-in that plagues single-agent generation
6. **Handle diversity** — each constraint naturally selects different handles, producing genuinely different cognitive processes

## Expected Costs

1. **3-4x token usage** — three design agents + one synthesis agent vs one design agent
2. **Synthesis complexity** — the fourth agent must compare three full designs without losing detail
3. **Human review time** — the synthesis output is substantial (the Ping experiment produced ~400 lines of comparison with 7 convergence, 6 divergence, 4 hybrids, and 8 blind spots). Budget 1-2 hours for the human to review the synthesis and make decisions, compared to 30-60 minutes for a single-agent design
4. **Human decision load** — the human now has to choose, which is harder than accepting a single proposal (but produces better outcomes)

## Failure Modes

### Convergence masquerading as independence

If the requirements are highly constrained, all three agents may produce nearly identical designs regardless of their triangle corner. This isn't a failure — it's a signal that the architecture is overdetermined by the requirements. The convergence points are genuine; there's just not much divergence to explore.

**Detection:** If the synthesis agent reports >90% convergence, the Triangle Protocol was overkill for this task. Note this for future calibration.

### Synthesis agent anchoring on first input

The synthesis agent reads three designs sequentially. It may give disproportionate weight to whichever it reads first.

**Mitigation:** Randomise the order of inputs to the synthesis agent. Alternatively, instruct it to process all three before beginning comparison: "Read all three designs in full before writing any comparison."

### Constraint caricature

Agents may exaggerate their sacrifice to differentiate themselves (TC produces a God-class; TQ produces astronaut architecture with 100+ components for a low-volume system).

**Mitigation:** The pair-based design reduces caricature (an agent optimising for *two* constraints can't go fully extreme on either axis) but does not eliminate it. In the Ping experiment, TC still produced a single-responsibility violation it explicitly acknowledged, and TQ produced ~105 metadata components for an integration handling fewer than 100 concurrent submissions. The "deprioritisation, not elimination" clause in the default contracts helps — it was added after observing this tendency. The Cynefin baseline forces complexity sizing, the MECE baseline forces completeness, and the STOP clause (Andon) guards against designs that violate hard requirements. If caricature persists, strengthen the STOP clause to explicitly halt on designs that are disproportionate to the stated requirements.

### Requirements ambiguity surfaced by agent disagreement

When agents interpret the same requirement differently, this is the protocol's most valuable output — not a failure. A single agent silently picks one interpretation and builds on it. Three agents may pick different interpretations, and the synthesis agent flags the disagreement.

**Detection:** The synthesis agent's STOP clause includes: "Flag any case where two agents interpret the same requirement differently." These should appear in the blind spots section as P0 blockers.

**Example:** In the Ping experiment, requirement 3 stated "Data Entry is the ONLY outbound status change." TC took this literally. TQ and CQ both designed Cleared as an additional outbound status change. The synthesis agent flagged this as a P0 contradiction requiring human resolution before any architecture choice.

### Context window pressure

Full design outputs can be long. In the Ping experiment, individual designs ranged from ~420 to ~790 lines, with ~1,900 lines total to the synthesis agent. Larger projects would produce longer outputs.

**Mitigation:** Each agent produces a structured summary section (Pyramid Principle — answer first) at the top. However, the synthesis agent should read all designs in full — working only from summaries risks missing detail-level contradictions that are the protocol's most valuable output (the Cleared status contradiction in the Ping experiment was only visible in specific component definitions, not summaries). If context pressure is a concern, consider splitting the synthesis into two passes: a structural comparison pass (summaries only) followed by a detail pass on divergence points.

## Implementation

The Triangle Protocol requires running 3 independent agents in parallel, then feeding their outputs to a 4th. How you do this depends on your environment:

### Claude Code (subagents)

Launch all three diverge agents in a single message using the Agent tool. Each runs in its own fresh context with no visibility of the others. When all three complete, launch the synthesis agent with their outputs concatenated.

```
# Single message with 3 parallel Agent tool calls:
Agent TQ: "Read [requirements]. Apply this Axis Contract: [TQ contract]. Produce a complete solution design."
Agent TC: "Read [requirements]. Apply this Axis Contract: [TC contract]. Produce a complete solution design."
Agent CQ: "Read [requirements]. Apply this Axis Contract: [CQ contract]. Produce a complete solution design."

# After all three return:
Agent Synthesis: "Read these three designs: [TQ output], [TC output], [CQ output].
                  Apply this Axis Contract: [synthesis contract]."
```

### Manual (separate sessions)

Open 3 separate chat sessions. Paste the same requirements into each with a different contract. Copy the 3 outputs into a 4th session for synthesis. This is the simplest approach and guarantees context isolation.

### API (programmatic)

Three parallel `messages.create` calls with different system prompts (one per contract). Concatenate responses into a 4th call for synthesis. Suitable for automation or CI/CD integration.

## Experiment Results

The Triangle Protocol was tested against the Ping Vision integration requirements — the same requirements used for the original single-agent design generation experiment.

### Setup

- **Input:** `testing/ping-requirements-only.md` (271-line pure requirements document)
- **Agents:** TQ, TC, CQ running in parallel as Claude Code subagents with full context isolation
- **Synthesis:** Fourth agent comparing all three outputs
- **Baseline comparison:** Original single-agent design (781 lines, ~90% architectural match with human-built solution, 4 silent gaps)

### The 4 original gaps — did they surface?

| Original Silent Gap | Surfaced? | Where in Synthesis |
|---|---|---|
| Missing dedicated output processor batch | **Yes** | Divergence 2.1 — the #1 divergence point. TQ/CQ built separate output processors; TC consolidated. Synthesis called this "the single highest-stakes tradeoff." |
| Missing separate scheduler classes | **Yes** | Divergence 2.1 — TQ: 4 schedulers, CQ: 4 schedulers, TC: 0 (self-scheduling batch). Explicitly compared in effort table. |
| Missing Named Credential indirection | **Yes** | Convergence 1.2 (all agents used Named Credentials) + Divergence 2.4 (shared API client vs inline callouts). |
| Missing Case-to-submission date sync trigger | **Yes** | Divergence 2.3 — CQ's user-driven pattern requires a Case trigger to sync dates; TC/TQ automate inception date retrieval instead. |

**4/4 gaps surfaced as explicit design choices.** What the single-agent approach silently omitted, the Triangle Protocol surfaced as divergence points with tradeoff analysis.

### Bonus finding: requirements contradiction

Beyond the original 4 gaps, the synthesis agent flagged a **requirements contradiction** that no single-agent run had detected: requirement 3 states "Data Entry is the ONLY outbound status change," but TQ and CQ both designed Cleared as an additional outbound status change. TC took the requirement literally. This disagreement surfaced an ambiguity in the requirements that would otherwise have been discovered during implementation.

### Agent output summary

| Agent | Functional Classes | Schedulers | Test Classes | Total Components | Effort |
|---|---|---|---|---|---|
| **TC** (Time+Cost) | 5 | 0 | ~4 | ~92 | ~55 hours |
| **CQ** (Cost+Quality) | 7 | 4 | 12+ | ~112 | ~105 hours |
| **TQ** (Time+Quality) | 10 | 4 | 11 | ~105 | ~100 hours |

### Synthesis output

7 convergence points, 6 divergence points, 4 hybrid opportunities, 8 blind spots (1 P0, 5 P1, 2 P2). Full outputs in `testing/triangle-ping-*.md`.

### Limitations

This is N=1 on a single domain (Salesforce/Apex integration). The hypothesis is confirmed for this problem class, but generalisability to other domains (frontend, data pipelines, mobile) is untested. The handle assignments, output skeleton, and caricature mitigations all need further testing across different project types.

## Related Work

The Triangle Protocol combines several ideas — multi-agent generation, constraint-based divergence, structured synthesis — in a way that appears novel as of early 2026. The closest related work uses **debate and argumentation** mechanisms rather than **constraint-optimised independent generation**. The key difference: debate-based approaches have agents argue with each other; the Triangle Protocol has agents work independently under different constraints, with a separate synthesis agent comparing the results.

### Multi-Agent Debate for Requirements Engineering (MAD for RE)

Ataei & Litchfield (2025) propose using multi-agent debate — agents with opposing viewpoints argue through multiple rounds — to improve requirements engineering tasks like ambiguity detection and completeness checking. The mechanism is adversarial argumentation: agents critique each other's positions until consensus or stalemate.

**How the Triangle Protocol differs:** Triangle agents never see each other's output and never argue. Divergence emerges from different constraint pairings, not from debate. The synthesis agent compares independently-generated designs rather than moderating an argument. This avoids the anchoring problem inherent in debate (agent B's response is conditioned on agent A's position).

### SWE-Debate

Zhang et al. (2025) apply competitive multi-agent debate to software engineering issue resolution. Multiple agents propose and critique solutions through structured rounds, with a judge agent selecting the winning approach.

**How the Triangle Protocol differs:** SWE-Debate operates on issue resolution (bug fixes, small features) where there's typically one correct answer. The Triangle Protocol operates on architecture design where multiple answers are genuinely viable — the question is which tradeoff to accept. Triangle agents produce complete designs, not arguments; the synthesis agent compares rather than judges.

### Ambig-SWE

Gu et al. (2026) introduce a benchmark for evaluating how AI agents handle underspecified requirements. Agents must detect ambiguity through interaction (asking clarifying questions) rather than through comparison of independently-generated outputs.

**How the Triangle Protocol differs:** Ambig-SWE tests single-agent ambiguity detection via interaction with the user. The Triangle Protocol detects ambiguity as an emergent property — when agents interpret the same requirement differently under different constraints, the synthesis agent flags the disagreement. No agent is explicitly tasked with finding ambiguities; the protocol's structure surfaces them.

### What the Triangle Protocol adds

The specific combination appears to be novel:

1. **Iron Triangle as forcing function** — using project management constraint pairs (not debate roles or personas) to generate genuinely different designs
2. **Context isolation** — agents work independently with no knowledge of each other, preventing anchoring
3. **Handle cocktails** — each constraint pair selects different Axis Engineering handles, activating different knowledge clusters in the model
4. **Convergence/divergence synthesis** — a structured comparison that distinguishes high-confidence decisions (convergence) from genuine tradeoffs (divergence), rather than picking a winner
5. **Requirements ambiguity as emergent signal** — not a design goal, but a structural consequence of running three independent interpretations against the same input

The closest conceptual ancestor is the Hegelian dialectic applied to information systems (Mason, 1969; Mitroff & Emshoff, 1979) — thesis, antithesis, synthesis — but the Triangle Protocol uses three positions rather than two, and the positions are defined by engineering constraints rather than opposing worldviews.