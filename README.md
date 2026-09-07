# LinkedIn Agentic AI System

An agentic AI system for discovering strategically relevant LinkedIn
interaction opportunities, evaluating whether they are worth pursuing,
preparing evidence-grounded contributions, and keeping a human in
control of publication.

> **Current stage:** active development. The project already includes a
> bounded Scout agent, hybrid LLM + deterministic Opportunity
> Evaluation, controlled LangGraph routing, structured outputs,
> guardrails, and an automated test suite. Research and the full
> end-to-end workflow are still being integrated.

![Architecture](docs/images/architecture-overview.png)

## Why This Project Exists

Strategic interaction on LinkedIn involves more than generating text.

A useful system must decide:

-   which opportunities are worth attention;
-   whether a contribution would be relevant and differentiated;
-   when additional research is justified;
-   what evidence is required;
-   how to write in the intended professional voice;
-   whether the generated contribution satisfies a quality contract;
-   when the system should stop, retry, queue, or escalate to a human.

This project explores that problem as a controlled agentic AI system
rather than as a single prompt or autonomous social-media bot.

The goal is to reduce the manual effort required to discover and prepare
high-value professional interactions while preserving human publication
authority.

## Product Principle

The system is designed around a simple rule:

``` text
Opportunity != Popularity
```

A popular post is not automatically a valuable opportunity.

The system should prioritize situations where the user can make a
relevant, differentiated, and professionally useful contribution.

Engagement matters, but it must not dominate contribution potential,
professional positioning, or topic relevance.

## Architecture Direction

The target architecture is:

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

The system is being built incrementally. Components are not described as
integrated until their workflow boundary has been implemented and
validated.

### Responsibility Model

A central architectural decision is to separate semantic reasoning from
deterministic operational control.

``` text
LLM
├── semantic interpretation
├── bounded action selection
└── structured outputs

Python
├── scoring
├── guardrails
├── action authorization
├── classifications
└── operational limits

LangGraph
├── workflow state
├── transitions
└── controlled routing
```

The LLM is used where semantic understanding adds value.

Deterministic application logic owns decisions that can be expressed
reliably as rules.

## Current System

The repository currently contains three major functional areas:

``` text
Bounded Scout Agent
        │
        └── produces PostCandidate objects

Opportunity Workflow
        │
        └── evaluates and routes a PostCandidate

Content Workflow
        │
        └── Writer ↔ Quality Evaluator
```

Scout and the Opportunity Workflow are not yet connected into one
end-to-end flow.

Research is also not yet integrated.

This separation is intentional while each boundary is validated
independently.

## Scout Agent v0.1

Scout is implemented as a bounded agentic loop whose objective is to
discover potentially valuable professional interaction opportunities.

Its current action vocabulary is:

``` text
SEARCH
READ
SELECT
FINISH
```

The internal loop follows:

``` text
State
  ↓
LLM chooses next allowed action
  ↓
Structured ScoutAction
  ↓
Python validates and authorizes
  ↓
Tool executes
  ↓
Observation updates State
  ↓
Next bounded decision
```

### Semantic Autonomy

The LLM may formulate search queries, choose discovered results to read,
select read content as a candidate, continue exploring, or finish.

The LLM does **not** control the runtime. It can only request actions
through a typed structured contract.

### Deterministic Guardrails

Python currently enforces rules including:

-   SEARCH requires a query;
-   repeated searches are rejected;
-   READ requires a URL;
-   READ can access only URLs previously returned by search;
-   visited URLs cannot be revisited;
-   SELECT requires previously read content;
-   SELECT requires a structured selection;
-   unsupported actions are rejected;
-   `max_steps` bounds total exploration.

A blocked action produces a controlled error that becomes part of the
agent state, allowing another bounded decision.

### Candidate Selection

