Project Context

Product Goal

Build an agentic AI system that identifies relevant LinkedIn

interaction opportunities, gathers supporting evidence, writes

comments aligned with Rodrigo's professional voice, evaluates

quality, and keeps a human in control of publication.

The system is intended to support strategic professional interaction,

not autonomous social-media engagement.

Human publication authority is mandatory.

Baseline Lineage

Previous committed checkpoint:

6f3ebbe

Commit description:

feat: integrate research and writer into opportunity workflow

The development increment documented in this file was built on top of

that checkpoint.

This file is intended to be committed together with the validated

increment described below.

The commit containing this validated state becomes the next recoverable

development checkpoint.

Last Completed Development Increment

The current completed and validated increment introduces:

Quality Evaluator Integration v0.1

This increment connects the previously validated Quality Evaluator to the active HIGH-opportunity LangGraph path after Writer, establishing the first bounded end-to-end quality path across Scout, Opportunity Evaluation, Research, Writer, and Quality Evaluator.

Research Capability v0.1 and its structured ResearchBrief → Writer boundary remain preserved. The validated HIGH path now executes Research, produces a grounded draft, evaluates that draft, and applies deterministic PASS / REVISE / REJECT routing. REVISE returns to Writer without rerunning Research and remains bounded by the existing iteration limit.

The validated Research action vocabulary is:

SEARCH
READ
EXTRACT
FINISH

The complete project test suite currently passes:

150 passed

Real-LLM smoke validation also passed and demonstrated conservative INSUFFICIENT termination when available evidence did not fully support the research objective.

Current Active LangGraph Workflows

The project currently preserves three compiled LangGraph workflows.

Content Workflow

The existing Writer / Quality Evaluator workflow remains:

START
↓
Writer
↓
Quality Evaluator

Quality Evaluator routing:

PASS → Human / END
REVISE → Writer
REJECT → END

Revision loops remain bounded by a maximum iteration limit.

Opportunity Workflow

Opportunity Evaluation is now integrated into a dedicated controlled
LangGraph workflow:

START
↓
Opportunity Evaluator
↓
Controlled Routing
├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT
├── MEDIUM → QUEUED → END
└── LOW → END

The Opportunity Evaluator receives a validated PostCandidate, performs
semantic evaluation through the LLM, applies deterministic Python
scoring and guardrails, stores the resulting OpportunityEvaluation in
workflow state, and routes according to the final classification.

HIGH now executes the bounded Research capability and then passes the resulting structured ResearchBrief to Writer.

MEDIUM is preserved as a distinct queued state.

LOW terminates the Opportunity Workflow.

Scout remains internally implemented as a bounded Python agent loop.

It is now connected to Opportunity Evaluation through a dedicated
LangGraph integration workflow while preserving the standalone
Opportunity Workflow.

Scout → Opportunity Workflow

Scout is now integrated with Opportunity Evaluation through a dedicated
compiled LangGraph workflow:

START
↓
Scout
↓
Scout Routing
├── no candidate → END
└── one candidate
↓
Opportunity Evaluator
↓
Controlled Routing
├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT
├── MEDIUM → QUEUED → END
└── LOW → END

The Scout itself remains a bounded Python agent loop. LangGraph does not
replace its internal perceive → decide → act → observe loop; instead,
scout_node adapts the Scout result into shared workflow state.

The current integration contract is deliberately narrow:

zero candidates → NO_CANDIDATE_FOUND → END;

exactly one candidate → Opportunity Evaluation;

more than one candidate → explicit ValueError.

The multi-candidate case remains unresolved by design. The system must
not silently choose a first candidate, invent ranking logic, or encode a
queueing policy without an explicit architectural decision.

Planned Workflow Direction

The target system direction remains:

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

This target is being implemented incrementally. Components must not be
described as integrated before the corresponding workflow boundary has
been implemented and validated.

Implemented Capabilities

Core Data Contracts

Implemented:

PostCandidate schema

OpportunitySignals schema

OpportunityEvaluation schema

ScoutAction schema

ScoutSelection schema

ScoutState schema

