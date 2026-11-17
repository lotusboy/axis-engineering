# Axis Engineering — Two-Pass Strategy

## The Problem

No single axis cocktail catches everything. Our A/B/C experiment showed:

- **Dispositional** (Gandharan + Genba) found process/systemic gaps (missing logging, trigger chains)
- **Standard** (no framing) found direct implementation bugs (stale values, field overwrites)
- **Axis Engineering cocktail** found structural quality, waste, and architectural debt

Each missed things the others caught.

## The Solution: Two Separate Passes

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

**Variant for refactors and guard changes — mutation probes.** When the change claims to preserve behaviour or to guard something, Pass 2 can break the code on purpose instead of reading it again: apply each mutation to a scratch copy (remove a guard, flip a condition, revert the fix), run the tests, restore. Each mutation that no test catches is a finding, unless the reviewer argues it cannot change behaviour. In field reviews, "8 of 13 mutations survive" and "11 of 18 site reversions survive the tests" were the findings that a second reading would not have produced.

### What to tell the reviewers

It depends on the job. A **discovery** review (what is wrong with this design?) keeps reviewers blind to the author's suspected issues, so they find their own. A **verification** review (does this change do what it claims?) names the claim under review and hands over the author's suspects, and the reviewer adds its own before reading closely. Withholding suspects from a verification review wastes the reviewer's budget re-finding what the author already knew.

Even a blind review may be given **checked facts about how the system runs** — its entry points, what is run by hand, what is staged and deliberately not yet wired — in a section labelled *"factual context, not a hint at findings"*. Never suspects, priors or another pass's output. In field runs, blind reviewers without this context raised false "dead code" P0s on paths that were run by hand on purpose; once contracts carried the section, the false flags stopped and real unwired code was still found. Include only facts you have checked: supplied context is a claim too, and a context pack that was itself wrong once misled two different models.

## Why Two Passes Instead of One Bigger Cocktail

Over-stacking handles (7+) causes the agent to name-drop all of them superficially. Two focused passes with 3-4 handles each produces deeper analysis than one pass with 8 handles.

The passes are also cognitively different:
- Pass 1 is **analytical** (compare docs to code, categorise findings)
- Pass 2 is **adversarial** (break things, find edge cases, verify guards)

Running them as separate passes avoids the agent trying to do both at once. "Separate" means isolated contexts, not a fixed order: Pass 2 never sees Pass 1, so the two can — and in field use usually do — run in parallel, with the synthesis after both return.

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

**When the target is split across reviewers** (one pair per component, or several batches), list every file in the target and assign each to a reviewer **before launch**, then state the coverage (lines assigned of lines in scope). And require every reviewer to say what it did **not** check, and why — silence about coverage reads as "all clear". In one field run, the first split left about 3,050 lines assigned to no one, and a large package was excluded because its name suggested a narrower job; "the five worst findings all sit in code that batch 1 never looked at". The final run reported 31,803 of 31,803 lines covered.

**If the agents cannot write files** (read-only subagents), the orchestrating session writes each agent's output to its file verbatim **as soon as it returns** — not later from memory. In one field batch, nine reviews were backfilled afterwards as condensed records, and the full reports were lost.

**Before committing a run folder to a public repository,** scan it for private names (customers, people, private files or repos) and machine paths, or keep the run in a private location instead. Prompts routinely quote the materials they were given. Field runs did both: some replaced machine paths before commit; others were kept out of the public repo because their prompts named private design files.

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
- **Severity:** start at `max(pass1_severity, pass2_severity)`, so nothing is lowered silently. The synthesis may then move a finding's severity **down or up**, but only after checking the evidence itself, and it states the reason in one line (e.g. "lowered P0 → P1: affects scale, not correctness"). Field runs used this authority in both directions: one milestone review lowered an adversarial-pass P0 that was about scale rather than correctness; another synthesis verified 22 findings itself and raised 3 of them. A pass's severity is an input to the synthesis, not a verdict binding on it.
- **Conflicts:** If Pass 2 contradicts Pass 1, prefer Pass 2 if it has stronger evidence: a reproduction beats a citation; between equals, more file:line citations and verbatim snippets. Pass 2 reads code fresh without anchoring on Pass 1.
- **Unique findings:** Anything found by only one pass is included as-is with source attribution.
- **Patterns:** After merging, the synthesis names **at most 3 systemic patterns** — a cause that shows up as several findings in different places — and lists the findings each one explains. In one field run, five separate gate findings shared one cause (each gate counted objects instead of measuring content); the synthesis named it "one bug with five faces" and warned that fixing the instances alone "guarantees a sixth face". In a **later round**, the synthesis reports each previously named pattern as *closed*, *still open*, or *new instance found*. **Sibling sweep:** for each named pattern, and each defect class fixed since the last round, list its sibling sites (same pattern, same input on another path, a parallel command or field) and check each. A pattern is *closed* only when its siblings have been checked. In field runs the most serious finding was repeatedly a defect already fixed one step away — one was "structurally identical to one fixed earlier the same day", in a sibling command; another was "a fourth instance" of a bug whose first three had been found.
- **Verification:** The synthesis may read the reviewed source. Independence comes from the two passes being blind to each other, not from blinding the synthesis. It spot-checks every factual claim it builds on; anything it did not check is labelled a lead (INFERENCE), not a fact. When its check refutes a claim a pass actually executed, it suspects its own check first (re-run it, widen it) before overruling the pass.