Scout can promote validated read content into a `PostCandidate`.

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
```

The semantic decision to select belongs to the LLM. Factual construction
and validation belong to Python.

### Current Tooling Limitation

Scout reasoning has been validated with a real OpenAI model, but the
current web tools are deterministic test doubles.

``` text
Agentic decision behavior = REAL
Web discovery environment = FAKE / DETERMINISTIC
```

The current Scout must therefore **not** be interpreted as production
LinkedIn discovery.

Real search, reading, metadata collection, and source-access strategy
remain future integration work.

## Opportunity Evaluation v0.1

Opportunity Evaluation answers a different question from content
quality:

> Is this discovered post a strategically valuable opportunity to
> contribute?

The current dimensions are:

  Dimension                  Weight
  ------------------------ --------
  Contribution Potential        30%
  Positioning Fit               25%
  Topic Relevance               20%
  Engagement Potential          15%
  Research Efficiency           10%

Where:

``` text
Research Efficiency = 100 - Research Cost
```

The deterministic score is:

``` text
Opportunity Score =
    Contribution Potential × 0.30
  + Positioning Fit        × 0.25
  + Topic Relevance        × 0.20
  + Engagement Potential   × 0.15
  + Research Efficiency    × 0.10
```

### Semantic vs Deterministic Evaluation

The LLM currently evaluates:

``` text
topic_relevance
positioning_fit
contribution_potential
research_cost
```

Python owns:

``` text
research_efficiency
weighted opportunity score
mandatory guardrails
final HIGH / MEDIUM / LOW classification
```

This prevents the semantic model from silently owning the final
operational decision.

### Guardrails

The current v0.1 guardrails force LOW when:

``` text
Contribution Potential < 30
Positioning Fit        < 30
Topic Relevance        < 25
```

If no guardrail is triggered:

``` text
HIGH   = score >= 80
MEDIUM = score >= 60 and < 80
LOW    = score < 60
```

These weights and thresholds are initial product hypotheses and should
eventually be calibrated using real opportunities and observed outcomes.

### Engagement Potential

Objective engagement scoring is intentionally not invented yet.

During the current systemic workflow validation, the graph uses a
temporary neutral placeholder:

``` text
DEFAULT_ENGAGEMENT_POTENTIAL = 50
```

This value is not a production formula or observed engagement metric.

## Opportunity Workflow

Opportunity Evaluation is integrated into a dedicated LangGraph
workflow.

``` text
PostCandidate in initial state
        ↓
Opportunity Evaluator
        ↓
Controlled Routing
        ├── HIGH   → ACCEPTED_FOR_RESEARCH → END
        ├── MEDIUM → QUEUED                → END
        └── LOW                           → END
```

The Opportunity Evaluator receives a validated `PostCandidate`, obtains
semantic `OpportunitySignals`, applies deterministic scoring and
guardrails, stores the resulting `OpportunityEvaluation` in workflow
state, and routes according to the final classification.

### Routing Semantics

**HIGH** means the opportunity is approved for the future Research
capability. Research is not executed yet.

**MEDIUM** is intentionally distinct from LOW and is preserved as a
queued opportunity without incurring Research cost.

**LOW** terminates the Opportunity Workflow.

When Research is integrated, the intended HIGH path becomes:

``` text
HIGH
  ↓
Research
```

## Content Workflow

The existing Writer / Quality Evaluator workflow remains preserved:

``` text
START
  ↓
Writer
  ↓
Quality Evaluator
```

Quality routing is deterministic:

``` text
PASS   → Human / END
REVISE → Writer
REJECT → END
```

Revision loops are bounded by a maximum iteration limit.

The Writer and Quality Evaluator remain separate from the newer
Opportunity Workflow while upstream integration proceeds incrementally.

## Human-in-the-loop

Human publication authority is mandatory.

The system is designed to assist with discovery, research, writing, and
evaluation --- not to autonomously publish or comment on LinkedIn.

``` text
AI prepares
AI evaluates
Human decides
```

Autonomous publication is an explicit non-goal.

## Structured Outputs

Typed contracts are used at AI boundaries where practical.

Current schemas include:

-   `PostCandidate`
-   `OpportunitySignals`
-   `OpportunityEvaluation`
-   `ScoutAction`
-   `ScoutSelection`
-   `ScoutState`
-   `SearchResult`
-   structured Writer output
-   structured Quality Evaluation output

Pydantic is used to make component boundaries explicit and
machine-validatable.

## State and Routing

The LangGraph layer is intentionally thin.

``` text
Schemas
  ↓
define data contracts

State
  ↓
carries validated working data

Nodes
  ↓
invoke components and update State

Routing
  ↓
chooses deterministic paths

Graph
  ↓
