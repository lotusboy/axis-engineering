# Axis Engineering — Experiment Results

## Experiments Overview

**Date:** 2026-03-08
**Task:** Review the rater integration design docs (`docs/rater/`) and implementation (`APP_Rater*.cls`, `APP_PremiumReviewController.cls`, etc.)
**Codebase:** ExampleCo Commercial Property (Salesforce/Apex)
**Model:** Claude Opus 4.6 (all experiments)

Nine controlled reviews were conducted across five experiments, followed by five real-world applications on production artifacts (including the Triangle Protocol experiment).

### Method

All experiments used Claude Opus 4.6 on the same corpus (ExampleCo rater integration — 11 design docs, 7 Apex classes, 6 test classes). Each agent received different axis priming but identical scope. Agents ran as subagents with no access to other agents' outputs.

**What counts as a finding:** A distinct `(artifact, symptom, root-cause-class)` tuple. Two findings about the same class with the same root cause (e.g., "missing field X" and "missing field Y" in `APP_RatingInputFields`) merge into one finding with multiple examples.

**Deduplication across passes:** Findings are keyed by `(artifact, symptom, root-cause-class)`. Severity = `max(pass severities)`. If Pass 2 contradicts Pass 1, prefer Pass 2 if it has stronger evidence. Unique findings (only one pass) are included with source attribution.

**What counts as "unique":** A finding is unique to an experiment if no other experiment identified the same root-cause-class for the same artifact. Severity escalation (e.g., Medium→Critical) counts as unique if the escalation is supported by new evidence.

| # | Experiment | Handles | Output file |
|---|-----------|---------|-------------|
| A | Dispositional only | Seven Factors + Genba | `review-dispositional.md` |
| B | Standard (control) | None | `review-standard.md` |
| C | Full axis cocktail | Seven Factors + Genba + Fowler + SOLID + Pre-mortem + Muda + MECE + Pyramid | `review-axis-engineering.md` |
| D | Two-pass: Pass 1 | Seven Factors + Genba + Fowler + SOLID + Pre-mortem + Muda + MECE + Pyramid | `review-pass1-structured.md` |
| E | Two-pass: Pass 2 | Genba + Shoshin + Andon + Chaos Engineering + Poka-yoke | `review-pass2-verification.md` |
| F | Two-pass v2: Pass 1 (with Contract) | Seven Factors + Genba + SOLID + Pre-mortem + Axis Contract | `review-pass1-v2.md` |
| G | Two-pass v2: Pass 2 (with Contract) | Genba + Chaos Engineering + Poka-yoke + Axis Contract | `review-pass2-v2.md` |
| H | Two-pass v3: Pass 1 (Contract + Session Continuation) | Seven Factors + Genba + SOLID + Pre-mortem + Axis Contract | `review-rater-pass1-v3.md` |
| I | Two-pass v3: Pass 2 (Contract + Fresh Subagent) | Genba + Chaos Engineering + Poka-yoke + Axis Contract | `review-rater-pass2-v3.md` |

Combined synthesis of D+E: `review-combined.md`
v1 vs v2 comparison: `review-v1-vs-v2-comparison.md`

---

## Experiment 1: Dispositional vs Standard (A/B Test)

Two agents launched in parallel with identical tasks, different framing.

### Agent A — Dispositional (Gandharan + Toyota)

Prompt included Seven Factors of Awakening (Sati, Dhamma Vicaya, Viriya, Pīti, Passaddhi, Samādhi, Upekkhā) and Genba mindset ("go to the source, don't trust summaries").

### Agent B — Standard (no framing)

Same task description, no philosophical or methodological framing.

### Results

| Metric | Agent A (Dispositional) | Agent B (Standard) |
|--------|------------------------|-------------------|
| Tool uses | 31 | 26 |
| Duration | 315s (~5.25 min) | 343s (~5.7 min) |
| Tokens | 152,097 | 154,006 |
| Overall grade | B+ | No grade (findings table) |

### Shared findings (11)

Wildfire API design absent, D24 not sent, D125 defaults, `PKG_IsActive__c` not filtered, D115 contradictory, location count band disagreement, E-cell ghost field references, factor cell stale refs, `without sharing` undocumented, LWC `@wire` examples stale, stale IP references.

### Unique to Agent A (Dispositional)

1. Missing API logging in `APP_RaterService` (process gap — checked CLAUDE.md against reality)
2. Double-DML trigger risk (traced full execution chain)
3. Building-level YearBuilt changes not detected in hash
4. Deductible amount validation gap
5. Verification Matrix (systematic accuracy rating per document)

### Unique to Agent B (Standard)

1. Stale inputs on first rate call (specific line number + fix)
2. D137/D138/D140 overwrite contradiction
3. Null year-built buildings skew average age
4. `APP_RatingInputFields.FIELDS` incomplete (flagged 2 fields)
5. Doc 08 pseudocode shows `@InvocableMethod` vs actual `Callable`
6. Doc consolidation proposal

### Interpretation

Agent A found **systemic/process issues** (missing logging, trigger chains, validation gaps) — the bugs that cause production incidents months later. Agent B found **implementation/accuracy issues** (stale values, field overwrites, missing fields) — the bugs that block the current sprint. Neither was sufficient alone.

---

## Experiment 2: Full Axis Cocktail (C)

Single pass with all eight handles from both dispositional and structural axes.

### Unique findings (vs A and B)

1. **Muda analysis** — identified 5 specific wastes (dead Callable interface, global access modifier, stale doc references, hash recalculation on every load, mock IP response in production class)
2. **SOLID violations** — 3 specific violations (SRP on controller, Open/Closed on parser, DIP on service)
3. **Per-document quality scoring** — letter grades for each of the 11 docs and 7 implementation classes
4. **Doc authority hierarchy** — ranked docs by reliability (doc 08 = A, doc 07 = C+)
5. **D33/D34 stale mapping** noted

### Interpretation

The cocktail produced the most structured output with the deepest waste analysis. However, it did not find the adversarial/runtime findings that would later emerge in Pass 2. The handles shaped the *type* of analysis rather than just the depth — Muda specifically prompted waste identification, SOLID prompted architectural critique, MECE ensured completeness.

---

## Experiment 3: Two-Pass Strategy (D + E)

Two sequential passes with different axis cocktails, each blind to the other's output.

### Pass 1 — Structured (same cocktail as Experiment 2)

