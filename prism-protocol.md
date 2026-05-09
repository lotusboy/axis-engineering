# Axis Engineering — Prism Protocol

> **Status:** v1.0 (2026-05-09). Authored by Steven Loftus.
>
> **What v1.0 adds over v0.2:** dual-rate convergence reporting (strict + broad), three-way unique-catch subdivision (complementary / hidden divergence / fluke), mermaid diagram as standard Phase 2 output, Phase 4 anti-anchoring guard, materials-richness as a tuning diagnostic, and the dev-tools-wider-band hypothesis revised to a measurement artifact. Empirical basis: ten multi-agent calibration runs across two industries and four substrate compositions.
>
> **Domain-specific companions:** `salesforce-prism.md` (TBD — substrate config for `salesforce + mga-overlay` and `salesforce + (no MGA frame)` stacks).
>
> **See also:** [main methodology](README.md) | [vocabulary](vocabulary-quick-ref.md) | [triangle protocol](triangle-protocol.md) | [seesaw principle](seesaw-principle.md) | [two-pass strategy](two-pass-strategy.md)

## The Problem

Axis Engineering's single-pass design works when the architecture is overdetermined by the requirements (Cynefin: Complicated). The Triangle Protocol works when the architecture has genuine tradeoffs that the team must explicitly choose (Cynefin: Complex). Neither addresses the upstream question: **what shape is the model in the first place?**

Modelling — the activity of taking raw customer materials and producing a stable, reviewable outline of the system — has its own asymmetry. Single-agent modelling commits to a first-pass shape and elaborates it; alternative shapes never surface. Triangle would generate three competing models, but the question at modelling-time isn't "which tradeoff?" — it's "which viewpoints have we accounted for?" Constraint pairings (TQ/TC/CQ) don't surface viewpoint gaps.

The Prism Protocol does for modelling what Triangle does for decisions: it surfaces the solution space rather than committing to one point in it. The mechanism is *refraction* through multiple viewpoints, with the Seesaw Principle as the diagnostic that surfaces imbalances during refraction.

## Why bring your own substrate?

Prism takes three inputs from the operator: **stack documentation** (what the platform CAN do), **industry documentation** (the actor lens-set, pipeline shape, domain vocabulary), and **customer materials** (SOW, transcripts, samples). All three are mandatory. None can be filled in from "the LLM probably knows."

**The alternative is the LLM defaulting to its training-data view of your platform.** That view may be:

- **Stale** — training cutoffs are months or years old; platform releases since then are invisible.
- **Too broad** — the LLM has seen all of Salesforce/Azure/etc., not the slice your project lives in. Without scoping, it pulls patterns from contexts that don't apply.
- **Cross-contaminated** — the LLM may have absorbed other customers' implementation patterns from public Q&A, blog posts, or open-source repos. Without your scoped substrate, those patterns leak into the model it produces for you.

**Substrate is how you tell the model: "use this, not whatever you happened to absorb."** The same logic applies to industry and customer materials. The discipline isn't bureaucracy — it's the *opposite*. It deliberately constrains the LLM to current, relevant, scoped knowledge instead of letting it default to generic training data.

If you don't bring substrate, Prism still runs — but the implementation lens fires from the LLM's defaults, and you lose the protocol's ability to honestly distinguish "platform capability" from "customer extension." The empty-by-design lens (where a stack layer is deliberately absent) only carries signal value if all *non*-empty layers are explicitly populated. Substrate is opt-in but uniformly so.

See `## Substrate and Industry as Inputs` below for the operator pre-launch checklist and sanitisation discipline.

## The Three Lens-Sets

Each requirement is refracted through three lens-sets. Each lens asks "what is true from *my* position?" — and where lenses produce mutually incompatible answers, that's the signal to stop and report.

### 1. Actor lenses (who sees this requirement?)

The set of actor lenses is industry-specific (loaded from industry config). For `insurance.mga`:

- **Underwriter** — quote/bind eligibility, risk shape
- **Producer/Broker** — self-service, status visibility
- **Carrier** — outward notification, paper-level visibility
- **State Regulator** — audit trail, immutable record per filing
- **Finance** — commission gating, effective dating
- **Operations** — reconciliation, anomaly detection
- **Compliance** — renewal tracking, cross-checks

Each lens asks "what do *I* need from this system, to do my job?" Lenses fire with different intensity per requirement — that's expected. A lens that fires weakly is honest signal, not a protocol failure.

### 2. Implementation lenses (three only, in priority order)