SearchResult schema

Writer structured output

Quality Evaluation structured output

Writer

Implemented:

Writer component

Rodrigo Voice prompt

structured Writer output

revision support through the controlled workflow

Quality Evaluator

Implemented:

semantic quality evaluation

structured quality signals

deterministic PASS / REVISE / REJECT decision

deterministic quality thresholds

controlled revision loop

bounded retries

isolated automated tests

integration into the active HIGH-opportunity workflow after Writer

PASS → Human / END routing

REVISE → Writer → Quality Evaluator bounded revision routing

REJECT → END routing

systemic tests confirming that REVISE does not rerun Research

Opportunity Evaluation v0.1

Implemented:

Opportunity Evaluation architecture and design

semantic evaluation contract

OpportunitySignals structured output

deterministic Research Efficiency calculation

deterministic weighted Opportunity Score

deterministic guardrails

deterministic HIGH / MEDIUM / LOW classification

isolated semantic evaluator

mocked semantic evaluation tests

deterministic scoring tests

boundary and guardrail tests

Opportunity Evaluation evaluates whether a discovered post represents

a strategically valuable opportunity for Rodrigo to contribute.

It does not evaluate whether the original post is simply good or
popular.

Opportunity Workflow Integration

Implemented:

opportunity_evaluator_node as the LangGraph adapter for semantic
evaluation and deterministic scoring;

deterministic HIGH / MEDIUM / LOW routing;

accepted_for_research_node state transition;

queued_opportunity_node state transition;

dedicated build_opportunity_workflow() graph;

systemic HIGH, MEDIUM, and LOW workflow-path tests;

preservation of the existing Writer / Quality Evaluator workflow.

HIGH opportunities now execute Research and then Writer in this workflow.

Scout → Opportunity Workflow Integration

Implemented:

scout_node as the explicit adapter between the bounded Scout runtime
and LinkedInAgentState;

scout_objective added to shared workflow state;

deterministic route_after_scout() routing;

dedicated build_scout_opportunity_workflow() graph;

automatic transfer of one validated PostCandidate from Scout into
Opportunity Evaluation;

explicit early termination when Scout finds no candidate;

prevention of unnecessary Opportunity Evaluation when no candidate
exists;

explicit failure when Scout returns multiple candidates because
multi-candidate ranking / queueing remains intentionally unresolved;

isolated Scout-node tests;

Scout-routing tests;

systemic Scout → Opportunity integration tests;

preservation of the standalone Opportunity Workflow and existing
Writer / Quality Evaluator workflow.

The validated integrated path is:

START
↓
Scout
↓
PostCandidate
↓
Opportunity Evaluator
↓
Controlled Routing
├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT
├── MEDIUM → QUEUED → END
└── LOW → END

If Scout returns no candidate:

Scout
↓
NO_CANDIDATE_FOUND
↓
END

Research and Writer are now executed for HIGH opportunities in this workflow.

Research Workflow + Writer Integration v0.1

Implemented and preserved:

research_node as the LangGraph adapter for the bounded Research runtime;

ResearchBrief added as the typed research_result contract in shared workflow state and WriterInput;

explicit ResearchBrief serialization for Writer-facing LLM context;

HIGH Opportunity routing extended from ACCEPTED_FOR_RESEARCH into Research and Writer;

systemic tests proving Opportunity → Research → Writer and Scout → Opportunity → Research → Writer;

preservation of MEDIUM → QUEUED and LOW → END behavior.

Quality Evaluator Integration v0.1

Implemented:

the existing Quality Evaluator is now connected after Writer in the integrated HIGH-opportunity workflow;

PASS terminates the automated quality path at the Human / END boundary;

REVISE returns only to Writer and then back to Quality Evaluator;

Research is not repeated during draft revision;

REJECT terminates the workflow;

the existing maximum iteration limit bounds the Writer ↔ Quality Evaluator revision loop;

systemic tests validate PASS, REVISE, REJECT, and revision-limit behavior;

Scout → Opportunity Evaluation → Research → Writer → Quality Evaluator is validated as an integrated path;

