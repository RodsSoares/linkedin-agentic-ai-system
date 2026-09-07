# Project Context

## Product Goal

Build an agentic AI system that identifies relevant LinkedIn

interaction opportunities, gathers supporting evidence, writes

comments aligned with Rodrigo's professional voice, evaluates

quality, and keeps a human in control of publication.

The system is intended to support strategic professional interaction,

not autonomous social-media engagement.

Human publication authority is mandatory.

## Baseline Lineage

Previous committed checkpoint:

`23bdb7c`

Commit description:

`feat: add opportunity evaluation and bounded scout agent`

The development increment documented in this file was built on top of

that checkpoint.

This file is intended to be committed together with the validated

increment described below.

The commit containing this validated state becomes the next recoverable

development checkpoint.

## Last Completed Development Increment

The current completed and validated increment introduces:

`Opportunity Evaluation Workflow Integration`

This increment connects Opportunity Evaluation to a controlled

LangGraph workflow and introduces deterministic routing based on the

final opportunity classification.

The validated routing behavior is:

``` text

HIGH

→ ACCEPTED_FOR_RESEARCH

→ END

MEDIUM

→ QUEUED

→ END

LOW

→ END

HIGH currently means that the opportunity is approved to proceed to

the future Research capability.

Research is not executed by this workflow yet.

MEDIUM opportunities are intentionally preserved as queued

opportunities rather than being treated as LOW.

The existing Writer / Quality Evaluator workflow remains preserved

and unchanged.

The complete project test suite currently passes:

50 passed
```

## Current Active LangGraph Workflow

The project currently preserves two compiled LangGraph workflows.

### Content Workflow

The existing Writer / Quality Evaluator workflow remains:

``` text
START
  ↓
Writer
  ↓
Quality Evaluator
```

Quality Evaluator routing:

``` text
PASS   → Human / END
REVISE → Writer
REJECT → END
```

Revision loops remain bounded by a maximum iteration limit.

### Opportunity Workflow

Opportunity Evaluation is now integrated into a dedicated controlled
LangGraph workflow:

``` text
START
  ↓
Opportunity Evaluator
  ↓
Controlled Routing
  ├── HIGH   → ACCEPTED_FOR_RESEARCH → END
  ├── MEDIUM → QUEUED                → END
  └── LOW                           → END
```

The Opportunity Evaluator receives a validated `PostCandidate`, performs
semantic evaluation through the LLM, applies deterministic Python
scoring and guardrails, stores the resulting `OpportunityEvaluation` in
workflow state, and routes according to the final classification.

HIGH does not execute Research yet. It records that the opportunity is
accepted for the future Research capability.

MEDIUM is preserved as a distinct queued state.

LOW terminates the Opportunity Workflow.

Scout remains implemented independently as a bounded Python agent loop
and is not yet connected to this LangGraph workflow.

## Planned Workflow Direction

The target system direction remains:

``` text
Scout
  ↓
Opportunity Evaluation
  ↓
Research
  ↓
Writer
  ↓
Quality Evaluator
  ↓
Human-in-the-loop
```

This target is being implemented incrementally. Components must not be
described as integrated before the corresponding workflow boundary has
been implemented and validated.

## Implemented Capabilities

### Core Data Contracts

Implemented:

-   PostCandidate schema

-   OpportunitySignals schema

-   OpportunityEvaluation schema

-   ScoutAction schema

-   ScoutSelection schema

-   ScoutState schema

-   SearchResult schema

-   Writer structured output

-   Quality Evaluation structured output

### Writer

Implemented:

-   Writer component

-   Rodrigo Voice prompt

-   structured Writer output

-   revision support through the controlled workflow

### Quality Evaluator

Implemented:

-   semantic quality evaluation

-   structured quality signals

-   deterministic PASS / REVISE / REJECT decision

-   deterministic quality thresholds

-   controlled revision loop

-   bounded retries

-   isolated automated tests

