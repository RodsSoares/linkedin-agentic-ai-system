Project Context

Product Goal

Build an agentic AI system that identifies relevant LinkedIn

interaction opportunities, gathers supporting evidence, writes

comments aligned with Rodrigo's professional voice, evaluates

quality, and keeps a human in control of publication.

The system is intended to support strategic professional interaction,

not autonomous social-media engagement.

Human publication authority is mandatory.

Current Stable Baseline

Stable baseline commit:

156aa07

Commit description:

feat: integrate quality evaluator into opportunity workflow

The current Real Web Tooling / Context Preparation increment was developed on top of this committed baseline.

The working tree intentionally contains the validated implementation described below. The commit containing this increment will become the next recoverable stable baseline.

Baseline lineage remains:

156aa07
← 6f3ebbe
← 0594a3d
← acff344
← 0f842fa
← 23bdb7c
← 80bd89a

The official checkpoint mechanism remains code + tests + audit + PROJECT_CONTEXT.md + Git commit.

Last Completed Development Increment

The current completed and validated increment introduces:

Real Web Tooling v0.1 — Contract and Bounded Integration

together with:

Context Preparation v0.1 — Bounded LLM Input

and:

Main Content Extraction v0.2.1 — Content Density Extraction

This increment replaces the previously fake-only execution environment with a provider-neutral web-tool contract and an explicit runtime selector between deterministic fake tools and bounded real tools.

Implemented real infrastructure includes:

SearchTool: query → list[SearchResult]

ReadTool: url → str

Brave Search as the current real SEARCH adapter;

HTTP Reader as the current real READ adapter;

WEB_TOOL_MODE = fake | real;

WebToolError as the controlled external-tool failure boundary;

shared Scout / Research tool selection through get_web_tools();

timeouts, content-size bounds, redirect validation, URL-scheme validation, DNS resolution, private/non-global IP rejection, and redirect-target revalidation;

bounded context preparation using tiktoken;

per-read and cumulative Research token budgets;

Scout read-context token budgeting;

candidate deduplication for repeated SELECT of the same source;

semantic main-content preference for article/main;

deterministic density-based extraction fallback for section/div pages;

boilerplate suppression for navigation, headers, footers, scripts, forms, sidebars, and related non-editorial structures.

The core architecture remains:

LLM interprets and decides semantically;
Python governs execution and limits;
LangGraph governs workflow.

The complete automated project test suite currently passes:

189 passing tests

Real-network smoke validation also passed.

Scout real smoke:

STATUS = FINISHED
LAST_ERROR = None
CANDIDATE_COUNT = 1
POST_TOKENS = 1800

The real Scout discovered and read:

https://www.scmr.com/article/how-agentic-ai-changes-supply-chain-operations

Main-content extraction began directly in editorial content rather than site navigation / boilerplate.

Research real smoke:

NODE_STATUS = RESEARCH_COMPLETED
BRIEF_STATUS = SUFFICIENT
SOURCE_COUNT = 5
EVIDENCE_COUNT = 2

The Research agent used real web search/read infrastructure, extracted evidence from authoritative NIST AI Risk Management Framework resources, preserved provenance, produced counterpoints and unresolved questions, and explicitly distinguished general governance evidence from supply-chain-specific interpretation.

The previous Quality Evaluator Integration v0.1, Research Capability v0.1, ResearchBrief → Writer typed boundary, bounded Writer revision loop, and Human publication boundary remain preserved.

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

Research v0.1 is implemented and validated through deterministic automated tests, real OpenAI semantic execution, and bounded real-web smoke validation.

Research now operates against either:

fake deterministic tools for automated tests and controlled development;

or:

real Brave Search + HTTP Reader tools when WEB_TOOL_MODE=real.

The evidence-promotion boundary remains unchanged:

SEARCH → READ → EXTRACT → EvidenceItem → ResearchBrief

Only extracted EvidenceItem objects may support Writer-facing factual findings.

Real Research smoke validation completed successfully with:

RESEARCH_COMPLETED;

SUFFICIENT;

5 discovered sources;

2 extracted evidence items;

authoritative NIST governance sources;

counterpoints;

unresolved questions;

explicit qualification where the evidence was general AI-governance guidance rather than a supply-chain-specific rule.

The smoke demonstrated that real web access did not weaken the established evidence, provenance, or bounded-runtime contracts.

Real Web Tooling v0.1

The shared web-tool boundary is now implemented.

Provider-neutral contracts:

SearchTool = Callable[[str], list[SearchResult]]

ReadTool = Callable[[str], str]

Runtime modes:

fake → deterministic web_search / web_reader

real → Brave Search / HTTP Reader

The mode selector is centralized in get_web_tools().

Real SEARCH behavior:

uses Brave Search API;

validates non-empty and provider-bounded queries;

uses timeout protection;

maps provider responses into SearchResult;

wraps infrastructure failures as WebToolError.

Real READ behavior:

accepts only http/https URLs;

rejects localhost, private, reserved, or otherwise non-global targets;

resolves DNS before execution;

