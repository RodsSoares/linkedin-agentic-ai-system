Current Architecture

Document Purpose

This document is the factual implementation view of the LinkedIn Agentic AI System.

01_system_overview.md explains the architectural model and design philosophy.

This file answers a different question:

What is implemented now, and how are the current components connected?

It should be updated when the implemented workflow, component boundaries, routing, tooling, state, or runtime limits materially change.

Current Development Snapshot

Current automated baseline:

189 passing tests

Current stable baseline before the active increment:

156aa07
feat: integrate quality evaluator into opportunity workflow

The current working increment extends that baseline with:

Real Web Tooling v0.1
Context Preparation v0.1
Main Content Extraction v0.2.1

Real Scout and Research smoke validations have also been completed.

The next planned capability is:

End-to-End Real Workflow Validation v0.1

Active Workflow

The implemented workflow is:

Scout
|
v
Opportunity Evaluation
|
+-- LOW ------------------------------> END
|
+-- MEDIUM --> QUEUED ----------------> END
|
+-- HIGH
|
v
ACCEPTED_FOR_RESEARCH
|
v
Research
|
v
ResearchBrief
|
v
Writer
|
v
Quality Evaluator
|
+-- PASS -----------------> Human / END boundary
|
+-- REVISE --> Writer
|               |
|               +--> Quality Evaluator
|
+-- REJECT ---------------------> END

The Writer revision loop is bounded by the workflow iteration limit.

Research is not automatically rerun when Writer receives a revision request.

Repository-Level Component Map

The implementation is organized around the following responsibilities:

app/
|
+-- agents/
|   +-- scout.py
|   +-- research.py
|
+-- components/
|   +-- writer.py
|   +-- evaluator.py
|   +-- opportunity_evaluator.py
|
+-- graph/
|   +-- state.py
|   +-- workflow.py
|   +-- nodes/
|       +-- scout_node.py
|       +-- opportunity_evaluator_node.py
|       +-- opportunity_routing_nodes.py
|       +-- research_node.py
|       +-- writer_node.py
|       +-- evaluator_node.py
|
+-- schemas/
|   +-- scout.py
|   +-- opportunity.py
|   +-- research.py
|   +-- writer.py
|   +-- quality.py
|   +-- tools.py
|
+-- tools/
|   +-- web_search.py
|   +-- web_reader.py
|   +-- brave_search.py
|   +-- http_reader.py
|   +-- web_tools.py
|   +-- errors.py
|
+-- context_preparation.py
|
+-- config/
|   +-- settings.py
|
+-- scripts/
+-- project_audit.py

Exact filenames can evolve, but the responsibility boundaries should remain explicit.

Orchestration Layer

Global State

The LangGraph workflow carries shared state across nodes.

The current state includes concepts such as:

post
opportunity_score
research_result
current_draft
quality_evaluation
iteration
next_step
human_feedback
status

Specialist components should not automatically receive this entire state.

Nodes are responsible for mapping the relevant global state into component-specific inputs.

Scout Node

The Scout node bridges the global workflow and the bounded Scout agent.

Conceptually:

Workflow
|
v
scout_node
|
+--> obtain configured SearchTool / ReadTool
|
v
run_scout(...)
|
v
ScoutState
|
v
selected PostCandidate
|
v
workflow state

Routing after Scout is deterministic.

Current behavior:

0 candidates
-> END

1 candidate
-> Opportunity Evaluation

1 distinct candidates
-> explicit unsupported-condition failure

Duplicate selection of the same candidate is controlled rather than treated as multiple independent opportunities.

Multiple-candidate orchestration remains intentionally unresolved.

Scout Runtime

Scout is implemented as a bounded Python agent loop rather than as an internal LangGraph subgraph.

Action vocabulary:

SEARCH
READ
SELECT
FINISH

Execution pattern:

ScoutState
|
v
LLM decision
|
v
ScoutAction
|
v
Python validation / authorization
|
v
tool execution
|
v
state mutation
|
+-------> next bounded decision

The LLM owns semantic action selection.

Python owns legal execution.

Opportunity Evaluator Node

The Opportunity Evaluator receives a validated PostCandidate.

The semantic evaluator produces:

topic_relevance
positioning_fit
contribution_potential
research_cost

The application then derives:

research_efficiency = 100 - research_cost

Current score:

