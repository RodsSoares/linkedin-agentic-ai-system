# ADR — Human-Centered Conversation Intelligence Architecture

**Status:** PROPOSED — NOT CANONICAL  
**Date:** 2026-09-15  
**Project:** LinkedIn Agentic AI System  
**Decision type:** Product / Architecture Proposal

> IMPORTANT
>
> This document describes a PROPOSED product architecture.
> It does NOT replace the current canonical architecture.
> No existing capability should be removed, rewritten, or reimplemented
> solely because of this proposal.
>
> Promotion to CANONICAL requires validation through real LinkedIn
> conversation experiments and an explicit architecture decision.

---

## 1. Context

The current LinkedIn Agentic AI System is evolving around a workflow in which
the system discovers relevant LinkedIn content, evaluates the opportunity,
researches the subject, generates content, evaluates quality, and routes the
result to human review.

Current conceptual flow:

Human Intent
→ Discovery / Scout
→ Opportunity Evaluation
→ Research
→ Writer
→ Evaluator
→ Human Review
→ Manual Publication

This architecture has demonstrated that the system can research, generate,
evaluate, and iteratively improve content while preserving Human-in-the-Loop
publication authority.

However, real editorial use revealed an important limitation in the original
product assumption:

The hardest part of producing a valuable contribution is not necessarily
writing the final text.

It is deciding what is worth saying.

Human interpretation depends on context that cannot be reliably reduced to a
finite set of editorial variables.

A person's interpretation of a conversation may depend on professional
experience, accumulated knowledge, current objectives, personal associations,
mood, recent events, intuition, values, and other contextual factors.

Attempting to reproduce all of this through increasingly large prompts,
scores, rules, and editorial variables risks creating false precision.

The proposed architecture therefore changes the role of AI from primarily
generating a final answer toward reducing the intellectual search space before
human judgment.

---

## 2. Product Hypothesis

The primary value proposition should evolve from:

> "Generate LinkedIn content that sounds like Rodrigo."

toward:

> "Find the right conversations, research what matters, build defensible
> perspectives, and help Rodrigo decide what is worth saying."

Content generation remains an important capability.

Rodrigo Voice also remains an important capability.

However, neither should be responsible for independently determining Rodrigo's
final intellectual position.

The system should augment human judgment rather than attempt to reproduce it.

---

## 3. Proposed Product Principle

### AI expands. Human converges. AI materializes. Human owns.

The system should use AI where machines have comparative advantages:

- discovery;
- filtering;
- reading;
- research;
- evidence retrieval;
- synthesis;
- comparison;
- contradiction detection;
- perspective generation;
- memory;
- drafting;
- evaluation;
- analytics.

Human judgment remains authoritative for:

- interpretation;
- intellectual direction;
- position selection;
- combination or rejection of perspectives;
- personal experience;
- contextual nuance;
- final editorial judgment;
- publication.

Human-in-the-Loop is therefore not merely a safety gate.

It is part of the cognitive architecture of the product.

---

## 4. Proposed High-Level Architecture

Human Intent
    ↓
Domain / Theme Selection
    ↓
Discovery
    ↓
Target Qualification
    ↓
Opportunity Evaluation
    ↓
Research
    ↓
Evidence & Source Synthesis
    ↓
Argument Intelligence
    ↓
Perspective Generation
    ↓
Rodrigo Voice Personalization
    ↓
Human Perspective Selection
    ↓
Final Writer
    ↓
Evaluator
    ↓
Human Final Review
    ↓
Manual Publication
    ↓
Performance Analytics
    ↓
Feedback Learning

---

## 5. Domain / Theme Selection

The future interface may begin with an explicit exploration domain.

Examples:

- AI / Agentic Systems
- Supply Chain / Operations
- Business Transformation
- Retail / Fashion
- Custom / Open Exploration

The selected domain should influence discovery configuration rather than act
only as a keyword filter.

Possible domain-specific configuration may include:

- topics;
- search strategies;
- preferred sources;
- domain vocabulary;
- research context;
- opportunity criteria;
- positioning context.

This direction is compatible with the emerging configurable Public Discovery
architecture.

---

## 6. Research Layer

Research should produce a reusable evidence base before any final content is
written.

The research artifact should distinguish:

- what the original author is arguing;
- relevant factual context;
- supporting evidence;
- challenging evidence;
- counterarguments;
- uncertainty;
- relevant sources;
- unresolved questions.

Research should remain independent from the final editorial direction whenever
possible.

This allows multiple perspectives to reuse the same evidence without repeating
research.

---