- **Substrate stdlib lens** — does the base platform do this natively? Try first.
- **Overlay pattern lens** — does any overlay in the stack provide a reusable pattern? Try second.
- **Customer extension lens** — only if the first two don't fit, with rationale recorded.

Lens content is loaded from substrate config. Salesforce stdlib lens is loaded for any project on Salesforce. Overlay lens is loaded with mga-overlay / FSC / Health Cloud / etc. patterns when those are in the stack — and is **EMPTY** when they're not. The empty lens is itself a signal: the cost of not having that overlay shows up as everything that has to land in the customer-extension lens.

### 3. Lifecycle lenses (three temporal positions)

- **Day-1 launch** — what does this look like at go-live? Is it shippable in current scope?
- **Year-3 maintenance** — steady-state operations. What does the team do daily/weekly with this?
- **Year-5 schema-shift** — regulator changes a format, jurisdiction expands, vendor changes API, customer pivots. Does the model absorb the change without rebuild, or does it need surgery?

Lifecycle lenses are substrate-and-industry agnostic. They're the temporal axis every system has to survive on.

## How It Works

### Phase 1: Refraction

Each requirement is refracted through all three lens-sets. Default mode is single-agent (cheap, sufficient for most modelling). Multi-agent mode (Phase 1b) is reserved for high-stakes or genuinely ambiguous requirements.

```
AXES:         Genba + MECE + Cynefin + Pre-mortem
TARGET:       [requirement statement] + [customer materials]
STRUCTURE:    Three lens-sets, walked in order: Actor → Implementation → Lifecycle
EVIDENCE:     For each lens that fires, cite the source material that triggered it
              (SOW clause, transcript timestamp, sample document line).
              For each lens that fires weakly or not at all, say so explicitly —
              do not pad. Honest empty is signal; manufactured content is noise.
SEESAW:       During refraction, watch for three imbalance types:
                - Actor-view / model imbalance: a stakeholder's view doesn't fit
                  any model slot. Either model gap or out-of-scope ask.
                - Model / framework imbalance: model can't be expressed in stdlib +
                  overlay; extension would be large. Either model is wrong shape
                  or this is genuinely customer-specific.
                - Lifecycle imbalance: Day-1 model breaks under Year-3 / Year-5.
                  Don't ship Day-1 model; refactor before sign-off.
              Each imbalance is a signal to surface, not a problem to paper over.
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
STOP:         Andon — halt and surface if a requirement is genuinely contradictory
              across two actor lenses. This is requirements-level ambiguity that
              must be resolved by the customer before modelling continues.
```

### Phase 1b: Multi-agent refraction (for high-stakes requirements)

For requirements where the model shape will persist for years, run the refraction in parallel under context isolation. N=2 is the recommended minimum (cost-effective; ~70% convergence rate observed empirically). N=3 increases coverage of edge cases but at proportional cost.

Each agent receives:
- The Prism Protocol description (this document)
- The same customer materials
- The same industry + stack config
- The same requirement statement

Agents must not see each other's output. Each produces three artefacts independently (see Phase 2). A separate synthesis agent then performs Phase 2 across all outputs.

### Phase 2: Synthesis

Each refraction (whether single- or multi-agent) produces **four artefacts** (v1.0):

1. **Model fragment** — objects, fields, relationships, status state machines, sharing implications. Substrate-flavoured (Salesforce primitives if substrate=salesforce, etc.).
2. **Seesaw log** — list of imbalances surfaced during refraction, with the signal each indicates and the action it forces.
3. **Open questions** — real ambiguities the materials don't resolve, each with an audience for resolution (UW domain expert, compliance lead, product owner, etc.).
4. **Mermaid model diagram** — a spatial representation of the model fragment intended for human-gate / stakeholder consumption. ~15-30 nodes, subgraphs by lifecycle stage or structural concern, risk markers placed at Seesaw imbalance points, substrate-origin distinction (substrate / overlay / customer-extension / external) made visually explicit. The diagram is a spatial view of artefact 1, not a separate model.

For multi-agent runs, a synthesis pass produces:

```
AXES:         MECE + First Principles
TARGET:       N agent outputs (model fragments + seesaw logs + open questions
              + mermaid diagrams)
TASK:         Compare and synthesise.
              Do NOT pick a winner — the human decides.
              Surface convergence (high-confidence — multiple agents agreed),
              divergence (genuine architectural choices),
              and unique catches (an edge case caught by only one agent).
STRUCTURE:    Convergence → Divergence → Unique catches → Mermaid comparison
              → Meta-findings
EVIDENCE:     Cite each agent's output for every comparison point.
              Read all agent outputs in full before writing comparison.
STOP:         Flag any case where two agents interpret the same requirement
              differently — that's requirements-level ambiguity, must be
              resolved before modelling continues.
```

