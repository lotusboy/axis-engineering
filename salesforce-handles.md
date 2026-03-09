# Axis Engineering for Salesforce

> What each handle finds — and what those findings look like — on the Salesforce platform.

Each handle activates specific checks AND implies a natural finding format. You don't need to think about output structure separately — the handles carry their own shape. Pick 2-3 handles, point them at your target files, and the output quality follows.

This is a companion to the [vocabulary reference](vocabulary-quick-ref.md) and [main methodology](README.md).

---

## Genba — Go to the source

**Why it's the #1 handle on Salesforce:** So much behavior is invisible — sharing rules, OWD, field-level security, trigger order, CMDT values. Code that looks correct in isolation can be wrong because of metadata you didn't read.

### What Genba checks on Salesforce

| Artifact | Read the actual... | Because... |
|----------|-------------------|------------|
| Class declaration | `with sharing` / `without sharing` / omitted | Omitted ≠ `with sharing`. Inherited sharing depends on the caller — changes silently between contexts |
| SOQL query | `WITH SECURITY_ENFORCED`, `WITH USER_MODE`, `stripInaccessible()` | `@AuraEnabled` runs in user context but SOQL defaults to system mode. Invisible gap until a restricted profile hits it |
| HttpRequest | Named Credential vs hardcoded URL vs Custom Setting | Hardcoded endpoints bypass credential rotation and IP allowlisting |
| Flow XML | DML/SOQL element count inside Loop elements | The flow canvas hides governor risk |
| CMDT records | Actual field values in the metadata files | CMDT often differs between sandboxes and production |
| Field metadata | `.field-meta.xml` — lookup vs master-detail, delete behavior, required | Master-detail cascade deletes are invisible in Apex |
| Test classes | `@TestSetup` vs `seeAllData=true` | `seeAllData=true` creates org-dependent tests |

### What a Genba finding looks like

Each finding proves it was read, not assumed:

> **[G-1] Missing FLS enforcement on @AuraEnabled query**
>
> `PolicyController.cls:47` — `SELECT Id, Name, Premium__c FROM Policy__c WHERE Account__c = :accountId`
>
> No `WITH SECURITY_ENFORCED`, no `stripInaccessible()`. This method is `@AuraEnabled(cacheable=true)` (line 45), so it runs in user context but queries in system mode. A user without read access to `Premium__c` will see premium values they shouldn't.
>
> Class sharing: `with sharing` (line 1) — record access is enforced, but field access is not.
>
> *Assumption: OWD on Policy__c is Private.* **[Unknown — verify in target org]**

The shape: **artifact → verbatim code → what's wrong → why it matters → assumption status.**

### Prompt fragment

```
Genba: Read every class declaration for its sharing keyword. Read every SOQL
query for its security enforcement. Read every HttpRequest for its endpoint
source. Don't assume — cite file:line for each. If you can't verify something
from the source, mark it as an Unknown assumption.
```

---

## Chaos Engineering — Inject failures

**Why it's the highest-value adversarial handle on Salesforce:** Governor limits create hard failure boundaries. Code that works with 10 records throws an unrecoverable exception at 201. There is no graceful degradation — only hard stops.

### Salesforce boundary scenarios

| Inject this | What breaks | Platform failure mode |
|-------------|------------|----------------------|
| 201 records through trigger | SOQL/DML inside loops | `System.LimitException` — no catch block can handle it |
| Null on non-required fields | Unguarded field access | `NullPointerException`, or worse: null `Decimal` in arithmetic silently produces wrong results |
| Double-click (500ms apart) | Missing idempotency | Two `@AuraEnabled` calls create duplicate records |
| DML then callout | Transaction ordering | `System.CalloutException: You have uncommitted work pending` — hard platform constraint |
| Empty query result + `.get(0)` | Unguarded list access | `List index out of bounds: 0` — the most common Apex runtime error |
| Batch fails at iteration 3/12 | Recovery path | `Database.Stateful` loses accumulated state. Non-idempotent batches create duplicates on re-run |
| Mixed DML (User + Account) | Setup/non-setup in same txn | `MIXED_DML_OPERATION` — requires `@future` separation |
| API returns 200 + empty body | Happy-path-only deserialization | `JSONException` on unexpected response shape |

### What a Chaos Engineering finding looks like

Each finding traces: **scenario → code path → outcome.**