### Opportunity Evaluation v0.1

Implemented:

-   Opportunity Evaluation architecture and design

-   semantic evaluation contract

-   OpportunitySignals structured output

-   deterministic Research Efficiency calculation

-   deterministic weighted Opportunity Score

-   deterministic guardrails

-   deterministic HIGH / MEDIUM / LOW classification

-   isolated semantic evaluator

-   mocked semantic evaluation tests

-   deterministic scoring tests

-   boundary and guardrail tests

Opportunity Evaluation evaluates whether a discovered post represents

a strategically valuable opportunity for Rodrigo to contribute.

It does not evaluate whether the original post is simply good or
popular.

### Opportunity Workflow Integration

Implemented:

-   `opportunity_evaluator_node` as the LangGraph adapter for semantic
    evaluation and deterministic scoring;
-   deterministic HIGH / MEDIUM / LOW routing;
-   `accepted_for_research_node` state transition;
-   `queued_opportunity_node` state transition;
-   dedicated `build_opportunity_workflow()` graph;
-   systemic HIGH, MEDIUM, and LOW workflow-path tests;
-   preservation of the existing Writer / Quality Evaluator workflow.

Research is not executed by this workflow yet.

## Opportunity Evaluation Principle

The central product rule is:

``` text

Opportunity != Popularity
```

The system should prioritize situations where Rodrigo can make a

relevant, differentiated, and professionally valuable contribution.

Audience size and engagement matter, but must not dominate:

-   contribution potential;

-   professional positioning;

-   topic relevance.

## Opportunity Evaluation v0.1 Dimensions

The current scoring dimensions are:

``` text

Contribution Potential

Positioning Fit

Topic Relevance

Engagement Potential

Research Cost
```

All conceptual scores use the range:

``` text

0–100
```

## Opportunity Evaluation v0.1 Weights

The approved initial weights are:

``` text

Contribution Potential = 30%

Positioning Fit        = 25%

Topic Relevance        = 20%

Engagement Potential   = 15%

Research Efficiency    = 10%
```

Where:

``` text

Research Efficiency = 100 - Research Cost
```

## Opportunity Score Formula

The deterministic Opportunity Score is:

``` text

Opportunity Score =

    Contribution Potential × 0.30

  + Positioning Fit        × 0.25

  + Topic Relevance        × 0.20

  + Engagement Potential   × 0.15

  + Research Efficiency    × 0.10
```

## Opportunity Guardrails

The current deterministic guardrails are:

``` text

Contribution Potential < 30

→ LOW
```

``` text

Positioning Fit < 30

→ LOW
```

``` text

Topic Relevance < 25

→ LOW
```

A triggered guardrail forces LOW classification regardless of the

weighted Opportunity Score.

## Opportunity Classification

If no guardrail is triggered:

``` text

HIGH

score >= 80
```

``` text

MEDIUM

score >= 60 and < 80
```

``` text

LOW

score < 60
```

These weights, thresholds, and guardrails are v0.1 product hypotheses.

They are approved for initial use but should eventually be calibrated

using real opportunities and observed outcomes.

## Semantic vs Deterministic Responsibility

Opportunity Evaluation deliberately separates semantic interpretation

from operational decision ownership.

The current pattern is:

``` text

PostCandidate

      ↓

LLM Semantic Evaluation

      ↓

OpportunitySignals

      ↓

Python Deterministic Scoring

      ↓

Guardrails

      ↓

HIGH / MEDIUM / LOW
```

The LLM currently evaluates:

``` text

topic_relevance

positioning_fit

contribution_potential

research_cost
```

The LLM must not own:

``` text

final Opportunity Score

final HIGH / MEDIUM / LOW classification
```

Those decisions remain deterministic Python responsibilities.

## Engagement Potential Status

Engagement Potential remains intentionally separate from

OpportunitySignals.

The semantic LLM must not invent objective engagement metrics.

The intended future data path is:

