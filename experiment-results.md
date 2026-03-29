# Axis Engineering — Experiment Results

## Experiments Overview

**Date:** 2026-03-08
**Task:** Review the rater integration design docs (`docs/rater/`) and implementation (`APP_Rater*.cls`, `APP_PremiumReviewController.cls`, etc.)
**Codebase:** ExampleCo Commercial Property (Salesforce/Apex)
**Model:** Claude Opus 4.6 (all experiments)

Nine controlled reviews were conducted across five experiments, followed by eleven real-world applications on production artifacts (including three Triangle Protocol experiments and four two-pass reviews spanning Salesforce/Apex, TypeScript/Node.js, JavaScript/Azure, Python, and Bash/DevOps).

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

2. **v3 Pass 1 LOW-4: `APP_QuoteTriggerHandler.isDisabled()` hardcoded to false** — No runtime bypass mechanism for data migrations or bulk operations. Other PKG handlers typically read from CMDT.

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

### Application 4: Solution Design Generation (ExampleVision Integration)

**Date:** 2026-03-09
**Handles:** Cynefin + First Principles + MECE + Pre-mortem (with Axis Contract)
**Target:** `testing/examplevision-requirements-only.md` — 247-line requirements-only document (all solution design stripped from 5 ExampleVision integration docs)
**Output:** `testing/examplevision-design-from-requirements.md` (781 lines)
**Comparison baseline:** Steve's actual solution design (`docs/examplevision-integration/EXAMPLEVISION_INTEGRATION_SOLUTION_DESIGN.md`, 760 lines)

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
- `APP_ExampleVisionApiSubmissionInitiator` — Queueable, .eml construction, POST /submission, Finalizer
- `APP_ExampleVisionApiEventPoller` — Batchable, cursor-based event polling
- `APP_ExampleVisionApiInceptionDateRetriever` — Queueable, inception date fetch + trigger date calculation
- `APP_ExampleVisionApiDataEntryTrigger` — Batchable, daily date comparison
- `APP_ExampleVisionApiStatusUpdater` — Batchable, PATCH confirmation
- `APP_ExampleVisionSubmissionCreator` — 3-phase orchestrator (IP + IP + CMDT mapper)
- `APP_ExampleVisionIpInputBuilder` — IP input JSON builder with ProductConfig inner class
- `APP_ExampleVisionRecordMapper` — Phase 3: location grouping, building linking, value transforms

**What was missing (4 items):**
1. `APP_ExampleVisionApiOutputProcessor` — separate batch for RUN_OUTPUTTERS polling + document download (Axis folded this into the event poller)
2. Named Credential indirection — Steve's design stores the NC name in `API_Base_URL__c` CMDT field so code does `callout:{API_Base_URL__c}/submission`, allowing NC swaps without code changes
3. Scheduler classes — Steve has 4 separate schedulers for admin reconfigurability; Axis made batch classes implement Schedulable directly
4. Case trigger for date syncing — Steve has a dedicated trigger to sync `Data_Entry_Scheduled_Date__c` from Case to `APP_ExampleVision_Submission__c`

**What the Pre-mortem caught:**
- IP rollback risk (Assumption A3: "IPs may commit internally — test whether rollback works across IP invocations") — this is the same DML constraint discovered during rater implementation
- Cursor corruption as the #1 failure mode — correctly identified why Custom Setting is needed
- .eml construction as a complexity hotspot

**What the Assumption Ledger caught:**
- 12 assumptions tracked, 7 verified, 5 unknown
- A3 (IP rollback safety) and A10 (RUN_OUTPUTTERS job structure) were correctly flagged as Unknown with proposed verification steps

**Insight:** This is the most demanding test of Axis Engineering to date. The methodology was not reviewing existing work or finding bugs — it was *generating* a complete solution design from scratch. The ~90% match with a human-designed, implemented, and tested architecture demonstrates that the handles (particularly Cynefin for domain categorisation, First Principles for decomposition, and MECE for completeness) guide the LLM toward the same architectural decisions a human engineer reaches. The 4 gaps are all reasonable design choices that a code review would catch — the core architecture (the hard part) was correct.

**Follow-up:** The 4 gaps from this experiment became the hypothesis test case for the Triangle Protocol (Application 5 below).

### Application 5: Triangle Protocol — Solution Space Exploration (ExampleVision Integration)

**Date:** 2026-03-24
**Protocol:** Triangle Protocol (3 diverge agents + 1 synthesis agent)
**Agent handles:**
- TQ (Time+Quality): Cynefin + MECE + First Principles + Pre-mortem
- TC (Time+Cost): Cynefin + MECE + YAGNI + Theory of Constraints
- CQ (Cost+Quality): Cynefin + MECE + Muda + Kent Beck's Four Rules
- Synthesis: Cynefin + MECE + First Principles

**Target:** `testing/examplevision-requirements-only.md` — same 271-line requirements document used in Application 4
**Outputs:**
- `testing/triangle-examplevision-agent-tq.md` — Time+Quality design
- `testing/triangle-examplevision-agent-tc.md` — Time+Cost design
- `testing/triangle-examplevision-agent-cq.md` — Cost+Quality design
- `testing/triangle-examplevision-synthesis.md` — Comparison and synthesis

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

The designs are genuinely different — not anchored variations. TC produced a God-class `APP_ExampleVisionEventPollerBatch` combining all processing; TQ produced well-separated classes with 4 independent scheduled jobs; CQ produced a NULL-timestamp coordination pattern with user-driven Cleared status and the most thorough "Components NOT Built" justification.

**Bonus finding — requirements contradiction:**

The synthesis agent flagged a P0 blocker that no single-agent run had detected: requirement 3 states "Data Entry is the ONLY outbound status change," but TQ and CQ both designed Cleared as an additional outbound status change. TC took the requirement literally. This disagreement surfaced a genuine requirements ambiguity — CQ explicitly flagged it as Unknown Assumption U8 with the note "Confirm with ExampleVision whether Cleared has `is_valid_for_user_transition = true`."

This is the strongest argument for the Triangle Protocol: multi-agent divergence surfaces **requirements ambiguities**, not just design alternatives. A single agent silently picks one interpretation. Three agents may pick different interpretations, and the synthesis agent flags the disagreement.

**Synthesis quality:**

The synthesis agent produced a 380-line structured comparison with all 8 required sections (Executive Summary, Convergence, Divergence, Tradeoff Matrix, Effort Comparison, Hybrid Opportunities, Risk Register, Blind Spots) plus a Next Steps section. Improvements applied after initial synthesis: prioritised decision guide (top 3 decisions), normalised effort estimates, uncertainty ranges on hybrid estimates, priority-ranked blind spots (P0/P1/P2), and suggested next steps.

**Insight:** The Triangle Protocol adds genuine value for architecture decisions where tradeoffs matter. The ~4x token cost is justified when the alternative is discovering silent gaps during implementation. The protocol's strongest finding was not one of the 4 predicted gaps — it was the requirements contradiction, a category of finding that single-agent design generation cannot produce because it requires multiple independent interpretations of the same requirement. The protocol also demonstrated that the Iron Triangle constraint pairs produce genuinely independent designs (not anchored variations) because each pair activates different handle cocktails in separate contexts. See `triangle-protocol.md` for the full protocol specification and methodology.

