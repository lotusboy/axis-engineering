# Triangle Protocol for Salesforce

> What the Triangle Protocol produces — and what divergence looks like — on the Salesforce platform.

The [Triangle Protocol](triangle-protocol.md) is domain-general. This companion provides the Salesforce-specific output skeleton, handle tuning, example contracts, and patterns observed when running the protocol against Salesforce integration requirements.

This is a companion to the [Salesforce handles guide](salesforce-handles.md) and [main methodology](README.md).

---

## Salesforce Output Skeleton

The Triangle Protocol requires all three agents to use the **same output skeleton** so the synthesis agent can perform structured comparison. The generic skeleton (sections 1-10 in the protocol) should be adapted for Salesforce as follows:

```
OUTPUT SKELETON (Salesforce):
  1.  Executive Summary (Pyramid Principle — answer first, ≤10 lines)
  2.  Cynefin Assessment (Simple / Complicated / Complex domains)
  3.  Data Model
      - Custom Objects (fields, relationships, record types)
      - Standard Object Extensions (new fields on Case, Opportunity, etc.)
      - Picklist Values and Value Sets
      - Validation Rules
  4.  Configuration
      - Custom Metadata Types (CMDT — deployable config)
      - Custom Settings (mutable runtime state)
      - Named Credentials (external auth)
      - Permission Sets and Custom Permissions
      - Feature Flags (CMDT boolean records or Custom Permissions)
  5.  Component Inventory
      - Apex Classes (with single responsibility stated)
      - Apex Triggers (object, events, handler delegation)
      - Scheduler / Batch / Queueable classes (async pattern choice)
      - LWC Components (if applicable)
      - Flows (if applicable)
      - Integration Procedure / OmniScript usage (if applicable)
  6.  Key Design Decisions (each citing requirement + constraint influence)
  7.  What This Design Sacrifices (explicit acknowledgment of the tradeoff)
  8.  Components Considered and Rejected (what was NOT built, and why)
  9.  Work Estimate
      - Component count with complexity rating (Low / Medium / High)
      - Effort in hours per component
      - Total hours and timeline (single dev and parallel options)
      - Development parallelisation plan
  10. Assumption Ledger
      - Verified assumptions (with source citation)
      - Unknown assumptions (with risk-if-wrong and verification step)
      - ANDON conditions (halt-everything triggers)
```

### Why these Salesforce-specific sections matter

**Section 3 — Data Model** is expanded because Salesforce data model choices cascade into everything: validation rules affect all entry points (UI, API, Flow, Data Loader), record types determine page layouts and business process visibility, and picklist values in status fields determine workflow transitions. A single missing picklist value can silently break an integration.

**Section 4 — Configuration** is split into CMDT vs Custom Settings because they have fundamentally different deployment and mutability characteristics. CMDT deploys with metadata but is immutable at runtime. Custom Settings survive deployments but are mutable. Confusing the two is a common integration bug (e.g., storing a polling cursor in CMDT — it gets overwritten on every deployment).

**Section 5 — Component Inventory** includes async pattern choice because Salesforce forces you to choose between Batch, Queueable, Schedulable, Future, and Platform Events — each with different governor limits, callout capabilities, and chaining rules. This is often the highest-divergence area between triangle agents.

**Section 10 — ANDON conditions** are Salesforce-specific halt triggers: things like "Email-to-Case does not create ContentVersion records" or "Integration Procedures cannot be invoked from Apex." These are hard platform constraints that kill an integration before it starts. All three agents should independently identify them so the synthesis can confirm which risks are real.

---

## Handle Tuning for Salesforce

The Triangle Protocol's baseline handles (Cynefin + MECE) and pair-specific handles work on Salesforce without modification. However, certain handles activate particularly useful Salesforce-specific knowledge:

### Pair-specific handle effects on Salesforce