> **[CE-1] 201-record Data Loader import causes governor breach in trigger**
>
> Scenario: Data Loader inserts 201 Account records in a single batch.
>
> Path: `AccountTrigger.trigger:3` fires `AccountTriggerHandler.afterInsert()` → `AccountTriggerHandler.cls:28` enters `for (Account acc : Trigger.new)` → line 31 executes `[SELECT Id FROM Contact WHERE AccountId = :acc.Id]` **inside the loop**.
>
> Outcome: 201 SOQL queries. Governor limit is 100. `System.LimitException` at record 101 — entire transaction rolls back, no records inserted. **No catch block can prevent this** — `LimitException` is uncatchable.
>
> Fix: Collect AccountIds into a Set, query once outside the loop, build a Map.

The shape: **scenario → entry point → loop boundary → violation line → governor math → impact.**

### Prompt fragment

```
Chaos Engineering: For each code path, inject:
- 201 records through the trigger
- Null on every non-required field used in the code
- Double invocation within 500ms
- Empty query result where .get(0) or [0] is used
- DML before callout (trace the full transaction to confirm ordering)
For each failure found: state the scenario, trace the path with file:line
references, show the governor math, and state the outcome.
```

---

## Poka-yoke — Make the wrong thing impossible

**Why it's critical on Salesforce:** The platform offers declarative guards (validation rules, required fields, restricted picklists, duplicate rules) that cover ALL entry points — UI, API, Flow, Data Loader, Apex. Guards that only exist in code are bypassable.

### Guard comparison

| Business rule | Code-only guard (bypassable) | Platform guard (covers all entry points) |
|--------------|----------------------------|----------------------------------------|
| Field is required | Apex `if (field == null) throw` | Field-level `required` attribute |
| Picklist values are controlled | Apex `if (!validValues.contains(val))` | Restricted picklist |
| No duplicate records | Apex query + check before insert | Duplicate Rule + Matching Rule |
| Can't delete active records | `before delete` trigger check | Validation rule on delete |
| Status transitions are valid | Apex `if (oldStatus != 'Draft')` | Validation rule with `PRIORVALUE()` |
| Record type determines behavior | Apex `if (rt.DeveloperName == 'X')` | Record type + page layout + validation rule |

### What a Poka-yoke finding looks like

Each finding contrasts what exists vs what's possible:

> **[PY-1] Required field enforced only in Apex — bypassable via API**
>
> `QuoteTriggerHandler.cls:55` — `if (quote.Effective_Date__c == null) { quote.addError('Effective Date is required'); }`
>
> This guard only fires on trigger context. A Data Loader import, Flow create, or direct API insert bypasses the trigger handler's validation path if the trigger is inactive or if the check is in `before insert` but the record enters via `after insert` from a different automation.
>
> Platform alternative: Set `required` on `Quote__c.Effective_Date__c.field-meta.xml` — enforced on every entry point including API, with no code to maintain.
>
> Guard strength: **Code-only** → recommend **Platform-enforced**.

The shape: **what the guard does → where it lives → what bypasses it → platform alternative → strength rating.**

### Prompt fragment

```
Poka-yoke: For each business rule enforced in Apex, check whether the platform
provides a declarative equivalent that covers all entry points (UI, API, Flow,
Data Loader). Flag rules that exist only in code as "bypassable." For each,
state what bypasses it and what the platform alternative is.
```

---

## Pre-mortem — It already failed in production

**Why it matters on Salesforce:** Salesforce failures are configuration-dependent. Code that passes in a full-copy sandbox can fail in production because of different OWD, missing CMDT records, governor limits at real data volumes, or profile differences.

### Salesforce failure scenarios to prompt with

| Scenario seed | What it surfaces |
|--------------|-----------------|
| "The nightly batch processed 50,000 records and failed at 11 PM" | Untested volume paths, scope size too large, missing error handling in `execute()` |
| "A Community user saw internal data they shouldn't have" | `without sharing` callable from `@AuraEnabled`, missing FLS checks |
| "Deployment succeeded but the feature doesn't work" | Missing CMDT records, permission set assignments, Named Credential not in package |
| "Users report wrong calculated values on 200 records" | Race conditions, stale field values, formula recalculation timing |
| "The external API has been returning 500s for 2 hours — nobody noticed" | No monitoring, no retry, no circuit breaker, error swallowed in catch block |

### What a Pre-mortem finding looks like

Each finding tells a story: **what failed → why → what the user experienced → what was missing.**

