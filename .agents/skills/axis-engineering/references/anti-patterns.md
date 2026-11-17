# Axis Engineering: Anti-Patterns

## Over-stacking

```
# BAD — too many handles, all applied superficially
Apply Genba, Seven Factors, GoF, SOLID, DDD, Fowler, Pre-mortem,
STRIDE, Cynefin, Kaizen, First Principles, and Hexagonal Architecture.
```

The model will name-drop all of them without going deep on any.

**Rule of thumb: 2-3 handles per prompt, max 4 in a single pass.**

## Wrong Hammer for the Nail

```
# BAD — DDD and Hexagonal Architecture for adding a checkbox field
Apply Domain-Driven Design and Hexagonal Architecture to add
APP_IsActive__c to APP_Building__c.
```

Use Cynefin first to size the problem, then pick appropriate handles.

## Dispositional Without Structural

```
# WEAK — beautiful thinking, unusable output
Approach with Seven Factors of Awakening and Genba mindset.
Review the rater integration.
```

Always pair a dispositional handle with a structural one (BLUF, MECE, Pyramid) so the output is actionable.

## Structural Without Dispositional

```
# WEAK — formatted checklist, shallow thinking
Give me a MECE analysis of the rater integration risks.
```

You get tidy categories with surface-level content. The disposition is what drives depth.

## Axis Leakage (Structure Dominates Disposition)

```
# WEAK — structure handle overpowers the investigation
Apply Genba and Chaos Engineering. Output as MECE with letter grades per component.
```

The rigid output format forces the agent to optimize presentation over investigation. It fills cells rather than following threads.

**Mitigation:** When pairing structure with adversarial handles, use lighter structure (Pyramid or BLUF) rather than heavy structure (MECE + grades). Or separate them into two passes.

## Keyword Cargo-Culting

```
# BAD — agent mentions handles without changing behavior
"Applying Genba mindset, I note that the code looks correct."
```

The agent name-drops the handle without demonstrating application. No artifact references, no verification steps.

**Mitigation:** Use the Axis Contract with explicit evidence rules. Require artifact pointers for every finding.

## Verification Theatre

```
# BAD — agent says "I verified" without evidence
"Genba: I checked the source code and confirmed the implementation is correct."
```

"I checked" is not verification. Where? What did you find? What was expected vs actual?

**Mitigation:** Require an **assumption ledger** — "List each assumption you made and how you verified it (or mark as Unknown)."

**Mitigation — reproduce or label:** a cited `file:line` shows *where*, not that the claim about it is true. Where a claim can be run (a command, a test, a scratch reproduction), require the run. A finding that was not reproduced is labelled **INFERENCE** (reasoned, not run) and ranked below **FACT** findings. A finding is FACT when a command shows it, or when a cited line states it directly **and the claim is about what the code or document says** (e.g. "this class is declared `without sharing`"). A claim about **what it does** (e.g. "this cannot lose data") needs a run; a cited line alone leaves it INFERENCE. Field data: in one review, source-only findings needed 3 of 5 checked claims corrected; once reviewers had to verify by running something, 0 of 17 checks were refuted. Where nothing can be run (a design document, a reasoning-only Prism), the same labels apply: a finding is FACT only when a cited line states it directly; anything reasoned is INFERENCE.

## Comment as Citation

```
# BAD — a comment is cited as proof of behaviour
"Safe: the comment above this branch says nothing here can lose data."
```

A code comment, docstring, changelog, release note or an earlier session's notes is a **claim** by whoever wrote it, not evidence. It can be stale, aspirational or wrong. In one field run, a comment beside the code stated the safety argument outright; the pass that took it at face value found no critical issue, and the pass that built the failing precondition found data loss. In another, an audit measured comments' claims against the real documents and refuted several (one claimed "0 → 44"; the measurement was +18).

**Mitigation:** treat each as a claim. Put it in the assumption ledger as **Unknown**, then trace it in the code or reproduce it, and only then cite it. The same applies to a release's own "how this was tested" notes: they are another session's claims, not independent verification.

## Persona Drift

```
# BAD — handle loses effect mid-conversation
Turn 1: Deep Genba verification with file:line citations
Turn 15: "The code looks correct based on the pattern."
```

On long tasks, the model drifts back to its default "helpful assistant" persona. The handle's behavioral effect decays over the context window.

**Mitigation:** Re-anchor periodically. In long sessions, restate the active handles every 5-10 turns.

## Hallucinated Risks

```
# BAD — adversarial handles force the model to invent problems
"Chaos Engineering: What if the server returns a 418 I'm A Teapot status?"
```

When adversarial handles are applied too aggressively, the model may fabricate plausible-sounding failure modes that cannot actually occur.

**Mitigation:** Pair adversarial handles with Genba (verify against source). The contract's EVIDENCE field forces the model to cite real code paths.
