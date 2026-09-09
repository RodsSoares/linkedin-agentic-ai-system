Data Model and Contracts

Purpose

This document maps the principal typed data contracts and state boundaries of the LinkedIn Agentic AI System.

It is intentionally different from:

01_system_overview.md, which explains the conceptual architecture;

02_current_architecture.md, which explains the implemented runtime topology;

04_decision_log.md, which records architectural decisions.

This file answers:

What data crosses each component boundary, what does it mean, and who is allowed to create or mutate it?

The project uses typed contracts to constrain LLM behavior, reduce implicit coupling, preserve provenance, and make workflow behavior testable.

Contract Philosophy

The system follows four rules.

Structured boundaries over free-form machine communication

Where practical, LLM-backed components return typed structured outputs rather than unvalidated prose.

Component-specific inputs over global-state exposure

Specialist components should receive only the data required for their responsibility.

Global State
|
+--> Scout input
+--> Opportunity input
+--> Research input
+--> Writer input
+--> Evaluator input

They should not automatically receive the complete orchestration state.

Semantic proposals do not equal factual state

An LLM may propose an action or semantic interpretation.

Python validates whether that proposal is authorized before mutating factual application state.

Provenance is data

For Research, source lineage is part of the contract rather than an informal prompt convention.

Contract Map

The principal implemented contracts include:

POST / OPPORTUNITY
├── PostCandidate
├── OpportunitySignals
└── OpportunityEvaluation

SCOUT
├── ScoutAction
├── ScoutSelection
└── ScoutState

TOOLS
├── SearchResult
├── SearchTool
└── ReadTool

RESEARCH
├── ResearchObjective
├── ResearchAction
├── ReadSource
├── EvidenceItem
├── ResearchState
├── ResearchBriefSynthesis
├── ResearchBrief
└── ResearchStatus

GENERATION
└── Writer structured contracts

QUALITY
└── Quality Evaluation structured contracts

ORCHESTRATION
└── LinkedInAgentState

The current architecture explicitly prefers Pydantic contracts for machine-to-machine AI communication.

Post Domain

PostCandidate

PostCandidate is the normalized opportunity object that crosses the boundary from discovery into Opportunity Evaluation.

Conceptually:

External discovery
|
v
Scout observation
|
v
validated selection
|
v
PostCandidate
|
v
Opportunity Evaluation

It represents a candidate discussion/post that the system may consider pursuing.

The contract must contain the factual content required by downstream evaluation rather than relying on the downstream LLM to rediscover or invent it.

Ownership

Semantic selection:
Scout LLM

Validation and construction:
Python

Downstream consumption:
Opportunity Evaluator
Research
Writer through orchestration

Important invariant

A candidate is not evidence.

PostCandidate represents the object being evaluated, not factual support for claims made in the final contribution.

Opportunity Domain

OpportunitySignals

OpportunitySignals is the semantic assessment returned by the LLM-facing Opportunity Evaluator.

Current semantic dimensions:

topic_relevance
positioning_fit
contribution_potential
research_cost

The LLM is responsible for these semantic judgments.

The contract deliberately does not give the LLM unrestricted ownership of the final opportunity classification.

Derived Opportunity Values

Python derives:

research_efficiency = 100 - research_cost

The current weighted score is:

Contribution Potential × 0.30
Positioning Fit        × 0.25
Topic Relevance        × 0.20
Engagement Potential   × 0.15
Research Efficiency    × 0.10

Mandatory guardrails can force a LOW classification independently of the weighted total.

OpportunityEvaluation

OpportunityEvaluation is the operational evaluation result used by workflow routing.

Conceptually:

PostCandidate
|
v
LLM
|
v
OpportunitySignals
|
v
Python scoring + guardrails
|
v
OpportunityEvaluation
|
v
HIGH / MEDIUM / LOW routing

The distinction is important:

OpportunitySignals
= semantic evidence for the decision

OpportunityEvaluation
= validated operational decision artifact

Current routing behavior is HIGH → Research, MEDIUM → QUEUED → END, and LOW → END.

Tool Domain

SearchResult

SearchResult is the provider-neutral normalized result returned by a search tool.

Current contract:

SearchResult
├── title
├── url
└── snippet

The real Brave adapter and deterministic fake search tool both map into this same internal representation.

This prevents Scout and Research from depending on provider-specific API response structures.

SearchTool

Functional contract:

SearchTool:
(query: str)
-> list[SearchResult]

It represents capability, not implementation.

Current implementations can therefore include:

fake deterministic search
real Brave Search
future provider

without changing the agent-facing contract.

ReadTool

Functional contract:

ReadTool:
(url: str)
-> str

The returned string is content from an authorized read operation.

The real reader performs network validation and main-content extraction before its output reaches later context preparation.

WebToolError

WebToolError is the infrastructure error boundary for expected web-tool failures.

Conceptually:

external timeout / HTTP / network failure
|
v
WebToolError
|
v
Scout / Research recovery policy