Contribution Potential × 0.30
Positioning Fit        × 0.25
Topic Relevance        × 0.20
Engagement Potential   × 0.15
Research Efficiency    × 0.10

Current mandatory LOW guardrails:

Contribution Potential < 30
Positioning Fit        < 30
Topic Relevance        < 25

Otherwise:

HIGH   >= 80
MEDIUM >= 60 and < 80
LOW    < 60

Where reliable engagement data is unavailable, the current implementation uses a neutral placeholder rather than allowing the model to invent engagement metrics.

Opportunity Routing

Routing is deterministic:

LOW
-> END

MEDIUM
-> QUEUED
-> END

HIGH
-> ACCEPTED_FOR_RESEARCH
-> Research

The semantic model therefore does not directly choose whether the graph enters Research.

It provides structured signals; deterministic application logic produces the operational classification.

Research Node

The Research node is integrated into the HIGH opportunity path.

Conceptually:

PostCandidate
+
Opportunity Evaluation
|
v
research_node
|
+--> get_web_tools()
|
v
ResearchState
|
v
run_research_loop(...)
|
v
ResearchBrief
|
v
research_result in workflow state
|
v
Writer

The node validates that the required opportunity context exists and that the opportunity is eligible for Research before invoking the agent.

Research Runtime

Research uses a bounded semantic loop with:

SEARCH
READ
EXTRACT
FINISH

The runtime separates discovery, reading, and evidence extraction:

SEARCH
|
v
SearchResult
|
v
READ
|
v
ReadSource
|
v
EXTRACT
|
v
EvidenceItem
|
v
ResearchBrief

Only extracted evidence is intended to support Writer-facing factual findings.

Current operational limits:

max steps           10
max decisions       12
max searches         3
max reads            5
max evidence items   6

Current completion statuses include:

SUFFICIENT
INSUFFICIENT
LIMIT_REACHED

Differentiated graph routing for all Research completion statuses remains a future hardening decision.

Writer Node

Writer receives the information required to generate the contribution draft.

The integration follows the component-specific-input principle:

Global workflow state
|
v
writer_node
|
v
Writer-specific input
|
v
Writer
|
v
current_draft

Research output is available to Writer through the integration boundary.

Writer does not own source authorization or evidence provenance.

Quality Evaluator Node

The Quality Evaluator evaluates the current draft against the quality contract.

Conceptually:

current_draft
|
v
evaluator_node
|
v
Quality Evaluator
|
v
quality_evaluation
|
v
deterministic route

Current outcomes:

PASS
REVISE
REJECT

Routing:

PASS
-> Human / END boundary

REVISE
-> Writer
-> Quality Evaluator

REJECT
-> END

Revision is bounded by MAX_ITERATIONS.

Web Tool Selection

The current web-tool factory selects execution mode through configuration.

Conceptually:

get_web_tools(mode)
|
+-- fake
|     |
|     +--> deterministic web_search
|     +--> deterministic web_reader
|
+-- real
|
+--> brave_search
+--> http_reader

The returned interface is always:

tuple[SearchTool, ReadTool]

This keeps Scout and Research independent from the concrete provider.

Search Adapter

The current real search implementation uses the Brave Search API.

Important implementation characteristics include:

bounded query size
bounded result count
API-key validation
request timeout
structured SearchResult mapping
controlled HTTP/network errors
injectable HTTP client for tests

The agent does not receive provider-specific response objects.

Provider output is mapped into the internal SearchResult contract.

HTTP Reader

The real reader is a bounded network adapter.

The current safety boundary includes:

HTTP / HTTPS only
localhost rejection
DNS resolution
private/non-global IP rejection
manual redirect handling
redirect revalidation
redirect limit
request timeout
text content-type restriction
response-size limit
controlled WebToolError conversion

This layer is important because READ actions originate from agent decisions.

The reader must therefore treat requested URLs as untrusted input.

Main Content Extraction

For HTML responses, the reader does not simply return the complete rendered page.

Current extraction behavior:

ignore common non-content elements

prefer non-empty <article>

otherwise prefer non-empty <main>

otherwise score section/div candidates

otherwise fall back to cleaned body text

Ignored structures include:

aside
form
footer
head
header
nav
noscript
script
style

Density scoring considers signals such as:

text length
paragraph count
heading count
list-item count
link-text density
positive content hints
negative navigation/promotion hints

Semantic article and main containers are authoritative even when short.