revalidates redirect targets;

bounds redirects;

requires text-compatible content;

bounds response size;

uses timeout protection;

wraps external HTTP failures as WebToolError.

Scout and Research catch only the controlled WebToolError boundary for recoverable external-tool failures. Arbitrary programming errors are not silently converted into web failures.

Context Preparation v0.1

External text is normalized before entering bounded LLM-facing state.

The current preparation layer:

collapses redundant whitespace;

removes exact duplicate lines while preserving first occurrence/order;

counts tokens with tiktoken;

applies hard token-level truncation;

records original token count, prepared token count, and truncation status.

Current configured budgets:

Scout READ context maximum = 1800 tokens;

Research READ context maximum = 2500 tokens per successful read;

Research total stored READ context maximum = 8000 tokens.

These are runtime-owned limits. The LLM may not override them.

Main Content Extraction v0.2.1

HTML reading now prefers semantic article content, then main content.

When semantic containers are unavailable, deterministic density scoring evaluates section/div candidates using content length, paragraph density, heading density, link ratio, list density, semantic hints, and boilerplate hints.

Ignored boilerplate containers include:

aside;
form;
footer;
head;
header;
nav;
noscript;
script;
style.

The semantic article/main path intentionally bypasses the generic density minimum so valid short editorial containers are not discarded.

Real Scout smoke against SCMR confirmed that the extracted content began with the article authors/date and key takeaways rather than site navigation.

Automated extraction coverage includes semantic article/main priority, nested boilerplate removal, body fallback, density selection, navigation penalties, and unchanged non-HTML text.

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

Scout tooling now supports both deterministic fake execution and bounded real-web execution.

Current runtime selector:

WEB_TOOL_MODE=fake
→ web_search + web_reader

WEB_TOOL_MODE=real
→ brave_search + http_reader

The fake mode remains the automated-test default so pytest does not depend on live network access.

The real mode has been manually smoke validated.

A real Scout run independently:

formulated a search query;

used Brave Search;

selected a discovered SCMR source;

read the source through the bounded HTTP Reader;

received main-content extraction rather than navigation boilerplate;

prepared the external content under the Scout token budget;

selected exactly one candidate;

terminated FINISHED with no final error.

Therefore:

Agentic decision behavior = REAL

Real web search/read capability = IMPLEMENTED AND SMOKE VALIDATED

Automated-test web environment = FAKE / DETERMINISTIC BY DEFAULT

This does not imply unrestricted browsing or production-grade LinkedIn-native discovery.

Scout Known Limitations

The following limitations remain intentionally known:

LinkedIn-native access

Real Web Tooling v0.1 provides bounded public web search/read capability. It does not yet establish a dedicated LinkedIn API, authenticated LinkedIn browsing, or guaranteed access to LinkedIn post content.

Candidate Metadata

Reliable real-world LinkedIn metadata is not yet established.

Reaction count, comment count, author reach, publication age, and related engagement metadata are not yet guaranteed inputs.

For sources where author identity is unavailable, the system must continue to avoid inventing identity.

Search / Reader Accessibility

Public pages may reject automated reading, return 403 responses, require JavaScript rendering, or expose structures the current deterministic HTML extractor cannot fully interpret.

WebToolError allows Scout to recover from supported external-tool failures, but it does not guarantee every discovered source is readable.

Main Content Extraction

The current semantic + density heuristic is validated against automated fixtures and successful real smoke pages, but it remains a deterministic heuristic rather than a general browser-rendering engine.

Action History

ScoutState preserves operational state but does not yet maintain a complete chronological action / observation trace.

The final state may show:

search queries;

visited URLs;

current search results;

latest prepared read content;

selected candidates;

latest recoverable error;

number of steps;

but it does not yet provide a complete ordered execution history.

Termination

Scout remains bounded by FINISH and max_steps.

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

189 passing tests

The suite covers Writer, Quality Evaluator, Opportunity Evaluation, Scout, Research, routing, workflow integration, web-tool selection, Brave Search mapping and failures, HTTP Reader security and content limits, controlled WebToolError recovery, context preparation, Scout/Research token guards, candidate deduplication, semantic main-content extraction, content-density extraction, and the previously established ResearchBrief / Writer / evaluator contracts.

Live network calls are not required by pytest. External providers are mocked or replaced with deterministic fakes in automated tests.

Real-network and real-LLM validation are performed separately as controlled smoke tests.

Current Development Status

The current development increment is:

IMPLEMENTED
TESTED
REAL-WEB SMOKE VALIDATED
AUDITED
READY FOR CONTEXT REFRESH AND CHECKPOINT COMMIT

Current automated test baseline:

189 passing tests

Project Context Snapshot integrity from the pre-context-update audit:

PASS

The audit confirmed repository content remained stable during collection.

The audit also correctly reported context-consistency warnings because PROJECT_CONTEXT.md still described the previous 150-test / fake-web checkpoint. This file update resolves that semantic-context drift before the final audit is generated.

Current Development Objective