It should not be used to hide arbitrary programming defects.

Scout Domain

ScoutAction

ScoutAction is the structured proposal produced by the Scout LLM.

Allowed semantic actions:

SEARCH
READ
SELECT
FINISH

The action object represents intent, not permission.

Conceptually:

LLM
|
v
ScoutAction
|
v
Python authorization
|
+--> legal   -> execute
|
+--> illegal -> reject / bounded recovery

This distinction is fundamental to bounded autonomy.

ScoutSelection

ScoutSelection carries the structured semantic information required when Scout requests SELECT.

The LLM can explain/select the candidate semantically, but Python validates the selection against observed/read state before a PostCandidate is created.

ScoutState

ScoutState is the operational state of the bounded Scout loop.

It preserves concepts including:

objective
search queries
current/discovered search results
visited URLs
latest read content
selected candidates
latest recoverable error
step count
status

The exact chronological action/observation history is not yet a production-grade trace.

State mutation rule

LLM requests action
|
v
Python validates action
|
v
tool executes
|
v
Python mutates ScoutState

The LLM does not directly mutate authoritative state.

Candidate Cardinality Boundary

The current workflow supports:

0 candidate  -> terminate before Opportunity Evaluation
1 candidate  -> Opportunity Evaluation

1 distinct candidates -> unsupported workflow condition

Multiple-opportunity ranking/queuing remains an explicit future design problem.

Research Domain

ResearchObjective

ResearchObjective defines what the Research capability is trying to establish for an approved opportunity.

It transforms a broad request to "research this opportunity" into a bounded semantic objective and focus areas.

Conceptually:

approved opportunity
|
v
ResearchObjective
|
v
bounded Research loop

ResearchAction

ResearchAction is the structured semantic proposal returned by the Research LLM.

Allowed actions:

SEARCH
READ
EXTRACT
FINISH

As with Scout:

action proposal != execution authority

Python validates authorization, provenance, counters, and limits before state mutation.

ReadSource

ReadSource represents a source that has actually crossed the READ boundary.

This is distinct from a SearchResult.

SearchResult
= discovered source candidate

ReadSource
= source actually read by Research

This distinction supports provenance and prevents search snippets from silently becoming authoritative evidence.

EvidenceItem

EvidenceItem is an explicitly extracted unit of factual support.

The provenance chain is:

SearchResult
|
v
authorized URL
|
v
ReadSource
|
v
EvidenceItem

Only extracted evidence is intended to support Writer-facing factual findings. The current architecture explicitly separates discovered sources, read sources, and evidence.

Important invariant

read content != evidence

Reading a source does not automatically authorize every statement on that page as a downstream factual claim.

ResearchState

ResearchState is the authoritative operational state of the Research loop.

It carries the evolving research process, including concepts such as:

objective
focus areas
search activity
discovered sources
read sources
evidence
counter/budget state
latest recoverable error
completion state

Python owns factual mutation of this state.

The LLM interprets observations and requests the next semantic action.

ResearchStatus

Current completion statuses include:

SUFFICIENT
INSUFFICIENT
LIMIT_REACHED

These represent materially different research outcomes.

The current workflow preserves the Research result downstream, while differentiated graph routing for all statuses remains a future hardening decision.

ResearchBriefSynthesis

ResearchBriefSynthesis is the structured semantic synthesis produced from the authorized Research evidence/state.

It separates synthesis from the lower-level operational state.

This prevents Writer from needing to interpret the complete internal Research execution history.

ResearchBrief

ResearchBrief is the Writer-facing Research artifact.

Conceptually:

ResearchState
|
v
validated evidence
+
semantic synthesis
|
v
ResearchBrief
|
v
Writer

It is the boundary between:

research execution

and:

content generation

The brief can carry findings, evidence, counterpoints, unresolved questions, source information, and completion status without exposing every internal runtime detail.

Context Preparation Domain

PreparedContext

External read content is bounded before becoming LLM-facing context.

Conceptual contract:

PreparedContext
├── content
├── original_tokens
├── prepared_tokens
└── truncated

This provides both the prepared text and metadata about what happened to it.

Current budgets

Scout read context
<= 1800 tokens

Research per-read context
<= 2500 tokens

Research cumulative stored read context
<= 8000 tokens

The cumulative Research limit applies to stored read content, not the complete serialized prompt.

Writer Domain

Writer Input Boundary

Writer receives component-specific input assembled by the orchestration layer.

Conceptually:

PostCandidate
+
Opportunity context
+
ResearchBrief
+
revision context when applicable
|
v
Writer-specific input
|
v
Writer

Writer should not need direct access to:

Scout internal action history
Research tool authorization state
web provider responses
global routing internals
publication authority

This follows the component-specific-input architectural rule.

Writer Structured Output

Writer returns a structured generation artifact rather than mutating workflow state directly.

The graph node maps that output into the global state, principally the current draft.

Conceptually:

Writer input
|
v
LLM-backed Writer
|
v
Writer structured output
|
v
writer_node
|
v
current_draft