## 7. Argument Intelligence Layer

A new conceptual layer is proposed between Research and Writer.

Its responsibility is not to write the final LinkedIn response.

Its responsibility is to transform research into an intellectual decision
space.

Possible responsibilities:

### Evidence Synthesis

Determine what the available evidence supports, challenges, or leaves
uncertain.

### Tension Mapping

Identify meaningful disagreements, trade-offs, contradictions, assumptions,
and unresolved questions.

### Argument Brief

Produce a compact artifact that allows a human to understand the conversation
without reading every source.

The Argument Brief may contain:

- original thesis;
- relevant context;
- strongest evidence;
- strongest counterevidence;
- central tensions;
- uncertainty;
- possible contribution areas;
- source references.

---

## 8. Perspective Engine

The system should deliberately preserve divergence before convergence.

Instead of immediately producing one "best" response, the system should
generate a small number of defensible intellectual directions.

Example:

Perspective A — Operational

Perspective B — Economic

Perspective C — Organizational

Perspective D — Human / Behavioral

These are not merely different writing styles.

They represent different answers to:

> "What could be worth saying here?"

Each perspective should remain grounded in the same Research Brief and
evidence base.

A possible perspective artifact may include:

- perspective identifier;
- core argument;
- why it matters;
- supporting evidence;
- counterargument;
- uncertainty / risk;
- possible contribution to the conversation.

The system should avoid creating artificial disagreement solely to produce
multiple options.

Perspectives must be materially distinct and defensible.

---

## 9. Perspective Is Not Expression

The architecture should explicitly distinguish:

### Perspective

What should be said.

from:

### Expression

How the selected idea could be communicated.

Examples of expression:

- conversational;
- technical;
- provocative;
- humorous;
- formal;
- academic.

A technical perspective could be expressed conversationally.

An organizational perspective could be expressed humorously.

These dimensions should not be collapsed into a single variable.

---

## 10. Rodrigo Voice

Rodrigo Voice remains part of the architecture.

However, its responsibility becomes narrower and more testable.

Instead of attempting to infer simultaneously:

- what Rodrigo believes;
- which argument Rodrigo would select;
- how Rodrigo would express it;

Rodrigo Voice should primarily answer:

> "Given this specific perspective, how might Rodrigo naturally express it?"

The system may generate short Rodrigo Voice previews for each proposed
perspective.

This allows human selection before spending additional model calls and tokens
on complete drafts.

Rodrigo Voice therefore becomes an adaptive personalization layer rather than
a simulator of human judgment.

---

## 11. Human Perspective Selection

The human should be able to:

- select a perspective;
- reject a perspective;
- combine perspectives;
- request another direction;
- add personal context;
- modify the intended position.

Example:

Generated:
A
B
C
D

Human decision:
C + part of A

Rejected:
B
D

Only after this convergence should the system generate the complete final
draft.

This interaction becomes valuable learning data.

---

## 12. Final Writer

The Writer remains an important downstream capability.

Its role changes from:

> infer the position + choose the argument + reproduce the voice + write

to:

> materialize the human-selected position using the available evidence and
> personalization context.

This substantially reduces the uncertainty of the Writer task.

The Writer should reuse the existing Research Brief and should not rerun
research merely because the user requests a different expression.

---

## 13. Evaluator

The Evaluator remains useful, but its role should not be to determine whether
the system successfully "became Rodrigo."

Potential evaluation dimensions include:

- factual accuracy;
- evidence consistency;
- selected-perspective fidelity;
- unsupported claims;
- relevance;
- editorial clarity;
- Rodrigo Voice consistency;
- Preview Before More;
- unnecessary repetition;
- premature reveal;
- stopping discipline.

Human preference remains authoritative.

An evaluator recommendation is advisory unless an explicit safety, factual, or
policy rule requires enforcement.

---

## 14. Learning Architecture

The proposed architecture creates multiple distinct learning signals.

### Choice Memory

Learns from which perspectives the human:

- selects;
- rejects;
- combines;
- requests again.

### Rodrigo Voice

Learns from the relationship between:

AI-generated expression
→ human-edited expression
→ final published expression.

### Editorial Decision Memory

Learns recurring transformations such as:

- shortening;
- removing overstatement;
- adding concrete examples;
- introducing personal experience;
- changing conclusion placement;
- changing humor;
- removing generic AI language.

### Performance Learning

Associates publication outcomes with content and decision history.

Performance should not be interpreted as a direct measure of content quality.

---

## 15. Learning Principle

### Observation ≠ Interpretation ≠ Hypothesis ≠ Learned Preference