MEDIUM → QUEUED and LOW → END behavior remains preserved.

The current integrated HIGH path is:

START
↓
Scout / Opportunity Evaluation
↓
HIGH
↓
ACCEPTED_FOR_RESEARCH
↓
Research
↓
ResearchBrief
↓
Writer
↓
Quality Evaluator
├── PASS → Human / END
├── REVISE → Writer → Quality Evaluator
└── REJECT → END

The revision loop remains bounded by the existing iteration limit, and REVISE does not rerun Research.

Research Capability v0.1

Research exists to transform an approved opportunity into the minimum evidence package required for the Writer to produce a relevant, factual, and defensible contribution. It is evidence-oriented rather than topic-oriented and must not become unrestricted autonomous browsing.

Research Contract

Implemented typed contracts include:

ResearchObjective;

ResearchAction;

EvidenceItem;

ReadSource;

ResearchState;

ResearchBriefSynthesis;

ResearchBrief;

ResearchStatus.

The bounded runtime follows:

PostCandidate + OpportunityEvaluation
↓
ResearchObjective
↓
LLM semantic action decision
↓
Python authorization / guardrails
↓
SEARCH / READ / EXTRACT / FINISH
↓
ResearchState
↓
ResearchBrief

Evidence Promotion Boundary

The established evidence chain is:

SEARCH → READ → EXTRACT → EvidenceItem → ResearchBrief

SEARCH discovers candidate sources. READ creates raw observations. EXTRACT is the explicit promotion boundary from observation to evidence. Only extracted EvidenceItem objects may support factual findings in the final brief. Raw read content and search snippets cannot bypass EXTRACT and become Writer-facing factual claims.

Search results are deduplicated deterministically by URL.

Semantic vs Deterministic Ownership

The LLM owns semantic tasks where interpretation is required: creating the narrow research objective, selecting the next permitted action, extracting evidence, judging whether the objective is semantically sufficient or insufficient, and synthesizing Writer-facing summary fields.

Python owns operational authorization, provenance checks, counters, limits, terminal runtime limits, factual state, and final brief assembly.

ResearchBriefSynthesis is restricted to:

summary;

key_findings;

counterpoints;

unresolved_questions.

Python copies research_objective, evidence, sources, and status directly from terminal ResearchState into ResearchBrief.

Research Termination

Semantic FINISH may request only:

SUFFICIENT;

INSUFFICIENT.

LIMIT_REACHED remains runtime-owned. FINISH does not mean success. Partial evidence is not equivalent to sufficient evidence. A SUFFICIENT finish without extracted evidence is rejected.

Local action budgets block only the exhausted action and allow bounded recovery through another valid action. Global operational or decision limits terminate the run with LIMIT_REACHED. decision_attempts counts valid and invalid LLM decisions so repeated invalid requests cannot create an unbounded loop.

Current bounds are:

MAX_RESEARCH_STEPS = 10
MAX_RESEARCH_DECISIONS = 12
MAX_RESEARCH_SEARCHES = 3
MAX_RESEARCH_READS = 5
MAX_RESEARCH_EVIDENCE_ITEMS = 6

Research Validation Status

Research v0.1 has been validated through deterministic automated tests and real OpenAI smoke runs against the current deterministic fake web environment. The latest smoke correctly produced extracted evidence while terminating INSUFFICIENT because the evidence did not establish the stronger requested claim.

Research web search and reading remain fake/deterministic. The capability validates agent mechanics, evidence boundaries, and semantic behavior; it is not yet production web research.

Opportunity Evaluation Principle

The central product rule is:

Opportunity != Popularity

The system should prioritize situations where Rodrigo can make a

relevant, differentiated, and professionally valuable contribution.

Audience size and engagement matter, but must not dominate:

contribution potential;

professional positioning;

topic relevance.

Opportunity Evaluation v0.1 Dimensions

The current scoring dimensions are:

Contribution Potential

Positioning Fit

Topic Relevance

Engagement Potential

Research Cost

All conceptual scores use the range:

0–100

Opportunity Evaluation v0.1 Weights

The approved initial weights are:

Contribution Potential = 30%

Positioning Fit = 25%

Topic Relevance = 20%

Engagement Potential = 15%

Research Efficiency = 10%

Where:

Research Efficiency = 100 - Research Cost

Opportunity Score Formula

The deterministic Opportunity Score is:

Opportunity Score =

Contribution Potential × 0.30
Positioning Fit × 0.25

Topic Relevance × 0.20

Engagement Potential × 0.15

Research Efficiency × 0.10

Opportunity Guardrails

The current deterministic guardrails are:

Contribution Potential < 30

→ LOW

Positioning Fit < 30

→ LOW

Topic Relevance < 25

→ LOW

A triggered guardrail forces LOW classification regardless of the

weighted Opportunity Score.

Opportunity Classification

If no guardrail is triggered:

HIGH

score >= 80

MEDIUM

score >= 60 and < 80

LOW

score < 60

These weights, thresholds, and guardrails are v0.1 product hypotheses.

They are approved for initial use but should eventually be calibrated

using real opportunities and observed outcomes.

Semantic vs Deterministic Responsibility

Opportunity Evaluation deliberately separates semantic interpretation

from operational decision ownership.

The current pattern is:

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

The LLM currently evaluates:

topic_relevance

positioning_fit

contribution_potential

research_cost

The LLM must not own:

final Opportunity Score

final HIGH / MEDIUM / LOW classification

Those decisions remain deterministic Python responsibilities.

Engagement Potential Status

Engagement Potential remains intentionally separate from

OpportunitySignals.

The semantic LLM must not invent objective engagement metrics.

The intended future data path is:

Scout / Metadata Collection

↓

Objective Engagement Signals

↓

Deterministic Engagement Calculation

Potential objective signals include:

reaction_count

comment_count

published_at

post age

reaction velocity

comment velocity

author reach, when reliably available

The exact Engagement Potential formula remains unresolved.

For the current systemic Opportunity Workflow validation, the graph node
temporarily uses:

DEFAULT_ENGAGEMENT_POTENTIAL = 50

This is a neutral placeholder for workflow testing, not a production
engagement formula or an observed metric.

No engagement formula should be silently invented before real Scout data
availability is validated.

Scout Agent v0.1

Scout v0.1 is now implemented as a bounded agentic loop.

Its objective is to discover potentially valuable professional

interaction opportunities.

The current Scout action vocabulary is:

SEARCH

READ

SELECT

FINISH

Scout Agent Architecture

The Scout follows the pattern:

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

The loop continues until:

FINISH

or:

max_steps

is reached.

Scout Semantic Autonomy

The LLM owns semantic next-action selection inside the permitted

action space.

Examples of decisions the LLM may make:

formulate a search query;

decide which discovered result appears worth reading;

decide whether the most recently read content should become a

candidate;

decide whether further exploration is useful.

The LLM does not control the runtime itself.

It can request actions only through the ScoutAction structured contract.

Scout Deterministic Guardrails

Python remains responsible for authorizing or rejecting requested
actions.

Current guardrails include:

SEARCH requires a query;

repeated search queries are rejected;

READ requires a URL;

READ may only access URLs returned by Scout search results;

previously visited URLs may not be revisited;

SELECT requires previously read content;

SELECT requires a structured ScoutSelection;

max_steps limits total agent iterations;

unsupported actions are rejected.

A blocked action raises a controlled ValueError.

The Scout runtime records the error in:

state.last_error

and allows the LLM to receive the updated state and attempt another

bounded decision.

Scout Candidate Selection

Scout can now promote previously read content into a PostCandidate.

The semantic decision belongs to the LLM:

"This content is worth selecting."

The factual construction belongs to Python.

The LLM does not invent the selected URL or reproduce the factual

content contract.

Current flow:

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

Scout Real-LLM Validation

Scout v0.1 has been manually executed using the real OpenAI API.

A real run successfully demonstrated autonomous semantic behavior

inside the bounded runtime.

The model independently:

formulated search queries;

refined search strategy;

selected a discovered result to read;

evaluated the observed content;