> **[PM-1] Deployment succeeds, feature silently broken — missing CMDT records**
>
> Scenario: The team deploys the Rater integration to production. Deployment succeeds. Users click "Rate" and nothing happens. No error message — just a spinner that never resolves.
>
> Why: `RaterService.cls:12` reads `Rater_Config__mdt.getInstance('Default')` to get the API endpoint. This CMDT record exists in the dev sandbox but is not included in the deployment package. `getInstance()` returns null. Line 15, `config.Endpoint__c`, throws `NullPointerException`. The LWC catch block at `raterComponent.js:88` shows a generic "An error occurred" toast.
>
> Missing: CMDT record `Rater_Config__mdt.Default` in the deployment package. No validation in `RaterService` that the config record exists before using it.
>
> User impact: Feature is completely non-functional in production. No actionable error message. Support ticket required to diagnose.

The shape: **scenario narrative → root cause with code path → what was missing → user impact.**

### Prompt fragment

```
Pre-mortem: Assume this feature is live in production and has failed. Write
three failure scenarios:
1. A governor/volume failure (batch or trigger at production data volumes)
2. A security/access failure (wrong user sees or modifies wrong data)
3. A deployment/config failure (code deployed correctly but feature broken)
For each: tell the story of what happened, trace the code path to root cause,
state what was missing, and describe the user experience.
```

---

## STRIDE — Threat modeling for Salesforce

Each STRIDE category maps to a specific Salesforce attack surface.

| Category | Salesforce meaning | What to check |
|----------|-------------------|---------------|
| **Spoofing** | Sharing model bypass | `without sharing` classes callable from user context via `@AuraEnabled`, `@RestResource`, `@RemoteAction` |
| **Tampering** | CRUD/FLS bypass | `@AuraEnabled` methods that accept SObject params and pass directly to DML without `stripInaccessible()` |
| **Repudiation** | Missing audit trail | Destructive ops (delete, status change, financial calc) without custom audit logging |
| **Info Disclosure** | Over-fetching / debug log exposure | SOQL returning more fields than needed. `System.debug()` with PII or tokens in production |
| **Denial of Service** | Governor abuse via user input | User-controlled input affects SOQL scope — unbounded date range, no LIMIT clause |
| **Elevation** | Community → internal escalation | Experience Cloud users reaching internal `@AuraEnabled` controllers. Check `lightning__CommunityPage` in `.js-meta.xml` targets |

### What a STRIDE finding looks like

Each finding maps to a category with exploitation path:

> **[S-3] Elevation of Privilege — Community user can access internal controller**
>
> `policySearch.js-meta.xml:8` — targets include `lightning__RecordPage` and `lightningCommunity__Page`.
>
> `PolicySearchController.cls:1` — declared `without sharing`.
> `PolicySearchController.cls:15` — `@AuraEnabled` method `searchPolicies(String searchTerm)` executes `[SELECT Id, Name, Premium__c, Underwriter_Notes__c FROM Policy__c WHERE Name LIKE :searchPattern]`
>
> No FLS enforcement. No SOQL LIMIT. A Community user can invoke this method, search across all Policy records (bypasses sharing via `without sharing`), and see `Underwriter_Notes__c` (internal-only field) and `Premium__c` (commercially sensitive).
>
> Combines: **Spoofing** (sharing bypass) + **Info Disclosure** (over-fetching) + **Elevation** (Community access to internal data).

The shape: **STRIDE category → entry point → code path → what's exposed → combined threat assessment.**

### Prompt fragment

```
STRIDE: For each @AuraEnabled method:
- Spoofing: trace sharing keyword from caller to implementation
- Tampering: does it accept SObject params that go directly to DML?
- Info Disclosure: does the SOQL return fields the consumer doesn't need?
  Does System.debug() log PII or credentials?
- Elevation: check .js-meta.xml — can Community users reach this?
For each finding, state the STRIDE category, the exploitation path, and
whether multiple categories compound.
```

---

## SOLID — Applied to Apex