| Handle | What it activates on Salesforce | Agent |
|--------|-------------------------------|-------|
| **First Principles** (TQ) | Decomposes into trigger handler → service → selector → callout layers. Produces the most separated class structure. | TQ |
| **Pre-mortem** (TQ) | Generates Salesforce-specific failure scenarios: governor breach at volume, DML-before-callout, deployment with missing CMDT records, sharing bypass from community context. | TQ |
| **YAGNI** (TC) | Strips fields from custom objects ("Retry_Number__c adds no consumer"), merges batch classes ("1 class instead of 3"), removes unnecessary abstractions ("no shared API client for 5 endpoints"). | TC |
| **Theory of Constraints** (TC) | Identifies the 100-callout governor limit as the bottleneck, drives batch size decisions, focuses effort on the constraint rather than gold-plating non-bottleneck components. | TC |
| **Muda** (CQ) | Produces explicit "Components NOT Built" sections. Rejects unnecessary objects, unnecessary API calls, unnecessary status fields. Most effective at eliminating Salesforce platform overhead (extra scheduled jobs, extra permission sets, extra CMDT types). | CQ |
| **Kent Beck's Four Rules** (CQ) | Drives toward fewest elements: "Does this class need to exist? Does this field reveal intention?" Produces the NULL-timestamp coordination pattern (NULL = needs processing, non-NULL = done) as a Kent Beck Rule 4 optimisation. | CQ |

### Cynefin domains on Salesforce

All three agents share the Cynefin baseline. The Salesforce-specific domain mapping:

| Domain | Salesforce components | Design approach |
|--------|----------------------|-----------------|
| **Simple** | Named Credentials, Permission Sets, Validation Rules, Picklist Values, Custom Object creation | Configure and move on. No custom code needed. |
| **Complicated** | MIME/.eml construction, IP input JSON assembly, CMDT field mapping, location grouping, value transformations | Deterministic once understood. Build once, test the tricky parts. |
| **Complex** | External API timing (when statuses transition), polling cursor management, inception_date availability, stuck submission recovery | ExampleVision's internal timing is opaque. Make it configurable, observable, and manually overridable. Feature flags let you disable subsystems independently. |

---

## Salesforce-Specific Divergence Patterns

Based on the ExampleVision experiment (N=1), these are the divergence patterns observed when running the Triangle Protocol against a Salesforce integration:

### 1. Async Architecture: Monolith vs Separated Batches

The highest-stakes divergence in the ExampleVision experiment. TC consolidated all processing into a single `Batchable + Schedulable` class. TQ and CQ each produced 4 independent batch classes with 4 scheduler wrappers.

**Why this diverges on Salesforce specifically:**
- Salesforce forces the choice between Batch, Queueable, and Schedulable — you can't compose them freely
- The 100-callout-per-transaction governor limit constrains how much work one `execute()` can do
- Scheduled Apex jobs count toward an org limit (100 total) — 4 jobs for one integration is ~4% of the budget
- Feature flags on individual batches are possible with separated architecture but not with a monolith

**What TC sacrifices:** Cannot disable output processing without disabling event polling. A bug in one stage crashes the entire pipeline.

**What TQ/CQ sacrifice:** 4x the scheduled jobs, 4x the test classes, higher metadata component count. More to manage operationally.

### 2. Trigger Object: Case vs EmailMessage

TC triggered on Case (`after insert`). TQ and CQ triggered on EmailMessage (`after insert`).

**Why this diverges on Salesforce specifically:**
- Email-to-Case creates Case → EmailMessage → ContentDocumentLink in a specific order
- ContentDocumentLinks may not be committed during the Case `after insert` trigger context
- EmailMessage has a `HasAttachment` field available at trigger time — more reliable gate
- Subsequent emails on the same Case create new EmailMessage records — only the EmailMessage trigger naturally handles resubmission

### 3. CMDT Architecture: Key-Value vs Typed Fields

TC used a key-value CMDT (`DeveloperName` as key, `Value__c` as value). TQ and CQ used typed-field CMDT with individual fields per config value.

**Why this diverges on Salesforce specifically:**
- Typed CMDT fields provide compile-time safety (`config.Polling_Interval__c` vs `Integer.valueOf(getConfig('Polling_Interval'))`)
- Key-value CMDT is faster to create but has no type safety — all values are Text(255)
- CMDT schema changes require a metadata deployment; key-value records can be added without schema change
- `Is_Production__c` discriminator on typed CMDT enables environment-specific config without Named Principal credentials

### 4. Automation Scope: Automated vs User-Driven Status Transitions