``` text

Scout / Metadata Collection

        ↓

Objective Engagement Signals

        ↓

Deterministic Engagement Calculation
```

Potential objective signals include:

-   reaction_count

-   comment_count

-   published_at

-   post age

-   reaction velocity

-   comment velocity

-   author reach, when reliably available

The exact Engagement Potential formula remains unresolved.

For the current systemic Opportunity Workflow validation, the graph node
temporarily uses:

``` text
DEFAULT_ENGAGEMENT_POTENTIAL = 50
```

This is a neutral placeholder for workflow testing, not a production
engagement formula or an observed metric.

No engagement formula should be silently invented before real Scout data
availability is validated.

## Scout Agent v0.1

Scout v0.1 is now implemented as a bounded agentic loop.

Its objective is to discover potentially valuable professional

interaction opportunities.

The current Scout action vocabulary is:

``` text

SEARCH

READ

SELECT

FINISH
```

## Scout Agent Architecture

The Scout follows the pattern:

``` text

ScoutState

    ↓

decide_next_action()

    ↓

LLM

    ↓

Structured ScoutAction

    ↓

Python Executor

    ↓

Guardrails

    ↓

Tool Execution

    ↓

Updated ScoutState

    ↓

Next LLM Decision
```

The loop continues until:

``` text

FINISH
```

or:

``` text

max_steps
```

is reached.

## Scout Semantic Autonomy

The LLM owns semantic next-action selection inside the permitted

action space.

Examples of decisions the LLM may make:

-   formulate a search query;

-   decide which discovered result appears worth reading;

-   decide whether the most recently read content should become a

    candidate;

-   decide whether further exploration is useful.

The LLM does not control the runtime itself.

It can request actions only through the ScoutAction structured contract.

## Scout Deterministic Guardrails

Python remains responsible for authorizing or rejecting requested
actions.

Current guardrails include:

-   SEARCH requires a query;

-   repeated search queries are rejected;

-   READ requires a URL;

-   READ may only access URLs returned by Scout search results;

-   previously visited URLs may not be revisited;

-   SELECT requires previously read content;

-   SELECT requires a structured ScoutSelection;

-   max_steps limits total agent iterations;

-   unsupported actions are rejected.

A blocked action raises a controlled ValueError.

The Scout runtime records the error in:

``` text

state.last_error
```

and allows the LLM to receive the updated state and attempt another

bounded decision.

## Scout Candidate Selection

Scout can now promote previously read content into a PostCandidate.

The semantic decision belongs to the LLM:

``` text

"This content is worth selecting."
```

The factual construction belongs to Python.

The LLM does not invent the selected URL or reproduce the factual

content contract.

Current flow:

``` text

SEARCH

  ↓

READ

  ↓

SELECT

  ↓

Python validation

  ↓

PostCandidate

  ↓

state.candidates
```

## Scout Real-LLM Validation

Scout v0.1 has been manually executed using the real OpenAI API.

A real run successfully demonstrated autonomous semantic behavior

inside the bounded runtime.

The model independently:

-   formulated search queries;

-   refined search strategy;

-   selected a discovered result to read;

-   evaluated the observed content;

-   requested SELECT;

-   caused a validated PostCandidate to be created.

The successful real-agent run produced a candidate related to:

``` text

AI agents + Supply Chain
```

without a hardcoded action sequence.

## Scout Tooling Status

Scout reasoning is real.

Scout web tools are not yet real.

Current implementations:

``` text

web_search

web_reader
```

are deterministic fake tools created specifically to isolate and

validate the agent mechanics.

The fake search tool currently returns the same predefined results

regardless of the search query.

Therefore:

``` text

Agentic decision behavior = REAL

Web discovery environment = FAKE / DETERMINISTIC
```

The current implementation must not be described as a production

LinkedIn discovery capability.

## Scout Known Limitations

The following limitations are intentionally known:

### Fake Web Environment

The current web_search implementation ignores the actual query and