The system should avoid turning individual outcomes into rules.

Example:

Observation:
Post A achieved higher initial impression velocity than Post B.

Hypothesis:
Reader-value framing may have contributed.

Not justified:
"Reader-value framing causes better LinkedIn distribution."

Learned preferences should require repeated evidence and should retain
uncertainty.

---

## 16. Human Complexity Principle

The system should not attempt to completely model the human.

Human decisions may depend on latent variables that are unavailable or
inappropriate to infer.

The architecture should therefore prefer observable behavioral signals such
as:

- selected perspective;
- rejected perspective;
- combined perspectives;
- edits;
- additions;
- deletions;
- final text;
- publication decision.

The system may learn useful behavioral patterns without claiming to explain
the human reasoning that caused them.

### Predict useful behavior where possible.
### Do not pretend to model the person.

---

## 17. Analytics

Analytics should support decision-making rather than search for a universal
formula for successful content.

Potential questions include:

- Which themes repeatedly reach relevant audiences?
- Which contribution types generate discussion?
- Which posts generate saves?
- Which posts lead to profile views?
- Which perspectives does the human repeatedly select?
- Which generated directions are repeatedly rejected?
- Which sources consistently produce useful evidence?
- Which editorial transformations frequently occur before publication?

A core principle is:

### Not every interaction means the same thing.

Reactions, comments, saves, profile views, follows, and impressions may
represent different forms of value.

Performance therefore requires multidimensional interpretation.

---

## 18. Cost-Aware Interaction

The proposed architecture should avoid generating multiple complete drafts
before human direction is known.

Preferred sequence:

Research once
→ synthesize once
→ generate compact perspectives
→ generate short Rodrigo Voice previews
→ human selects
→ generate full draft only for selected direction.

This reduces unnecessary model usage while preserving intellectual diversity.

---

## 19. Existing Capabilities — DO NOT REIMPLEMENT

This proposal does not invalidate existing infrastructure.

The following capabilities remain relevant:

- Public Discovery;
- configurable discovery queries;
- web search provider;
- public HTTP reader;
- Target Qualification;
- novelty / memory mechanisms;
- Opportunity Evaluation;
- Research;
- evidence handling;
- Writer;
- Evaluator;
- Human-in-the-Loop;
- LangGraph orchestration;
- telemetry;
- token governance;
- editorial preferences;
- Preview Before More;
- Interaction Memory.

The proposal primarily changes how these capabilities are composed and where
human judgment enters the workflow.

---

## 20. Proposed Validation

The architecture should NOT become canonical based only on conceptual appeal.

Validation should use real LinkedIn conversations.

Initial experiment:

5–10 real opportunities.

For each opportunity:

1. Discover a relevant conversation.
2. Evaluate whether it is worth entering.
3. Research the topic.
4. Produce an Argument Brief.
5. Generate 3–4 materially different perspectives.
6. Apply Rodrigo Voice previews.
7. Record human selection / rejection / combination.
8. Generate the final draft.
9. Record human edits.
10. Record whether the result would actually be published.

Primary validation question:

> Does this workflow help Rodrigo reach a contribution he genuinely wants to
> make faster and with less cognitive friction than the current
> draft-first workflow?

Secondary questions:

- Are the perspectives materially different?
- Is the Argument Brief useful?
- Does Rodrigo Voice add value before selection?
- How often are perspectives combined?
- How much final editing remains?
- Does the workflow reduce rejected full drafts?
- Is research reused effectively?
- Does the additional architecture justify its complexity?

---

## 21. Promotion Criteria

This architecture may be promoted from PROPOSED to CANONICAL only after:

- real-use validation has been completed;
- the new workflow demonstrates meaningful utility;
- architectural implications have been reviewed;
- state/schema/node changes have been designed;
- migration impact has been assessed;
- existing capabilities have been mapped to the new workflow;
- an explicit human architecture decision is made.

Until then:

### CURRENT architecture remains authoritative.
### PROPOSED architecture remains experimental.

---

## 22. Proposed Product Thesis

The LinkedIn Agentic AI System should not attempt to replace human authorship.

Its purpose is to reduce the intellectual search space around relevant
professional conversations.

AI should discover, research, structure, compare, generate alternatives,
remember, draft, evaluate, and learn.

The human should interpret, choose, combine, judge, position, edit, and own the
final contribution.

Over time, the system may become increasingly personalized through observed
human decisions and final outputs.

The objective is not to simulate Rodrigo.

The objective is to become progressively better at collaborating with Rodrigo.