### Application 6: Triangle Protocol — Solution Space Exploration (Wildfire Endorsement + Cancellation)

**Date:** 2026-03-28
**Protocol:** Triangle Protocol (3 diverge agents + 1 synthesis agent)
**Agent handles:**
- TQ (Time+Quality): Cynefin + MECE + First Principles + Pre-mortem
- TC (Time+Cost): Cynefin + MECE + YAGNI + Theory of Constraints
- CQ (Cost+Quality): Cynefin + MECE + Muda + Kent Beck's Four Rules
- Synthesis: Cynefin + MECE + First Principles

**Target:** Wildfire endorsement re-pricing + cancellation MEP calculation — extending the existing `APP_WildfireApiService` (new-business already implemented) to support endorsement and cancellation endpoints.
**Outputs:**
- `testing/triangle-wildfire-ec-agent-tq.md` — Time+Quality design
- `testing/triangle-wildfire-ec-agent-tc.md` — Time+Cost design
- `testing/triangle-wildfire-ec-agent-cq.md` — Cost+Quality design
- `testing/triangle-wildfire-ec-synthesis.md` — Comparison and synthesis

**Context:** This is the second Triangle Protocol experiment (N=2). Unlike Application 5 (greenfield integration from requirements), this tests the protocol on extending existing infrastructure — the wildfire new-business service, AOP rater V2 endorsement/cancellation, and PKG cancellation hook already exist. The agents must design around established patterns, transaction boundaries, and governor limit constraints.

**Results:**

| Metric | App 5 (ExampleVision, N=1) | App 6 (Wildfire E/C, N=2) |
|--------|-------------------|--------------------------|
| Convergence points | 7 | 7 |
| Divergence points | 6 | 6 |
| Blind spots | 8 (1 P0, 5 P1, 2 P2) | 8 (2 P0, 3 P1, 3 P2) |
| Hybrid options | 4 | 4 |
| Effort spread | 1.9x (55h–105h) | 3.25x (24h–78h) |
| Requirements ambiguity found | 1 (Cleared status) | 1 (date source: Quote vs InsurancePolicy) |

**Structural consistency:** The synthesis produced nearly identical output structure across both experiments — 7/6/8/4 (convergence/divergence/blind spots/hybrids) in both cases. This suggests the protocol produces stable, comparable output across different problem types.

**Key findings:**

**1. Requirements ambiguity detected (again).** CQ sourced inception/expiration dates from `InsurancePolicy.EffectiveDate`/`ExpirationDate` (canonical policy record). TQ/TC sourced from `PKG_PolicyEffectiveDate__c`/`PKG_PolicyExpirationDate__c` on Quote (consistent with existing AOP rater pattern). This is a genuine requirements ambiguity — the wildfire API contract specifies `policy_inception_date` and `policy_expiration_date` without stating which Salesforce field is the source. A single agent would silently pick one; three agents surfaced the disagreement as a P0 blind spot.

**2. P0 architectural blocker: override parameter contract.** TC and CQ both solved the DML-before-callout governor limit by passing wildfire results to the AOP rater via an in-memory override parameter. TQ took a different approach — two sequential LWC server calls. The synthesis flagged that no agent verified whether the override parameter actually exists and propagates correctly. If it doesn't, TC and CQ's entire design collapses and only TQ's approach works. A single-agent design would have silently assumed one approach without flagging the dependency.