requested SELECT;

caused a validated PostCandidate to be created.

The successful real-agent run produced a candidate related to:

AI agents + Supply Chain

without a hardcoded action sequence.

Scout Tooling Status

Scout reasoning is real.

Scout web tools are not yet real.

Current implementations:

web_search

web_reader

are deterministic fake tools created specifically to isolate and

validate the agent mechanics.

The fake search tool currently returns the same predefined results

regardless of the search query.

Therefore:

Agentic decision behavior = REAL

Web discovery environment = FAKE / DETERMINISTIC

The current implementation must not be described as a production

LinkedIn discovery capability.

Scout Known Limitations

The following limitations are intentionally known:

Fake Web Environment

The current web_search implementation ignores the actual query and

returns predefined SearchResult objects.

The current web_reader reads predefined content.

Candidate Metadata

Current fake search results do not provide complete real LinkedIn

metadata.

For the current isolated implementation:

author_name = "Unknown"

is used rather than allowing the LLM to invent author identity.

Action History

ScoutState currently preserves operational state but does not maintain

a complete chronological action / observation trace.

The final state may show:

search queries;

visited URLs;

current search results;

latest read content;

selected candidates;

latest recoverable error;

number of steps;

but it does not yet provide a complete ordered execution history.

Termination

The Scout can finish through:

FINISH

or by reaching:

max_steps

Real test runs have demonstrated max_steps termination.

The runtime must remain bounded.

Agent Definition Established During This Increment

The project uses the following architectural understanding:

Agent =

LLM

objective

state

actions

tools

decision loop

guardrails

An LLM alone is not an agent.

A deterministic loop alone is not semantic agent autonomy.

Agentic behavior emerges from combining semantic decision-making with

controlled executable capabilities and operational constraints.

Current Scout Loop Technology

The internal Scout loop is currently implemented directly in Python.

It is not currently implemented as a LangGraph subgraph.

This was intentional so that the fundamental agent mechanics remain

explicit and understandable:

perceive

→ decide

→ act

→ observe

→ update state

→ decide again

LangGraph remains part of the broader system architecture and may

later organize Scout or multi-agent orchestration when doing so adds

clear value.

Current Test Baseline

Full project suite:

150 passing tests

The suite covers the previously established Writer, Quality Evaluator, Opportunity Evaluation, Scout, routing, and workflow contracts plus Research v0.1 schemas, SEARCH / READ / EXTRACT / FINISH behavior, provenance guardrails, local action-budget recovery, global step and decision limits, semantic FINISH statuses, ResearchBrief trust boundaries, evidence-only synthesis, source deduplication, and bounded research-loop behavior.

Live OpenAI calls are not required by the automated test suite. LLM-facing tests use mocks where appropriate. Real OpenAI smoke validation is performed separately.

Current Development Status

The current development increment is:

IMPLEMENTED
TESTED
AUDITED
READY FOR CHECKPOINT COMMIT

Full test suite result:

150 passed

Project Context Snapshot integrity:

PASS

The automated audit confirmed that repository content remained stable during audit collection.

Current Development Objective

The current increment integrates the existing Quality Evaluator into the active HIGH-opportunity path after Writer. The integrated workflow now preserves the ResearchBrief → Writer typed boundary and continues from the resulting draft into semantic quality evaluation and deterministic PASS / REVISE / REJECT routing.

The validated integrated path is now:

Scout
↓
PostCandidate
↓
Opportunity Evaluation
↓
HIGH → ACCEPTED_FOR_RESEARCH
↓
Research
↓
ResearchBrief
↓
Writer
↓
Quality Evaluator
├── PASS → Human / END
├── REVISE → Writer → Quality Evaluator
└── REJECT → END

REVISE returns only to Writer; Research is not repeated. The revision loop remains bounded by the existing iteration limit.

Current WIP

Quality Evaluator Integration v0.1 is implemented, tested, and audited and is ready for checkpoint commit.

The current working tree contains the workflow routing changes and systemic integration tests required to connect Quality Evaluator to the integrated HIGH-opportunity path. No additional capability should be mixed into this checkpoint before commit.

