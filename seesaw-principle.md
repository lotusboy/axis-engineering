# Axis Engineering — The Seesaw Principle

> A diagnostic heuristic for knowing when to stop fighting your tools and fix the problem upstream. **Cross-cutting** — fires inside Triangle, Prism, Two-Pass, and during ordinary single-pass work.
>
> **See also:** [main methodology](README.md) | [vocabulary](vocabulary-quick-ref.md) | [triangle protocol](triangle-protocol.md) | [prism protocol](prism-protocol.md) | [two-pass strategy](two-pass-strategy.md)

## Core Idea

> If a puzzle is getting difficult and I'm having to make convoluted solutions, I'm down the wrong hole and need to rethink.

That's the principle in one sentence. When effort starts compounding — workarounds layered on workarounds, tests rewritten three times, models bent to fit — it's a signal you're patching a flawed substrate, not solving the problem.

When building software, the principle plays out as a constant tension between three things:

```
TEST ←──────→ DESIGN ←──────→ IMPLEMENTATION
```

**Design sits in the middle.** It is the intended behaviour — the spec, the UX intent, the contract.

When either side of the seesaw becomes hard to write, it is a signal that something is wrong — not with your effort, but with the balance. You're down the wrong hole. Step back, find the heavy end, and fix upstream rather than adding more weight to the side that's already fighting.

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