| Principle | Salesforce application | Common violation |
|-----------|----------------------|------------------|
| **S** — Single Responsibility | Trigger handler ≠ service ≠ selector ≠ callout class | God-class `@AuraEnabled` method: query + logic + callout + DML in 200 lines |
| **O** — Open/Closed | Record type behavior via CMDT / Strategy pattern | Hardcoded `if/else` on `RecordType.DeveloperName` — code change per new record type |
| **L** — Liskov Substitution | Virtual/abstract Apex class subtypes | Subclass changes `with sharing` → `without sharing`, silently altering security |
| **I** — Interface Segregation | `Queueable`, `Batchable`, `Schedulable` as separate concerns | One class implements all three — untestable, unreadable |
| **D** — Dependency Inversion | Service depends on interface, not concrete `HttpRequest` | Direct `HttpRequest` instantiation — can't mock, can't swap |

### What a SOLID finding looks like

> **[SO-1] Single Responsibility violation — God-class @AuraEnabled method**
>
> `RaterController.cls:23-187` — `calculatePremium()` is 164 lines spanning 4 concerns:
> - Query (lines 25-38): 3 SOQL queries fetching policy, building, and coverage data
> - Transform (lines 40-92): field mapping into rater request payload
> - Callout (lines 94-130): HTTP callout to external rater API
> - Save (lines 132-187): DML to save response fields back to policy
>
> Each concern should be a separate class: `PolicySelector`, `RaterRequestBuilder`, `RaterCalloutService`, `PremiumWriter`. Currently, changing the API payload format forces you to also re-test query logic and DML, and vice versa.

The shape: **principle violated → method span → enumerated concerns with line ranges → separation proposal.**

---

## Fowler's Refactoring Catalog — Apex code smells

| Smell | Salesforce manifestation |
|-------|-------------------------|
| **Long Method** | `@AuraEnabled` method doing query + transform + callout + save in 200+ lines |
| **Feature Envy** | `OpportunityService` constantly accessing `Account` fields — logic belongs in `AccountService` |
| **Shotgun Surgery** | Adding a field requires changes in handler + service + test + LWC + Flow |
| **Primitive Obsession** | `String recordId` instead of typed `Id`. String status values instead of enum |
| **Data Clumps** | Same 5 address fields passed together across methods |
| **Speculative Generality** | Abstract base class with one implementation |

### What a Fowler finding looks like

> **[F-2] Shotgun Surgery — adding a ratable field requires 5 file changes**
>
> Adding `Roof_Material__c` to the rater integration requires modifying:
> 1. `RaterRequestBuilder.cls:45` — add field to request mapping
> 2. `RaterRequestBuilderTest.cls:23` — add field to test data
> 3. `APP_ChangeDetection.cls:88` — add field to change-detection hash
> 4. `raterPanel.html:67` — add field to UI display
> 5. `RaterFieldMapping__mdt` — add CMDT record
>
> Files 1-4 are code changes requiring deployment. If the field mapping were fully CMDT-driven (not partially), only file 5 would change — an admin-manageable config change with no deployment.

The shape: **smell name → concrete scenario → enumerated change sites with file:line → what the abstraction should be.**

---

## Kent Beck's Four Rules — Test class quality

Applied in priority order (rule 1 > rule 2 > rule 3 > rule 4).

### What a Kent Beck finding looks like

> **[KB-1] Rule 1 violation — zero assertions, coverage-only test**
>
> `PolicyRenewalHandlerTest.cls:45` — `testBulkRenewal()`
>
> ```apex
> @isTest static void testBulkRenewal() {
>     List<Policy__c> policies = TestDataFactory.createPolicies(200);
>     Test.startTest();
>     insert policies; // fires trigger
>     Test.stopTest();
>     // no assertions
> }
> ```
>
> This method inflates code coverage for `PolicyRenewalHandler` without verifying any outcome. The trigger could silently produce wrong data and this test would still pass. Add: `System.assertEquals(200, [SELECT COUNT() FROM Renewal_Quote__c], 'Expected one renewal quote per policy');`

The shape: **rule number → method name → verbatim code → what's missing → concrete fix with assertion.**

---

## Five Whys — Root cause chains

Salesforce bugs have deep causal chains because of the order of execution and multi-layer automation (trigger → flow → process builder → workflow rule → trigger again).

### What a Five Whys finding looks like