Close Real Web Tooling v0.1, Context Preparation v0.1, and Main Content Extraction v0.2.1 as one recoverable checkpoint without weakening the already validated agent boundaries.

The functional objective has been achieved:

Scout can discover and read real public web content through bounded tools;

Research can gather real evidence through the same provider-neutral tooling boundary;

external content is bounded before entering LLM-facing state;

recoverable web failures are represented explicitly;

security and operational limits remain Python-owned;

Research provenance and EXTRACT evidence promotion remain intact;

the integrated HIGH-opportunity workflow architecture remains unchanged.

The current validated integrated path remains:

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

WEB_TOOL_MODE determines whether Scout and Research use fake or real web infrastructure; it does not change workflow responsibility boundaries.

Current WIP

Real Web Tooling v0.1, Context Preparation v0.1, and Main Content Extraction v0.2.1 are implemented, covered by the 189-test automated suite, and separately validated through real Scout and real Research smoke runs.

The remaining work for this increment is checkpoint hygiene only:

keep WEB_TOOL_MODE=fake as the normal deterministic development/test default;

confirm .env remains ignored by Git;

refresh PROJECT_CONTEXT.md to this factual state;

rerun project_audit.py;

verify context consistency and snapshot integrity;

review git diff / git status;

stage;

commit;

push.

No additional product capability should be mixed into this checkpoint.

Next Planned Capability

After this checkpoint commit, development should continue with:

End-to-End Real Workflow Validation v0.1 — Controlled Live Path

The next increment should validate the already integrated architecture under explicit real-web mode rather than immediately adding another large capability.

Target controlled path:

Scout real search/read
↓
Opportunity Evaluation
↓
HIGH
↓
Research real search/read
↓
ResearchBrief
↓
Writer
↓
Quality Evaluator
↓
Human / END boundary

The objective is to validate composition, not to loosen autonomy.

The increment should capture:

whether the complete real path terminates correctly;

whether real Scout content produces a coherent OpportunityEvaluation;

whether Research remains evidence-grounded on the live path;

whether Writer receives the exact structured ResearchBrief;

whether Quality Evaluator routing remains bounded;

where real latency, token use, source accessibility, and provider failures appear across the complete path.

No autonomous publication should be introduced.

After controlled end-to-end validation, later work can address real candidate metadata / engagement signals, multi-candidate handling, observability, and product-facing Human-in-the-loop experience.

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

Research Capability v0.1 remains a bounded specialist capability with real semantic execution and optional real-web infrastructure.

Its responsibility remains:

Given an approved opportunity,
gather and promote the minimum evidence required
to produce a factual and defensible contribution.

Research executes after HIGH Opportunity Evaluation and passes its structured ResearchBrief to Writer.

Its web environment is now selectable:

fake/deterministic for automated testing;

real Brave Search + HTTP Reader for controlled live execution.

Real Research smoke validation completed successfully with SUFFICIENT status, five discovered NIST sources, and two promoted EvidenceItem objects.

The smoke preserved the architectural distinction between sourced evidence and interpretation: the resulting brief explicitly stated when governance guidance was general rather than a supply-chain-specific rule.

Current bounded Research limits remain:

MAX_RESEARCH_STEPS = 10

MAX_RESEARCH_DECISIONS = 12

MAX_RESEARCH_SEARCHES = 3

MAX_RESEARCH_READS = 5

MAX_RESEARCH_EVIDENCE_ITEMS = 6

RESEARCH_READ_CONTEXT_MAX_TOKENS = 2500

RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS = 8000

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

How reliable LinkedIn-native candidate content and metadata can be collected.

Whether reaction_count is consistently available.

Whether comment_count is consistently available.

Whether author follower counts are consistently available.

Exact Engagement Potential normalization.

Handling of missing engagement data.

Calibration of engagement velocity thresholds.

How queued MEDIUM opportunities should later be revisited, prioritized, or promoted.

Whether Research SUFFICIENT, INSUFFICIENT, and LIMIT_REACHED should receive differentiated routing before Writer in a later hardening increment.

Whether Brave Search remains the long-term search provider or should become one provider behind a broader adapter layer.

Whether HTTP Reader should later be complemented by a browser-rendered reader for JavaScript-heavy or anti-bot pages.

How source credibility / authority should eventually influence Research decisions beyond the current semantic judgment.

Model selection per component.

Whether Opportunity semantic dimensions should remain in one LLM call or be separated.

Long-term Opportunity Evaluation calibration methodology.

Whether measured token/tool cost should later influence Research Cost.

Whether author relevance should become a separate evaluation dimension.

Whether Scout should later become a LangGraph subgraph.

Whether ScoutState should include a complete action / observation history.

How multiple distinct Scout candidates should be ranked or queued.

How the active workflow should represent multiple opportunities.

How production-grade observability should record agent decisions, tool calls, token usage, latency, cost, and failures.

How real LinkedIn engagement or publication should be integrated while preserving mandatory human publication authority.

These decisions must be resolved incrementally.

They must not be silently encoded into implementation without an explicit architectural or product decision.

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