## Repeated Rounds

Two-Pass is often re-run after the author fixes the findings. What to expect depends on whether the scope stayed the same.

- **Same artefact, revised between rounds: expect convergence.** In one field series, a design document reviewed three times as it was revised went 20 → 14 → 7 merged findings (P0: 8 → 5 → 0), and the verdict reached build-ready. The protocol ran out of real things to find; it did not manufacture noise to fill a target count.
- **If findings do not fall between rounds of the same artefact,** check that the fixes address the pattern behind the findings (see **Patterns** in the Merge Contract), not each instance one by one. Fixing instances leaves the pattern free to produce new ones.
- **A growing system reviewed at each milestone: do not expect convergence.** In another field series, milestone reviews of a system under active construction went ~74 → 44 → 79 → ~188 raw findings, because each round reviewed a larger system (the last ~32,000 lines). A rise there is not evidence that fixes made things worse. Compare rounds only over the same scope.

## Failure Modes

### Pass 2 anchoring on Pass 1

The "Do NOT read Pass 1" instruction is enforced by **agent isolation** in subagent architectures (each pass runs in a separate context). In a single-session workflow where a human runs both prompts sequentially, the model *will* have Pass 1 in context and may anchor on it despite the instruction.

**Mitigation:** For single-session use, run Pass 2 in a new conversation or a separate agent. If that's impractical, instruct Pass 2 to "actively contradict at least 2 Pass 1 findings" — this forces genuine re-examination rather than passive agreement.

### Author as synthesiser

The synthesis is often written by the orchestrating session, which may also be the author of what is under review. The risk is rationalising: the author's own choices get the benefit of the doubt. A fresh-context synthesis is the default when the author wrote the artefact under review. Author-written synthesis is acceptable when it is **stated in the synthesis**, and it must still meet the Merge Contract's Verification rule — every fact it builds on spot-checked against the source.

### Merge step confabulation

The third agent synthesising two reviews may fabricate connections between findings that don't actually relate, or make severity changes it has not verified.

**Mitigation:** The merge contract's dedupe key `(artifact, symptom, root-cause-class)` constrains the synthesis. Additionally, require the merge output to cite which pass originated each finding — any finding not traceable to Pass 1 or Pass 2 is held back from the findings table and listed separately for the human. Blinding the synthesis to the source does not prevent confabulation: in one field run, a synthesis told not to read the reviewed repository still added a finding traceable to neither pass, and miscounted its own convergence. It only removed the check that would have caught both.

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
- **Follow-up reviews** (a fix after a Two-Pass, or a fix to that fix):
  - A **single pass** is enough only when it **cites the parent Two-Pass** (its run folder) and the follow-up adds **no new reasoning** — same root cause, same area, carrying out what the parent already reviewed. In field use this cost about a third of a Two-Pass.
  - **No cited parent, a new root cause, or a change to the design → Two-Pass.**
  - **Re-run each finding's own reproduction (and any surviving mutation) against the fix.** Green tests and gates are not proof the finding is closed. In field runs a fix "moved the blind spot instead of closing it", and in another "every gate passes" while the original reviewer's mutation still passed. A review's own suggested fix was wrong once too; replaying the reproduction caught it.
  - **The loop stops** when a single pass finds nothing at P1 or above.
  - A third fix for the same root cause is a Seesaw signal, not another review round — see `seesaw-principle.md` "When to Trigger It".
  - Every review records which depth it used and why, so a step down can be checked later.