Next Planned Capability

After this checkpoint commit, development should continue with:

Real Web Tooling v0.1 — Contract and Bounded Integration

The next increment should replace the current deterministic fake search/read environment with bounded real-world search and reading while preserving the already validated Scout and Research responsibility boundaries.

Concept and responsibility should be decided before code. The increment should explicitly define:

which real search mechanism Scout may use;

which real search mechanism Research may use;

which reading/fetch mechanism may access discovered URLs;

allowed source/domain behavior;

provenance requirements;

timeouts and external-tool failure handling;

rate, tool, and cost limits;

deduplication and content-size limits;

how failures are represented in agent state;

whether Scout and Research share infrastructure while retaining separate contracts;

mocked external-response tests before real-network smoke validation.

The objective is not unrestricted browsing. It is to make the existing bounded agents operate against real external information without weakening their current guardrails, evidence boundaries, or deterministic runtime ownership.

Opportunity Routing Direction

The current v0.1 routing behavior is established as:

HIGH
↓
ACCEPTED_FOR_RESEARCH
↓
Research
↓
Writer
↓
Quality Evaluator
↓
PASS / REVISE / REJECT

MEDIUM
↓
QUEUED
↓
END

LOW
↓
END

HIGH means the opportunity is approved to proceed into the integrated
Research → Writer → Quality Evaluator path.

MEDIUM opportunities remain distinct from LOW opportunities. They are
preserved in a lower-priority queued state without incurring Research
cost.

LOW opportunities terminate the Opportunity Workflow.

Research is already integrated for HIGH opportunities, and Quality Evaluator now follows Writer in that path.

The lifecycle of queued MEDIUM opportunities may be revisited later
using real operational evidence, but the current v0.1 routing behavior
is explicitly QUEUED.

Research Status

Research Capability v0.1 is implemented, tested, audited, and real-LLM smoke validated as a standalone bounded specialist capability.

Its responsibility is:

Given an approved opportunity,
gather and promote the minimum evidence required
to produce a factual and defensible contribution.

Research now executes after HIGH Opportunity Evaluation and passes its structured ResearchBrief to Writer. Its web environment remains fake/deterministic until real search and reading tools are explicitly designed and validated.

Architectural Principles

The following principles are established:

Human-in-the-loop is mandatory before publication.

The system must never publish autonomously.

Agent autonomy must remain bounded.

Prefer deterministic decisions where deterministic logic provides

sufficient reliability.

Use LLM reasoning where semantic understanding adds material value.

Use structured outputs between AI components.

Keep explicit workflow state.

Bound retries, revisions, and agent exploration.

Deterministic application code owns operational guardrails.

LLMs may propose actions but cannot bypass runtime authorization.

Objective factual data should not be invented by an LLM.

Separate semantic interpretation from deterministic decision logic.

Preserve component responsibility boundaries.

Treat LLM consumption as computational infrastructure.

Apply cost-aware orchestration and token governance.

Reserve expensive/frontier models for high-value reasoning.

Prefer cheaper models or deterministic logic where quality

requirements can still be satisfied.

Add complexity only when it provides clear behavioral or product

value.

Cost-Aware Orchestration

LLM consumption is treated as infrastructure cost.

The orchestration layer should eventually consider not only:

Which component should run?

but also:

Which model is appropriate for this task?

The target optimization principle is:

Minimum inference cost capable of satisfying the required Quality

Contract.

Frontier models should be reserved for reasoning tasks where their

additional capability materially improves the result.

Deterministic logic and cheaper models should be preferred where they

can satisfy the requirement reliably.

Explicit Non-Goals

Current non-goals include:

autonomous LinkedIn publication;

autonomous LinkedIn commenting;

unbounded web browsing;

unbounded agent loops;

unbounded agent-to-agent delegation;

letting an LLM bypass deterministic guardrails;

using an LLM for decisions that can be reliably deterministic;

inventing objective engagement data;

claiming the current fake Scout tools perform real LinkedIn
discovery;

prematurely optimizing Opportunity Evaluation weights without data;