Found 12 findings. Strengths: completeness gaps (D24, D125), doc consistency, SOLID analysis, waste identification, per-document/class grades.

### Pass 2 — Adversarial (Genba + Shoshin + Andon + Chaos Engineering + Poka-yoke)

Found 15 findings. Strengths: runtime risk discovery (null paths, cascade traces, missing guards), observability gaps, governor limit budget analysis.

### Combined results

| Metric | Pass 1 | Pass 2 | Combined |
|--------|--------|--------|----------|
| Total findings | 12 | 15 | **19** (deduplicated) |
| Critical/P0 | 4 | 3 | **6** |
| Unique findings | 7 | 7 | — |

### Key unique findings by pass

**Only Pass 1 found:**
- D24 Policy State missing (wrong wildfire premiums)
- D125 Wildfire adj missing
- SOLID violations (3)
- Muda wastes (5)
- Doc authority hierarchy
- No retry logic on callout

**Only Pass 2 found:**
- No API logging on rater callout (C1) — zero observability
- Null YearBuilt → 687-year building age (H4)
- Null ExpirationDate silent failure (H2)
- 13 missing fields in change detection (H3) — Pass 1 found ~5, Pass 2 found the full list
- Triple trigger cascade with trace diagram (M1)
- No double-click guard (H5)
- Null customerId → malformed URL (M3)
- Zero buildings not validated (M4)
- JSONException not caught (M5)
- Misleading API log entries (H6)

---

## Cross-Experiment Comparison

### Finding discovery by experiment

| Finding | A | B | C | D | E |
|---------|---|---|---|---|---|
| Stale inputs race condition | — | ✅ | ✅ | ✅ | ✅ |
| UW field overwrite (D137/D138/D140) | — | ✅ | ✅ | ✅ | ✅ |
| Missing change-detection fields | — | ✅(2) | ✅(~5) | ✅(~5) | ✅(13) |
| D24 Policy State missing | ✅ | ✅ | ✅ | ✅ | — |
| D125 Wildfire adj missing | ✅ | ✅ | ✅ | ✅ | — |
| No API logging on callout | ✅ | — | — | — | ✅ |
| `without sharing` on @AuraEnabled | ✅ | ✅ | ✅ | ✅ | ✅ |
| Null YearBuilt → wrong age | — | ✅ | — | — | ✅ |
| Null ExpirationDate failure | — | — | — | — | ✅ |
| No double-click guard | — | — | — | — | ✅ |
| Triple trigger cascade | ✅ | — | — | — | ✅ |
| Null customerId URL | — | — | — | — | ✅ |
| Zero buildings not validated | — | — | — | — | ✅ |
| JSONException not caught | — | — | — | — | ✅ |
| Misleading API log entries | — | — | — | — | ✅ |
| SOLID violations | — | — | ✅ | ✅ | — |
| Muda wastes | — | — | ✅ | ✅ | — |
| SRP on controller | — | — | ✅ | ✅ | — |
| Stale doc references | ✅ | ✅ | ✅ | ✅ | — |
| No retry logic | — | — | — | ✅ | — |
| mockIPResponse in prod | — | — | ✅ | ✅ | — |
| global + dead Callable | — | — | ✅ | ✅ | — |

### Effectiveness ranking

| Rank | Approach | Unique findings | Total findings | Best at |
|------|----------|-----------------|----------------|---------|
| 1 | **Two-pass combined (D+E)** | 19 | 19 | Everything — strictly dominates |
| 2 | **Pass 2 adversarial alone (E)** | 7 unique | 15 | Runtime risk, null paths, cascades |
| 3 | **Axis cocktail single-pass (C)** | 3 unique | 12 | Structure, waste, grades |
| 4 | **Pass 1 structured alone (D)** | 0 unique vs C | 12 | Same as C (same cocktail) |
| 5 | **Dispositional only (A)** | 2 unique | ~16 | Process compliance, verification |
| 6 | **Standard / no framing (B)** | 2 unique | ~17 | Direct bugs, fix proposals |

### Key takeaway

**The two-pass strategy found 19 findings — 58% more than any single pass (12) and caught every critical finding.** The adversarial pass (E) is the highest-value single pass, discovering 7 findings no other approach found, including the #1 priority fix (missing API logging). But it missed structural/architectural findings (SOLID, waste, D24) that the structured pass caught.

No single axis cocktail is optimal. The cognitive separation — analytical first, adversarial second — produces deeper analysis than either mindset alone or both combined in one pass.

---

## Conclusions

1. **Axis Engineering works.** Compressed philosophical/industrial/software terms demonstrably steer LLM behavior toward specific types of analysis. The effect is consistent across experiments.

2. **Different handles find different bugs.** Muda finds waste. Chaos Engineering finds null paths. SOLID finds architectural debt. Pre-mortem finds production risks. The handle selection determines the finding profile.

3. **Over-stacking handles (7+) causes breadth at the expense of depth.** The single-pass cocktail (C) produced the most structured output but missed the deep runtime analysis that the focused adversarial pass (E) found.

4. **Two sequential passes > one larger pass.** The cognitive separation (analytical then adversarial) produces the most comprehensive review. Pass 2's "do NOT read Pass 1" instruction is critical — Shoshin (beginner's mind) prevents anchoring on prior findings.

5. **The adversarial pass is the highest-ROI single pass.** If you can only run one pass, use Genba + Shoshin + Andon + Chaos Engineering + Poka-yoke. It found the most critical and most unique findings.

6. **For routine reviews, use a single structured pass.** For pre-production audits, architecture reviews, or anything touching external APIs, use two passes.

---

## Experiment 4: Axis Contract Hardening (F + G)

Repeated the two-pass strategy with hardened prompts using the Axis Contract format.

### What Changed in the Prompts

| Element | v1 | v2 |
|---------|----|----|
| Format | Free-form instructions | Axis Contract (AXES/TARGET/STRUCTURE/EVIDENCE/STOP) |
| Evidence rules | "Read the files" | "Every finding must cite file:line. Include 'I read [file] line [N] and found [specific thing]'" |
| Assumptions | Not mentioned | "List assumptions. Mark each Verified or Unknown with proposed verification step" |
| Missing guards | Not mentioned | "For each finding, state what guard is missing (Poka-yoke)" |
| Stop condition | Not mentioned | "Andon — CRITICAL prefix for data-loss or security" |

### Results