returns predefined SearchResult objects.

The current web_reader reads predefined content.

### Candidate Metadata

Current fake search results do not provide complete real LinkedIn

metadata.

For the current isolated implementation:

``` text

author_name = "Unknown"
```

is used rather than allowing the LLM to invent author identity.

### Action History

ScoutState currently preserves operational state but does not maintain

a complete chronological action / observation trace.

The final state may show:

-   search queries;

-   visited URLs;

-   current search results;

-   latest read content;

-   selected candidates;

-   latest recoverable error;

-   number of steps;

but it does not yet provide a complete ordered execution history.

### Termination

The Scout can finish through:

``` text

FINISH
```

or by reaching:

``` text

max_steps
```

Real test runs have demonstrated max_steps termination.

The runtime must remain bounded.

## Agent Definition Established During This Increment

The project uses the following architectural understanding:

``` text

Agent =

LLM

+ objective

+ state

+ actions

+ tools

+ decision loop

+ guardrails
```

An LLM alone is not an agent.

A deterministic loop alone is not semantic agent autonomy.

Agentic behavior emerges from combining semantic decision-making with

controlled executable capabilities and operational constraints.

## Current Scout Loop Technology

The internal Scout loop is currently implemented directly in Python.

It is not currently implemented as a LangGraph subgraph.

This was intentional so that the fundamental agent mechanics remain

explicit and understandable:

``` text

perceive

→ decide

→ act

→ observe

→ update state

→ decide again
```

LangGraph remains part of the broader system architecture and may

later organize Scout or multi-agent orchestration when doing so adds

clear value.

## Current Test Baseline

Full project suite:

``` text
50 passing tests
```

The current test suite covers:

-   Writer behavior
-   Quality Evaluator behavior
-   Quality scoring
-   deterministic quality routing
-   schema validation
-   OpportunitySignals validation
-   Opportunity Evaluation scoring
-   Research Efficiency
-   Opportunity guardrails
-   Opportunity classification
-   semantic Opportunity Evaluation contract
-   opportunity classification routing
-   accepted-for-research state transition
-   queued-opportunity state transition
-   HIGH Opportunity Workflow path
-   MEDIUM Opportunity Workflow path
-   LOW Opportunity Workflow path
-   Scout SEARCH behavior
-   Scout READ behavior
-   Scout SELECT behavior
-   Scout FINISH behavior
-   repeated-search protection
-   undiscovered-URL protection
-   revisited-URL protection
-   max_steps enforcement
-   structured Scout action parsing
-   blocked-action recovery
-   PostCandidate creation from Scout selection
-   structured SELECT action behavior

Live OpenAI calls are not required by the automated test suite.

LLM-facing tests use mocks where appropriate.

## Current Development Status

The current development increment is:

``` text
IMPLEMENTED
TESTED
AUDITED
READY FOR CHECKPOINT COMMIT
```

Full test suite result:

``` text
50 passed
```

Project Context Snapshot integrity:

``` text
PASS
```

The automated audit confirmed that repository content remained stable
during audit collection.

## Current Development Objective

The current increment integrated Opportunity Evaluation into a
controlled LangGraph workflow.

The implemented flow is:

``` text
PostCandidate
  ↓
Opportunity Evaluation
  ↓
Controlled Routing
```

The routing behavior is:

``` text
HIGH   → ACCEPTED_FOR_RESEARCH → END
MEDIUM → QUEUED                → END
LOW                            → END
```

The integration validates the system boundary between semantic
Opportunity Evaluation, deterministic scoring, explicit workflow state,
deterministic routing, and LangGraph execution.

Research remains intentionally unimplemented in this workflow.

Scout remains independently implemented and has not yet been connected
to the Opportunity Workflow.

The existing Writer / Quality Evaluator workflow remains preserved.

## Current WIP

No new capability should be started before the current validated
increment is committed and pushed.