**3. Wider effort spread driven by genuine constraint divergence.** TC produced a 6-component, 24-hour design (3 fields, hardcoded constants, no CMDT). TQ produced a 15-component, 78-hour design (6 fields, 3-record CMDT with feature flags, separate payload class, two-call LWC pattern). CQ landed at 10 components, 33 hours (6 fields, 1-record CMDT, dedicated test class). The 3.25x spread (wider than ExampleVision's 1.9x) reflects that this problem has more viable architectural approaches — extending existing code offers more degrees of freedom than greenfield.

**4. Seven high-confidence convergence points.** All three agents independently chose: `InsurancePolicy.Name` as `policy_id`, 2-hop prior premium traversal (same as AOP rater V2), wildfire failure does not block AOP, MEP enforcement is soft/advisory (defer to AOP rater's T138), `APP_WfSeasonalityFactor__c` and `APP_WfMinEarnedPremiumRate__c` as core fields, `PKG_TransactionEffectiveDate__c` for transaction date. These can be adopted with high confidence.

**Agent output comparison:**

| Agent | Components | New Fields | New Classes | CMDT | Effort |
|---|---|---|---|---|---|
| **TC** (Time+Cost) | 6 | 3 | 0 | None | ~24h |
| **CQ** (Cost+Quality) | 10 | 6 | 1 (test) | 1 record | ~33h |
| **TQ** (Time+Quality) | 15 | 6 | 1 (payload) | 3 records | ~78h |

**Insight:** This experiment confirms that the Triangle Protocol's value properties are structural, not incidental. Requirements ambiguity detection via agent disagreement appeared in both experiments (N=1 and N=2) on different problem types (greenfield vs extension). The P0 blind spot (override parameter) is a category of finding specific to extension work — it validates that the protocol adds value beyond greenfield. The protocol is also effective on Complicated-domain problems (not just Complex), surfacing tradeoffs in how to extend established patterns that a single agent would resolve silently.

### Application 7: Triangle Protocol — Cross-Domain Validation (ExampleRater Batch Design)

**Date:** 2026-03-28
**Protocol:** Triangle Protocol (3 diverge agents + 1 synthesis agent)
**Agent handles:** Same as Applications 5 and 6
**Domain:** Azure Functions / Node.js / SharePoint — **non-Salesforce** (first cross-domain test)

**Target:** Design a batch/bulk rating feature for ExampleRater, a serverless Azure Functions API that exposes Excel-based insurance raters as REST services. The system currently supports single-policy rating only; the design extends it to support batch operations (500–50,000 policies per batch).
**Outputs:**
- `testing/triangle-example-rating-batch-agent-tq.md` — Time+Quality design
- `testing/triangle-example-rating-batch-agent-tc.md` — Time+Cost design
- `testing/triangle-example-rating-batch-agent-cq.md` — Cost+Quality design
- `testing/triangle-example-rating-batch-synthesis.md` — Comparison and synthesis
- `testing/example-rating-batch-requirements.md` — Manufactured requirements document

**Context:** This is the third Triangle Protocol experiment (N=3) and the first on a non-Salesforce platform. The purpose is to test cross-domain generalisability — whether the protocol produces genuine divergence and useful findings on Azure/Node.js without Salesforce-specific constraints (no governor limits, no DML-before-callout, no OmniStudio). Requirements were manufactured from the existing codebase context and real business need (insurance portfolio re-rating).

**Results:**

| Metric | App 5 (ExampleVision, SF) | App 6 (Wildfire, SF) | App 7 (Batch, Azure/Node.js) |
|--------|-------------------|--------------------------|------------------------------|
| Convergence points | 7 | 7 | 6 |
| Divergence points | 6 | 6 | 5 |
| Blind spots | 8 (1 P0, 5 P1, 2 P2) | 8 (2 P0, 3 P1, 3 P2) | 9 (3 P0, 3 P1, 3 P2) |
| Hybrid options | 4 | 4 | 4 |
| Effort spread | 1.9x (55h–105h) | 3.25x (24h–78h) | 1.4x (80h–112h) |
| Platform | Salesforce/Apex | Salesforce/Apex | Azure Functions/Node.js |

**Key findings:**

**1. The protocol works cross-domain.** Three genuinely different architectures emerged on Azure/Node.js: TQ used Azure Service Bus fan-out with Blob Storage and Premium Functions Plan (~£125-370/month additional). TC used a self-chaining HTTP Function on Consumption plan with zero new services. CQ used a timer-triggered orchestrator on Consumption plan with per-item retry. These are fundamentally different patterns driven by the Iron Triangle constraint pairing, not by platform-specific constraints.

**2. Cynefin domain disagreement surfaced.** TQ classified worker pool contention as Complex (requiring adaptive infrastructure). TC and CQ classified the entire problem as Complicated (solvable with known patterns). This is the same category of finding as the date source disagreement (N=2) and Cleared status contradiction (N=1) — agents interpreting the problem space differently under different constraints.

**3. P0 blind spots unique to cross-domain.** The synthesis flagged that single-item processing time (p50/p95/p99) is uncharacterised — if p99 exceeds 5 minutes, only TQ's Premium Plan design survives. This is a platform constraint (Azure Functions Consumption plan 10-minute limit) that would not exist on Salesforce. TC also omitted data cleanup entirely — a P0 blind spot caught by comparison with TQ and CQ, both of which addressed TTL.

**4. The output structure is stable across platforms.** 6 convergence, 5 divergence, 9 blind spots, 4 hybrids — within the same range as the Salesforce experiments (7/6/8/4). The protocol produces consistent, comparable output regardless of whether the target is Salesforce/Apex or Azure/Node.js.

**5. Infrastructure cost emerged as a genuine divergence axis.** On Salesforce, all designs use the same infrastructure (the org). On Azure, TQ's design adds ~£125-370/month in new services (Service Bus, Blob Storage, Premium Plan) while TC and CQ add ~£0. This is a category of divergence that only appears on infrastructure-variable platforms — the Iron Triangle constraint pairs naturally separate "throw money at it" (TQ) from "use what you have" (TC/CQ).

**Agent output comparison:**

| Agent | Components | New Azure Services | Functions | Hours | Monthly Cost Addition |
|---|---|---|---|---|---|
| **TC** (Time+Cost) | 6 | 0 | 3 | ~80h | ~£0 |
| **CQ** (Cost+Quality) | 10 | 0 | 6 | ~112h | ~£0 |
| **TQ** (Time+Quality) | 20 | 3 (Service Bus, Blob, Premium Plan) | 8 | ~95h | ~£125-370 |

**Insight:** The Triangle Protocol's value properties transfer across platforms. Requirements ambiguity detection (via Cynefin domain disagreement), architectural blocker identification (p99 processing time as a platform constraint), and genuine divergence from constraint pairing all appeared on Azure/Node.js just as they did on Salesforce/Apex. The protocol is not platform-specific — it is a general-purpose tool for solution space exploration on any technology stack where architecture decisions have genuine tradeoffs.

### Application 8: Two-Pass Code Review — Cross-Domain Validation (example-modelling)

**Date:** 2026-03-28
**Strategy:** Two-pass, fresh sessions (Pass 1: analytical, Pass 2: adversarial)
**Pass 1 handles:** Genba + SOLID + MECE + Pyramid Principle
**Pass 2 handles:** Chaos Engineering + Pre-mortem + Poka-yoke
**Domain:** TypeScript / Node.js CLI tool (~184 source files) — **first non-Salesforce code review**

**Target:** `example-modelling` — a TypeScript CLI that walks Salesforce repos and generates deterministic, AI-consumable models of every component (classes, objects, LWCs, OmniStudio, journeys, architecture views).
**Outputs:**
- `testing/review-example-modelling-pass1.md` — Analytical review
- `testing/review-example-modelling-pass2.md` — Adversarial review

**Context:** This is the first Axis Engineering code review on a non-Salesforce codebase. The purpose is to validate that the handles and two-pass strategy transfer to TypeScript/Node.js — a fundamentally different language, runtime, and error model from Salesforce/Apex.

**Results:**

| Metric | Pass 1 (Analytical) | Pass 2 (Adversarial) |
|--------|--------------------|--------------------|
| Grade | B (solid, minor issues) | C- (happy-path only, fragile) |
| P0 findings | 2 | 3 |
| P1 findings | 5 | 5 |
| P2 findings | 7 | 6 |
| P3 findings | 4 | 6 |
| Strengths noted | 7 | 6 |

**Deduplicated critical findings (P0):**

| # | Finding | Found By | Category |
|---|---------|----------|----------|
| P0-1 | Undeclared variable `graphEdgesLoaded` — compile/runtime error | Both passes | Code defect |
| P0-2 | Command injection via unsanitized `gitUrl` in shell exec | Pass 2 only | Security |
| P0-3 | `logicalNameMap` last-writer-wins — silent wrong dependency resolution | Pass 2 only | Data correctness |
| P0-4 | Division by zero when graph has zero edges | Both passes | Code defect |

**Independent rediscovery:** Both passes independently found P0-1 (undeclared variable) and P0-4 (division by zero) — the same "big findings" reproducibility observed in the Salesforce experiments. Pass 2 uniquely found the security vulnerability (command injection) and the data correctness issue (logicalNameMap) — both adversarial findings that analytical review missed, confirming the value of the two-pass split.

**Handle transfer to TypeScript/Node.js:**

| Handle | Salesforce Effect | TypeScript Effect | Transferred? |
|--------|-------------------|-------------------|-------------|
| **Genba** | Reads actual Apex code, catches `without sharing` issues | Read actual TS source, caught 203 `any` usages and undeclared variable | Yes |
| **SOLID** | SRP violations in Apex classes, DDD boundary issues | Open/Closed violation in metadata routing (3-place changes), SRP in services | Yes |
| **MECE** | Completeness of field coverage, test coverage gaps | Missing test coverage for commands/derived generators, missing metadata types | Yes |
| **Chaos Engineering** | DML-before-callout, governor limits, null injection | Symlink cycles, concurrent CI corruption, XML parse failure → empty models | Yes |
| **Pre-mortem** | "It failed in production because..." | "The model was wrong and the AI made a bad decision based on it" → logicalNameMap | Yes |
| **Poka-yoke** | Validation rules, sharing keyword checks | No guardrail against output dir overlapping source, no input validation on --root | Yes |

**Insight:** The handles and two-pass strategy transfer cleanly to TypeScript/Node.js without modification. The handle names activate the same investigation behaviors regardless of language: Genba still means "read the actual code," SOLID still means "check single responsibility and open/closed," Chaos Engineering still means "inject failures." The findings are platform-appropriate (symlink cycles instead of governor limits, command injection instead of DML-before-callout) but the investigation patterns are identical. This confirms that Axis Engineering handles are language-agnostic — they activate cognitive patterns in the model, not platform-specific knowledge.

### Application 9: Two-Pass Code Review — Cross-Language Validation (pkg-connect-product-mover, Python)

**Date:** 2026-03-28
**Strategy:** Two-pass, fresh sessions (Pass 1: analytical, Pass 2: adversarial)
**Pass 1 handles:** Genba + SOLID + MECE + Pyramid Principle
**Pass 2 handles:** Chaos Engineering + Pre-mortem + Poka-yoke
**Domain:** Python CLI (~4,000 LOC, 16 modules) — **first Axis review on Python and first review on someone else's code**

**Target:** `pkg-connect-product-mover` — a Python CLI for migrating complex Salesforce Product2 data hierarchies between orgs (export to CSV, import with smart upsert, schema comparison, purge). Built by a different developer (Nigel), not the Axis reviewer.
**Outputs:**
- `testing/review-product-mover-pass1.md` — Analytical review
- `testing/review-product-mover-pass2.md` — Adversarial review
- `testing/review-product-mover-combined.md` — Combined deduplicated review

**Context:** Third language (after Salesforce/Apex and TypeScript/Node.js). First time reviewing code the reviewer has no prior context on. Tests whether Axis works as a consulting tool — "review this colleague's tool."

**Results:**

| Metric | Pass 1 (Analytical) | Pass 2 (Adversarial) |
|--------|--------------------|--------------------|
| Grade | B (solid, config gap) | D (fragile, dangerous for production) |
| P0 findings | 2 | 4 |
| P1 findings | 5 | 6 |
| P2 findings | 7 | 5 |
| P3 findings | 4 | 4 |

**Deduplicated: 29 findings (4 P0, 8 P1, 10 P2, 7 P3). 4 independently rediscovered by both passes.**

**Critical findings:**

| # | Finding | Found By | Category |
|---|---------|----------|----------|
| P0-1 | Partial import failure leaves org corrupted — no rollback, delete-then-insert with no transaction boundary | Pass 2 only | Data integrity |
| P0-2 | Upsert continues past partial failures — orphaned data, no failure threshold | Pass 2 only | Data integrity |
| P0-3 | Salesforce access tokens logged to disk in debug mode (dataclass `__repr__`) | Both passes | Security |
| P0-4 | PKG_Binder__c exported but never imported — silent data loss on round-trip | Both passes | Data loss |

**Key observation — adversarial pass is essential for tools that write to production.** The analytical pass found code quality and architecture issues (dead code, exit codes, SOLID violations). The adversarial pass found the data integrity and safety issues that matter most: no rollback on partial failure, no org verification before destructive ops, purge deletes ALL products (not just managed), and SOQL length limits on large datasets. For a tool that writes to production Salesforce orgs, the adversarial findings are the ones that prevent incidents.

**Handle transfer to Python (third language):**

| Handle | Effect on Python | Transferred? |
|--------|-----------------|-------------|
| **Genba** | Read actual source; caught dataclass `__repr__` leaking tokens, dead code with undefined variables | Yes |
| **SOLID** | Found exporter using globals while importer correctly uses dataclass (inconsistent SRP) | Yes |
| **MECE** | Found PKG_Binder__c config asymmetry, missing test coverage for critical paths | Yes |
| **Chaos Engineering** | "Network drops mid-import" → found no rollback/checkpoint; "500+ products" → SOQL length limit | Yes |
| **Pre-mortem** | "Someone ran import against production" → no org verification; "purge deleted other systems' products" → no archive ID filter | Yes |
| **Poka-yoke** | No guardrail against wrong org; dry-run validates nothing; CSV not checksummed | Yes |

**Insight:** The handles and two-pass strategy now work across three languages (Salesforce/Apex, TypeScript/Node.js, Python) and on code written by someone other than the reviewer. The adversarial pass consistently finds the highest-severity issues that the analytical pass misses — confirming the two-pass split is not redundant but complementary. For tools that modify production data, the adversarial pass should be considered mandatory.

### Application 10: Two-Pass Code Review — Premium-Critical System (example-rating, JavaScript/Azure)

**Date:** 2026-03-28
**Strategy:** Two-pass, fresh sessions (Pass 1: analytical, Pass 2: adversarial)
**Pass 1 handles:** Genba + SOLID + MECE + Pyramid Principle
**Pass 2 handles:** Chaos Engineering + Pre-mortem + Poka-yoke
**Domain:** JavaScript / Azure Functions (~57 source files) — premium-critical insurance rating system

**Target:** `example-rating` — a serverless REST API that exposes Excel-based insurance raters as REST services. Pre-warmed worker pools in SharePoint, multi-tenant, Azure AD auth. **Incorrect values mean wrong premiums charged to policyholders.**
**Outputs:**
- `testing/review-example-rating-pass1.md` — Analytical review
- `testing/review-example-rating-pass2.md` — Adversarial review
- `testing/review-example-rating-combined.md` — Combined deduplicated review

**Context:** This is the author's own code (unlike Application 9 which was someone else's). It tests Axis on a premium-critical system where calculation correctness is paramount — the highest-stakes review domain so far.

**Results:**

| Metric | Pass 1 (Analytical) | Pass 2 (Adversarial) |
|--------|--------------------|--------------------|
| Grade | B (clean architecture, race condition) | D (silent wrong premiums, cross-tenant leakage) |
| P0 findings | 3 | 5 |
| P1 findings | 7 | 5 |
| P2 findings | 6 | 5 |
| P3 findings | 3 | 7 |

**Deduplicated: 34 findings (7 P0, 10 P1, 9 P2, 8 P3). 6 independently rediscovered by both passes.**

**Critical findings — the adversarial pass found the premium-critical issues:**

| # | Finding | Found By | Category |
|---|---------|----------|----------|
| P0-1 | Excel error values (#REF!, #VALUE!) silently returned as premium results with HTTP 200 | Pass 2 only | Calculation correctness |
| P0-2 | Recalculation failure swallowed — stale values from previous customer returned | Pass 2 only | Data leakage |
| P0-3 | `persistChanges=true` on Excel sessions — Customer A's inputs persist in worker, contaminate Customer B | Pass 2 only | Cross-tenant contamination |
| P0-4 | Race condition in worker locking (TOCTOU) — two requests can claim same worker | Both passes | Concurrency |
| P0-5 | No tenant isolation on API — any Customer.Access token accesses all tenants | Pass 2 only | Security |
| P0-6 | OData filter injection — user input interpolated into query strings | Both passes | Security |
| P0-7 | Null dereference when entity not found in 3 of 4 table classes | Pass 1 only | Code defect |

**Key observation — widest grade gap yet (B vs D) on the highest-stakes system.** The analytical pass gave a B ("clean architecture, good patterns"). The adversarial pass gave a D ("silent wrong premiums, cross-tenant data leakage"). For a system that calculates insurance premiums, the adversarial findings are the ones that prevent regulatory incidents. P0-1 through P0-3 form a chain: Excel errors returned as premiums + recalculation failure swallowed + persistent sessions contaminating across tenants = a system that can silently charge customers wrong prices based on stale or erroneous data from other tenants.

**The adversarial pass found 4 of 7 P0s that the analytical pass missed entirely.** All four are premium-critical: wrong calculations, stale data, cross-tenant contamination, and no tenant isolation. These are not code quality issues — they are business-critical defects that directly affect policyholders.

**Insight:** This is the strongest evidence yet that the two-pass strategy is not redundant but essential. The B-vs-D grade gap appeared in Application 9 (B vs D on product-mover) and now again here. For any system that modifies production data or calculates financial values, the adversarial pass is mandatory — the analytical pass alone gives a dangerously optimistic assessment.

### Application 11: Two-Pass Review — DevOps/IaC (example-rating Deployment System, Bash/Bicep/CI/CD)

**Date:** 2026-03-28
**Strategy:** Two-pass, fresh sessions (Pass 1: analytical, Pass 2: adversarial)
**Pass 1 handles:** Genba + SOLID + MECE + Pyramid Principle
**Pass 2 handles:** Chaos Engineering + Pre-mortem + Poka-yoke
**Domain:** Bash / Node.js / Bicep / Bitbucket Pipelines — **first Axis review on DevOps/IaC artifacts (not application code)**

**Target:** Complete deployment system for example-rating: 10 bash scripts (~2,100 LOC) for Azure infrastructure provisioning, Azure AD setup, managed identity with Graph API permissions, secret generation, deployment, and cleanup. Plus Node.js build tools and Bitbucket Pipelines CI/CD.
**Outputs:**
- `testing/review-example-rating-deployment-pass1.md` — Analytical review
- `testing/review-example-rating-deployment-pass2.md` — Adversarial review
- `testing/review-example-rating-deployment-combined.md` — Combined deduplicated review

**Context:** This tests whether Axis handles work on infrastructure-as-code and CI/CD pipelines — a fundamentally different artifact type from application code. These scripts handle the most security-sensitive operations: Azure AD registrations, Graph API permissions, client secrets, and production deployments. A bug here is worse than a bug in the application.

**Results:**

| Metric | Pass 1 (Analytical) | Pass 2 (Adversarial) |
|--------|--------------------|--------------------|
| Grade | C+ (modular but credential leaks) | D (no rollback, secrets in logs, excessive permissions) |
| P0 findings | 3 + 3 ANDON flags | 4 |
| P1 findings | 6 | 6 |
| P2 findings | 6 | 6 |
| P3 findings | 4 | 5 |

**Deduplicated: 29 findings (5 P0, 8 P1, 9 P2, 7 P3). 8 independently rediscovered — highest overlap yet.**

**Critical findings — credential exposure dominates:**

| # | Finding | Found By | Category |
|---|---------|----------|----------|
| P0-1 | Client secret echoed to stdout, written to JSON, persisted as downloadable pipeline artifact | Both passes | Credential exposure |
| P0-2 | Storage connection string (with account key) written to disk and echoed to logs | Both passes | Credential exposure |
| P0-3 | `Sites.FullControl.All` Graph API permission — full control of ALL SharePoint sites in tenant | Both passes | Least privilege |
| P0-4 | No rollback on partial failure; `show_spinner` never checks exit codes; orphaned AD apps with active secrets | Both passes | Failure handling |
| P0-5 | GNU `date -d` syntax breaks on macOS and Alpine BusyBox — SAS token generation fails | Both passes | Cross-platform |

**Key observation — handles transfer to DevOps/IaC.** The handle effects on deployment scripts:

| Handle | Effect on Bash/CI/CD | Transferred? |
|--------|---------------------|-------------|
| **Genba** | Read actual bash — caught `SCRIPT_DIR` overwrite, subshell scoping, undefined variables | Yes |
| **SOLID** | SRP per script is good; found build/verify inconsistency (verify expects what build removes) | Yes |
| **MECE** | Found `--quiet` flag not handled in subscript, GUID validation gaps between scripts | Yes |
| **Chaos Engineering** | "Pipeline fails halfway" → orphaned AD apps; "two pipelines run simultaneously" → no concurrency guard | Yes |
| **Pre-mortem** | "Secret was leaked" → found in logs, artifacts, JSON files, process list; "deleted wrong environment" → no subscription verification | Yes |
| **Poka-yoke** | No guardrail against cleanup on wrong subscription; no confirmation before AD app deletion | Yes |

**Insight:** The handles and two-pass strategy extend to DevOps/IaC — a new artifact category beyond application code. The credential exposure findings (P0-1, P0-2) are the DevOps equivalent of the "wrong premium" findings in the example-rating application review — the domain-specific highest-stakes issue. The 8/29 independent rediscovery rate (28%) is higher than application code reviews (~20%), likely because credential exposure is equally obvious to both analytical ("I can see the secret in the code") and adversarial ("where would an attacker find the secret?") lenses. Axis Engineering now covers: code review, design review, design generation (Triangle Protocol), implementation retrospective, and DevOps/IaC review.

### Cross-Application Observations

1. **Handles transfer across artifact types, programming languages, and platforms.** Genba (verify against source) works on code, design docs, and doc chains. MECE (no gaps) works on code coverage and design completeness. Pre-mortem (assume failure) works on code deployment and design readiness. Cynefin + First Principles + MECE work for solution design generation. All handles tested on Salesforce/Apex, TypeScript/Node.js, and Python with consistent results.

2. **The assumption ledger is valuable in every context.** In code review it catches runtime assumptions. In design review it catches field type assumptions. In retrospectives it catches framework behavior assumptions. In design generation it catches platform constraint assumptions. In multi-agent synthesis it catches requirements ambiguities. The forcing function is the same: declare what you assumed, then check.

3. **Design review needs different handle combinations than code review.** Code review benefits from Fowler + SOLID (pattern recognition). Design review benefits from MECE + First Principles (completeness + justification). Design generation benefits from Cynefin + First Principles + MECE + Pre-mortem (domain sizing + decomposition + completeness + failure anticipation). Solution space exploration benefits from the Triangle Protocol (3 agents with different constraint pairs + synthesis). Both benefit from Genba (verify) and Pre-mortem (assume failure).

4. **The Genba gap is consistent.** In every application, the most impactful finding was something that could only be caught by reading the actual artifact (field metadata, framework source code, existing implementation) rather than trusting documentation or abstractions. Genba is the single most valuable handle across all contexts.

5. **Design generation is the ultimate completeness test for MECE.** When generating (not reviewing), MECE forces the agent to ask "what's missing from this design?" at every level — objects, fields, classes, execution flow, scheduling, error handling. The 4 gaps in the ExampleVision design are all things MECE *could* have caught with more exhaustive system boundary analysis (scheduler separation, date sync direction, output processing isolation).

6. **Multi-agent divergence surfaces requirements ambiguities that single-agent approaches cannot.** All three Triangle Protocol experiments (Applications 5, 6, and 7) independently surfaced ambiguities through agent disagreement. Application 5: Cleared status contradiction. Application 6: date source disagreement (Quote vs InsurancePolicy). Application 7: Cynefin domain disagreement (Complex vs Complicated). This is a confirmed structural property of the protocol across platforms — not platform-specific. It requires independent parallel generation under different constraints; no single-agent strategy can produce it.

7. **The Iron Triangle produces genuine divergence, not anchored variations.** Application 5: 5-10 classes, monolith vs separated batches. Application 6: 6-15 components, two LWC calls vs in-memory override. Application 7: Service Bus fan-out vs self-chaining HTTP vs timer-polling — fundamentally different orchestration patterns on Azure. Context isolation and different handle cocktails prevent the anchoring that plagues "give me 3 options" in a single context, regardless of platform.

8. **Convergence across independent agents is a strong correctness signal.** All three experiments produced 6-7 convergence points. These are high-confidence decisions the team can adopt without deliberation. The convergence signal works on both Salesforce (governor limits, PKG patterns) and Azure (Table Storage, worker pools).

9. **The Triangle Protocol produces structurally consistent output across platforms.** Three experiments across two platforms (Salesforce/Apex and Azure/Node.js) produced 6-7 convergence, 5-6 divergence, 8-9 blind spots, and 4 hybrids. This consistency confirms the protocol is a calibrated tool, not a one-off exercise — and that its value is not tied to Salesforce-specific constraints.

10. **The protocol surfaces architectural blockers that single-agent design cannot.** Application 6: override parameter contract unverified. Application 7: single-item processing time uncharacterised (if p99 > 5 min, only TQ survives). These are findings that emerge only when agents take different architectural paths and the synthesis compares them.

11. **Infrastructure cost is a natural divergence axis on variable-cost platforms.** On Salesforce (fixed infrastructure), all designs use the same org. On Azure (Application 7), TQ added ~£125-370/month in new services while TC/CQ added ~£0. The Iron Triangle constraint pairs naturally separate "throw money at it" from "use what you have" — a category of divergence that only appears when the platform offers infrastructure choices.

### Application 8: Source Code Audit (ExampleCo Modelling CLI)

**Date:** 2026-03-28
**Handles:** 
- Pass 1: Seven Factors + Genba + SOLID + Pre-mortem
- Pass 2: Genba + Chaos Engineering + Poka-yoke
**Target:** `temp-projects/example-modelling/src`
**Output:** `testing/review-example-modelling-cascade-combined.md`

**Results:**

| Metric | Value |
|--------|-------|
| Total findings | 9 (1 Critical, 3 High, 4 Medium, 1 Low) |
| Assumption ledger | 4 items (3 verified, 1 unknown) |

**Key Findings:**
- **Critical (Pass 2):** Silent exception swallowing. Empty `catch` blocks in `registry.ts` and `parser/index.ts` mask true errors like file system permission failures, causing components to silently drop from the output graph rather than failing the build. (Chaos Engineering / Poka-yoke)
- **High (Pass 1):** `Orchestrator` God Class. Violates OCP and SRP by handling project config, Git resolution, graph orchestration, and file I/O within a massive `build()` method. (SOLID)
- **High (Pass 2):** Unbounded concurrency. `buildSourceGraph` uses a hardcoded `CONCURRENCY = 50` while doing synchronous XML parsing into memory, posing a severe risk of OOM on large XML layout files. (Pre-mortem / Chaos Engineering)
- **Medium (Pass 1):** Global state for tracking sessions (`tracker.ts`). Prevents the CLI from safely running as a long-lived concurrent process (e.g. IDE language server).

**Insight:** This run demonstrated the classic Pass 1 vs Pass 2 dichotomy perfectly. Pass 1 (SOLID / Pre-mortem) surfaced deep structural and architectural concerns. Pass 2 (Chaos Engineering / Poka-yoke) immediately pivoted to runtime failure scenarios (silent empty catch blocks, OOM concurrency limits) that the architectural pass completely ignored.

### Application 8: Agent Comparison (Cascade vs Claude Code)

**Date:** 2026-03-28
**Target:** `temp-projects/example-modelling/src`
**Strategy:** Two-pass Axis Review (Pass 1: SOLID/Genba/Pre-mortem, Pass 2: Chaos/Poka-yoke)
**Models:** Claude 3.7 Sonnet (Claude Code) vs Gemini 3.1 Pro High Thinking (Cascade)

**Context:** Both Cascade and Claude Code independently reviewed the same repository using the exact same Axis handles. This tests whether Axis Engineering produces consistent behavioral shifts across different AI agent architectures.

**Results:**

| Metric | Claude Code | Cascade |
|--------|-------------|---------|
| Total Findings | 31 | 9 |
| Critical / P0 | 4 | 1 |
| High / P1 | 8 | 3 |

**Key Overlaps (Independent Rediscovery):**
1. **Empty Catch Blocks (Resilience):** Both agents flagged silent exception swallowing in `registry.ts` and `parser/index.ts` as a critical operational risk.
2. **Parser Routing (Architecture):** Both agents flagged the hardcoded switch statement for metadata types in `parser/index.ts` as a direct violation of the Open/Closed Principle.

**Agent-Specific Discoveries:**
- **Claude Code uniquely found:** Command injection via unsanitized `gitUrl` (`gitService.ts`), `logicalNameMap` collision bugs, and quantified exact occurrences of bad practices (e.g., 203 `any` usages). It performed a much broader, SAST-like repository sweep.
- **Cascade uniquely found:** Unbounded concurrency OOM risk (`CONCURRENCY = 50` during massive synchronous XML parsing) and Global Singleton state risks in `tracker.ts`. Cascade performed a more localized, depth-first evaluation of the primary execution hot-paths.

**Insight:** 
Axis Engineering is **agent-agnostic**. Both agents exhibited the exact same cognitive separation between passes—Pass 1 focused purely on structural SOLID violations and architectural boundaries, while Pass 2 immediately pivoted to runtime failures (swallowed exceptions, concurrency limits, injections). The difference in finding volume (31 vs 9) reflects the agents' distinct codebase exploration strategies (breadth-first exhaustive sweeping vs depth-first hot-path analysis), but the *lens* applied to the code they read was consistently and successfully shaped by the behavior handles.

### Application 9: Agent Comparison on Design Generation (Cascade vs Claude Code)

**Date:** 2026-03-28
**Target:** `testing/examplevision-requirements-only.md`
**Protocol:** Triangle Protocol (3 independent agents + synthesis)

**Context:** Cascade ran the Triangle Protocol on the ExampleVision integration requirements. The goal was to see if Cascade (Gemini 3.1 Pro High Thinking) produces similar structured divergence and convergence compared to Claude Code (Claude 3.7 Sonnet) when constrained by the Iron Triangle (Time, Cost, Quality).

**Results:**

| Metric | Claude Code (Original) | Cascade |
|--------|------------------------|---------|
| Convergence Points | 7 | 4 |
| Divergence Axes | 5 | 3 |
| Blind Spots / Ambiguities | 8 | 3 |

**Key Overlaps:**
1. **The Monolith vs Separated Architecture:** Both Cascade's TC agent and Claude Code's TC agent converged on the exact same "lowest cost/time" solution: a Monolithic single Batch class (`APP_ExampleVisionLifecycleEngineBatch`) running on the `Case` object with no new custom objects.
2. **The DML-Before-Callout Constraint:** Both models correctly identified the fundamental platform constraint as the driving force behind the design, forcing batching and Queueables/Platform Events to separate DML from HTTP requests.
3. **Dedicated Domain Objects:** Both models' Quality-focused agents (TQ and CQ) independently decided to create a dedicated `APP_ExampleVision_Submission__c` custom object rather than polluting the `Case` UI object, directly contradicting their respective TC agents.

**Cascade's Unique Divergence Path (Event Polling vs Direct Polling):**
- Cascade's TC agent explicitly decided to bypass the `/submission-events` endpoint completely, opting to poll individual `Case` records using `GET /submission?exampleid={id}` to save on cursor management infrastructure.
- Cascade's TQ and CQ agents recognized the API rate limits and forced the usage of the `/submission-events` cursor stream.
- *Insight:* This was a brilliant, genuine architectural divergence driven by the constraint. TC chose API inefficiency to save build time, while TQ/CQ chose architectural efficiency at the cost of building cursor state management.

**Cascade's Unique Blind Spot (The Cursor Storage Problem):**
- Cascade's synthesis perfectly captured a classic Salesforce platform ambiguity: how to store a high-frequency polling cursor. TQ used a Custom Setting, TC tried a Custom Label before realizing it can't be updated via DML, and CQ stored it on the latest data record to avoid Custom Setting row locks.

**Conclusion:** 
The Triangle Protocol works seamlessly on Cascade (Gemini 3.1 Pro High Thinking). The handles forced the LLM to adopt genuinely distinct architectural postures. The TC constraint produced a hyper-pragmatic, monolithic, API-inefficient design, while the CQ constraint produced a textbook Domain-Driven Design (DDD) event-driven architecture. The synthesized outputs were structurally identical to Claude Code's, confirming the protocol is a calibrated tool, not a model-specific trick. Additionally, running these multi-agent protocols via Cascade (using Gemini 3.1 Pro High Thinking) proved significantly faster and highly cost-effective compared to executing the equivalent workflow through Claude Code.
### Application 10: Axis Review (ExampleRater) — Cascade (GPT-5.1-Codex Max High) vs Claude Code

**Date:** 2026-03-28
**Target:** `temp-projects/example-rating`
**Method:** Two-pass Axis Review (Pass 1 analytical, Pass 2 adversarial)
**Model:** GPT-5.1-Codex Max High (Cascade) — ran noticeably faster and cheaper than Claude Code’s run
**Outputs:** `testing/review-example-rating-cascade-pass1.md`, `testing/review-example-rating-cascade-pass2.md`, `testing/review-example-rating-cascade-combined.md`

| Metric | Claude Code | Cascade |
|--------|-------------|---------|
| P0 count | 7 | 2 |
| P1 count | 10 | 3 |
| P2+P3 count | 17 | 5 |

**Key Overlaps (independent rediscovery):**
- Excel-driven pricing can return wrong/stale premiums when recalculation or worksheet checks fail (batch read/write + recalc gap).
- Worker pool replenishment via `setImmediate` is risky; errors are swallowed, leading to depleted/undersized pools.
- Excessive logging of inputs/outputs risks PII leakage.

**Where Claude Found More:**
- Multi-tenant security: OData injection, missing tenant ownership checks, `persistChanges=true` on Excel sessions, and API auth gaps (customerId not enforced).
- Concurrency: TOCTOU worker locking using custom version field, optimistic locking gaps, and transaction no-ops.
- Surface hygiene: health endpoint leakage, Content-Disposition injection, build-time deps in prod, malformed OData on empty filters.

**Where Cascade Added/Made Clearer:**
- Emphasized silent propagation of null/error values as premiums when batch read/write/recalc fails (log-and-continue design).
- Highlighted pool depletion visibility gap and need for telemetry/alerts when async replenishment fails.
- Noted performance/test flakiness from hardcoded sleeps and full payload logging, suggesting correlation IDs and tighter auth checks.

**Synthesis:** Claude’s broader SAST-style sweep surfaced more security and concurrency defects; Cascade’s review focused on runtime failure modes in the Excel pricing hot path. Both agree pricing integrity hinges on treating any Excel or worksheet failure as a hard error and tightening worker lifecycle/telemetry. GPT-5.1-Codex Max High delivered results faster/cheaper while maintaining the Axis handle behaviors.
### Application 11: Batch Rating Design (ExampleRater) — Cascade (GPT-5.1-Codex Max High) vs Claude Code

**Date:** 2026-03-28  
**Target:** `testing/example-rating-batch-requirements.md` / `temp-projects/example-rating`  
**Method:** Triangle Protocol (TQ, TC, CQ + synthesis)
**Cascade outputs:** `testing/triangle-example-rating-batch-cascade-tq.md`, `...-tc.md`, `...-cq.md`, `...-synthesis.md`  
**Claude outputs (kept untouched):** `testing/triangle-example-rating-batch-agent-tq.md`, `...-tc.md`, `...-cq.md`, `...-synthesis.md`

| Dimension | Claude Code | Cascade (GPT-5.1-Codex Max High) |
|-----------|-------------|-----------------------------------|
| Infra posture | TQ: Service Bus + Blob + Premium; TC: self-chaining HTTP; CQ: timer/Table-only | TQ: Table+Queue+Timer-only; TC: Consumption timer/queue; CQ: Table+Queue+Timer with audit
| Item retry / poison | TQ yes (SB DLQ), CQ yes, TC none | TQ: reuse backoff; CQ: retries + poison handling; TC: simple, no retries
| Result storage | TQ: Append Blob; TC/CQ: Table Storage | TQ/CQ: Table/queue, optional blob export; TC: Table-only
| Interactive protection | TQ: heuristic delay; CQ: reserved concurrency; TC: none | TQ: respects pool cap; CQ: reserved; TC: none
| Cancellation | Flag/session per design; some stall risk in TC | Flag on BatchJob; queue respect; in-flight finish
| Throughput posture | TQ aims higher via Premium; TC/TQ may stall if chain breaks | TQ/CQ loop within tick while workers free; TC 30s cadence, cheap

**Key overlaps (independent rediscovery):**
- Reuse existing `calculateRisk`; batch is orchestration only.
- Two tables (`BatchJob`, `BatchItem`), queue messages `{batchId, itemId}`; polling status + cancel endpoint.
- Hard cap on batch size (50k) and shared output schema per batch.

**Where Claude went further:**
- Service Bus/Append Blob design with Premium plan for high throughput (TQ).  
- Explicit stall detection for self-chaining gaps (TC) and detailed cleanup timer (CQ).  
- Rich test plan and config matrix in CQ (12 tests, config defaults).

**Where Cascade added/clarified:**
- Emphasized treating worksheet/recalc failures as hard failures (no 200 with null/error strings).  
- Simplified infra: all three Cascade agents stay on Table+Queue+Timer, no new Azure services.  
- Recommended hybrid: TC cost baseline + CQ guardrails + TQ faster loop per tick.

**Net:** Claude explored a higher-cost, higher-throughput path (Service Bus + Premium) and a riskier self-chaining TC. Cascade prioritized minimal dependencies with guardrails on correctness (hard-fail on Excel errors) and simpler orchestration. Both agree the core is chunked queue-driven processing over existing workers, with polling status and cancellation flags.

---

## Standardized Scoring Rubric (Introduced v2.0)

Starting from future experiments, all reviews and design tasks should append the following rubric to ensure data-driven model comparison and tracking over time.

### Review Rubric & Metrics
- **P0 / P1 count:** [Number of critical and high findings]
- **Rediscovery %:** [Overlap with previous/baseline runs]
- **Model used:** [e.g., Claude 3.7 Sonnet, GPT-5.1-Codex Max High, Gemini 3.1 Pro High Thinking]
- **Estimated Elapsed Time:** [e.g., 45 seconds, 3 minutes]
- **Estimated Cost/Tokens:** [e.g., ~$0.10, ~120k tokens]

### Application 12: Two-Pass Review (PKG Connect) — Cascade (GPT-5.1-Codex Max High)
**Date:** 2026-03-28  
**Target:** `temp-projects/pkg-connect/salesforce/src/main/default/classes/` (sampled 5 classes)  
**Method:** Two-pass Axis Review (Pass 1 analytical, Pass 2 adversarial) using the **v2 Two-Pass Checklist** and **Scoring Rubric**  
**Outputs:** `testing/review-pkg-connect-measured-pass1.md`, `testing/review-pkg-connect-measured-pass2.md`, `testing/review-pkg-connect-measured-combined.md`

#### Results vs v1 Methodology
This review strictly adhered to the newly implemented v2 checklist and evidence contract.
1. **Zero Overlap:** Pass 1 and Pass 2 yielded completely orthogonal findings. Pass 1 caught LWC mapping and type-casting issues. Pass 2 caught concurrency lock races and rollback exception masking.
2. **Zero Hallucination:** Every single finding cited exact `file:line` locations and extracted the exact snippet causing the issue, fulfilling the new Evidence requirement.
3. **Formalized Output:** The scoring rubric correctly quantified the effort vs impact.

#### Review Rubric & Metrics
- **P0 / P1 count:** 5 (2 P0, 3 P1)
- **Rediscovery %:** N/A (Baseline run on this subset)
- **Model used:** GPT-5.1-Codex Max High (Cascade)
- **Estimated Elapsed Time:** ~3 minutes
- **Estimated Cost/Tokens:** ~$0.15, ~120k tokens

### Application 14: Triangle Protocol Re-Run (Wildfire EC) — Cascade (Gemini 3.1 Pro High Thinking)
**Date:** 2026-03-28  
**Target:** Wildfire Endorsement & Cancellation Integration (re-run of Application 6)  
**Method:** Triangle Protocol (TQ, TC, CQ + synthesis) using the **v2 Triangle Checklist**  
**Outputs:** `testing/triangle-wildfire-ec-cascade-tq.md`, `...-tc.md`, `...-cq.md`, `...-synthesis.md`

#### Results vs v1 Methodology (Claude Code)
This re-run aimed to measure if the v2 improvements (explicit checklists, assumption ledgers, scoring rubrics) forced tighter, more measurable design outputs from Gemini 3.1 Pro High Thinking compared to the original Claude Code run.

| Dimension | Claude Code (v1) | Cascade (v2 - Gemini) |
|-----------|------------------|-----------------------|
| **Divergence Clarity** | Good, but architectural differences were somewhat blurred in the prose. | Exceptional. TQ (Method extension), TC (If-statement injection), CQ (Interface/Factory refactor) were starkly different code topologies. |
| **Data Model Approach** | Incremental field additions across the board. | Highly opinionated. TQ used Formula fields for data integrity (Poka-yoke). TC used zero fields (YAGNI). CQ used strictly memory-mapped Domain Objects (Muda elimination). |
| **Blind Spots Caught** | Sequencing and testing overhead. | Transaction isolation (what if Wildfire succeeds but AOP fails?) and missing Parent Policy edge cases. |

**Conclusion:** The v2 checklist forced the agents to explicitly justify *why* they were sacrificing cost or time. Because Gemini had to adhere to the rigid contract, it stopped hallucinating filler text and focused purely on the architectural topology (Interface vs Extension vs If-Statement).

#### Review Rubric & Metrics
- **Model used:** Gemini 3.1 Pro High Thinking (Cascade)
- **Estimated Elapsed Time:** ~3 minutes (Total across TQ, TC, CQ, Synthesis)
- **Estimated Cost/Tokens:** ~$0.15, ~110k tokens

### Application 15: Triangle Protocol (Deployment CI/CD) — ExampleDeploy (Redacted)
**Date:** 2026-03-29  
**Target:** `temp-projects/example-deployment` (redacted deployment automation repository)  
**Method:** Triangle Protocol (TQ, TC, CQ + synthesis) using v2 contracts, assumptions ledger, and rubric output  
**Outputs:** `testing/triangle-exampledeploy-agent-tq.md`, `testing/triangle-exampledeploy-agent-tc.md`, `testing/triangle-exampledeploy-agent-cq.md`, `testing/triangle-exampledeploy-synthesis.md`

#### Results

**Convergences:**
1. Keep the existing script-based deployment backbone; avoid a full rewrite.
2. Preserve hash-based rollback model, but tighten execution guarantees.
3. Treat partial-failure recovery and release-state consistency as primary risks.
4. Keep module-driven deployment control (`pipeline-config*` pattern).

**Divergences:**
1. **Topology:** TQ favored parallelized modules with canary checks; TC favored sequential low-change execution; CQ favored a deterministic wrapper orchestrator.
2. **Validation depth:** TC minimal; TQ targeted fast-fail + canary; CQ staged validation with stronger mutation preconditions.
3. **Observability:** TC minimal telemetry; TQ moderate uplift; CQ rich per-module artifacts for deterministic triage.

**Blind spots surfaced by synthesis:**
- Postdeploy/reactivation idempotency contract not formalized.
- Rollback atomicity gap between metadata pointer updates and deployment completion.
- No explicit emergency-lane policy for urgent production fixes.
- Shared API/limit contention model under parallel+retry load is under-specified.

#### Meaning

This run showed the protocol's practical value on CI/CD architecture decisions: it did not just produce three styles of prose — it produced three materially different operating models and forced the trade-offs into explicit choices. The best outcome was a hybrid: **TC baseline** (low implementation cost) + **TQ canary checks** (early defect capture) + **CQ idempotency/rollback artifacts** (state safety).

#### Review Rubric & Metrics
- **P0 / P1 count:** 1 P0, 4 P1 (deduplicated synthesis)
- **Rediscovery %:** N/A (first run for this scenario)
- **Model used:** Manual Triangle Protocol run (repo-grounded)
- **Estimated Elapsed Time:** ~40 minutes total (3 agents + synthesis)
- **Estimated Cost/Tokens:** N/A