| Metric | v1 Pass 1 | v2 Pass 1 | v1 Pass 2 | v2 Pass 2 |
|--------|-----------|-----------|-----------|-----------|
| Total findings | 12 | **14** | 15 | **17** |
| Assumption ledger | 0 | **14 items** | 0 | **13 items** |
| Evidence citations/finding | 1.5 | **2.7** | 1.5 | **2.5** |
| Findings with "missing guard" | 0 | 6 | 0 | **15** |

### New Findings Only v2 Caught

1. **Stale premium fields not cleared on re-rate** (Pass 2) — Chaos Engineering: "What if rater stops returning a cell?"
2. **D-column inputs saved even when IP fails** (Pass 2) — traced DML-before-success-check path
3. **Location band mismatch elevated to CRITICAL** (Pass 1) — cross-referenced code vs doc 09 valid values
4. **LocationTriggerHandler silent skip without logging** (Pass 2)
5. **BuildingTriggerHandler lacks FLS guard** (Pass 2) — asymmetry between two handlers
6. **Full payload in System.debug** (Pass 2) — data exposure
7. **Test mock uses wrong JSON key** (Pass 2) — success test doesn't verify premiums
8. **@AuraEnabled as dual entry point bypass** (Pass 2) — upgraded from simple `without sharing` finding
9. **HashMap iteration non-determinism in protection class mode** (Pass 1 assumption ledger)

### Biggest Win: The Assumption Ledger

The assumption ledger surfaced bugs that deeper reading alone wouldn't catch:
- A12: "HashMap iteration order in Apex is not guaranteed" — protection class mode tie-breaking is non-deterministic
- A13: "Rater returns ALL cells in every response — ASSUMED" — directly led to the stale-fields-not-cleared finding
- A5: "Gets earliest non-expired ProductRating; should it be latest?" — questions business logic correctness

These emerged because the contract forced the agent to declare "I assumed X" and then evaluate whether that assumption was verified.

### Verified vs Unknown Ratio

| Pass | Total assumptions | Verified | Unknown | Verified rate |
|------|------------------:|--------:|---------:|--------------:|
| Pass 1 v2 | 14 | 8 | 6 | 57% |
| Pass 2 v2 | 13 | 5 | 8 | 38% |
| **Combined** | **27** | **13** | **14** | **48%** |

The 48% verified rate means the agent was honest about uncertainty in roughly half its assumptions — a strong anti-hallucination signal. Every Unknown includes a proposed verification step, making the review directly actionable even where the agent couldn't confirm.

### Evidence Quality Example

**v1 finding:**
> "APP_RaterService has no API logging"

**v2 finding:**
> "I read `APP_PremiumReviewController.cls` line 260 and found `// TODO: Pass inputValues to IP instead of saving to Quote first`. The code at line 261 calls the IP first, then lines 264-276 save the inputs. `APP_RaterPayloadBuilder.buildRiskInputsJson()` at line 84 queries `FROM Quote WHERE Id = :quoteId` — it reads whatever is in the database."

v2 findings would survive a "show me" challenge. v1 findings require the reader to go verify.

### Conclusion

The Axis Contract produced **+70% evidence density**, **27 tracked assumptions** (vs 0), and **9 genuinely new findings**. The cost was slightly longer agent runtime (~350s vs ~310s). The ROI is clearly positive for pre-production audits.

**Recommended defaults:**
- Routine reviews: v1 prompts (axis cocktail, no contract)
- Pre-production audits: v2 contract (evidence rules + assumption ledger + stop conditions)
- Security reviews: v2 contract + Poka-yoke "missing guard" mandatory

---

## Experiment 5: Two-Pass v3 (Contract + Session Continuation)

Repeated the two-pass strategy with the same Axis Contract as v2. The key difference: v3 ran in a continued session where Pass 1 executed first, then Pass 2 ran as a fresh subagent with explicit "do NOT read Pass 1" instruction. Pass 1's context had been summarized due to context window limits before Pass 2 launched, meaning Pass 2 had zero access to Pass 1's findings.

### What Changed in v3 vs v2

| Element | v2 | v3 |
|---------|----|----|
| Session context | Fresh session for each pass | Continued session; Pass 1 ran first, Pass 2 launched after context compaction |
| Axis Contract | Identical | Identical |
| Pass 2 isolation | Separate subagent, no access to Pass 1 | Separate subagent with explicit "do NOT read Pass 1" instruction |
| Handles | Same per pass | Same per pass |

The Axis Contract was unchanged. The only variable was session context: v2 passes ran in completely independent sessions, while v3 Pass 2 ran after Pass 1's context had been compacted within the same parent session.

### Results

| Metric | v1 Pass 1 | v2 Pass 1 | v3 Pass 1 | v1 Pass 2 | v2 Pass 2 | v3 Pass 2 |
|--------|-----------|-----------|-----------|-----------|-----------|-----------|
| Total findings | 12 | 14 | **19** | 15 | 17 | **18** |
| Critical | 4 | 2 | **2** | 3 | 2 | **1** |
| High | — | — | **5** | 6 | 6 | **7** |
| Medium | — | — | **8** | 6 | 7 | **6** |
| Low | — | — | **4** | — | — | **4** |
| Assumption ledger | 0 | 14 | **10** | 0 | 13 | **10** |
| Evidence citations/finding | 1.5 | 2.7 | **~2.5** | 1.5 | 2.5 | **~2.5** |
| Findings with "missing guard" | 0 | 6 | **0** | 0 | 15 | **~12** |
| Unique findings (within experiment) | — | — | **4** | — | — | **5** |

**Note on v3 Pass 1 finding count:** v3 Pass 1 produced 19 findings vs v2 Pass 1's 14 because it included more granular LOW-severity items (redundant null check, hardcoded isDisabled(), unused DTO fields, System.debug) that v2 Pass 1 either omitted or folded into waste analysis. The CRITICAL+HIGH count is comparable (7 in v3 Pass 1 vs ~8 in v2 Pass 1 when including items from the consistency/waste sections).

**Note on v3 Pass 2 finding count:** v3 Pass 2 initially listed 19 findings but explicitly retracted M6 (TypeException catch) after deeper analysis, yielding 18 actual findings. v3 Pass 2 also downgraded its C2 (global access modifier) from CRITICAL to HIGH in the text, so the effective severity distribution is: 1 Critical, 7 High, 6 Medium, 4 Low.

### Verified vs Unknown Ratio (v3)

