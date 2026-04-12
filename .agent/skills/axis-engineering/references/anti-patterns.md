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