implementing unrelated platform capabilities before the core
workflow

becomes operational;

building large infrastructure layers without a demonstrated need.

Established Product Decisions

Human Authority

Humans retain final publication authority.

No component may autonomously publish.

Opportunity Evaluation

Opportunity means strategic professional contribution potential, not

simple popularity.

Contribution Potential receives the highest current scoring weight.

Final Opportunity Decision

The LLM does not own final HIGH / MEDIUM / LOW classification.

Python owns:

Research Efficiency;

weighted Opportunity Score;

mandatory guardrails;

final classification.

Scout

Scout has bounded semantic autonomy.

The LLM chooses among allowed actions.

Python authorizes execution.

Tools perform the actual external or simulated operation.

State records observations.

max_steps limits exploration.

Scout → Opportunity Integration

The integration boundary between Scout and Opportunity Evaluation is now
established.

scout_node owns adaptation from ScoutState into
LinkedInAgentState.

The current v0.1 cardinality contract is:

zero candidates → terminate without Opportunity Evaluation;

one candidate → continue to Opportunity Evaluation;

multiple candidates → fail explicitly.

This is a temporary boundary contract, not a final product rule for
multi-opportunity handling.

Opportunity Routing

Current v0.1 routing is deterministic:

HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT;

MEDIUM → QUEUED → END;

LOW → END.

ACCEPTED_FOR_RESEARCH records the approval transition and now leads directly into the integrated Research capability.

The later lifecycle of queued MEDIUM opportunities remains open to
calibration.

Structured Outputs

LLM boundaries should use typed structured outputs where practical.

Pydantic contracts are preferred for machine-to-machine AI component

communication.

Open Design Decisions

The following decisions remain intentionally unresolved:

How Scout will access real LinkedIn or web candidate sources.

Which real search mechanism will replace the deterministic fake

web_search tool.

Which real reading mechanism will replace the deterministic fake

web_reader tool.

How reliable LinkedIn metadata can be collected.

Whether reaction_count is consistently available.

Whether comment_count is consistently available.

Whether author follower counts are consistently available.

Exact Engagement Potential normalization.

Handling of missing engagement data.

Calibration of engagement velocity thresholds.

How queued MEDIUM opportunities should later be revisited,
prioritized, or promoted.

Whether Research SUFFICIENT, INSUFFICIENT, and LIMIT_REACHED should receive differentiated routing before Writer in a later hardening increment.

Which real search and reading tools should replace the deterministic fake Research environment.

Model selection per component.

Whether Opportunity semantic dimensions should remain in one LLM

call or be separated.

Long-term Opportunity Evaluation calibration methodology.

Whether measured token/tool cost should later influence Research

Cost.

Whether author relevance should become a separate evaluation

dimension.

Whether Scout should later become a LangGraph subgraph.

Whether ScoutState should include a complete action / observation

history.

How selected candidates should be deduplicated.

How multiple Scout candidates should be ranked or queued.

How the active workflow should represent multiple opportunities.

How production-grade observability should record agent decisions,

tool calls, costs, and failures.

These decisions must be resolved incrementally.

They must not be silently encoded into implementation without an

explicit architectural or product decision.

Context Maintenance Rule

Update this file whenever any of the following changes:

current development objective;

baseline lineage;

current WIP;

completed capability;

active workflow architecture;

planned workflow direction;

architectural principle;

frozen decision;

explicit non-goal;

test baseline;

next planned capability;

important known limitation.

Before each checkpoint commit:

complete the development increment;

run the full test suite and obtain approval;

run python app/scripts/project_audit.py;

validate the generated audit;

update this PROJECT_CONTEXT.md from the validated factual state;

review repository diff/status;

stage;

commit;

push.

The audit is the factual repository snapshot.

PROJECT_CONTEXT.md is the human-maintained interpretation of that

snapshot and should explain:

where the project came from

what is currently implemented

what remains intentionally incomplete

what decisions are established

what should happen next

The combination of:

code

tests

audit

PROJECT_CONTEXT.md

Git checkpoint

is the official development recovery mechanism for the project.