| Pass | Total assumptions | Verified | Unknown | Verified rate |
|------|------------------:|--------:|---------:|--------------:|
| Pass 1 v3 | 10 | 4 | 6 | 40% |
| Pass 2 v3 | 10 | 4 | 6 | 40% |
| **v3 Combined** | **20** | **8** | **12** | **40%** |
| **v2 Combined** | **27** | **13** | **14** | **48%** |

v3 produced fewer total assumptions (20 vs 27) but a similar verified rate (40% vs 48%). Both versions were honest about uncertainty. The smaller ledger may reflect context compaction reducing the agent's capacity for meta-reasoning.

### New Findings Unique to v3 (Not in v2)

Four findings appeared in v3 that were not present in any v2 review:

1. **v3 Pass 1 LOW-2: Redundant null check (ternary no-op)** — `APP_RaterPayloadBuilder.cls:233` has `x != null ? x : null` which is semantically equivalent to just `x`. Minor code quality issue.

2. **v3 Pass 1 LOW-4: `APP_QuoteTriggerHandler.isDisabled()` hardcoded to false** — No runtime bypass mechanism for data migrations or bulk operations. Other MGA handlers typically read from CMDT.

3. **v3 Pass 2 M8: Fragile success check** — `APP_PremiumReviewController.cls:277` uses `ipResult.get('success') == false` which evaluates to `false` when the key is absent (null == false is false in Apex), so missing key is treated as success.

4. **v3 Pass 2: Re-rate trigger cascade step-state bug (specific conclusion)** — While v2 Pass 2 identified the triple trigger cascade, v3 Pass 2 traced the specific DML ordering to a concrete bug: on re-rate, DML #2 (D-column input save) triggers `APP_QuoteTriggerHandler` which resets `PKG_QuoteStep__c` to "In Progress", and DML #3 sets `APP_PremiumReviewComplete__c = true` on the Quote but does NOT restore the step to "Complete". The traffic light stays orange after every successful re-rate. This specific conclusion was not stated in v2.

### Findings v2 Found That v3 Missed

Six findings from v2 were absent from both v3 passes:

1. **D24 Policy State not sent in payload** — v2 Pass 1 flagged this (§3.2) and the v1 combined review listed it as P0. v3 mentions D125 (MED-8) but never mentions D24. This is the most significant miss -- D24 is a CRITICAL-tier finding in v1/v2.

2. **UW premium overwrite (D137/D138/D140 parser issue)** — v2 Pass 1 CRITICAL-1 identified that `APP_RaterOutputParser` writes D137/D138/D140 to the same fields the UW manually enters, silently erasing UW overrides. v3 Pass 1 HIGH-5 covers save() overwriting rater values (the reverse direction) but not the parser overwriting UW values. Partial overlap, but the specific D137/D138/D140 data-loss scenario is absent.

