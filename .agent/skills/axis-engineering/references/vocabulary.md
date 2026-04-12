# Axis Engineering: Full Vocabulary Reference

## Axis 1: Dispositional — How to Think

Terms that set the agent's cognitive stance.

| Handle | Origin | Unpacks to | Evidence | Domain |
|--------|--------|-----------|----------|--------|
| **Genba** | Toyota Production System | Go to the source. Verify reality. Don't trust abstractions — read the actual artifact. | File:line citations, grep results, verbatim snippets | any |
| **Seven Factors of Awakening** | Gandharan Buddhism | Mindful, Investigative, Energetic, Engaged, Tranquil, Concentrated, Equanimous | Explicit mention of each factor's application | any |
| **Kaizen** | Toyota / Lean | Small continuous improvements. Targeted fixes over big rewrites. | Incremental change proposals with minimal blast radius | any |
| **Shoshin** | Zen Buddhism | Beginner's Mind. Read fresh even if you've seen it before. | Questions that reveal unstated assumptions | any |
| **First Principles** | Aristotle / Musk | Decompose to fundamentals. Don't reason by analogy. | Chain of "why" questions to root cause | architecture |
| **Wabi-sabi** | Japanese aesthetics | Accept imperfection. Working code has value. | Explicit decision to NOT refactor | any |
| **Wu Wei** | Taoism | Effortless action. Find the natural path. | Solution that works with framework, not against | any |

## Axis 2: Structural — How to Output

Terms that shape the format and organisation of results.

| Handle | Origin | Unpacks to | Evidence | Domain |
|--------|--------|-----------|----------|--------|
| **MECE** | McKinsey | Mutually Exclusive, Collectively Exhaustive. No overlaps, no gaps. | Explicit categorization with gap analysis | any |
| **Pyramid Principle** | Barbara Minto | Lead with the answer. Supporting detail below. | BLUF + hierarchical supporting points | any |
| **BLUF** | US Military | Bottom Line Up Front. Conclusion in first sentence. | Single-sentence verdict before details | any |
| **Five Whys** | Toyota | Chain causal analysis. Don't stop at symptoms. | 5-level deep causal chain | bug, ops |
| **Eisenhower Matrix** | Dwight Eisenhower | Urgency × Importance categorization. Four quadrants. | 2×2 matrix with items placed in quadrants | planning |

## Axis 3: Pattern-Oriented — What to Recognise

Terms that activate specific pattern libraries.

| Handle | Origin | Unpacks to | Evidence | Domain |
|--------|--------|-----------|----------|--------|
| **Gang of Four** | Gamma et al. | Recognise and apply the 23 design patterns. | Named pattern citations with locations | code |
| **Fowler's Catalog** | Martin Fowler | Recognise code smells and named refactorings. | Smell name + location + suggested refactoring | code |
| **SOLID** | Robert C. Martin | Single Responsibility, Open/Closed, Liskov, ISP, DIP. | Principle violations with file:line | code |
| **DDD** | Eric Evans | Ubiquitous language, bounded contexts, aggregates. | Domain term glossary, context boundaries | architecture |
| **Feathers' Legacy Code** | Michael Feathers | Characterisation tests, seams, safe refactoring. | Seams identified, characterization test proposals | code |
| **Kent Beck's Four Rules** | Kent Beck | 1. Passes tests. 2. Reveals intention. 3. No duplication. 4. Fewest elements. | Rule-by-rule assessment | code |
| **Hexagonal Architecture** | Alistair Cockburn | Ports and adapters. Depend inward only. | Port/adapter mapping, dependency direction check | architecture |
| **12-Factor App** | Heroku | Config in env, stateless processes, logs as streams. | Factor-by-factor compliance check | ops |

## Axis 4: Adversarial — What to Break

Terms that activate critical/destructive testing instincts.

| Handle | Origin | Unpacks to | Evidence | Domain |
|--------|--------|-----------|----------|--------|
| **Red Team** | Military / Security | Actively try to break it. Think like an attacker. | Attack vectors with exploitation steps | security |
| **Pre-mortem** | Gary Klein | Assume it already failed. Explain why. | Concrete failure scenario with causal chain | any |
| **STRIDE** | Microsoft | Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation. | Threat categorized by STRIDE dimension | security |
| **Chaos Engineering** | Netflix | Deliberately inject failures. Test resilience. | Failure injection scenarios + system response | ops, code |
| **Muda** | Toyota | Find waste: dead code, premature abstraction, etc. | Named waste type + location + removal | code |
| **Andon** | Toyota | Stop the line immediately on critical defect. | Explicit stop recommendation with trigger condition | any |
| **Devil's Advocate** | Catholic Church | Argue against the solution. Surface counterarguments. | Structured counterargument with evidence | any |

## Axis 5: Contextual — How to Size the Problem

Terms that help calibrate response to problem complexity.

| Handle | Origin | Unpacks to | Evidence | Domain |
|--------|--------|-----------|----------|--------|
| **Cynefin** | Dave Snowden | Categorize: Simple, Complicated, Complex, Chaotic. | Explicit domain classification with rationale | any |
| **Poka-yoke** | Shigeo Shingo | Mistake-proof it. Make wrong thing impossible. | Guard mechanism that prevents error class | any |
| **Jidoka** | Toyota | Build quality checks into the process itself. | Automated detection at point of creation | ops |
| **YAGNI** | Kent Beck | You Aren't Gonna Need It. Don't build hypotheticals. | Explicit scope exclusion with justification | any |
| **Occam's Razor** | William of Ockham | Simplest explanation/solution is usually correct. | Simpler alternative proposed and selected | any |
| **Theory of Constraints** | Goldratt | Find the bottleneck. Optimize the constraint. | Identified bottleneck + targeted optimization | ops |

## Defining a Behavior Handle

A term qualifies as a behavior handle when it has three properties:

1. **Dense training signal.** Extensive consistent representation in LLM training data.
2. **Transferable abstraction.** Developed in one domain but maps cleanly to software.
3. **Behavioral, not procedural.** Describes *how to be*, not *what to do*.

## The Evidence Field

The Evidence field prevents cargo-culting. Without it, agents name-drop handles. With it, they must demonstrate application through:
- Artifact references (`file:line`)
- Verification steps (grep results, test output)
- Specific patterns found (with names and locations)