Quality Domain

Quality Evaluation Contract

The Quality Evaluator consumes the generated draft and returns a structured quality result.

Its job is not to decide whether the original opportunity was strategically valuable.

It answers:

"Is this draft good enough?"

rather than:

"Was this opportunity worth pursuing?"

Current operational outcomes:

PASS
REVISE
REJECT

The structured quality result is then interpreted by deterministic routing.

Revision Data

When the quality result is REVISE, the workflow returns to Writer with the relevant revision context.

Research is not automatically repeated during draft revision.

This means the data lifecycle is:

ResearchBrief
|
v
Writer
|
v
Draft v1
|
v
Quality Evaluation
|
v
revision feedback
|
v
Writer
|
v
Draft v2

The evidence package remains stable unless a later architecture explicitly introduces a Research-reentry path.

Orchestration State

LinkedInAgentState

LinkedInAgentState is the shared workflow-level state.

It connects specialist nodes without making the specialist components themselves responsible for orchestration.

Current state concepts include:

post
opportunity_score
research_result
current_draft
quality_evaluation
iteration
next_step
human_feedback
status

The active HIGH path represented by this state is documented as Scout/supplied candidate → Opportunity Evaluation → Research → ResearchBrief → Writer → Quality Evaluator, with PASS/REVISE/REJECT routing.

Global State Is Not a Universal Component API

A key rule is:

LinkedInAgentState
!=
input contract for every component

Instead:

LinkedInAgentState
|
v
node mapping
|
v
specialist input

This limits coupling and makes future state evolution safer.

End-to-End Data Flow

The current HIGH path can be represented as:

External Web
|
v
SearchResult
|
v
Scout READ
|
v
Prepared external content
|
v
ScoutSelection
|
v
PostCandidate
|
v
OpportunitySignals
|
v
OpportunityEvaluation
|
v
ResearchObjective
|
v
ResearchAction(s)
|
+--> SearchResult(s)
|
+--> ReadSource(s)
|
+--> EvidenceItem(s)
|
v
ResearchState
|
v
ResearchBriefSynthesis
|
v
ResearchBrief
|
v
Writer structured output
|
v
current_draft
|
v
Quality Evaluation
|
+--> PASS   -> Human / END
+--> REVISE -> Writer
+--> REJECT -> END

Trust Boundaries

The data model also encodes trust levels.

External/untrusted

search-provider response
URLs
webpage HTML/text

These require validation and preparation.

Model-proposed

ScoutAction
ScoutSelection
OpportunitySignals
ResearchAction
ResearchBriefSynthesis
Writer output
Quality semantic output

These require schema validation and, where operationally relevant, deterministic interpretation.

Application-authoritative

authorized URL state
visited/read source state
weighted opportunity score
guardrail result
counters
token budgets
workflow iteration
routing
validated provenance

These belong to deterministic code.

Human-authoritative

publication decision

Data Invariants

The current architecture depends on the following invariants:

A SELECT cannot legitimize content that was never read.

A READ cannot target an unauthorized arbitrary URL.

A SearchResult is not automatically evidence.

A ReadSource is not automatically EvidenceItem.

Evidence must preserve source provenance.

Opportunity semantic signals do not directly own routing.

The final opportunity classification is deterministic.

External content must pass through bounded context preparation.

Research cannot grow stored read context without limit.

Writer does not own research provenance.

Quality Evaluation does not replace Opportunity Evaluation.

REVISE does not automatically rerun Research.

Workflow iteration is bounded.

The human retains publication authority.

These invariants are more important than any individual field name because they define the safety and responsibility boundaries between contracts.

Current Model Gaps

The current data model does not yet fully solve:

multiple active opportunities
candidate ranking / queue persistence
reliable LinkedIn engagement metadata
production chronological action/observation telemetry
cost telemetry per decision/tool/model
production deployment/runtime metadata
human approval persistence
long-term outcome/feedback learning records

These should be added only when the corresponding capability is designed.

They should not be guessed into the schema prematurely.

Evolution Rules

When changing a schema or state contract:

identify the component that owns the data;

identify every producer and consumer;

preserve semantic vs deterministic responsibility;

preserve provenance where factual claims are involved;

avoid exposing global state merely for convenience;

update routing if the new field changes operational behavior;

update tests before considering the contract stable;

update 02_current_architecture.md when runtime topology changes;

update this document when the data boundary itself changes;

record material architectural rationale in 04_decision_log.md.

Summary

The system's data model is designed around a chain of increasingly validated artifacts:

external observation
|
v
normalized tool result
|
v
bounded agent state
|
v
validated candidate
|
v
semantic opportunity signals
|
v
deterministic opportunity decision
|
v
authorized research state
|
v
provenanced evidence
|
v
ResearchBrief
|
v
structured draft
|
v
structured quality evaluation
|
v
human decision

The central rule is:

LLMs may propose and interpret; authoritative state is validated, bounded, and moved through explicit contracts.