The working tree currently contains the validated Opportunity Evaluation
Workflow Integration together with its routing logic, workflow nodes,
state changes, automated tests, and this context update.

## Next Planned Capability

After the current checkpoint commit, development should continue with:

``` text
Scout → Opportunity Workflow Integration
```

The next increment should connect validated `PostCandidate` objects
selected by Scout to the existing Opportunity Workflow.

The integration should remain incremental. It should not attempt to
implement Research at the same time unless the Scout-to-Opportunity
boundary is first validated and stable.

Initial target:

``` text
Scout
  ↓
PostCandidate
  ↓
Opportunity Evaluation
  ↓
Controlled Routing
```

The existing Opportunity Workflow and Writer / Quality Evaluator
workflow must remain stable while this integration is introduced.

## Opportunity Routing Direction

The current v0.1 routing behavior is established as:

``` text
HIGH
  ↓
ACCEPTED_FOR_RESEARCH
  ↓
END

MEDIUM
  ↓
QUEUED
  ↓
END

LOW
  ↓
END
```

HIGH means the opportunity is approved to proceed to Research when that
capability becomes integrated. It does not mean Research has already
executed.

MEDIUM opportunities remain distinct from LOW opportunities. They are
preserved in a lower-priority queued state without incurring Research
cost.

LOW opportunities terminate the Opportunity Workflow.

When Research is implemented, the intended HIGH path becomes:

``` text
HIGH
  ↓
Research
```

The lifecycle of queued MEDIUM opportunities may be revisited later
using real operational evidence, but the current v0.1 routing behavior
is explicitly QUEUED.

## Research Status

Research remains a planned specialist capability.

Its intended responsibility is:

``` text

Given a selected opportunity,

gather the evidence and context required

to produce a factual and defensible contribution.
```

Research should occur after Opportunity Evaluation.

Research must remain bounded.

Research should not be implemented as unrestricted autonomous browsing.

## Architectural Principles

The following principles are established:

-   Human-in-the-loop is mandatory before publication.

-   The system must never publish autonomously.

-   Agent autonomy must remain bounded.

-   Prefer deterministic decisions where deterministic logic provides

    sufficient reliability.

-   Use LLM reasoning where semantic understanding adds material value.

-   Use structured outputs between AI components.

-   Keep explicit workflow state.

-   Bound retries, revisions, and agent exploration.

-   Deterministic application code owns operational guardrails.

-   LLMs may propose actions but cannot bypass runtime authorization.

-   Objective factual data should not be invented by an LLM.

-   Separate semantic interpretation from deterministic decision logic.

-   Preserve component responsibility boundaries.

-   Treat LLM consumption as computational infrastructure.

-   Apply cost-aware orchestration and token governance.

-   Reserve expensive/frontier models for high-value reasoning.

-   Prefer cheaper models or deterministic logic where quality

    requirements can still be satisfied.

-   Add complexity only when it provides clear behavioral or product

    value.

## Cost-Aware Orchestration

LLM consumption is treated as infrastructure cost.

The orchestration layer should eventually consider not only:

``` text

Which component should run?
```

but also:

``` text

Which model is appropriate for this task?
```

The target optimization principle is:

> Minimum inference cost capable of satisfying the required Quality

> Contract.

Frontier models should be reserved for reasoning tasks where their

additional capability materially improves the result.

Deterministic logic and cheaper models should be preferred where they

can satisfy the requirement reliably.

## Explicit Non-Goals

Current non-goals include:

-   autonomous LinkedIn publication;

-   autonomous LinkedIn commenting;

-   unbounded web browsing;

-   unbounded agent loops;

-   unbounded agent-to-agent delegation;

-   letting an LLM bypass deterministic guardrails;

-   using an LLM for decisions that can be reliably deterministic;

-   inventing objective engagement data;

-   claiming the current fake Scout tools perform real LinkedIn
    discovery;

-   prematurely optimizing Opportunity Evaluation weights without data;

-   implementing unrelated platform capabilities before the core
    workflow

    becomes operational;