> **[5W-1] Wrong premium on policies renewed via batch**
>
> 1. **Why** did the user see $0 premium? → Renewal_Quote__c.Calculated_Premium__c is 0.00
> 2. **Why** is it 0.00? → `RenewalBatch.cls:67` calls `RaterService.rate()` with `Building__r.Year_Built__c = null`
> 3. **Why** is Year_Built__c null? → The batch SOQL at line 34 queries `Policy__c` but doesn't include `Building__r.Year_Built__c` in the SELECT
> 4. **Why** doesn't the query include it? → The query was copied from the UI controller where Building fields are loaded separately by the LWC
> 5. **Why** wasn't this caught in testing? → `RenewalBatchTest.cls:28` creates test Policies without Building records (Building__c is a lookup, not master-detail, so it's not required)
>
> **Root cause:** Query designed for UI context reused in batch context without adjusting the field list. Test data doesn't create the full object graph.

The shape: **symptom → 5 chained "why" questions, each citing file:line → root cause statement.**

---

## Cynefin — Size it before you start

| Domain | Salesforce example | Handles to use |
|--------|-------------------|----------------|
| **Simple** | Add a field, update a validation rule, modify a list view | Poka-yoke + YAGNI |
| **Complicated** | New trigger with callout, multi-object Flow, LWC with wire services | Genba + SOLID + Pyramid |
| **Complex** | Platform event architecture, multi-org integration, Experience Cloud hybrid | Cynefin + First Principles + MECE + Pre-mortem |
| **Chaotic** | Production data corruption, governor limit breach in managed package | Genba + Five Whys + Andon |

---

## MECE — Completeness checking

Most powerful on Salesforce when applied against a known, enumerable set.

### What a MECE finding looks like

> **[MECE-1] Field mapping gap — 3 of 22 Building fields unmapped**
>
> Building__c has 22 custom fields. The rater request at `RaterRequestBuilder.cls:30-75` maps 19.
>
> | Field | Status |
> |-------|--------|
> | `Roof_Material__c` | **Gap** — not mapped, not excluded |
> | `Sprinkler_Type__c` | **Gap** — not mapped, not excluded |
> | `Last_Inspection_Date__c` | **Gap** — not mapped, not excluded |
> | `Year_Built__c` | Mapped (line 42) |
> | `Square_Footage__c` | Mapped (line 44) |
> | ... | ... |
>
> No overlaps found. 3 gaps require disposition: map, default, or explicitly exclude with documented reason.

The shape: **enumerable set → full coverage table → gaps and overlaps identified → disposition needed.**

---

## Wu Wei — Don't fight the platform

| Fighting the platform | Natural path |
|----------------------|-------------|
| Custom Apex scheduler | Scheduled Flow — monitored, retryable, admin-manageable |
| Custom REST endpoint for integration | Platform Event or Change Data Capture — replay, retry, ordering built in |
| Apex trigger doing validation | Validation Rule — covers all entry points, no deployment needed |
| Custom auth logic | Named Credentials — token refresh, rotation, per-user auth native |
| Custom UI framework | `lightning-record-form` — FLS, responsive, accessible out of the box |

### What a Wu Wei finding looks like

> **[WW-1] Custom scheduling logic where Scheduled Flow suffices**
>
> `PolicyExpirationScheduler.cls` (47 lines) + `PolicyExpirationSchedulerTest.cls` (52 lines) = 99 lines of Apex that schedule a daily job to query expiring policies and send notifications.
>
> A Scheduled Path on a Record-Triggered Flow achieves the same result with zero code: trigger on `Policy__c` where `Expiration_Date__c = TODAY + 30`, action = send notification. Admin-manageable, visible in Setup, no deployment for schedule changes.
>
> Custom code justified only if: the scheduling logic needs dynamic intervals, the query is too complex for Flow filter conditions, or the notification requires custom Apex rendering. None of these apply here based on the current implementation.

The shape: **what exists → lines of code involved → declarative alternative → when custom code IS justified → verdict.**

---

## Salesforce Recipes

```
Field/config change:             Poka-yoke + YAGNI
Apex trigger review:             Genba + Chaos Engineering + Poka-yoke
LWC component review:            Genba + Fowler's Catalog + SOLID
Flow review:                     Genba + Pre-mortem + Poka-yoke
Integration review:              Genba + STRIDE + Chaos Engineering
Test class audit:                Genba + Kent Beck's Four Rules + Chaos Engineering
Security audit:                  Red Team + STRIDE + Genba
Data migration review:           Genba + Chaos Engineering + MECE
Design doc review:               Genba + MECE + Pre-mortem + Poka-yoke
Pre-production audit (2-pass):   Pass 1: Genba + SOLID + MECE
                                 Pass 2: Chaos Engineering + Pre-mortem + Poka-yoke
Solution design from reqs:       Cynefin + First Principles + MECE + Pre-mortem
Bug investigation:               Genba + Five Whys + First Principles
```