Density thresholds apply to fallback candidates rather than invalidating legitimate short semantic containers.

Context Preparation

app/context_preparation.py creates bounded LLM-facing external context.

The main value object is:

PreparedContext
├── content
├── original_tokens
├── prepared_tokens
└── truncated

Current processing:

external text
|
v
normalize whitespace
|
v
remove exact duplicate lines
|
v
tokenize / count
|
v
truncate if required
|
v
PreparedContext

Current token encoding defaults to:

o200k_base

with a controlled fallback encoding.

Current configured budgets:

SCOUT_READ_CONTEXT_MAX_TOKENS       = 1800
RESEARCH_READ_CONTEXT_MAX_TOKENS    = 2500
RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS = 8000

The cumulative Research budget applies to stored read context, not the complete serialized Research prompt.

Scout Context Boundary

Real or fake reader output is prepared before becoming Scout LLM-facing read context.

Conceptually:

ReadTool(url)
|
v
raw content
|
v
prepare_context(...)
|
v
bounded content
|
v
ScoutState / next LLM decision

Raw oversized page content should not bypass this boundary.

Research Context Boundary

Research applies both:

per-read limit
+
cumulative stored-read limit

Conceptually:

Read 1 -> prepare -> store
Read 2 -> prepare -> check cumulative budget -> store
Read N -> bounded by remaining budget

This creates a deterministic context ceiling independent from the model's semantic decision to continue researching.

Error Boundary

External web infrastructure failures use:

WebToolError

Scout and Research catch expected external-tool failures at the agent boundary.

The failure can be recorded in state and the bounded agent may choose a valid recovery action.

The runtime does not intentionally catch arbitrary programming errors and disguise them as external observations.

Fake vs Real Execution

Fake tooling remains a first-class testing capability.

Unit / integration tests
|
v
deterministic fake tools

Real tooling is used for explicit real-infrastructure validation:

Smoke / real workflow validation
|
v
Brave Search + HTTP reader

This separation provides deterministic automated tests without pretending that fake infrastructure represents production web behavior.

Current Real Validation

Scout

A real Scout smoke execution has demonstrated:

real LLM decision-making
real search
real read
main-content extraction
bounded context
candidate creation
normal completion

Research

A real Research smoke execution has demonstrated:

approved opportunity
real search
real source reading
evidence extraction
source provenance
ResearchBrief synthesis
SUFFICIENT completion

The Research run also preserved uncertainty rather than inventing supply-chain-specific rules that were not present in the source evidence.

Automated Test Baseline

Current full suite:

189 passing tests

The active test surface includes:

Scout
Opportunity Evaluation
workflow routing
Research
Research -> Writer integration
Writer
Quality Evaluator
web tool factory
Brave Search adapter
HTTP reader
web-tool recovery
context preparation
Scout context guards
Research context guards
main-content extraction
content-density extraction

Automated tests are intentionally isolated from live web/API dependencies where deterministic test doubles are more appropriate.

Current Known Gaps

The following are not yet implemented as production capabilities:

LinkedIn-specific production discovery
reliable LinkedIn metadata acquisition
objective Engagement Potential calculation
multiple distinct candidate orchestration
production-grade chronological agent telemetry
production cost/latency telemetry
cloud deployment architecture
long-term model routing
real-world score calibration
complete real end-to-end workflow validation

The system must not be described as production-ready while these boundaries remain unresolved.

Next Increment

The next planned increment is:

End-to-End Real Workflow Validation v0.1

The validation target is the actual integrated path:

Real Web
|
v
Scout
|
v
Opportunity Evaluation
|
v
HIGH
|
v
Research
|
v
Writer
|
v
Quality Evaluator
|
v
Human / END boundary

The objective is not merely to obtain a successful output.

The objective is to verify that the integrated real path respects the same contracts, context limits, provenance rules, routing rules, and failure boundaries already established in isolated capabilities.

Maintenance Rule

Update this document whenever any of the following materially changes:

implemented workflow topology
node responsibilities
component integration
routing behavior
web tooling implementation
context boundaries
runtime limits
failure handling
real validation status
major implemented capability

Do not use this document as a development diary.

Historical rationale belongs in 04_decision_log.md.

Deep capability specifications belong in dedicated architecture documents.

Recovery/checkpoint state belongs in:

docs/context/PROJECT_CONTEXT.md