-   building large infrastructure layers without a demonstrated need.

## Established Product Decisions

### Human Authority

Humans retain final publication authority.

No component may autonomously publish.

### Opportunity Evaluation

Opportunity means strategic professional contribution potential, not

simple popularity.

Contribution Potential receives the highest current scoring weight.

### Final Opportunity Decision

The LLM does not own final HIGH / MEDIUM / LOW classification.

Python owns:

-   Research Efficiency;

-   weighted Opportunity Score;

-   mandatory guardrails;

-   final classification.

### Scout

Scout has bounded semantic autonomy.

The LLM chooses among allowed actions.

Python authorizes execution.

Tools perform the actual external or simulated operation.

State records observations.

max_steps limits exploration.

### Opportunity Routing

Current v0.1 routing is deterministic:

-   HIGH → `ACCEPTED_FOR_RESEARCH` → END;
-   MEDIUM → `QUEUED` → END;
-   LOW → END.

`ACCEPTED_FOR_RESEARCH` records approval for the future Research
capability; it does not imply that Research has executed.

The later lifecycle of queued MEDIUM opportunities remains open to
calibration.

### Structured Outputs

LLM boundaries should use typed structured outputs where practical.

Pydantic contracts are preferred for machine-to-machine AI component

communication.

## Open Design Decisions

The following decisions remain intentionally unresolved:

1.  How Scout will access real LinkedIn or web candidate sources.

2.  Which real search mechanism will replace the deterministic fake

    web_search tool.

3.  Which real reading mechanism will replace the deterministic fake

    web_reader tool.

4.  How reliable LinkedIn metadata can be collected.

5.  Whether reaction_count is consistently available.

6.  Whether comment_count is consistently available.

7.  Whether author follower counts are consistently available.

8.  Exact Engagement Potential normalization.

9.  Handling of missing engagement data.

10. Calibration of engagement velocity thresholds.

11. How queued MEDIUM opportunities should later be revisited,
    prioritized, or promoted.

12. Final Research Agent design.

13. Research tool boundaries.

14. Model selection per component.

15. Whether Opportunity semantic dimensions should remain in one LLM

    call or be separated.

16. Long-term Opportunity Evaluation calibration methodology.

17. Whether measured token/tool cost should later influence Research

    Cost.

18. Whether author relevance should become a separate evaluation

    dimension.

19. Whether Scout should later become a LangGraph subgraph.

20. Whether ScoutState should include a complete action / observation

    history.

21. How selected candidates should be deduplicated.

22. How multiple Scout candidates should be ranked or queued.

23. How the active workflow should represent multiple opportunities.

24. How production-grade observability should record agent decisions,

    tool calls, costs, and failures.

These decisions must be resolved incrementally.

They must not be silently encoded into implementation without an

explicit architectural or product decision.

## Context Maintenance Rule

Update this file whenever any of the following changes:

-   current development objective;

-   baseline lineage;

-   current WIP;

-   completed capability;

-   active workflow architecture;

-   planned workflow direction;

-   architectural principle;

-   frozen decision;

-   explicit non-goal;

-   test baseline;

-   next planned capability;

-   important known limitation.

Before each checkpoint commit:

1.  complete the development increment;

2.  run the full test suite and obtain approval;

3.  run `python app/scripts/project_audit.py`;

4.  validate the generated audit;

5.  update this PROJECT_CONTEXT.md from the validated factual state;

6.  review repository diff/status;

7.  stage;

8.  commit;

9.  push.

The audit is the factual repository snapshot.

PROJECT_CONTEXT.md is the human-maintained interpretation of that

snapshot and should explain:

``` text

where the project came from

what is currently implemented

what remains intentionally incomplete

what decisions are established

what should happen next
```

The combination of:

``` text

code

+

tests

+

audit

+

PROJECT_CONTEXT.md

+

Git checkpoint
```

is the official development recovery mechanism for the project.