TC and TQ fully automated the Cleared → Data Entry flow (system fetches inception date, calculates trigger date, sends PATCH). CQ made it user-driven (UW enters inception date manually, validation rule enforces it).

**Why this diverges on Salesforce specifically:**
- Salesforce validation rules can enforce "inception date required before status change" — a platform guard that covers all entry points
- A Case trigger can sync user-edited dates to the integration object — standard Salesforce pattern
- The additional API call for automated inception_date retrieval adds a callout and a failure mode within governor limits

---

## Salesforce Triangle Contracts

Ready-to-use contracts for running the Triangle Protocol on a Salesforce integration project.

### Agent TQ — Time + Quality (sacrifice Cost)

```
AXES:         Cynefin + MECE + First Principles + Pre-mortem
TARGET:       [requirements document]
CONSTRAINT:   Optimise for TIME and QUALITY. Ship fast and ship correctly.
              Accept higher operational cost, more infrastructure, larger team burden
              if it means delivering a robust solution sooner.
              Your sacrifice (Cost) is a deprioritisation, not an elimination.
              Ask: "What's the best architecture if we can throw resources at it?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the Salesforce output skeleton (sections 1-10).
              Section 3 must include: Custom Objects with field-level detail,
              Standard Object extensions, Validation Rules, Permission Sets.
              Section 5 must state the async pattern for each class
              (Batch / Queueable / Schedulable / Future) and why.
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Time+Quality priority influenced it.
              If a choice would be the same regardless of constraint, say so.
              Every Apex class must state: sharing keyword, async interface,
              single responsibility, and governor-limit-relevant operations.
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
              Include ANDON conditions — hard platform constraints that would halt
              the project (e.g., IPs not callable from Apex, Named Creds can't send
              custom auth headers).
STOP:         Andon — halt if a design choice creates a single point of failure
              or violates a hard constraint.
```

### Agent TC — Time + Cost (sacrifice Quality)

```
AXES:         Cynefin + MECE + YAGNI + Theory of Constraints
TARGET:       [requirements document]
CONSTRAINT:   Optimise for TIME and COST. Ship fast and ship cheap.
              Accept reduced robustness, less test coverage, thinner error handling
              if it reduces delivery time and operational surface.
              Your sacrifice (Quality) is a deprioritisation, not an elimination.
              Ask: "What is the minimum viable architecture?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the Salesforce output skeleton (sections 1-10).
              Section 3: for each field NOT included, state the YAGNI rationale
              and what quality is sacrificed.
              Section 5: state the governor limit bottleneck and how batch size
              / scope size / callout budget addresses it.
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Time+Cost priority influenced it.
              Every simplification must state what quality it sacrifices and why
              that's acceptable.
              Every YAGNI cut on a custom object field must state what diagnostics
              are lost and where they can still be found (e.g., API logs).
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
              Include ANDON conditions.
STOP:         Andon — halt if a simplification would violate a hard constraint
              or make the system unshippable.
```

### Agent CQ — Cost + Quality (sacrifice Time)

```
AXES:         Cynefin + MECE + Muda + Kent Beck's Four Rules
TARGET:       [requirements document]
CONSTRAINT:   Optimise for COST and QUALITY. Build it right and build it to last.
              Accept longer delivery timeline if it means lower TCO, cleaner architecture,
              and less cognitive load for the team maintaining it over 2+ years.
              Your sacrifice (Time) is a deprioritisation, not an elimination.
              Ask: "What will a new developer understand in 6 months?"
STRUCTURE:    Pyramid Principle (answer first, then supporting detail)
SKELETON:     Follow the Salesforce output skeleton (sections 1-10).
              Section 5: each Apex class must be under 200 lines.
              If a class exceeds this, split it and justify the split.
              Section 8 (Components NOT Built): for each rejected component,
              state what it would have done and why it's waste (Muda).
EVIDENCE:     Every design choice must cite the requirement it satisfies.
              For each major choice, state how the Cost+Quality priority influenced it.
              Every component must justify its existence — if it's waste (Muda), cut it.
              Apply Kent Beck's Four Rules in order: does it pass tests? Does it
              reveal intention? Is there duplication? Are there fewer elements possible?
ASSUMPTIONS:  Maintain Verified/Unknown ledger.
              Include ANDON conditions.
STOP:         Andon — halt if a design choice introduces unnecessary operational fragility
              or maintenance burden.
```