3. **Zero buildings not validated before rating** — v2 Pass 2 M4 (also in v1 combined as finding #14). A Quote with zero buildings sends nonsensical aggregates to the rater. Not mentioned in v3.

4. **LocationTriggerHandler silent skip without logging** — v2 Pass 2 M5. The handler's `hasExampleCoFieldAccess()` guard returns silently with no log. Not mentioned in v3.

5. **BuildingTriggerHandler lacks FLS guard** — v2 Pass 2 M6. Asymmetry between the two trigger handlers. Not mentioned in v3.

6. **Null ExpirationDate silent failure** — v2 Pass 2 H2 (also in v1 combined as finding #8). v3 Pass 2 mentions this only in the "test coverage gaps" section as an untested path, not as a finding with severity/recommendation.

**Ambiguous overlap:**
- v2 Pass 1 A12 (HashMap iteration non-determinism in protection class mode) appeared in v2's assumption ledger and is absent from v3's ledger. However, this is an assumption-ledger item rather than a finding.
- v2 Pass 2 H3 (D-column inputs saved even when IP fails) -- v3 Pass 2 does not have this as a standalone finding, though the DML ordering analysis in v3 Pass 2 M5 partially covers the same territory.

### Cross-Version Finding Discovery Table

| Finding | A | B | C | D | E | F | G | H | I |
|---------|---|---|---|---|---|---|---|---|---|
| Stale inputs race condition | — | yes | yes | yes | yes | yes | yes | **yes** | **yes** |
| UW field overwrite (D137/D138/D140) | — | yes | yes | yes | yes | yes | yes | — | — |
| Missing change-detection fields | — | yes(2) | yes(~5) | yes(~5) | yes(13) | yes(~5) | yes(13) | **yes(2)** | **yes(13)** |
| D24 Policy State missing | yes | yes | yes | yes | — | yes | — | — | — |
| D125 Wildfire adj missing | yes | yes | yes | yes | — | yes | — | **yes** | — |
| No API logging on callout | yes | — | — | — | yes | — | yes | **yes** | **yes** |
| `without sharing` on @AuraEnabled | yes | yes | yes | yes | yes | yes | yes | **yes** | **yes** |
| Null YearBuilt -> wrong age | — | yes | — | — | yes | — | yes | **yes** | **yes** |
| Null ExpirationDate failure | — | — | — | — | yes | — | yes | — | — |
| No double-click guard | — | — | — | — | yes | — | yes | — | **yes** |
| Triple trigger cascade | yes | — | — | — | yes | — | yes | **yes** | **yes** |
| Null customerId URL | — | — | — | — | yes | — | yes | **yes** | **yes** |
| Zero buildings not validated | — | — | — | — | yes | — | yes | — | — |
| JSONException not caught | — | — | — | — | yes | — | — | — | — |
| Misleading API log entries | — | — | — | — | yes | — | — | — | **yes** |
| SOLID violations | — | — | yes | yes | — | yes | — | **yes** | — |
| Muda wastes | — | — | yes | yes | — | — | — | — | — |
| SRP on controller | — | — | yes | yes | — | yes | — | — | — |
| Stale doc references | yes | yes | yes | yes | — | yes | — | **yes** | — |
| No retry logic | — | — | — | yes | — | — | yes | — | **yes** |
| mockIPResponse in prod | — | — | yes | yes | — | — | — | — | — |
| global + dead Callable | — | — | yes | yes | — | yes | yes | **yes** | **yes** |
| Stale fields not cleared on re-rate | — | — | — | — | — | — | yes | — | **yes** |
| D-column saved on IP failure | — | — | — | — | — | — | yes | — | — |
| Location band elevated to CRITICAL | — | — | — | — | — | yes | — | **yes** | — |
| LocationTriggerHandler silent skip | — | — | — | — | — | — | yes | — | — |
| BuildingTriggerHandler lacks FLS | — | — | — | — | — | — | yes | — | — |
| Full payload in System.debug | — | — | — | — | — | — | yes | **yes** | **yes** |
| Test mock wrong key | — | — | — | — | — | — | yes | — | **yes** |
| @AuraEnabled dual entry point | — | — | — | — | — | — | yes | — | **yes** |
| HashMap non-determinism (A-ledger) | — | — | — | — | — | yes | — | — | — |
| save() overwrites rater outputs | — | — | — | — | — | — | yes | **yes** | **yes** |
| Redundant null check (ternary no-op) | — | — | — | — | — | — | — | **yes** | — |
| isDisabled() hardcoded | — | — | — | — | — | — | — | **yes** | — |
| Fragile success check (null==false) | — | — | — | — | — | — | — | — | **yes** |
| Re-rate step-state bug (specific) | — | — | — | — | — | — | — | — | **yes** |

**Legend:** A-E = Experiments 1-3 (v1), F-G = Experiment 4 (v2), H-I = Experiment 5 (v3).

### Key Observations

#### 1. Reproducibility: Core findings are stable across versions

The "big 5" findings appear in every version that used the Contract:
- Stale inputs race condition (v1, v2, v3 -- all passes)
- `without sharing` on `@AuraEnabled` (v1, v2, v3 -- all passes)
- Missing change-detection fields (v1, v2, v3 -- all passes, with Pass 2 consistently finding more fields)
- No API logging on callout (v1 Pass 2, v2 Pass 2, v3 both passes)
- Null YearBuilt wrong age (v1 Pass 2, v2 Pass 2, v3 both passes)

These findings are **highly reproducible** -- the same root causes are independently rediscovered across 3 separate runs with different session contexts. This suggests they are genuine signal, not artifacts of prompt framing.

#### 2. Session continuation had mixed effects on quality

**Positive:** v3 Pass 1 found more total findings (19 vs 14 in v2 Pass 1), including several LOW-severity items that v2 omitted. v3 Pass 2 produced a detailed trigger cascade trace with a specific step-state bug conclusion that v2 didn't reach.

**Negative:** v3 missed D24 Policy State (a CRITICAL-tier finding in v1/v2), the D137/D138/D140 UW overwrite (CRITICAL in v2), and several medium-severity findings (zero buildings, LocationTriggerHandler skip, BuildingTriggerHandler FLS). The assumption ledger was smaller (20 vs 27 items) and the "missing guard" annotation was inconsistently applied in Pass 1 (0 findings with missing guard vs 6 in v2 Pass 1).

**Interpretation:** Context compaction may have reduced the agent's working memory for the comprehensive "what's missing from the payload" analysis that catches omission bugs like D24. Meanwhile, the agent compensated by going deeper on individual findings it did discover (e.g., the cascade step-state bug). This is a breadth-vs-depth tradeoff.

#### 3. Contract stability: v2 and v3 converge on ~75% of findings

Counting deduplicated findings across both passes:

| | v2 only | v3 only | Both v2 and v3 |
|-|--------:|--------:|---------------:|
| Findings | 6 | 4 | ~20 |

The 6 v2-only findings are mostly medium-severity (LocationTriggerHandler, BuildingTriggerHandler, zero buildings, D-column saved on failure) plus two critical-tier misses (D24, D137/D138/D140 overwrite). The 4 v3-only findings are all low-to-medium severity. The core high-value findings converge.

This ~75% overlap rate across independent runs with the same Contract suggests the Contract provides strong guidance for reproducibility but does not guarantee completeness. Two runs with the same Contract will find the same important bugs but may differ on edge-case and medium-severity findings.

#### 4. Pass 2 isolation worked correctly

v3 Pass 2 produced genuinely independent findings. It did not simply echo Pass 1's discoveries. Several findings were independently rediscovered (stale inputs, without sharing, missing fields) which validates the isolation mechanism. The fresh subagent approach with explicit "do NOT read Pass 1" instruction is effective even within a continued session.

### Updated Effectiveness Ranking

| Rank | Approach | Unique findings | Total findings | Best at |
|------|----------|-----------------|----------------|---------|
| 1 | **Two-pass v2 combined (F+G)** | ~30 deduplicated | 31 raw | Highest total coverage; caught D24 and D137/D138/D140 |
| 2 | **Two-pass v3 combined (H+I)** | ~26 deduplicated | 37 raw | Deepest individual finding analysis; cascade step-state bug |
| 3 | **Two-pass v1 combined (D+E)** | 19 | 27 raw | Baseline two-pass; proved the approach |
| 4 | **Pass 2 adversarial alone (any version)** | 7+ unique | 15-18 | Runtime risk, null paths, cascades |
| 5 | **Axis cocktail single-pass (C)** | 3 unique | 12 | Structure, waste, grades |
| 6 | **Dispositional only (A)** | 2 unique | ~16 | Process compliance, verification |
| 7 | **Standard / no framing (B)** | 2 unique | ~17 | Direct bugs, fix proposals |

---

## Updated Conclusions

1. **Axis Engineering works.** Compressed philosophical/industrial/software terms demonstrably steer LLM behavior toward specific types of analysis. The effect is consistent across all five experiments and three versions of the two-pass strategy.

2. **Different handles find different bugs.** Muda finds waste. Chaos Engineering finds null paths. SOLID finds architectural debt. Pre-mortem finds production risks. The handle selection determines the finding profile. This holds across all versions.

3. **Over-stacking handles (7+) causes breadth at the expense of depth.** The single-pass cocktail (C) produced the most structured output but missed the deep runtime analysis that the focused adversarial pass (E) found.

4. **Two sequential passes > one larger pass.** The cognitive separation (analytical then adversarial) produces the most comprehensive review. This is confirmed by all three versions (v1, v2, v3). The combined output is strictly stronger than either pass alone in every case.

5. **The adversarial pass is the highest-ROI single pass.** If you can only run one pass, use Genba + Chaos Engineering + Poka-yoke. It found the most critical and most unique findings across all three versions.

6. **The Axis Contract improves evidence quality and assumption tracking but does not guarantee finding completeness.** v2 and v3 both used identical Contracts. v2 caught D24 and D137/D138/D140 overwrite; v3 missed both but found the cascade step-state bug and fragile success check. The Contract provides strong guardrails for *how* findings are reported but does not fully control *which* findings are discovered.

7. **Reproducibility is high for critical findings, moderate for medium-severity findings.** The "big 5" findings appeared in all three versions. Medium-severity and edge-case findings varied by ~25% across runs. For maximum coverage, running the two-pass strategy twice (4 total passes) and deduplicating would catch nearly everything.

8. **Session continuation introduces a breadth-vs-depth tradeoff.** v3's continued session context may have caused the agent to go deeper on individual findings at the expense of comprehensive payload/omission analysis. For maximum breadth, fresh sessions (v2 approach) may be preferable. For maximum depth on known-problematic areas, continued sessions (v3 approach) may be preferable.

9. **Recommended defaults (updated):**
   - Routine reviews: v1 prompts (axis cocktail, no contract)
   - Pre-production audits: v2 contract in a fresh session (evidence rules + assumption ledger + stop conditions)
   - Critical security reviews: Run v2 contract twice (4 passes) and deduplicate findings
   - Deep-dive on specific subsystem: v3 approach (continued session, contract)

---

## Real-World Applications

These are not controlled experiments — they are production uses of the methodology on real project artifacts. They demonstrate that the handles and contracts transfer beyond code review to design review, documentation analysis, implementation retrospectives, and multi-agent solution space exploration.

### Application 1: Wildfire API Design Review

**Date:** 2026-03-09
**Handles:** Genba + MECE + Pre-mortem + Poka-yoke (with Axis Contract)
**Target:** `docs/wildfire-integration/WILDFIRE_API_SOLUTION_DESIGN.md` — 687-line solution design doc for a ExampleCo-hosted wildfire API
**Output:** `testing/review-wildfire-design.md`

**Results:**

| Metric | Value |
|--------|-------|
| Grade | B- |
| Total findings | 15 (1 P0, 5 P1, 6 P2, 3 P3) |
| Assumption ledger | 16 items (14 verified, 1 refuted, 1 partial) |
| MECE completeness gaps | 7 |
| Evidence citations/finding | ~2.5 |

**Key findings:**
- **P0-1:** `Callable` interface + `@AuraEnabled` static method conflict — will not compile as designed. The doc claims both patterns simultaneously, but a static method cannot satisfy a non-static interface.
- **P1-1:** `APP_OccupancyType__c` is `Text(255)`, not `Picklist` as the doc claims — Genba verified against actual field metadata.
- **P1-4:** 120s callout timeout contradicts confirmed 5-15s API latency — the design copied a boilerplate timeout without adjusting for the specific API.
- **P1-5:** API logging placed after Quote DML creates an audit gap — if the DML fails, the API call is unlogged.

**What the assumption ledger caught:** A14 ("APP_OccupancyType__c is a Picklist") was marked Unknown, then refuted by reading the actual field metadata. Without the ledger requirement, the agent would have accepted the doc's claim at face value.

**Insight:** MECE is particularly effective on design documents. It forces completeness checking against the actual system components — the 7 gaps (error handling, retry logic, Named Credential setup, test strategy, etc.) were invisible in a linear read of the doc but immediately apparent when checking whether every system concern was addressed.

### Application 2: Rater Documentation Chain Review

**Date:** 2026-03-09
**Handles:** First Principles + Genba + MECE (informal — no Axis Contract)
**Target:** `docs/rater/00-07` (analysis) → `08` (design) → `09` (validation)
**Output:** Inline analysis (not a separate file)

**Scope:** Assess whether 8 analysis docs properly supported the design doc, and whether the validation confirmed the design.

**Results:**

| Metric | Value |
|--------|-------|
| Chain completeness | 85% |
| Design decisions traced to source docs | 100% of major decisions |
| Validation bugs found | 6 (all implementation details, 0 design flaws) |
| Gaps identified | 3 blocking, 2 unresolved |

**Key findings:**
- Every major design decision in doc 08 traces to a supporting analysis doc (field mappings → doc 02, SOV aggregations → doc 01, architecture → doc 06, picklist strategy → doc 05).
- Doc 09 validation found 6 bugs — cell mapping swaps, value format mismatches — but no architectural flaws. The design withstood validation.
- **Critical gap:** `Product2.PKG_RatingType__c` (mandatory configuration for the entire integration to work) wasn't discovered until doc 07 via AI model analysis. Docs 00-06 don't mention it. Without doc 07's model-driven insights, this would have blocked the team on day 1 of implementation.
- **Unresolved:** Wildfire API details and deductibles re-rating UX — both flagged as HIGH PRIORITY in doc 00 but still open by doc 08.

**Insight:** First Principles is the right handle for doc chain review. It forces "does this decision have a documented reason?" for each design choice. This caught that the chain was strong on field mapping but weak on prerequisite configuration — the gap that would block a project before any code is written.

### Application 3: Implementation Retrospective

**Date:** 2026-03-09
**Handles:** Genba + Pre-mortem + Five Whys (informal — no Axis Contract)
**Target:** Design docs (06, 08) → tickets (APP-186 through APP-200) → implementation summary → actual source code
**Output:** Inline analysis (not a separate file)

**Scope:** Assess whether the right solution was built, where it deviated from the design, and whether Axis Engineering would have arrived at the same design.

**Results:**

| Metric | Value |
|--------|-------|
| Tickets executed as planned | 11 of 15 |
| Tickets created but removed | 2 (IP tickets — platform constraint) |
| Tickets not needed | 1 (ephemeral strings replaced stored fields) |
| Tickets deferred | 1 (production deploy steps) |
| Architectural deviation | 1 (IP bypass → direct service) |
| Deviation justified | Yes — hard platform constraint |

**The deviation:** The original design specified an OmniStudio IP chain (`PKG_Rate IP → APP_Rate_Before IP → callout → APP_Rate_After IP`). During implementation, the team discovered that OmniStudio IPs perform internal DML before Remote Actions, causing `DML-before-callout` errors. The IPs were built, tested, and then deliberately removed. A direct `APP_RaterService` facade was created instead.

**Five Whys trace:**
1. Why did the IP approach fail? → OmniStudio performs internal DML before callouts.
2. Why wasn't this discovered during design? → Doc 06 designed around the IP chain based on documentation, not source code verification.
3. Why wasn't the source code verified? → The analysis phase (docs 00-07) focused on field mapping and architecture, not framework implementation details.
4. Why didn't the framework details surface? → Nobody read the `PKG_Rate` IP source code before designing the custom extension path.
5. Why? → **Genba was not applied to the framework layer.** The team verified Salesforce fields and data model (thorough) but trusted the OmniStudio framework abstractions (assumption).

**Counterfactual:** Genba applied during doc 06 authoring would have required reading the actual `PKG_Rate` IP source code — not the documentation, not the architecture diagram, the source. This would have surfaced the DML-before-callout constraint before any tickets were created. Estimated savings: ~3 days of investigation + 2 throwaway tickets (APP-192, APP-195).

**The design itself would have been identical.** The same classes, the same field mappings, the same test strategy. The only difference: `APP_RaterService` would have been in the original design (doc 08) instead of being an "emergency bypass" discovered during implementation.

**Insight:** This is the strongest evidence that Axis Engineering works beyond code review. The methodology doesn't produce a *different* design — it produces the *same* design faster by catching framework constraints before they become implementation blockers.

### Application 4: Solution Design Generation (Ping Vision Integration)

**Date:** 2026-03-09
**Handles:** Cynefin + First Principles + MECE + Pre-mortem (with Axis Contract)
**Target:** `testing/ping-requirements-only.md` — 247-line requirements-only document (all solution design stripped from 5 Ping integration docs)
**Output:** `testing/ping-design-from-requirements.md` (781 lines)
**Comparison baseline:** Steve's actual solution design (`docs/ping-integration/PING_INTEGRATION_SOLUTION_DESIGN.md`, 760 lines)

**Task:** Generate a complete Salesforce solution design from requirements alone — no access to any existing solution design, class names, data model, or implementation details. Then compare with the actual design that was built.

**Results:**

| Metric | Value |
|--------|-------|
| Classes matching actual design | **9 of 10** (exact name + responsibility match) |
| Data model match | **10/10** — object, fields, naming all identical |
| Configuration match | **9/10** — same CMDT + Custom Setting split; missed NC indirection |
| Execution pattern match | **10/10** — same Queueable/Batchable/scope/bypass patterns |
| Overall architectural similarity | **~90%** |

**What matched exactly (9 classes):**
- `APP_EmailMessageTriggerHandler` — trigger handler with attachment check, reuse/skip logic
- `APP_PingApiSubmissionInitiator` — Queueable, .eml construction, POST /submission, Finalizer
- `APP_PingApiEventPoller` — Batchable, cursor-based event polling
- `APP_PingApiInceptionDateRetriever` — Queueable, inception date fetch + trigger date calculation
- `APP_PingApiDataEntryTrigger` — Batchable, daily date comparison
- `APP_PingApiStatusUpdater` — Batchable, PATCH confirmation
- `APP_PingSubmissionCreator` — 3-phase orchestrator (IP + IP + CMDT mapper)
- `APP_PingIpInputBuilder` — IP input JSON builder with ProductConfig inner class
- `APP_PingRecordMapper` — Phase 3: location grouping, building linking, value transforms

**What was missing (4 items):**
1. `APP_PingApiOutputProcessor` — separate batch for RUN_OUTPUTTERS polling + document download (Axis folded this into the event poller)
2. Named Credential indirection — Steve's design stores the NC name in `API_Base_URL__c` CMDT field so code does `callout:{API_Base_URL__c}/submission`, allowing NC swaps without code changes
3. Scheduler classes — Steve has 4 separate schedulers for admin reconfigurability; Axis made batch classes implement Schedulable directly
4. Case trigger for date syncing — Steve has a dedicated trigger to sync `Data_Entry_Scheduled_Date__c` from Case to `APP_Ping_Submission__c`

**What the Pre-mortem caught:**
- IP rollback risk (Assumption A3: "IPs may commit internally — test whether rollback works across IP invocations") — this is the same DML constraint discovered during rater implementation
- Cursor corruption as the #1 failure mode — correctly identified why Custom Setting is needed
- .eml construction as a complexity hotspot

**What the Assumption Ledger caught:**
- 12 assumptions tracked, 7 verified, 5 unknown
- A3 (IP rollback safety) and A10 (RUN_OUTPUTTERS job structure) were correctly flagged as Unknown with proposed verification steps

**Insight:** This is the most demanding test of Axis Engineering to date. The methodology was not reviewing existing work or finding bugs — it was *generating* a complete solution design from scratch. The ~90% match with a human-designed, implemented, and tested architecture demonstrates that the handles (particularly Cynefin for domain categorisation, First Principles for decomposition, and MECE for completeness) guide the LLM toward the same architectural decisions a human engineer reaches. The 4 gaps are all reasonable design choices that a code review would catch — the core architecture (the hard part) was correct.

**Follow-up:** The 4 gaps from this experiment became the hypothesis test case for the Triangle Protocol (Application 5 below).

### Application 5: Triangle Protocol — Solution Space Exploration (Ping Vision Integration)

**Date:** 2026-03-24
**Protocol:** Triangle Protocol (3 diverge agents + 1 synthesis agent)
**Agent handles:**
- TQ (Time+Quality): Cynefin + MECE + First Principles + Pre-mortem
- TC (Time+Cost): Cynefin + MECE + YAGNI + Theory of Constraints
- CQ (Cost+Quality): Cynefin + MECE + Muda + Kent Beck's Four Rules
- Synthesis: Cynefin + MECE + First Principles

**Target:** `testing/ping-requirements-only.md` — same 271-line requirements document used in Application 4
**Outputs:**
- `testing/triangle-ping-agent-tq.md` — Time+Quality design
- `testing/triangle-ping-agent-tc.md` — Time+Cost design
- `testing/triangle-ping-agent-cq.md` — Cost+Quality design
- `testing/triangle-ping-synthesis.md` — Comparison and synthesis

**Comparison baseline:** Application 4's single-agent design (781 lines, ~90% match, 4 silent gaps)

**Task:** Test whether 3 independent agents with different Iron Triangle constraint pairs would surface the 4 gaps from Application 4 as explicit design choices rather than silent omissions.

**Results:**

| Metric | Single-Agent (App 4) | Triangle Protocol (App 5) |
|--------|---------------------|--------------------------|
| Designs produced | 1 | 3 |
| Architectural gaps (silent) | 4 | 0 — all surfaced as divergence points |
| Convergence points | N/A | 7 (high-confidence decisions) |
| Divergence points | N/A | 6 (genuine tradeoff zones) |
| Blind spots identified | 0 | 8 (1 P0, 5 P1, 2 P2) |
| Requirements contradictions found | 0 | 1 (Cleared status — P0 blocker) |
| Hybrid options proposed | N/A | 4 |
| Token cost | 1x | ~4x |

**The 4 original gaps — all surfaced:**

| Gap from Application 4 | Where it surfaced in synthesis |
|---|---|
| Missing dedicated output processor batch | Divergence 2.1 — the #1 divergence point. TQ/CQ built separate output processors; TC consolidated into a single batch. Synthesis called this "the single highest-stakes tradeoff." |
| Missing separate scheduler classes | Divergence 2.1 — TQ: 4 schedulers, CQ: 4 schedulers, TC: 0 (self-scheduling batch). Explicitly compared in effort table. |
| Missing Named Credential indirection | Convergence 1.2 (all three used Named Credentials) + Divergence 2.4 (shared API client vs inline callouts). |
| Missing Case-to-submission date sync trigger | Divergence 2.3 — CQ's user-driven Cleared pattern requires a Case trigger to sync dates; TC/TQ automate inception date retrieval instead. |

**Agent output comparison:**

| Agent | Functional Classes | Schedulers | Test Classes | Total Components | Effort Estimate |
|---|---|---|---|---|---|
| **TC** (Time+Cost) | 5 | 0 | ~4 | ~92 | ~55 hours |
| **CQ** (Cost+Quality) | 7 | 4 | 12+ | ~112 | ~105 hours |
| **TQ** (Time+Quality) | 10 | 4 | 11 | ~105 | ~100 hours |

The designs are genuinely different — not anchored variations. TC produced a God-class `APP_PingEventPollerBatch` combining all processing; TQ produced well-separated classes with 4 independent scheduled jobs; CQ produced a NULL-timestamp coordination pattern with user-driven Cleared status and the most thorough "Components NOT Built" justification.

**Bonus finding — requirements contradiction:**

The synthesis agent flagged a P0 blocker that no single-agent run had detected: requirement 3 states "Data Entry is the ONLY outbound status change," but TQ and CQ both designed Cleared as an additional outbound status change. TC took the requirement literally. This disagreement surfaced a genuine requirements ambiguity — CQ explicitly flagged it as Unknown Assumption U8 with the note "Confirm with Ping whether Cleared has `is_valid_for_user_transition = true`."

This is the strongest argument for the Triangle Protocol: multi-agent divergence surfaces **requirements ambiguities**, not just design alternatives. A single agent silently picks one interpretation. Three agents may pick different interpretations, and the synthesis agent flags the disagreement.

**Synthesis quality:**

The synthesis agent produced a 380-line structured comparison with all 8 required sections (Executive Summary, Convergence, Divergence, Tradeoff Matrix, Effort Comparison, Hybrid Opportunities, Risk Register, Blind Spots) plus a Next Steps section. Improvements applied after initial synthesis: prioritised decision guide (top 3 decisions), normalised effort estimates, uncertainty ranges on hybrid estimates, priority-ranked blind spots (P0/P1/P2), and suggested next steps.

**Insight:** The Triangle Protocol adds genuine value for architecture decisions where tradeoffs matter. The ~4x token cost is justified when the alternative is discovering silent gaps during implementation. The protocol's strongest finding was not one of the 4 predicted gaps — it was the requirements contradiction, a category of finding that single-agent design generation cannot produce because it requires multiple independent interpretations of the same requirement. The protocol also demonstrated that the Iron Triangle constraint pairs produce genuinely independent designs (not anchored variations) because each pair activates different handle cocktails in separate contexts. See `triangle-protocol.md` for the full protocol specification and methodology.

### Cross-Application Observations

1. **Handles transfer across artifact types.** Genba (verify against source) works on code, design docs, and doc chains. MECE (no gaps) works on code coverage and design completeness. Pre-mortem (assume failure) works on code deployment and design readiness. Cynefin + First Principles + MECE work for solution design generation.

2. **The assumption ledger is valuable in every context.** In code review it catches runtime assumptions. In design review it catches field type assumptions. In retrospectives it catches framework behavior assumptions. In design generation it catches platform constraint assumptions. In multi-agent synthesis it catches requirements ambiguities. The forcing function is the same: declare what you assumed, then check.

3. **Design review needs different handle combinations than code review.** Code review benefits from Fowler + SOLID (pattern recognition). Design review benefits from MECE + First Principles (completeness + justification). Design generation benefits from Cynefin + First Principles + MECE + Pre-mortem (domain sizing + decomposition + completeness + failure anticipation). Solution space exploration benefits from the Triangle Protocol (3 agents with different constraint pairs + synthesis). Both benefit from Genba (verify) and Pre-mortem (assume failure).

4. **The Genba gap is consistent.** In every application, the most impactful finding was something that could only be caught by reading the actual artifact (field metadata, framework source code, existing implementation) rather than trusting documentation or abstractions. Genba is the single most valuable handle across all contexts.

5. **Design generation is the ultimate completeness test for MECE.** When generating (not reviewing), MECE forces the agent to ask "what's missing from this design?" at every level — objects, fields, classes, execution flow, scheduling, error handling. The 4 gaps in the Ping design are all things MECE *could* have caught with more exhaustive system boundary analysis (scheduler separation, date sync direction, output processing isolation).

6. **Multi-agent divergence surfaces requirements ambiguities that single-agent approaches cannot.** Application 5 demonstrated that a single agent silently picks one interpretation of an ambiguous requirement, while three independent agents may pick different interpretations. The synthesis agent then flags the disagreement. This is a category of finding unavailable to any single-agent strategy — it requires independent parallel generation under different constraints. The requirements contradiction found in Application 5 (Cleared as outbound status change) would have been discovered during implementation otherwise.

7. **The Iron Triangle produces genuine divergence, not anchored variations.** Application 5 produced designs ranging from 5 to 10 classes, with fundamentally different async architectures (monolith vs separated batches), different automation scopes (fully automated vs user-driven), and different configuration strategies (key-value vs typed CMDT). Context isolation and different handle cocktails prevent the anchoring that plagues "give me 3 options" in a single context.

8. **Convergence across independent agents is a strong correctness signal.** When all three Triangle Protocol agents independently make the same choice (7 convergence points in Application 5), that's stronger evidence than one agent making the choice once. Convergence points can be adopted with high confidence. This is the multi-agent analogue of reproducibility in the two-pass experiments (the "big 5" findings appearing across all versions).