---

## Ready-to-Use Contracts

The contracts below use the handles defined above. The EVIDENCE field references the finding shapes — you don't need to redefine the output format because the handles carry it.

### Apex Trigger Review

```
AXES:         Genba + Chaos Engineering + Poka-yoke
TARGET:       [ObjectName]Trigger.trigger, [ObjectName]TriggerHandler.cls,
              [ObjectName]TriggerHandlerTest.cls
EVIDENCE:     Genba: cite file:line for sharing keyword, SOQL security, and
              every governor-relevant operation.
              Chaos: inject 201 records, null fields, empty query results.
              For each failure: scenario → code path → governor math → outcome.
              Poka-yoke: for each guard, state what bypasses it.
ASSUMPTIONS:  Trigger execution order, recursion guard state, other triggers
              on this object. Mark each Verified or Unknown.
STOP:         Andon on: SOQL/DML inside a loop, missing recursion guard,
              data loss path, or sharing bypass from user context.
```

### Integration Review

```
AXES:         Genba + STRIDE + Chaos Engineering
TARGET:       *Service.cls, *Callout*.cls, Named Credentials, endpoint CMDT
EVIDENCE:     Genba: for each callout, show the full transaction path
              (entry → DML? → callout → DML? → return).
              STRIDE: evaluate each @AuraEnabled method against all six categories.
              Chaos: inject timeout, 500, empty body, malformed JSON.
              For each: scenario → code path → outcome.
ASSUMPTIONS:  Named Credential existence, timeout values, callout limit (100),
              DML-before-callout ordering. Mark each Verified or Unknown.
STOP:         Andon on: credentials in code, PII in debug logs, DML before
              callout without async separation.
```

### Security Audit

```
AXES:         Red Team + STRIDE + Genba
TARGET:       *Controller.cls, *Service.cls, *.js-meta.xml, permission sets
EVIDENCE:     STRIDE: one finding per category with exploitation path.
              Genba: cite sharing keyword, FLS enforcement method, and
              .js-meta.xml targets for every relevant class.
              Flag compounds (e.g., Spoofing + Elevation in same method).
ASSUMPTIONS:  OWD per object, role hierarchy, system vs user context per
              entry point. Mark each Verified or Unknown.
STOP:         Andon on: without sharing + user-context caller, SOQL without
              FLS in @AuraEnabled, credentials in source.
```

### Pre-Production Audit (Two-Pass)

```
=== PASS 1 (Fresh Session) ===
AXES:         Genba + SOLID + MECE
TARGET:       [all classes, LWC, flows, objects, config in the feature]
EVIDENCE:     Genba findings with file:line evidence.
              SOLID findings with concern enumeration and line ranges.
              MECE coverage table for fields, methods, and config.
ASSUMPTIONS:  Full ledger — relationships, field types, picklist values,
              CMDT records, profile access.
STOP:         Andon on data loss or security vulnerability.

=== PASS 2 (Separate Fresh Session — Do NOT read Pass 1) ===
AXES:         Chaos Engineering + Pre-mortem + Poka-yoke
TARGET:       [same files]
EVIDENCE:     Chaos findings with scenario → path → governor math → outcome.
              Pre-mortem scenarios with narrative → code path → user impact.
              Poka-yoke findings with bypass analysis.
ASSUMPTIONS:  Independent ledger. Do NOT reference Pass 1.
STOP:         Andon on data loss or security vulnerability.

=== MERGE ===
Deduplicate by (file, symptom, root cause). Severity = max(pass severities).
Findings discovered by both passes independently marked [Confirmed].
```

### Solution Design from Requirements

```
AXES:         Cynefin + First Principles + MECE + Pre-mortem
TARGET:       [requirements doc — no existing solution design]
EVIDENCE:     Cynefin: state complexity domain per component with justification.
              First Principles: every design decision cites the requirement it satisfies.
              MECE: every requirement has a design element. Every design element has a requirement.
              Pre-mortem: top 5 production failure scenarios with code path traces.
              Every Apex class states its single responsibility.
              Every integration specifies: auth, retry, timeout, error shape.
ASSUMPTIONS:  Full ledger. For each: the assumption, what breaks if wrong,
              and how to verify.
STOP:         Andon if requirements are ambiguous enough that two valid designs
              would produce incompatible data models.
```