### Synthesis Agent

```
AXES:         Cynefin + MECE + First Principles
TARGET:       Agent TQ output, Agent TC output, Agent CQ output
TASK:         Compare and synthesize three Salesforce architecture proposals.
              Do NOT pick a winner — the human decides.
              Do not use language like "best", "recommended", "preferred",
              or conditional recommendations like "lean toward" or "consider choosing".
              Present options with tradeoffs only. Every comparison must state
              what is gained AND what is lost.
STRUCTURE:    MECE (no overlaps, no gaps in comparison)
SF-SPECIFIC:  Pay particular attention to:
              - Async pattern choices (Batch vs Queueable vs Schedulable)
              - Governor limit strategies (callout budget, DML-before-callout splits)
              - CMDT vs Custom Setting usage and the deploy/mutability tradeoff
              - Trigger object choices and Email-to-Case timing implications
              - Permission model (how many permission sets, custom permissions)
              - Scheduled job count vs org limit (100 max)
OUTPUT:       [Follow the synthesis output sections 0-8 from triangle-protocol.md]
EVIDENCE:     Every comparison point must cite the specific section from each agent's output.
              Read all three designs in full before writing any comparison.
              For Salesforce-specific divergences, state the platform constraint
              that drives the divergence (governor limit, deployment model, sharing model).
STOP:         Flag any case where an agent's output contradicts the requirements.
              Flag any case where two agents interpret the same requirement differently.
              Flag any design that would hit a governor limit under stated volume assumptions.
```

---

## Salesforce-Specific Failure Modes

In addition to the failure modes listed in the [main protocol](triangle-protocol.md):

### Governor limit blind spot

All three agents may design around the same governor limit assumption (e.g., "fewer than 100 active submissions") without testing what happens if the assumption is wrong. In the ExampleVision experiment, all three agents used batch size of 1 without calculating the actual callout budget — a batch size of 10 would use ~30 of the 100-callout limit, well within bounds.

**Detection:** The synthesis agent's blind spots section should flag identical-without-justification governor strategies.

### Platform constraint discovery too late

Salesforce has hard constraints that aren't obvious from requirements alone: IPs performing internal DML before Remote Actions (DML-before-callout), EmailMessage/ContentDocumentLink commit timing, Custom Setting mutability during batch execution. These can kill an integration.

**Mitigation:** Each agent contract includes ANDON conditions. The synthesis agent should compare ANDON lists across agents — if all three flag the same risk, it's a validated concern. If only one flags it, it needs investigation.

### OmniStudio / PKG Connect assumptions

When the integration touches OmniStudio Integration Procedures (IPs), all three agents may assume IPs are callable from Apex. This assumption needs validation in a sandbox before sprint planning. The ExampleVision experiment flagged this as ANDON condition A2 across all agents.

---

## Experiment Evidence

The Triangle Protocol was validated on the ExampleVision integration (a Salesforce + external API integration). Full results are in the [main protocol](triangle-protocol.md#experiment-results), with design outputs in `testing/triangle-examplevision-*.md`.

Key Salesforce-specific observations from the experiment:

| Observation | Evidence |
|---|---|
| Async pattern is the #1 divergence driver | TC: 1 consolidated batch. TQ: 4 batches + 4 schedulers. CQ: 4 batches + 4 schedulers. (Synthesis Divergence 2.1) |
| CMDT architecture diverges on type safety | TC: key-value. TQ/CQ: typed fields. (Synthesis Divergence 2.5) |
| Trigger object choice is platform-driven | TC: Case trigger (simpler). TQ/CQ: EmailMessage trigger (more reliable CDL timing). (Synthesis Divergence 2.2) |
| Governor limit strategy converges | All three used batch size of 1, all citing 100-callout limit. (Synthesis Blind Spot 7.6) |
| Requirements contradiction surfaced | TQ/CQ designed Cleared as outbound; TC did not. Requirement ambiguity detected via agent disagreement. (Synthesis Blind Spot 7.1) |
| ANDON conditions converge | All three flagged .eml format acceptance, IP invocability from Apex, and EmailMessage timing as halt-everything risks. |