**Unique-catches three-way subdivision (v1.0):** classify each unique catch as one of:

- **Complementary coverage** — real signal, no contradiction; the other agent simply didn't surface this thread.
- **Hidden divergence** — the catch implies a position the other agent took the opposite of (without saying so explicitly). Hidden divergences are model disagreements in substance and should be promoted to the Divergence list for human-gate visibility.
- **Fluke / noise** — invented, low-evidence, or one-agent imagination.

This subdivision exists because lumping all uniques as non-convergence inflates the disagreement signal: most uniques are complementary (one agent saw something the other didn't, no conflict), only some are hidden divergences (real model disagreement), and fluke is rare.

**Mermaid comparison section** reports: structural overlap (node-by-node), connection overlap (edge-by-edge), risk-marker placement (per-node), diagram type and granularity, stakeholder-readability verdict, and **diagram-vs-text alignment per agent** (the diagram should match each agent's own textual model fragment; drift is a quality concern).

**Tuning diagnostic — substrate-citation density.** Multi-agent calibrations to date show citation density scales with substrate file size and corpus richness. Read it as a value-band, not a single target:

- **Below ~0.3/kB:** warning signal. Substrate is not doing its job — likely too generic, too removed from the requirement, or padded with content the implementation lens cannot use. Treat as input to the next sanitisation pass, not as an agent failure.
- **~1-4/kB:** healthy engagement. Agents are grounding decisions in specific substrate sections.
- **Above ~4/kB:** signal that customer corpus is sparse and the substrate is carrying weight beyond its share. Not a failure — agents correctly shift evidence-weight onto the only cite-able anchor — but worth flagging the corpus as thin and asking whether the materials set should be enriched.

Empirical anchors so far: intake-vendor ~21kB substrate → ~22 citations per agent (~1.0/kB, fuller corpus); rater ~9kB → ~13 citations (~1.4/kB); PDF Butler ~12kB → ~38 citations (~3.2/kB, sparse corpus shifted weight onto substrate). The ~1/kB number is one anchor, not a target.

**Tuning diagnostic — convergence rate (v1.0 dual reporting).** Report two rates as standard:

- **Strict rate** = `convergence / (convergence + divergence + unique-catches-total)`. This is the v0.2 measurement, retained for backwards compatibility.
- **Broad rate** = `convergence / (convergence + divergence)` — where "divergence" includes both explicit and hidden-divergence subtypes. Broad measures *agreement that survives commitment to shape*, excluding complementary-coverage uniques (which are real signal but not model disagreement).

**Empirical band (v1.0):** the **broad rate** lands in a **62-65% band** across multi-agent runs spanning two industries, four substrate compositions, and Phase 1, Phase 4, and mermaid-augmented variants. The strict rate is materials-richness-dependent and ranges more widely (40-71%); read the strict rate as a tuning diagnostic for materials richness rather than a model-shape convergence measure.

Practical corollaries (apply to broad rate):

- **Substantially higher than ~65%** suggests the requirement was overdetermined. Single-agent next time may be fine.
- **Substantially lower than ~62%** suggests requirements-level ambiguity (Andon-class) or substrate-confounded inputs (operator should re-check substrate sanitisation).
- **Within band:** healthy multi-agent run; expected character of divergence is *real architectural choices the human gate must resolve*, not contradictory readings.

**Tuning diagnostic — materials richness affects strict rate.** Materials with explicit empty zones (e.g., "Follow-Up Questions" columns, TBD lists, open issue trackers) inflate complementary-uniques volume without indicating model-shape divergence. Strict rate will be deflated proportionally. Broad rate is the right comparator across runs with different materials shapes. Operator-side mitigation: aim for substrates and materials that pull both blind agents to similar reading depth; asymmetric reading depth produces asymmetric catch character.

**Phase 4 has its own band.** Phase 4 (Maintenance Loop) outputs amendment-shape choices that have more granular ways to disagree than Phase 1 model-shape claims. Phase 4 broad rate sits provisionally at **40-50%** (N=1 datapoint with anti-anchoring guard applied). Don't compare Phase 4 numbers to Phase 1 numbers.

**Historical note — dev-tools-wider-band hypothesis revised.** An earlier conjecture that dev-tools utility runs have wider effective convergence bands than insurance.mga runs was a v0.2 strict-measurement artifact. Under v0.3+ broad-rate measurement, dev-tools and insurance.mga produce similar convergence (~62-65%). Retained as historical note.

### Phase 3: Sign-Off (the human gate)

The model fragment + seesaw log + open questions are reviewed by:
- **Domain expert** — confirms actor lens output reflects real stakeholder needs
- **Tech lead** — confirms implementation lens output is correctly scoped
- **Product owner** — answers open questions or escalates them
- **Compliance / regulatory advisor** — for regulated domains, confirms the audit dimensions are right

Sign-off is binding. Once signed:
- Model fragment is frozen for build (per fixed-discovery → fixed-price methodology)
- Open questions become decisions, recorded in a project decision log
- Seesaw log becomes the project's *don't-redo-this-debate* artefact

### Phase 4: Maintenance Loop

The model fragment is the long-running artefact. As new requirements arrive:

1. Each new requirement is refracted (Phase 1) — extends or refines the model.
2. If refraction produces a Seesaw trigger that signals *the existing model is wrong shape*, the model is amended (with a new sign-off cycle for that section).
3. The seesaw log accumulates — it's the project's institutional memory of architectural decisions.

When customer materials change (SOW amendment, regulatory change, integration vendor change), the affected model fragments are re-refracted. The Prism doesn't fork the model; it amends it.

**Anti-anchoring guard (v1.0 — required for Phase 4 agent prompts).** Phase 4 has a known failure mode: agents anchor on the existing model's named primitives instead of refracting the new requirement freshly. This produces architectural-choice misses where the new requirement should suggest a different shape than the existing model used. Empirical evidence shows the failure mode is **prompt-mitigable**, not model-fundamental — the guard below has held across the Phase 4 datapoints where it was applied. **Include this instruction verbatim in every Phase 4 agent prompt:**

> Treat the existing model's named primitives as candidates, not commitments. If the new requirement suggests a different shape, propose the different shape with rationale rather than forcing the new requirement into the existing names. Weight new-requirement materials over existing-model materials when they conflict.

The guard is mandatory, not optional. Omitting it returns Phase 4 to its pre-v1.0 anchoring failure mode.

## Substrate and Industry as Inputs

The Prism Protocol takes three inputs at invocation:

```
prism({
  materials: [SOW, transcripts, samples, …],
  industry: 'insurance.mga',                          // dotted-path config
  stack:    'salesforce + mga-overlay + fsc + nipr.api'  // composed substrate
})
```

**Industry config** (e.g. `industries/insurance.mga.yaml`) loads:
- Pipeline shape (`gather → rate → docs → bind → manage` for insurance)
- Standard actor set (the lens-set used in Phase 1, lens 1)
- Domain vocabulary (TIV, premium, NPN, NAIC, etc.)
- Lifecycle constraints (renewal cycles, regulatory cadence)

**Substrate config** (e.g. `substrates/salesforce.yaml` + `substrates/mga-overlay.yaml`) loads, per layer:
- Native primitives (sharing model, declarative tools, integration shape)
- Idiomatic patterns ("for record-level variation, use record types not picklists")
- Anti-patterns
- Lifecycle profile (release cadence, breakage history, deprecation behaviour)

Substrates compose. `salesforce + mga-overlay + fsc` loads three substrate configs, each contributing patterns to the implementation lens. `salesforce + (no MGA frame)` loads only Salesforce — the overlay lens is empty.

The protocol code never branches on substrate or industry name. Configs are data the protocol loads and refracts through. New substrate = new YAML file. New industry = new YAML file. No protocol fork.

### Operator pre-launch responsibilities

Before launching agents, the operator MUST produce or identify a **sanitised substrate file for each non-empty layer in the stack string**. The protocol cannot trust that the operator hands it clean substrate — the protocol must require the operator to demonstrate they have one.

**Honest caveat (v1.0):** substrate sanitisation is **operator discipline, not yet schema-enforced**. The checklist below is reliable when followed but manual; leaks happen when operators reuse substrate across customer engagements without re-sanitising for the new context. A schema + automated validator (lint for known customer-namespace prefixes, structural check against the substrate template) is a v1.x candidate. Until then: read substrate carefully before reuse, especially the extension-points section where customer-prefix examples typically live.

**Why this matters.** Vendor API documentation in any integrator's repo is typically co-located with the team's implementation choices (per-endpoint "how we use this" notes, deploy-time discoveries dressed as docs facts, change logs of the team's own usage). Including such an annotated reference raw leaks ground truth. Excluding it entirely leaves the substrate-stdlib lens for that layer empty, which produces architecturally-confounded findings:

- Agents infer substrate behaviour from customer-side materials, which carry the customer's mental model rather than the platform contract.
- Agents may invent reasonable-but-wrong specifics (class names, endpoint shapes) that pattern-match plausibly but don't match reality.
- The implementation lens fires with a hidden hole — divergences land at the wrong granularity (substrate-level, not architectural).

**Motivating experiments (paired calibrations on example-broker).**

- **Intake-vendor integration** (lifecycle ingestion, paired runs). Run 1 substrate-omitted vs Run 2 substrate-curated. Convergence flat at 68%, but Run 2's findings cited specific substrate sections (~22-24 per agent vs zero in Run 1) and substrate-attributable gaps closed. See `testing/corpus/prism-example-broker-intake-vendor-calibration.md`.
- **Rater integration Run 1** (synchronous request/response, v0.2 discipline applied to the vendor-API substrate with mga-overlay declared empty). Convergence at 68%, and **the protocol-attributable gap pattern reproduced** — same shape of misses (mga-overlay-shaped Salesforce-side normalisation choices), different specific items. See `testing/corpus/prism-example-broker-rater-calibration.md`.
- **Rater integration Run 2** (paired with Run 1; mga-overlay substrate now curated). Tested v0.2's implicit closure claim: are the gap-pattern misses *closable* by overlay substrate, or fundamentally customer-extension? Result: **3 of 4 protocol-attributable gaps closed, 1 partially closed appropriately. Character of findings shifted from invention to wiring** — agents now ask "how does customer-extension wire up against substrate-shipped primitives?" not "what primitives must we invent?" See `testing/corpus/prism-example-broker-rater-r2-calibration.md`.

The combined evidence — gap-pattern *reproduction* across two requirements (Intake R1, Rater R1) and gap-pattern *closure* when overlay is curated (Rater R2) — establishes the substrate-curation discipline as a protocol-level property, not a one-off artefact. Convergence band held at 68-70% across all five paired multi-agent runs (NIPR ~70%, Intake R1 68%, Intake R2 68%, Rater R1 68%, Rater R2 70.6%). v0.2 is empirically sufficient.

**Sanitisation checklist (per non-empty stack layer):**

1. **Strip implementation cross-references** — every "[project] usage:", every "this class implements this endpoint", every project-specific binding.
2. **Strip team-specific architectural decisions dressed as docs facts** — e.g., sequential-vs-parallel upload patterns the team chose, storage conventions, deploy-time discoveries.
3. **Strip change logs of the team's own usage.**
4. **Keep:** endpoints, request/response shapes, auth, rate limits, vendor-side state machines, vendor-side data model.

**Sanitisation test:** does the file declare what the platform CAN do, or what THIS implementation does WITH the platform? Only the former is substrate.

**For empty-by-design layers** (e.g. `salesforce + (no MGA frame)`): the protocol still requires the operator to declare them empty. The empty-lens cost is itself a value driver; the protocol must know which layer is empty by design vs missing-by-omission.

### Requirement-statement framing — name load-bearing dimensions explicitly

When drafting the requirement statement to pass to agents, customer-terms purity is a goal but not at the cost of dimensions that are load-bearing in the model. Agents do not recover transaction-type, temporal-lifecycle, or multi-tenancy dimensions from input materials alone — those dimensions live in the team's institutional model and need to be named explicitly.

**Empirical motivation.** The example-broker Rater calibration. The drafted requirement statement was customer-terms-clean ("calculate the premium and write the result back") and implicitly assumed "rate" = "New Business rate." Both blind agents missed the entire Endorsement / Cancellation / Renewal / Reinstatement transaction model (Trans / Delta / PoC field family, prior-quote read for delta math, pro-rata calculations). The team's actual implementation has an entire field family for this — invisible to agents because the requirement statement omitted the dimension and the input materials alone didn't surface it.

**Operator discipline.** Before drafting the requirement statement, ask: what dimensions are load-bearing in the customer's existing system that aren't in the customer's words? Common ones to name explicitly:

- **Transaction types** — New Business / Endorsement / Cancellation / Renewal / Reinstatement / Reversal. Each may have its own pro-rata, delta, or prior-policy-traversal logic.
- **Temporal lifecycle** — Day-1 launch / Year-3 maintenance / Year-5 schema-shift are already in Prism's lifecycle lens-set, but the requirement may have its own time horizons (renewal cycles, regulatory reporting cadences) worth naming.
- **Multi-tenancy** — single-tenant vs multi-tenant, OWD model, sharing implications.
- **Multi-vendor** — when one vendor exists, ask if there might be a second class of vendor in scope (e.g. wildfire as a second rater alongside AOP — the multi-rater modelling question that emerged as a unique-catch in the rater run).

If a dimension is load-bearing, name it in the requirement statement even at the cost of customer-terms purity. Customer-terms framing belongs in stakeholder-facing artefacts; agent-facing framing should declare every dimension.

## Why Lens-Sets, Not Triangle Pairs

Triangle uses constraint pairings (TQ/TC/CQ — pick two, sacrifice one) because architecture decisions involve genuine tradeoffs the team must accept. The pairing forces three independent designs by activating different handle clusters in the model.

Modelling has different semantics. The question isn't "which constraint do we sacrifice?" — it's "which viewpoint are we missing?" A model that omits the carrier lens isn't *cheaper than* a model that includes it; it's *wrong*. There's no tradeoff. The lens is either accounted for or it isn't.

Lens-sets force completeness. Constraint pairings force divergence. Different problems, different protocols.

## Relationship to Other Strategies

The Prism Protocol is part of the same family as the Triangle Protocol and the Seesaw Principle. Family hierarchy (with Seesaw as cross-cutting diagnostic):

```
┌────────────────────────────────────────────────────────────────┐
│                     Axis Engineering                           │
│           (vocabulary of 33 named handles)                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Triangle   │  │    Prism     │  │  Two-Pass    │          │
│  │   Protocol   │  │   Protocol   │  │   Strategy   │          │
│  │ (decisions)  │  │ (modelling)  │  │  (review)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                    │
│                  ┌────────▼────────┐                           │
│                  │     Seesaw      │  ← cross-cutting          │
│                  │    Principle    │     diagnostic            │
│                  │  (don't paper   │     fires inside any      │
│                  │     over)       │     of the protocols      │
│                  └─────────────────┘                           │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│              Single-Pass Recipes (the building blocks)         │
└────────────────────────────────────────────────────────────────┘
```

- **Triangle Protocol** — multi-agent decision exploration. Use when the architecture has genuine tradeoffs.
- **Prism Protocol** — multi-lens modelling. Use when the system shape itself isn't yet stable.
- **Two-Pass Strategy** — sequential review (constructive then adversarial in fresh context). Use when reviewing existing artefacts.
- **Seesaw Principle** — diagnostic that fires *inside* any of the above when a 3-pole tension surfaces an imbalance. Originally framed at Test↔Design↔Implementation; generalises to Actor↔Design↔Implementation, Actor↔Model↔Framework, User↔Design↔UI. Always raises a ticket; always fixes upstream, not downstream.

The seesaw-principle.md document already self-identifies as cross-cutting. Promotion to high-level protocol formalises what's already implicit and gives Triangle and Prism a shared diagnostic vocabulary.

## When to Use

```
Is this a modelling problem (raw materials → stable system outline)?
  Is the model shape genuinely uncertain (Cynefin: Complex)?
    → Prism Protocol (Phase 1 + 2)
  Is the model shape mostly known but with high stakes?
    → Prism Protocol multi-agent (Phase 1b + 2)

Is this an architecture decision (model exists, choosing how to build it)?
  Are there genuine tradeoffs across cost/quality/time?
    → Triangle Protocol
  Is the architecture deterministic from requirements?
    → Single-pass with Cynefin + First Principles + MECE + Pre-mortem

Is this a review of existing artefacts?
  → Two-Pass Strategy (with axis contracts)
```

**Rule of thumb:** if you're producing the first draft of an objects-and-fields outline from customer materials, that's Prism. If you have an outline and need to choose between viable architectures, that's Triangle.

## Expected Benefits

1. **Viewpoint-completeness signal** — when an actor lens or lifecycle lens fires weakly, that's honest signal. When it doesn't fire at all, that's a model gap (or scope-out).
2. **Substrate cost legibility** — the empty overlay lens explicitly costs the absence of platform overlays. ExampleMGA's NIPR sync run produced "~6 months of avoidable build" as a quantifiable cost statement, not a vague "we'd save time on the mga-overlay." Lands with non-engineering audiences.
3. **Requirements ambiguity surfacing** — when actor lenses produce mutually contradictory needs from the same requirement, that's a customer-side ambiguity the materials missed.
4. **Year-5 imbalance detection** — schema-shift lens routinely surfaces "Day-1 model breaks under realistic future" signals that single-pass modelling misses.
5. **Reproducibility** — N=2 blind agent runs converge in a 67-71% band across six multi-agent calibrations (two industries, three substrate configurations, two requirement shapes). Strong evidence the protocol's mechanism is reproducible across agents and across domains. See `experiment-results.md` for catalogue.

## Expected Costs

1. **Single-agent run** — comparable to single-pass design. ~30 minutes per non-trivial requirement once the protocol is internalised.
2. **Multi-agent run (N=2)** — ~2x token cost + a synthesis pass. Reserved for high-stakes requirements.
3. **Synthesis pass (N=2)** — adds ~20 minutes of human review time to compare convergence/divergence/unique catches.
4. **Industry + substrate config maintenance** — needs an explicit owner. Configs are living artefacts (Salesforce releases, mga-overlay adds patterns, customer overlays accumulate).

## Failure Modes

### Lens-set asymmetry mistaken for protocol failure

Some requirements are naturally Compliance-heavy (regulatory) or UW-heavy (risk-shape) or Finance-heavy (commission/billing). The actor lens-set fires asymmetrically — that's appropriate.

**Mitigation:** the lens-set must remain exhaustive (run all of them) even when individual lenses fire weakly. Honest "this lens didn't fire because [reason]" is the right output, not padding.

### Substrate config drift

If the substrate config (e.g. `substrates/salesforce.yaml`) becomes stale — Salesforce releases new features, mga-overlay adds patterns — the implementation lens output becomes increasingly inaccurate.

**Mitigation:** substrate configs are living artefacts. The Year-5 lifecycle lens helps: if it routinely flags "this substrate doesn't support that," the substrate config probably needs updating.

### Industry config gap

Industry configs encode pipeline shape and standard actors. If a customer's actual pipeline diverges (e.g. a non-standard intake source), the actor lens-set may miss them.

**Detection:** Seesaw fires (actor-view / model imbalance). Action: the actor isn't in the industry config — either add them (industry config evolution) or flag as customer-specific (handled by customer extension lens).

### Multi-agent over-reach

Running multi-agent (Phase 1b) for trivial requirements wastes tokens. Two agents on a CRUD object spec will converge ~95%+ — the divergence value isn't there.

**Detection:** if synthesis reports >90% convergence, the requirement was overdetermined; default to single-agent next time.

### Honest-empty masking real gaps

Phase 1 instructs agents to say "this lens didn't fire" when honest. There's a risk of over-using this — claiming a lens didn't fire when actually it did but was hard.

**Mitigation:** the Seesaw Principle's "don't paper over" discipline guards against this. If a lens nearly fired or fired weakly, that's a Seesaw trigger to log, not to suppress.

## Experiment Results

The Prism Protocol's empirical evidence base is catalogued in [`experiment-results.md`](experiment-results.md). At v1.0, the evidence base spans:

- **Ten multi-agent calibration runs** (Phase 1b, Phase 4, and mermaid-augmented variants) across two industries (insurance.mga, dev-tools), four substrate compositions (salesforce + mga-overlay; python + salesforce; bash + azure.cli + bicep + bitbucket-pipelines; salesforce + mga-overlay + mermaid), and multiple requirement shapes (system-build, utility-tool, infrastructure, maintenance-loop).
- **Broad convergence-rate band 62-65%** under v1.0 dual-rate measurement (strict + broad). The strict rate ranges 40-71% depending on materials richness; the broad rate is the model-shape convergence measure and is materially more stable across domains.
- **Substrate-curation discipline validated** by paired calibrations (Intake R1/R2, Rater R1/R2). Curating overlay substrate shifts agent character predictably from *invention* (making up plausible-but-wrong primitives) to *wiring* (asking how customer-extension wires up against substrate-shipped primitives).
- **Phase 4 anchoring bias is prompt-mitigable.** The verbatim anti-anchoring guard (see Phase 4 above) held the failure mode at bay across the Phase 4 datapoints where it was applied. Operating without the guard returns Phase 4 to the original anchoring failure mode.
- **Mermaid as Phase 2 output is additive.** The mermaid ask exposes architectural commitments that text-only runs leave soft (forced spatial commitment surfaces silent disagreement) without disrupting strict or broad convergence rates beyond noise. Two diagrams from blind agents agree on shape (~18 shared entities) when they agree on text.
- **Hidden-divergence subtype is doing real classification work.** Across runs, ~25% of unique catches classify as hidden divergences — model disagreements where one agent's framing presupposes the opposite of what the other agent committed to, without saying so. v0.2 strict measurement collapsed these into "non-convergence" undifferentiated; v1.0 broad measurement promotes them to the divergence list for human-gate visibility.
- **Fluke / noise subtype empty across N=10 runs.** Retained as safety category through N=15; reconsider for v1.x if still empty.

See `experiment-results.md` for per-application detail. Per-run blind/synthesis/calibration writeups live in `testing/` (gitignored — they reference customer-specific artefacts).

### Limitations

Honest caveats:

- **N=2 multi-agent at each datapoint.** Larger N (3, 4, 5 agents) is untested.
- **Substrate sanitisation is operator discipline, not yet schema-enforced.** Manual leaks happen, especially when substrates are reused across customer engagements. A formal schema + automated validator (lint for known customer-namespace prefixes, structural check against the substrate template) is a v1.x candidate.
- **Phase 4 has one datapoint with the anti-anchoring guard applied.** A replication-without-the-guard would lift the prompt-mitigable claim from N=1 to N=2.
- **Mermaid additivity verified on N=1 datapoint.** Cross-stack confirmation pending.
- **All ten calibration runs used Claude Opus.** Cross-model reproducibility (Sonnet, GPT, Gemini) is untested.
- **No automated industry-config or substrate-config schema validation.** Configs are described narratively in this doc; YAML schemas are TBD.

## Implementation

### Claude Code (subagents)

For multi-agent mode, launch parallel Agent invocations in a single message. Each receives identical prompts (this protocol document + materials + requirement). When all return, launch a synthesis agent with their outputs.

```
# Phase 1b — parallel refraction (single message, multiple Agent calls):
Agent A: "Run Prism Protocol on [requirement]. Use [industry] + [stack] config.
          Materials: [...]. Produce model fragment + seesaw log + open questions."
Agent B: [identical prompt]

# Phase 2 — synthesis (after both return):
Agent Synthesis: "Compare these N outputs. Surface convergence, divergence,
                  unique catches, and meta-findings about the protocol's behaviour."
```

### Manual (separate sessions)

Open N separate chat sessions. Paste identical prompts into each (protocol doc + materials + requirement). Copy outputs into a synthesis session.

### API (programmatic)

N parallel `messages.create` calls with the same system prompt. Concatenate responses into a synthesis call. Suitable for automation.

## Related Work

The Prism Protocol's lens-set design draws from:

- **Soft Systems Methodology** (Checkland, 1981) — multiple-perspective modelling of complex problem situations. Differs: SSM is primarily for problem-structuring without commitment to implementation; Prism is explicitly oriented toward Salesforce-shape model fragments.
- **4+1 Architectural View Model** (Kruchten, 1995) — multiple viewpoints on software architecture (logical, process, physical, development, scenarios). Differs: 4+1 views are dimensions of an existing architecture; Prism's lenses are stakeholder/temporal viewpoints during model emergence.
- **Domain-Driven Design / bounded contexts** (Evans, 2003) — modelling around stakeholder language. Prism's actor lenses share this orientation but explicitly include non-user actors (regulators, future-self at Year-5) and implementation substrate.
- **Triangle Protocol** (Loftus, 2026) — direct sibling. Prism uses Triangle's multi-agent + synthesis structure but for modelling rather than architecture decisions, and substitutes constraint-pairings (TQ/TC/CQ) for viewpoint-pairings (actor / implementation / lifecycle).

The combination — Triangle's multi-agent structure + Soft Systems' multi-perspective + 4+1's structural-view discipline + DDD's stakeholder language + substrate-as-data parameterisation — appears to be novel as of 2026.

## Open Items (v1.x candidates)

- [ ] **Substrate sanitisation tooling** — automated validator (schema check + customer-namespace lint) to catch sanitisation leaks before agents read the substrate. Currently operator-discipline; the cost of leaks is real (cross-customer contamination, biased model outputs).
- [ ] **YAML schemas** for substrate config and industry config (currently described only narratively). Suggested approach: schema follows usage; build the first 2-3 substrate configs informally, then formalise.
- [ ] **Phase 4 without the anti-anchoring guard** — empirical replication-without-guard to confirm the prompt-mitigation claim (currently N=1 with guard applied).
- [ ] **Cross-model reproducibility** — replicate one Phase 1b run on Sonnet, one on a non-Anthropic model, see if the broad-rate band (62-65%) holds.
- [ ] **`salesforce-prism.md` companion** — Salesforce-substrate-flavoured version of this protocol, mirroring how `salesforce-triangle.md` extends `triangle-protocol.md`.
- [ ] **Substrate-conditional actor lenses** — empirical pattern observed across three runs (Actuary in rater contexts; Document Template Author in PDF Butler) where substrate-density elevates a substrate-relevant actor into the lens-set. v1.x candidate; not load-bearing for v1.0.
- [ ] **YAGNI-pass operator discipline** for tool-shape (utility-tool) requirements — currently a single-datapoint observation; needs more runs before formalising.