connects the workflow
```

Business and scoring intelligence should remain in their responsible
components rather than being duplicated inside graph nodes.

## Engineering Principles

-   human-in-the-loop before publication;
-   no autonomous publishing;
-   bounded agent autonomy;
-   structured outputs between AI components;
-   explicit workflow state;
-   deterministic guardrails;
-   deterministic logic where rules provide sufficient reliability;
-   LLM reasoning where semantic understanding adds material value;
-   bounded retries, revisions, and exploration;
-   factual data must not be invented by an LLM;
-   semantic interpretation and operational decisions remain separated;
-   component responsibility boundaries are preserved;
-   complexity is added only when it provides clear product or
    behavioral value.

## Cost-Aware Orchestration

LLM consumption is treated as computational infrastructure.

The long-term orchestration question is not only which component should
run, but also which model is appropriate for each task.

The optimization principle is:

> Use the lowest inference cost capable of satisfying the required
> quality contract.

Frontier models should be reserved for tasks where their additional
reasoning capability materially improves the result.

Deterministic logic and cheaper models should be preferred when they can
satisfy the requirement reliably.

## Tech Stack

-   Python
-   OpenAI API
-   LangGraph
-   Pydantic
-   pytest
-   SQLite
-   web search / reading interfaces --- currently deterministic test
    implementations in Scout

## Testing

The current automated baseline is:

``` text
50 passing tests
```

Coverage includes Writer and Quality Evaluator behavior, deterministic
quality routing, schema validation, Opportunity Evaluation scoring and
guardrails, Research Efficiency, HIGH / MEDIUM / LOW classification and
routing, workflow state transitions, all three Opportunity Workflow
paths, and the bounded Scout action loop including its authorization
guardrails.

Automated tests do not require live OpenAI calls. LLM-facing behavior is
mocked where appropriate.

## Current Status

### Implemented and validated

``` text
Scout Agent v0.1
Opportunity Evaluation v0.1
Opportunity Workflow Integration
Writer
Quality Evaluator
Controlled Quality Revision Loop
Structured AI Contracts
Deterministic Routing and Guardrails
```

### Intentionally incomplete

``` text
Scout → Opportunity Workflow handoff
Research capability
Real Scout web/search environment
Objective Engagement Potential formula
Full end-to-end orchestration
Production-grade observability
Autonomous publication — intentionally excluded
```

## Next Development Increment

The next planned capability is:

``` text
Scout → Opportunity Workflow Integration
```

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

The boundary should be validated before Research is added.

## Known Limitations

-   Scout uses deterministic fake search and reader tools;
-   real LinkedIn/web discovery is not implemented;
-   reliable engagement metadata availability has not been validated;
-   Engagement Potential still uses a temporary neutral value in the
    Opportunity Workflow;
-   Research is not implemented in the active opportunity flow;
-   Scout and Opportunity Workflow are not connected yet;
-   Scout state does not maintain a complete chronological
    action/observation trace;
-   multiple selected candidates are not yet ranked or orchestrated;
-   production-grade observability and cost telemetry are not yet
    complete.

These limitations are documented rather than hidden because the project
is being developed as a sequence of validated capabilities.

## Explicit Non-Goals

-   autonomous LinkedIn publication;
-   autonomous LinkedIn commenting;
-   unbounded browsing;
-   unbounded agent loops;
-   unbounded agent-to-agent delegation;
-   allowing an LLM to bypass deterministic guardrails;
-   inventing objective engagement data;
-   claiming fake Scout tools provide real LinkedIn discovery;
-   prematurely optimizing scoring weights without operational evidence.

## Development Discipline

Relevant increments are closed through a recoverable checkpoint process:

``` text
Implement
  ↓
Run full test suite
  ↓
Generate and validate project audit
  ↓
Update PROJECT_CONTEXT.md
  ↓
Review Git diff/status
  ↓
Commit
  ↓
Push
```

The repository uses code, tests, audit snapshots, project context, and
Git checkpoints together as the development recovery mechanism.

## Project Philosophy

This project is not intended to demonstrate that an LLM can generate a
LinkedIn comment.

The more interesting engineering problem is controlling **when AI should
reason, when deterministic software should decide, how autonomous
exploration should be bounded, how state should move through the system,
and where human authority must remain final**.

That distinction is the foundation of the architecture.
