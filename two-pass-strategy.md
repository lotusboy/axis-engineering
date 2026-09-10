# Axis Engineering — Two-Pass Strategy

## The Problem

No single axis cocktail catches everything. Our A/B/C experiment showed:

- **Dispositional** (Gandharan + Genba) found process/systemic gaps (missing logging, trigger chains)
- **Standard** (no framing) found direct implementation bugs (stale values, field overwrites)
- **Axis Engineering cocktail** found structural quality, waste, and architectural debt

Each missed things the others caught.

## The Solution: Two Sequential Passes

### Pass 1: Wide Net (Axis Engineering Cocktail)

**Purpose:** Comprehensive structured analysis across all dimensions.

**Handles:**
- Dispositional: Seven Factors of Awakening + Genba
- Pattern-oriented: Fowler's Refactoring Catalog + SOLID
- Adversarial: Pre-mortem + Muda
- Structural: MECE + Pyramid Principle

**What it catches:** Completeness gaps, consistency issues, SOLID violations, waste, per-document quality scoring, authority hierarchy, runtime risk scenarios.

**What it misses:** Process adherence gaps (does the code follow the project's own stated rules?), trigger chain side effects, systemic integration issues.

### Pass 2: Focused Verification (Genba + Andon)

**Purpose:** Verify the actual implementation against the project's own rules and patterns. Catch what the structured review missed.

**Handles:**
- Dispositional: Genba (go to the source) + Shoshin (read fresh, don't trust Pass 1)
- Adversarial: Andon (stop on first critical finding) + Chaos Engineering (what if this field is null? this list empty? this API down?)
- Contextual: Poka-yoke (are mistake-proofing guards in place?)

**What it catches:** Process compliance (logging, CRUD checks, sharing rules), trigger cascade effects, null/empty edge cases, missing guards, governor limit risks.

**Key instruction:** "Do NOT read the Pass 1 review. Approach the code fresh. Focus on what could go wrong at runtime that a document review would miss."

## Why Two Passes Instead of One Bigger Cocktail

Over-stacking handles (7+) causes the agent to name-drop all of them superficially. Two focused passes with 3-4 handles each produces deeper analysis than one pass with 8 handles.

The passes are also cognitively different:
- Pass 1 is **analytical** (compare docs to code, categorise findings)
- Pass 2 is **adversarial** (break things, find edge cases, verify guards)

Running them sequentially avoids the agent trying to do both at once.

## Output Structure — save the run

**By default, persist the run to the repository being reviewed.** Create
`axis/runs/<YYYY-MM-DD>-<subject>-two-pass/`. The shape below is a proven **starting** example,
not a fixed rule — of the four Axis protocols it's the one with enough repeated real runs to
generalise from, but even it keeps adapting: a review spanning several components typically needs
one Pass 1 / Pass 2 pair *per component* (`pass1-<component>.md`, `pass2-<component>.md`) rather
than one pair total, and a longer engagement may add its own later-numbered files on top (a
calibration pass, a verification log) once this base shape is in place.

| File | What it is |
|---|---|
| `00-contract.md` | The Axis Contract for the run — axes, target, structure, evidence rule, stop condition |
| `01-pass1-prompt.md` | Pass 1 (analytical) instructions |
| `02-pass2-prompt.md` | Pass 2 (adversarial) instructions |
| `03-synthesis-prompt.md` | Merge instructions |
| `04-pass1-output.md` | Pass 1 result, verbatim |
| `05-pass2-output.md` | Pass 2 result, verbatim |
| `06-synthesis.md` | Merged, deduplicated, severity-ordered findings |

Write the prompts *before* the agents run; keep the outputs unedited, exactly as they came back.
Adapt file names and counts to the run — the invariant that matters is stated below, not this
exact table.

**The same folder convention applies to Prism and Triangle runs**, with the same default-on,
tell-the-user, easy-opt-out discipline — see `prism-protocol.md` and `triangle-protocol.md`.
Neither has a file shape proven stable enough to template the way the table above does; name
their outputs however fits (one per lens, one per agent, or a single consolidated file).

**Why it is worth the files.** A reader — including you in six months — can judge each finding
against the exact instructions that produced it. Without the prompts, a finding is an assertion;
with them, it is reproducible. The isolation is also only verifiable on paper: when both passes
independently reach the same finding and you can see that Pass 2's prompt never mentioned Pass 1,
the convergence is genuine agreement rather than an echo. Committing the folder makes every
review run on a project transparent and reviewable alongside the code it changed.

**Tell the user you did it.** When the run finishes, say plainly what was created and how to
opt out — for example: *"Saved this run under `axis/runs/2026-09-10-billing-api-two-pass/` —
contract, both prompts, both raw outputs, synthesis. Delete the folder or tell me to skip this
next time if you'd rather not keep it."* Do not save silently.

**When to skip.** Don't create the folder if the user asks you not to, if the review is a quick
ad hoc question rather than a real protocol run, or if the target isn't a repository you can
write to. This is a strong default, not a rule — the convention is one that works well in
practice, but the methodology does not depend on it and users should bend it to fit their own
project.

## Merge Contract

The synthesis step needs deterministic rules to avoid drift:

- **Dedupe key:** `(artifact, symptom, root-cause-class)`. Two findings about the same artifact with the same root cause merge into one.
- **Severity:** `max(pass1_severity, pass2_severity)`. If Pass 2 escalates a Pass 1 finding, use the higher severity.
- **Conflicts:** If Pass 2 contradicts Pass 1, prefer Pass 2 if it has stronger evidence (more file:line citations, verbatim snippets). Pass 2 reads code fresh without anchoring on Pass 1.
- **Unique findings:** Anything found by only one pass is included as-is with source attribution.

## Failure Modes

### Pass 2 anchoring on Pass 1

The "Do NOT read Pass 1" instruction is enforced by **agent isolation** in subagent architectures (each pass runs in a separate context). In a single-session workflow where a human runs both prompts sequentially, the model *will* have Pass 1 in context and may anchor on it despite the instruction.

**Mitigation:** For single-session use, run Pass 2 in a new conversation or a separate agent. If that's impractical, instruct Pass 2 to "actively contradict at least 2 Pass 1 findings" — this forces genuine re-examination rather than passive agreement.

### Merge step confabulation

The third agent synthesising two reviews may fabricate connections between findings that don't actually relate, or invent severity escalations not supported by either pass.

**Mitigation:** The merge contract's dedupe key `(artifact, symptom, root-cause-class)` constrains the synthesis. Additionally, require the merge output to cite which pass originated each finding — any finding not traceable to Pass 1 or Pass 2 is suspect and should be flagged.

## Beyond Code Review

The two-pass strategy was developed for code review but the cognitive separation principle applies to any analytical task. Tested applications:

### Design Document Review

**Pass 1:** First Principles + MECE + Genba — trace each claim to evidence, check completeness
**Pass 2:** Pre-mortem + Chaos Engineering + Poka-yoke — assume the design will fail, find why

Applied to the Wildfire API Solution Design (687 lines). Pass 1 found completeness gaps and field type mismatches (Genba verified actual metadata). A single-pass approach with all handles combined would likely have been shallower on both dimensions.

### Documentation Chain Review

**Single pass** (First Principles + Genba + MECE) is usually sufficient for doc chains because the task is traceability, not adversarial analysis. The question is "does each decision have a documented reason?" — not "what could go wrong at runtime?"

Applied to the 8-doc rater analysis chain (docs/rater/00-07 → 08 → 09). Assessed completeness at 85%. Every design decision traced to source. Caught that a blocking configuration prerequisite was missing from docs 00-06.

### Implementation Retrospective

**Single pass** (Genba + Pre-mortem + Five Whys) — compare design to implementation, trace deviations to root causes.

Applied to the rater integration (15 tickets, implementation summary, source code). Found the IP bypass deviation and traced it via Five Whys to a Genba gap during design (framework source code not read). Estimated savings if Genba had been applied earlier: ~3 days + 2 throwaway tickets.

### Solution Design Generation

**Single pass** (Cynefin + First Principles + MECE + Pre-mortem) — generate a complete solution design from requirements alone.

Applied to the ExampleVision integration. Requirements were extracted from 5 integration docs (stripping all solution design, class names, data model). The agent produced a 781-line solution design with 9 Apex classes, 1 custom object, CMDT/Custom Setting configuration, and a 10-ticket work breakdown. Compared against the actual implemented design: ~90% architectural match. 9 of 10 classes matched exactly (same names, responsibilities, patterns). The 4 gaps (missing output processor batch, NC indirection, separate schedulers, date sync trigger) are all reasonable design choices, not architectural flaws.

**Key insight:** This is the strongest test of MECE — when generating (not reviewing), it forces the agent to ask "what's missing?" at every level. Cynefin correctly categorised the complexity domains (Simple: config/permissions, Complicated: .eml construction/IP mapping, Complex: polling timing/error recovery). First Principles drove the class decomposition. Pre-mortem caught the IP rollback risk that was also discovered during the real rater implementation.

**Two-pass variant not tested** — the single pass achieved ~90% match, suggesting the handles are sufficient for design generation without adversarial verification. A two-pass approach (analytical design then adversarial review of own design) might close the remaining 10% gap but has not been tested.

## When to Use

- **Single pass (axis cocktail only):** Routine code reviews, PR reviews, small features, doc chain reviews, retrospectives, solution design generation
- **Two passes:** Architecture reviews, integration designs, pre-production audits, design document reviews, anything touching shared infrastructure or external APIs