# Axis Engineering — The Seesaw Principle

> A diagnostic heuristic for knowing when to stop fighting your tools and fix the problem upstream. **Cross-cutting** — fires inside Triangle, Prism, Two-Pass, and during ordinary single-pass work.
>
> **See also:** [main methodology](README.md) | [vocabulary](vocabulary-quick-ref.md) | [triangle protocol](triangle-protocol.md) | [prism protocol](prism-protocol.md) | [two-pass strategy](two-pass-strategy.md)

## Core Idea

When building software, there is a constant tension between three things:

```
TEST ←──────→ DESIGN ←──────→ IMPLEMENTATION
```

**Design sits in the middle.** It is the intended behaviour — the spec, the UX intent, the contract.

When either side of the seesaw becomes hard to write, it is a signal that something is wrong — not with your effort, but with the balance.

## The Seesaw Subtypes

The pattern generalises beyond test/design/implementation. Anywhere there's a 3-pole tension — actor pulling on one side, implementation pushing back on the other, design as the contract in the middle — Seesaw applies.

### 1. Test ↔ Design ↔ UI (Maestro / E2E)

> "I'm writing a test for a UI element and it's really hard."

- **Test is too hard** → the UI is broken (missing labels, wrong text, inaccessible elements)
- **UI is too hard to implement cleanly** → the design may be over-engineered or unclear
- **Both are fine but they don't match** → the design contract was never agreed

*Example:* Tab bar items had no `accessibilityLabel`. Every Maestro test had to use `"Settings, tab, 6 of 7"`. That wasn't a test problem — it was a code problem that made the test artificially hard.

### 2. Test ↔ Design ↔ Component (Jest / unit)

> "I'm writing a unit test for a component and it's really hard."

- **Test is too hard** → the component is doing too much, has no clear interface, or its state is entangled
- **Component is too complex** → probably needs breaking down
- **Test is too easy / tests nothing** → the component has no meaningful behaviour to test

### 3. User ↔ Design ↔ UI (UX)

> "Users are struggling with a screen."

- **User finds it confusing** → the design doesn't match the user's mental model
- **UI is complex to build** → the design may not be feasible or needs simplification (KISS)
- **Both seem fine but users still struggle** → the user expectation was never set (onboarding, empty states, copy)

### 4. Actor ↔ Model ↔ Framework (modelling — used inside Prism Protocol)

> "I'm modelling a customer requirement and a stakeholder's view doesn't fit."

- **Actor's view doesn't fit any model slot** → either model gap or out-of-scope ask
- **Model can't be expressed in stdlib + overlay; extension would be large** → either model is wrong shape or this is genuinely customer-specific
- **Day-1 model breaks under Year-3 / Year-5 lens** → don't ship Day-1 model; refactor before sign-off

This is the subtype that fires inside the [Prism Protocol](prism-protocol.md) during refraction. Three lens-sets (actor / implementation / lifecycle) intersecting on a model-in-progress; imbalances surface as Seesaw triggers.

### 5. Actor ↔ Design ↔ Implementation (top-level / abstract)

> The generalised form. Any actor (user, test, developer, API consumer, future-self, regulator) struggling to interact with any implementation is a signal to look at the design in the middle.

## When to Trigger It

You're on the seesaw when:

- You're copy-pasting workarounds across multiple tests → **code bug, not test problem**
- A simple interaction (tap a button, read a label) requires unusual effort → **design/implementation gap**
- You've rewritten the same test three times with different approaches → **stop, look at the code**
- A UI component is hard to unit test → **component is doing too much**
- Users ask "where is X?" when X is visible → **design/copy problem**
- A stakeholder's needs from a requirement don't fit any model slot you've drawn → **model gap or out-of-scope ask** (Prism context)
- You're contorting the model to make it fit a substrate's idiom → **either the model is wrong or the substrate is wrong** (Prism context)

## The Response

When you detect you're on the seesaw, apply this discipline:

1. **Identify which end is heavy** — is the test/user/actor fighting the implementation, or is the implementation fighting the design?
2. **Find the fulcrum** — what is the design contract? Is it written down (spec, ticket, wireframe, model fragment)?
3. **Raise a ticket** — always. Even if you fix it immediately. The ticket is the record that the imbalance existed. It links the fix to the cause, and it tells the team this pattern was found here.
4. **Move the weight** — fix upstream, not downstream. Fix the code, not the test. Fix the design, not the workaround. Fix the model, not the test that papers over it.
5. **Close the ticket with the fix** — reference the commit. `closes #NNN`.
6. **Re-balance** — re-run the test / re-test with a user / re-refract the requirement. Did it get easier?

> Never add weight to the test (or workaround) to compensate for a broken implementation. That just hides the imbalance.

> Never fix without a ticket. A fix without a ticket is invisible — no one knows why it changed, what it cost, or whether it might regress.

## Relationship to Other Strategies

The Seesaw Principle is **cross-cutting** — it fires *inside* the other axis-engineering protocols, not as a peer.

```
Axis Engineering
├── Triangle Protocol      (decisions — multi-agent + synthesis)
├── Prism Protocol         (modelling — multi-lens refraction)
├── Two-Pass Strategy      (review — sequential constructive then adversarial)
└── Seesaw Principle       (cross-cutting diagnostic — fires inside any of the above)
    ├── Test↔Design↔UI         (E2E / Maestro)
    ├── Test↔Design↔Component  (Jest / unit)
    ├── User↔Design↔UI         (UX / product)
    ├── Actor↔Model↔Framework  (modelling — used inside Prism)
    └── Actor↔Design↔Implementation  (top-level / abstract)
```

- **Triangle** is good for decision-time when there's a real tradeoff and you need three independent designs.
- **Prism** is good for modelling-time when the system shape isn't yet stable and you need viewpoint-completeness.
- **Two-Pass** is good for review-time when an artefact exists and needs adversarial pressure-testing.
- **Seesaw** is the diagnostic that fires *during* any of the above. When the balance is wrong, it tells you which end to fix.

## Open Questions

- Does the Seesaw Principle need a name that scales better? "Seesaw" is intuitive but informal.
- ~~Should there be a formal trigger checklist (e.g. "3 workarounds = raise a ticket")?~~ **Resolved: always raise a ticket, even for one workaround.**
- ~~Is the Triangle Protocol already doing some of this at a higher level? Worth comparing.~~ **Resolved: Triangle is decision-level multi-agent; Seesaw is cross-cutting diagnostic. They're siblings, not nested.**
- How does this interact with deadlines? (When do you accept the imbalance temporarily and log it as debt?)
- Could this be built into PR review criteria? ("Does this PR add test workarounds that should be code fixes?")
- Could this be built into model review criteria? ("Does this model fragment have an actor lens that fired weakly without explanation?")

## Next Steps

1. ~~Apply to Maestro E2E tests~~ — done; see test-review-protocol applications.
2. Apply to Jest component tests — audit for hard-to-test components.
3. Write the User↔Design↔UI subtype with a UX checklist.
4. ~~Decide if this is a standalone methodology or an Axis sub-protocol~~ — **Resolved: cross-cutting diagnostic that fires inside Triangle, Prism, and Two-Pass.**
5. Calibrate the Actor↔Model↔Framework subtype against more Prism Protocol experiments.
6. Consider whether to formalise as a team document or keep as engineering heuristic.