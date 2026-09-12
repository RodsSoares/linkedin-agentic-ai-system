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

753df83

Commit description:

feat: validate real end-to-end agent workflow

This committed baseline includes the completed End-to-End Real Workflow Validation v0.1 checkpoint and all preceding capabilities, including Real Web Tooling v0.1, Context Preparation v0.1, Main Content Extraction v0.2.1, Opportunity Evaluation, bounded Scout, Research, Writer, Quality Evaluator, and the mandatory Human / END publication boundary.

The current Interaction Memory v0.1 — Persistent Discovery History / Scout Integration increment was developed on top of this committed baseline.

The working tree intentionally contains the validated Interaction Memory implementation, calibration artifact, regression protection, and context/checkpoint material described below. The commit containing this increment will become the next recoverable stable baseline.

Recent baseline lineage:

753df83 ← 3ce9349 ← 12c290d ← bc608e6 ← 156aa07 ← 6f3ebbe ← 0594a3d ← acff344 ← 0f842fa ← 23bdb7c ← 80bd89a

The official checkpoint mechanism remains code + tests + audit + PROJECT_CONTEXT.md + Git commit.

Last Completed Development Increment

The current completed and validated increment is:

End-to-End Real Workflow Validation v0.1 — Controlled Live Path

Purpose:

Validate the already integrated architecture as one live composition under explicit real-web mode, without adding autonomous publication or loosening existing guardrails.

Validated live path:

Scout real search/read ↓ PostCandidate ↓ Opportunity Evaluation ↓ HIGH ↓ Research real search/read ↓ ResearchBrief ↓ Writer ↓ Quality Evaluator ↓ Human / END boundary

Controlled E2E result:

WEB_TOOL_MODE = real

Scout selected a current public supply-chain / agentic-AI article through real Brave Search + bounded HTTP Reader.

Opportunity Evaluation produced:

topic_relevance = 96 positioning_fit = 94 contribution_potential = 81 engagement_potential = 50 research_cost = 27 research_efficiency = 73 opportunity_score = 81.8 classification = HIGH

Research completed with:

status = SUFFICIENT

The ResearchBrief contained a bounded research objective, summary, key findings, promoted EvidenceItem objects, counterpoints, unresolved questions, and discovered sources. Evidence included authoritative NIST AI RMF governance material plus operational examples for bounded automation.

Writer produced a grounded contribution from the structured ResearchBrief.

Quality Evaluator produced:

factual_accuracy = 97 relevance = 99 voice_match = 97 decision = PASS

The final workflow state reached the existing human-publication boundary with no autonomous publication.

Observed live elapsed time for the successful run:

84.88 seconds

Integration defect discovered during controlled E2E:

EvaluatorInput still expected research_result as dict | None while the shared workflow correctly supplied a typed ResearchBrief.

The defect appeared only when the complete live path reached Quality Evaluator, demonstrating that isolated and mocked tests had not fully protected this cross-capability boundary.

Implemented fix:

EvaluatorInput now accepts:

ResearchBrief | None

The typed ResearchBrief remains intact across workflow state and node boundaries. Serialization occurs only at the LLM prompt boundary inside the Evaluator component.

Regression protection added:

test_evaluator_input_accepts_typed_research_brief

The complete automated project test suite now passes:

190 passing tests

The previous Real Web Tooling v0.1, Context Preparation v0.1, Main Content Extraction v0.2.1, Quality Evaluator Integration v0.1, Research Capability v0.1, ResearchBrief → Writer typed boundary, bounded Writer revision loop, and Human publication boundary remain preserved.

The core architecture remains:

LLM interprets and decides semantically; Python governs execution and limits; LangGraph governs workflow.

Current Active LangGraph Workflows

The project currently preserves three compiled LangGraph workflows.

Content Workflow

The existing Writer / Quality Evaluator workflow remains:

START ↓ Writer ↓ Quality Evaluator

Quality Evaluator routing:

PASS → Human / END REVISE → Writer REJECT → END

Revision loops remain bounded by a maximum iteration limit.

Opportunity Workflow

Opportunity Evaluation is now integrated into a dedicated controlled LangGraph workflow:

START ↓ Opportunity Evaluator ↓ Controlled Routing ├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT ├── MEDIUM → QUEUED → END └── LOW → END

The Opportunity Evaluator receives a validated PostCandidate, performs semantic evaluation through the LLM, applies deterministic Python scoring and guardrails, stores the resulting OpportunityEvaluation in workflow state, and routes according to the final classification.

HIGH now executes the bounded Research capability and then passes the resulting structured ResearchBrief to Writer.

MEDIUM is preserved as a distinct queued state.

LOW terminates the Opportunity Workflow.

Scout remains internally implemented as a bounded Python agent loop.

It is now connected to Opportunity Evaluation through a dedicated LangGraph integration workflow while preserving the standalone Opportunity Workflow.

Scout → Opportunity Workflow

Scout is now integrated with Opportunity Evaluation through a dedicated compiled LangGraph workflow:

START ↓ Scout ↓ Scout Routing ├── no candidate → END └── one candidate ↓ Opportunity Evaluator ↓ Controlled Routing ├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT ├── MEDIUM → QUEUED → END └── LOW → END

The Scout itself remains a bounded Python agent loop. LangGraph does not replace its internal perceive → decide → act → observe loop; instead, scout_node adapts the Scout result into shared workflow state.

The current integration contract is deliberately narrow:

zero candidates → NO_CANDIDATE_FOUND → END;

exactly one candidate → Opportunity Evaluation;

more than one candidate → explicit ValueError.

The multi-candidate case remains unresolved by design. The system must not silently choose a first candidate, invent ranking logic, or encode a queueing policy without an explicit architectural decision.

Planned Workflow Direction

The target system direction remains:

Scout ↓ Opportunity Evaluation ↓ Research ↓ Writer ↓ Quality Evaluator ↓ Human-in-the-loop

This target is being implemented incrementally. Components must not be described as integrated before the corresponding workflow boundary has been implemented and validated.

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

It does not evaluate whether the original post is simply good or popular.

Opportunity Workflow Integration

Implemented:

opportunity_evaluator_node as the LangGraph adapter for semantic evaluation and deterministic scoring;

deterministic HIGH / MEDIUM / LOW routing;

accepted_for_research_node state transition;

queued_opportunity_node state transition;

dedicated build_opportunity_workflow() graph;

systemic HIGH, MEDIUM, and LOW workflow-path tests;

preservation of the existing Writer / Quality Evaluator workflow.

HIGH opportunities now execute Research and then Writer in this workflow.

Scout → Opportunity Workflow Integration

Implemented:

scout_node as the explicit adapter between the bounded Scout runtime and LinkedInAgentState;

scout_objective added to shared workflow state;

deterministic route_after_scout() routing;

dedicated build_scout_opportunity_workflow() graph;

automatic transfer of one validated PostCandidate from Scout into Opportunity Evaluation;

explicit early termination when Scout finds no candidate;

prevention of unnecessary Opportunity Evaluation when no candidate exists;

explicit failure when Scout returns multiple candidates because multi-candidate ranking / queueing remains intentionally unresolved;

isolated Scout-node tests;

Scout-routing tests;

systemic Scout → Opportunity integration tests;

preservation of the standalone Opportunity Workflow and existing Writer / Quality Evaluator workflow.

The validated integrated path is:

START ↓ Scout ↓ PostCandidate ↓ Opportunity Evaluator ↓ Controlled Routing ├── HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT ├── MEDIUM → QUEUED → END └── LOW → END

If Scout returns no candidate:

Scout ↓ NO_CANDIDATE_FOUND ↓ END

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

START ↓ Scout / Opportunity Evaluation ↓ HIGH ↓ ACCEPTED_FOR_RESEARCH ↓ Research ↓ ResearchBrief ↓ Writer ↓ Quality Evaluator ├── PASS → Human / END ├── REVISE → Writer → Quality Evaluator └── REJECT → END

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

PostCandidate + OpportunityEvaluation ↓ ResearchObjective ↓ LLM semantic action decision ↓ Python authorization / guardrails ↓ SEARCH / READ / EXTRACT / FINISH ↓ ResearchState ↓ ResearchBrief

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

MAX_RESEARCH_STEPS = 10 MAX_RESEARCH_DECISIONS = 12 MAX_RESEARCH_SEARCHES = 3 MAX_RESEARCH_READS = 5 MAX_RESEARCH_EVIDENCE_ITEMS = 6

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

aside; form; footer; head; header; nav; noscript; script; style.

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

Contribution Potential × 0.30 Positioning Fit × 0.25

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

↓ LLM Semantic Evaluation

↓ OpportunitySignals

↓ Python Deterministic Scoring

↓ Guardrails

↓ HIGH / MEDIUM / LOW

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

For the current systemic Opportunity Workflow validation, the graph node temporarily uses:

DEFAULT_ENGAGEMENT_POTENTIAL = 50

This is a neutral placeholder for workflow testing, not a production engagement formula or an observed metric.

No engagement formula should be silently invented before real Scout data availability is validated.

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

↓ decide_next_action()

↓ LLM

↓ Structured ScoutAction

↓ Python Executor

↓ Guardrails

↓ Tool Execution

↓ Updated ScoutState

↓ Next LLM Decision

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

Python remains responsible for authorizing or rejecting requested actions.

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

WEB_TOOL_MODE=fake → web_search + web_reader

WEB_TOOL_MODE=real → brave_search + http_reader

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

Interaction Memory v0.1 — Persistent Discovery History / Scout Integration

Purpose:

Persist operational discovery history across application runs so Scout can avoid repeatedly consuming the same successfully read public content.

Implemented:

SQLite-backed interaction repository and service under app/memory/;

canonical URL identity with deterministic normalization;

tracking parameters and fragments removed while functional query parameters are preserved;

canonical URL uniqueness prevents duplicate interaction records;

persistent VISITED state is recorded only after a successful Scout READ and context preparation;

failed Scout READ attempts do not become persistent VISITED interactions;

SELECT promotes the persisted interaction to SELECTED;

Scout SEARCH filters URLs already present in persistent interaction memory before they are offered for semantic READ selection;

current-run revisit protection and persistent cross-run memory operate together;

SEARCH outcomes distinguish HAS_NOVEL_RESULTS, NO_SEARCH_RESULTS, and NO_NOVEL_RESULTS;

NO_NOVEL_RESULTS allows bounded semantic search reformulation rather than forcing immediate termination;

novelty-search retries are bounded independently from the Scout global operational step budget;

a novel result resets the novelty retry counter;

the real scout_node composition root instantiates InteractionMemoryService and injects it into the Scout runtime;

the runtime SQLite file is intentionally excluded from Git;

repository/service contracts already support storing an Agentic draft and a later human final version, but those workflow integrations are intentionally deferred.

Operational state semantics established during this increment:

Scout visited_urls means successful READs within the current runtime.

Persistent VISITED means a source was successfully read and prepared for Scout consumption.

A failed Scout READ remains recoverable but is not treated as successfully visited.

Research retains its existing local runtime semantics for visited_urls, where an attempted blocked source may remain recorded to prevent repeated attempts inside the same research run. This distinction is intentional and was preserved rather than silently changing Research behavior during the Scout-memory increment.

Interaction Memory is operational history, not LLM conversational memory.

Rodrigo Voice Golden Set is a separate curated calibration artifact under docs/calibration/ and must not be treated as operational interaction memory.

Validation:

28 dedicated Interaction Memory foundation tests pass;

10 dedicated Scout + Interaction Memory integration tests pass;

existing Scout web-recovery tests were updated to preserve the successful-read VISITED semantic;

the complete automated project suite passes with 228 tests;

a controlled real E2E Run 1 completed successfully with WEB_TOOL_MODE=real after the memory integration and reached the existing Human / END quality boundary;

the successful real Scout READ created runtime interaction_memory.db data while the database remained excluded from Git.

Additional live validation intentionally pending:

Run the same real discovery workflow again without deleting the runtime database and observe that previously persisted content cannot be consumed again by Scout.

This Run 2 validation is useful behavioral evidence but is not a blocker for checkpointing the already automated and smoke-tested implementation.

Intentionally incomplete:

Writer → agentic_draft persistence in the live workflow;

Human → human_final persistence in the live workflow;

recent-history retrieval in a frontend or operator interface;

full ordered Scout action / observation tracing;

token/cost optimization of Scout, Research, Writer, and Evaluator context;

LinkedIn-native candidate acquisition.

Current Test Baseline

Full project suite:

228 passing tests

The suite covers Writer, Quality Evaluator, Opportunity Evaluation, Scout, Research, routing, workflow integration, web-tool selection, Brave Search mapping and failures, HTTP Reader security and content limits, controlled WebToolError recovery, context preparation, Scout/Research token guards, candidate deduplication, semantic main-content extraction, content-density extraction, ResearchBrief / Writer contracts, the typed ResearchBrief → EvaluatorInput regression contract discovered by live E2E validation, Interaction Memory URL canonicalization and SQLite persistence, and Scout persistent-memory filtering / novelty-search behavior.

Live network calls are not required by pytest. External providers are mocked or replaced with deterministic fakes in automated tests.

Real-network and real-LLM validation are performed separately as controlled smoke tests.

Current Development Status

The current development increment is:

Interaction Memory v0.1 — Persistent Discovery History / Scout Integration

Status:

IMPLEMENTED

TESTED

REAL RUN 1 VALIDATED

AUDITED

READY FOR CHECKPOINT COMMIT

Current automated test baseline:

228 passing tests

Project Context Snapshot integrity from the pre-context-update audit:

PASS

The audit confirmed repository content remained stable during collection.

The audit correctly reported context-consistency INFO messages because this PROJECT_CONTEXT.md still declared stable baseline 3ce9349 and 190 passing tests while the actual repository HEAD was 753df83 and the current suite had 228 passing tests. This context refresh resolves that semantic drift before the checkpoint commit.

Current Development Objective

Close Interaction Memory v0.1 — Persistent Discovery History / Scout Integration as one recoverable checkpoint.

The functional objective achieved in this increment is narrower than a full interaction-history product:

Scout can persist successfully read URLs across application runs;

canonical equivalent URLs resolve to one interaction identity;

known persistent URLs are filtered before Scout can consume them again;

successful READ and SELECT transitions are reflected in persistent interaction state;

failed Scout READ attempts do not become persistent VISITED records;

Scout can distinguish no provider results from no novel results;

the LLM may semantically reformulate search after NO_NOVEL_RESULTS;

Python bounds novelty retries and retains deterministic ownership of persistence and execution;

the full pre-existing workflow remains green with 228 passing tests;

a real Run 1 confirmed the memory-enabled composition still completes the live Scout → Opportunity → Research → Writer → Quality Evaluator path.

The additional real Run 2 memory-reuse observation remains pending and can be executed after this checkpoint without changing the committed implementation.

Current WIP

Interaction Memory v0.1 — Persistent Discovery History / Scout Integration is implemented, tested, audited, and ready for checkpointing.

The current dirty working tree intentionally contains:

.gitignore

app/agents/scout.py

app/graph/nodes/scout_node.py

app/schemas/scout.py

app/memory/

docs/context/PROJECT_CONTEXT.md

docs/calibration/RODRIGO_VOICE_GOLDEN_SET.md

tests/test_interaction_memory.py

tests/test_scout_interaction_memory.py

tests/test_web_tool_recovery.py

The runtime database:

data/memory/interaction_memory.db

is intentionally excluded from Git and must remain local runtime data.

The Rodrigo Voice Golden Set is included in the checkpoint as a separate calibration artifact. It is not part of the Interaction Memory runtime model.

Remaining work for this checkpoint is checkpoint hygiene only:

rerun project_audit.py after this context refresh;

verify context consistency and snapshot integrity;

review git diff / git status;

stage;

commit;

push.

No Token Governance implementation should be mixed into this checkpoint.

Next Planned Capability

After this checkpoint commit, development should continue with:

Token Governance v0.1 — Bounded Research & Lean Context

Objective:

Reduce LLM/context consumption while preserving the quality contract required to produce a short, factual, relevant, differentiated LinkedIn comment.

The first optimization target is the mismatch between the small final artifact and the comparatively large intermediate research/context footprint.

Initial investigation should measure and map:

Web → Scout prepared-context size;

Scout / Opportunity → Research input size;

Research SEARCH / READ / EXTRACT consumption;

ResearchBrief size and field duplication;

ResearchBrief → Writer context size;

Writer → Quality Evaluator context size;

model usage, latency, and cost per component where measurable.

Initial architectural direction:

keep the existing evidence-provenance boundary SEARCH → READ → EXTRACT → EvidenceItem → ResearchBrief;

make Research sufficiency proportional to the final artifact rather than maximizing research depth;

prefer early semantic stop once sufficient high-quality evidence exists;

reduce duplicated or low-value Writer-facing research fields;

compress context before Writer and Evaluator boundaries;

preserve Python-owned hard budgets and deterministic guardrails;

preserve semantic LLM ownership where interpretation materially adds value;

do not weaken factual grounding, source provenance, quality evaluation, or Human publication authority merely to save tokens.

Likely design questions to resolve before code:

the minimum useful number of promoted EvidenceItem objects for a short LinkedIn comment;

whether key_findings, counterpoints, and unresolved_questions should remain mandatory Writer-facing fields;

appropriate lower SEARCH / READ / evidence budgets for this specific product;

whether Scout and Research read-context limits should be reduced or made adaptive;

which components can safely use cheaper models;

how token usage and cost should be measured so future optimization is evidence-based rather than estimated from output length alone.

LinkedIn-native Integration remains a later planned capability. Token Governance is intentionally prioritized first because the real E2E run demonstrated that the current system can generate a short high-quality comment while carrying substantially larger intermediate research context than the final artifact requires.

Future Agent Experience / Observable Workflow Direction

A lightweight product-facing observability layer is now an explicit future direction for both this LinkedIn Agentic AI System and the reusable AI Solution Factory architecture.

The first implementation should be deliberately simple: a live textual execution feed analogous to pytest progress, where each visible line corresponds to a real workflow event rather than simulated progress.

Example event classes include:

SCOUT_STARTED; SEARCH_COMPLETED; CANDIDATE_FOUND; OPPORTUNITY_EVALUATED; RESEARCH_STARTED; SOURCE_READ; EVIDENCE_EXTRACTED; RESEARCH_COMPLETED; WRITER_STARTED; DRAFT_COMPLETED; EVALUATION_COMPLETED; HUMAN_APPROVAL_REQUIRED; controlled provider/tool failure events.

The governing UX principle is:

Never leave the user waiting for an agent without showing what the system actually knows is happening.

The frontend must not fabricate percentages or progress states. When workflow size is not known in advance, factual stage/event visibility is preferred over artificial completion percentages.

The event layer should remain decoupled from the Orchestrator and reusable by future solutions. SSE is a suitable initial server-to-client transport unless later bidirectional requirements justify WebSocket.

Future extensions may expose latency, token consumption, tool/provider calls, source counts, cost, failures, approval states, cards, richer visualizations, and eventually avatar/voice/digital-human representations without coupling those presentation technologies to the Core Engine.

This observability layer is not part of the current checkpoint and must not delay LinkedIn-native integration.

Opportunity Routing Direction

The current v0.1 routing behavior is established as:

HIGH ↓ ACCEPTED_FOR_RESEARCH ↓ Research ↓ Writer ↓ Quality Evaluator ↓ PASS / REVISE / REJECT

MEDIUM ↓ QUEUED ↓ END

LOW ↓ END

HIGH means the opportunity is approved to proceed into the integrated Research → Writer → Quality Evaluator path.

MEDIUM opportunities remain distinct from LOW opportunities. They are preserved in a lower-priority queued state without incurring Research cost.

LOW opportunities terminate the Opportunity Workflow.

Research is already integrated for HIGH opportunities, and Quality Evaluator now follows Writer in that path.

The lifecycle of queued MEDIUM opportunities may be revisited later using real operational evidence, but the current v0.1 routing behavior is explicitly QUEUED.

Research Status

Research Capability v0.1 remains a bounded specialist capability with real semantic execution and optional real-web infrastructure.

Its responsibility remains:

Given an approved opportunity, gather and promote the minimum evidence required to produce a factual and defensible contribution.

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

Agent-facing product experiences should expose real workflow state and events rather than opaque waiting indicators or fabricated progress.

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

claiming the current fake Scout tools perform real LinkedIn discovery;

prematurely optimizing Opportunity Evaluation weights without data;

implementing unrelated platform capabilities before the core workflow

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

The integration boundary between Scout and Opportunity Evaluation is now established.

scout_node owns adaptation from ScoutState into LinkedInAgentState.

The current v0.1 cardinality contract is:

zero candidates → terminate without Opportunity Evaluation;

one candidate → continue to Opportunity Evaluation;

multiple candidates → fail explicitly.

This is a temporary boundary contract, not a final product rule for multi-opportunity handling.

Opportunity Routing

Current v0.1 routing is deterministic:

HIGH → ACCEPTED_FOR_RESEARCH → Research → Writer → Quality Evaluator → PASS / REVISE / REJECT;

MEDIUM → QUEUED → END;

LOW → END.

ACCEPTED_FOR_RESEARCH records the approval transition and now leads directly into the integrated Research capability.

The later lifecycle of queued MEDIUM opportunities remains open to calibration.

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

How the shared Agent Experience / observability event protocol should represent agent decisions, workflow stages, tool calls, token usage, latency, cost, failures, and Human Approval across both LinkedIn Agentic AI System and AI Solution Factory.

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

Development Interaction Contract

The following rules are part of the project's recoverable development context and must be preserved across development sessions.

Repository and Execution Context

Development commands must assume:

Operating system: Windows

Shell: PowerShell

Repository root: C:\Users\rods_\Desktop\AI - LAB\linkedin-agentic-ai-system

Virtual environment: .venv

Commands are normally executed from the repository root.

Python modules under app/ must be invoked using Python module notation when -m is used.

Examples:

Correct:

python -m app.scripts.smoke_e2e

Incorrect:

python -m app/scripts/smoke_e2e.py

Test Execution Convention

Tests should be executed through the active Python interpreter rather than depending directly on the pytest launcher executable.

Preferred:

python -m pytest tests/test_interaction_memory.py -v

Full suite:

python -m pytest

This convention ensures pytest runs from the active project virtual environment and avoids Windows launcher/path inconsistencies.

Do not use:

pytest -m tests/...

because -m in pytest means marker selection, not Python module execution.

Code Structure Preservation

Before proposing new production files, tests, imports, or commands:

Respect the existing repository package structure captured by the audit.

Do not invent directories or relocate existing capabilities without an explicit architectural decision.

New capabilities should follow the established separation of concerns.

Python packages created under app/ should include init.py where appropriate for explicit package semantics.

Imports should be compatible with execution from the repository root.

Test paths must correspond to actual files under tests/.

Code Delivery Convention

When providing implementation code:

provide the exact destination path for every file;

prefer complete file contents when creating a new file;

preserve existing architectural boundaries;

provide terminal commands separately from source code;

commands must be directly copyable into PowerShell;

never assume Bash/Linux commands unless explicitly required.

Architecture Preservation Rule

Code suggestions must preserve the established project ownership model:

LLM owns semantic interpretation and bounded semantic decisions;

Python owns deterministic execution, state, authorization, limits, persistence, and factual contracts;

LangGraph owns workflow orchestration;

external infrastructure must remain behind explicit tool/repository/service boundaries.

A new development session should treat this contract as authoritative unless the current repository state explicitly supersedes it.

CURRENT CHECKPOINT UPDATE — TOKEN GOVERNANCE & BEHAVIORAL CALIBRATION

This section supersedes older status, baseline, WIP, test-count, and next-step declarations above where they conflict with the current repository state. Historical sections remain preserved because they document the architectural evolution of the project.

Current Stable Baseline

Last clean committed baseline before the current WIP:

72002eb
feat: add persistent interaction memory to scout

Branch:

main

This commit supersedes the older 753df83 stable-baseline declaration retained in the historical context above.

Current Test Baseline

Current validated full regression suite:

250 passed

Canonical command:

python -m pytest -q

The current suite includes the previously established behavioral contracts plus Token Usage Observability instrumentation and Gap-Driven Research tests.

Current WIP

The current dirty working tree intentionally contains the next validated development increment on top of 72002eb.

Primary capability areas:

Token Usage Observability v0.1

Implemented:

run-scoped usage capture through a ContextVar-backed collector;

LLM usage records by component and operation;

input, output, total, cached-input, and reasoning token capture when available;

LLM latency capture;

context-usage records before and after preparation;

aggregation by run and component;

no-op behavior when telemetry capture is inactive;

instrumentation across Scout, Opportunity Evaluator, Research, Writer, and Quality Evaluator;

real E2E telemetry runner at app/scripts/run_with_usage.py.

Current real E2E execution command:

python -m app.scripts.run_with_usage

Pricing is intentionally not hardcoded into telemetry. Model identity and observed usage are recorded as facts; mutable pricing should later be applied through configurable cost derivation.

Gap-Driven Research / Lean Research Contract v0.1

The Research contract now carries explicit semantic sufficiency information:

material_gaps;

next_research_goal;

sufficiency_reason.

The governing principle is:

Evidence quantity alone does not determine sufficiency.

After evidence exists, an additional SEARCH requires semantic justification through:

at least one explicit material gap; and

a concrete next research goal.

The LLM continues to own semantic judgments about:

claim coverage;

source authority;

independence;

relevance;

contradictions;

unresolved material gaps;

whether the available evidence is semantically sufficient.

Python continues to own:

action authorization;

counters;

hard ceilings;

provenance;

runtime status;

tool execution;

final factual state.

The established evidence-promotion boundary remains unchanged:

SEARCH → READ → EXTRACT → EvidenceItem → ResearchBrief

No deterministic rule such as "two evidence items means sufficient" has been introduced.

The existing hard Research ceilings remain runtime-owned.

The new Gap-Driven Research behavior is covered by automated tests, but it has not yet received a post-change HIGH real E2E validation.

Therefore no production token-saving claim should yet be made for the new Research contract.

Rodrigo Voice Golden Set

The Rodrigo Voice Golden Set remains a separate calibration artifact:

docs/calibration/RODRIGO_VOICE_GOLDEN_SET.md

The dataset now contains additional real human-vs-Agentic calibration evidence.

Current interpretation:

technical and semantic quality is already strong;

the Writer still tends to produce more explanatory completeness than Rodrigo naturally prefers for LinkedIn comments;

Rodrigo tends to preserve the central technical thesis while removing secondary detail;

conversational professional positioning is preferred over white-paper-like exposition;

Human publication preference remains the calibration ground truth;

high automated voice_match alone is not sufficient evidence of publication readiness;

the evidence is not yet mature enough to freeze a permanent Social Writing Contract.

Token Governance Real Baseline

The original expensive HIGH real E2E run established the main optimization target.

Observed E2E usage:

Total tokens: 104,783
Input tokens: 100,904
Output tokens: 3,879
LLM calls: 22

Research alone consumed approximately:

75,474 total tokens
14 LLM calls

The Research loop reached:

LIMIT_REACHED

despite producing useful evidence and a final draft that passed Quality Evaluation.

This mismatch between a short final social artifact and a large intermediate Research footprint is the empirical basis for the current Lean Research / Token Governance work.

The existing context-preparation layer also demonstrated material value during this baseline. Observed external context was reduced from approximately:

15,091 original tokens

to:

6,800 prepared tokens

across the recorded Scout/Research READ contexts.

The primary optimization target therefore remains the Research loop and semantic stopping behavior rather than removing the existing context-preparation boundary.

E2E Behavioral Calibration Baseline

A controlled natural battery of eight unchanged real-web E2E runs was completed.

Detailed experimental record:

docs/calibration/E2E_BEHAVIOR_BASELINE.md

Consolidated results:

Run

Outcome

Opportunity Score

Research

Total Tokens

1

HIGH

83.45

Yes → PASS

104,783

2

NO_CANDIDATE_FOUND

—

No

8,452

3

MEDIUM

79.45

No

15,297

4

NO_CANDIDATE_FOUND

—

No

5,160

5

MEDIUM

79.75

No

16,889

6

MEDIUM

79.60

No

16,350

7

NO_CANDIDATE_FOUND

—

No

5,937

8

NO_CANDIDATE_FOUND

—

No

4,514

Observed distribution:

HIGH: 1/8
MEDIUM: 3/8
NO_CANDIDATE_FOUND: 4/8

The system did not force downstream Research/Writer execution when the opportunity threshold was not met.

The natural repeated-run battery is now complete. Continuing to rerun Scout merely until a random HIGH appears would weaken experimental control and consume resources without resolving the main Research question.

Interaction Memory — Live Behavioral Observation

Repeated real runs produced behavior consistent with persistent cross-run URL novelty filtering.

Previously consumed URLs were not observed being recycled as the next selected candidate.

This strengthens the operational validation of Interaction Memory v0.1.

Important limitation:

Interaction Memory currently establishes URL-level identity, not semantic identity.

Different URLs discussing the same thesis, event, article, or idea may still be treated as novel.

Semantic duplicate detection remains future work.

Opportunity Calibration Observation

Three independent MEDIUM opportunities clustered immediately below the current HIGH threshold:

79.45
79.75
79.60

This is a meaningful calibration signal but is not sufficient evidence to lower the HIGH threshold.

Across these cases, Topic Relevance and Positioning Fit remained high while Contribution Potential was the main limiting factor.

Current hypothesis:

The evaluator may be distinguishing correctly between content that is highly relevant to Rodrigo and content that offers a sufficiently differentiated contribution.

The HIGH threshold remains unchanged pending broader evidence.

Scout Search-Budget Hypothesis

Repeated NO_CANDIDATE_FOUND outcomes create a new evidence-backed design question:

Is the current Scout exploration budget too restrictive as persistent memory makes novel discovery progressively harder?

This must not be confused with the Research ceiling:

MAX_RESEARCH_STEPS = 10

Before changing Scout limits, the system should distinguish and observe:

raw SEARCH calls;

READ calls;

Scout semantic decisions;

novelty retries;

context growth;

global Scout step ceilings.

Architectural direction to evaluate:

Adaptive Scout Search Budget

Possible policy:

bounded initial discovery
→ if results are known/non-novel, permit targeted semantic reformulation
→ remain selective about READ
→ stop on strong candidate, repeated lack of novelty, or hard ceiling

The principle is to be relatively generous with cheap discovery while remaining progressively stricter as operations become more expensive.

No Scout budget value is changed by this checkpoint.

Web / Tool Latency Observation

Real E2E runs showed substantial variance in elapsed time outside captured LLM latency.

Examples included runs with only a few seconds of remainder and others with more than 80–100 seconds.

The current metric:

workflow elapsed time - captured LLM latency

must not be described as pure web latency.

It may include:

SEARCH latency;

READ latency;

provider/network delay;

tool runtime;

orchestration overhead;

other uncaptured execution time.

Future Web / Tool Latency Observability is justified, but it is not required to close the current checkpoint.

Current Product Direction — LinkedIn Content Intelligence

The product direction is now broader than a comment-only assistant.

The target architecture should evolve toward a reusable LinkedIn Content Intelligence System with two primary content intents:

COMMENT
AUTHORIAL_POST

The system should reuse the same core engine wherever appropriate:

Discovery
↓
Opportunity Intelligence
↓
Research / Evidence
↓
Content-specific Writer
↓
Content-specific Quality Evaluation
↓
Human Review

A discovery should eventually be classifiable into outcomes such as:

IGNORE
COMMENT
AUTHORIAL_POST
COMMENT + AUTHORIAL_POST
SAVE_FOR_LATER

This creates two connected entry paths rather than two isolated systems.

A source discovered while searching for comment opportunities may reveal a stronger authorial-post opportunity.

Research performed for an authorial post may reveal relevant external conversations worth commenting on.

The two modes should use different writing and evaluation contracts.

COMMENT intent

Expected characteristics:

shorter;

conversational;

directly contextual to another person's thesis;

contribution-focused;

lower acceptable research footprint;

strong Rodrigo Voice calibration;

avoid white-paper or mini-essay behavior.

AUTHORIAL_POST intent

Expected characteristics:

longer;

more structured;

stronger narrative development;

more formal where appropriate;

capable of developing an original thesis;

potentially larger evidence requirement;

stronger opening/hook and argument progression;

explicit authorial positioning.

The long-term voice model should therefore be understood as:

Rodrigo Voice
+
Communication Context

rather than one universal style for every social artifact.

Golden Set evidence should eventually distinguish comment calibration from authorial-post calibration.

Research as a Reusable Asset

A new architectural principle is established for the future product direction:

Research is a reusable product asset, not a disposable intermediate artifact.

The future system should avoid automatically repeating equivalent research for every social artifact.

Conceptual direction:

Discovery
↓
Research Asset / Evidence
↓
Content Memory
├── Comment
├── Authorial Post
├── Follow-up
└── Future Idea

This direction is aligned with Token Governance because validated evidence may support more than one downstream artifact.

The exact persistence model for reusable Research/Evidence remains unresolved and must not be silently implemented without a dedicated design increment.

Current Architectural Position

The current system remains operationally comment-oriented.

The new authorial-post direction is a product/architecture target, not an implemented capability.

Existing production ownership remains:

LLM → semantic interpretation and bounded semantic decisions
Python → deterministic execution, authorization, state, limits, persistence, factual contracts
LangGraph → workflow orchestration
Human → final publication authority

No autonomous LinkedIn publication or autonomous commenting is introduced.

LinkedIn-native integration is still not implemented.

Current Development Status

Current increment:

Token Governance v0.1
+
Gap-Driven Research
+
Usage Observability
+
Behavioral / Voice Calibration

Status:

IMPLEMENTED
TESTED
250 PASSING TESTS
REAL BEHAVIORAL BASELINE CAPTURED
DOCUMENTATION CLOSURE IN PROGRESS
CHECKPOINT COMMIT PENDING

The current working tree should remain focused on closing this increment.

Do not mix the future Authorial Post implementation, LinkedIn-native integration, model routing, or Web/Tool Latency instrumentation into this checkpoint.

Immediate Checkpoint Closure

Before committing the current increment:

preserve docs/calibration/E2E_BEHAVIOR_BASELINE.md;

update this PROJECT_CONTEXT.md;

run the full regression suite:

python -m pytest -q

run:

python app/scripts/project_audit.py

validate snapshot integrity and context consistency;

review git diff and git status;

stage;

commit;

push.

Next Planned Capability

The next scientifically useful development step is not another uncontrolled Scout repetition.

It is:

Controlled Gap-Driven Research Validation

Purpose:

Compare the current Gap-Driven Research behavior with the original expensive Research baseline under a known HIGH opportunity.

The controlled comparison should measure:

Research LLM calls;

input/output/total tokens;

decision-prompt growth;

terminal status;

EvidenceItem quality and quantity;

ResearchBrief size;

latency;

Writer/Evaluator quality if downstream execution is included.

The production HIGH threshold must not be lowered merely to manufacture a Research run.

After the controlled Research validation, reassess:

Scout search-budget policy;

Opportunity calibration evidence;

Web/tool latency instrumentation priority.

Only after the current Token Governance / Research calibration stage is closed should implementation begin on the generalized content-intent architecture for:

COMMENT
AUTHORIAL_POST

and cross-pollination between both.

Future Product Roadmap

Current architectural sequence:

Close Token Governance / calibration checkpoint

Controlled Gap-Driven Research validation

Scout search-budget calibration

Generalized Content Intent / Opportunity architecture

Authorial Post Pipeline v0.1

Comment ↔ Authorial Post cross-pollination

Context-specific Voice / Golden Sets

LinkedIn-native discovery integration

Human Review / publication workflow hardening

Product-facing Agent Experience / observability

This sequence is directional rather than a rigid delivery contract. Evidence from controlled validation may change ordering where justified.

Local Development Command Rules

Rodrigo develops this project on Windows using VS Code, PowerShell, and a project-local .venv.

Python / pytest

The canonical test command is python -m pytest, never bare pytest.

For targeted tests, use:

python -m pytest <test_path> -q

For the full regression suite, use:

python -m pytest -q

When the PowerShell prompt already shows (.venv), do not provide an additional virtual-environment activation command unless there is evidence that the environment is not actually active.

Do not shorten previously validated project commands merely for convenience.

Prefer commands that explicitly use the active Python interpreter over Windows executable launchers such as pytest.exe.

Treat these commands as part of the project's operational contract, not as stylistic preferences.

Command Delivery

Provide shell commands in separate code blocks.

Commands must be directly executable from the repository root in the established Windows/PowerShell environment.

Before proposing a command, preserve the project's already-established execution convention unless the current task specifically requires changing it.

CURRENT CHECKPOINT UPDATE — TARGET CONTENT INPUT v0.1

This section supersedes older status, WIP, test-count, and next-step declarations above where they conflict with the current repository state.

Current Stable Baseline

Current committed HEAD:

07cb91e
feat: add token governance and gap-driven research

Branch:

main

This commit closes the preceding Token Governance / Gap-Driven Research checkpoint and is the recoverable baseline for the current Target Content Input work.

Current Test Baseline

Current validated full regression suite:

255 passed

Canonical command:

python -m pytest -q

The full pre-existing behavioral suite remains green after introducing the Target Content Input path.

Current Development Increment

Target Content Input v0.1

Purpose:

Provide a deliberate second entry path for known content that Rodrigo explicitly wants the system to evaluate, without forcing Scout to rediscover a predetermined target.

The architectural distinction is:

AUTO

Scout
↓
PostCandidate
↓
Opportunity Evaluation
↓
Research
↓
Writer
↓
Quality Evaluator
↓
Human / END

TARGET / MANUAL

LinkedIn URL
↓
Target Content Loader
↓
PostCandidate
↓
Opportunity Evaluation
↓
Research
↓
Writer
↓
Quality Evaluator
↓
Human / END

The central boundary rule is:

Both discovery paths converge on the existing PostCandidate contract.

From PostCandidate onward, downstream components must remain agnostic to whether the candidate originated from Scout or from a manually supplied target URL.

Implemented

A new input boundary exists under:

app/inputs/target_content.py

The Target Content Loader:

accepts an explicitly supplied target URL;

normalizes surrounding URL whitespace before use;

rejects an empty URL before attempting external reading;

uses the existing bounded content-reading/preparation boundary rather than introducing a parallel scraping architecture;

rejects empty prepared content;

constructs a validated PostCandidate from the target content;

preserves the existing downstream PostCandidate contract.

Dedicated validation exists under:

tests/test_target_content.py

Coverage includes:

successful URL → read/prepared content → PostCandidate construction;

surrounding URL whitespace normalization;

empty URL rejection before reading;

empty prepared-content rejection.

Workflow Integration

The target/manual entry path is now covered by:

tests/test_target_content_workflow.py

The controlled target path feeds the normalized PostCandidate into the existing Opportunity Workflow rather than duplicating Opportunity Evaluation, Research, Writer, or Quality Evaluator logic.

The intended invariant is:

Input origin != downstream policy.

Scout discovery policy remains Scout-owned.

Manual target acquisition remains Target Content Loader-owned.

Opportunity Evaluation and all downstream stages consume the shared factual contract and do not encode special behavior merely because the content was manually selected.

Architectural Rationale

A known target must not be simulated as an autonomous Scout discovery.

Doing so would contaminate the distinction between:

discovery;

ingestion;

evaluation;

research;

content generation.

Target Content Input therefore adds a second legitimate input gate instead of changing Scout behavior.

This preserves the project's ownership model:

LLM → semantic interpretation and bounded semantic decisions

Python → deterministic execution, authorization, state, limits, persistence, and factual contracts

LangGraph → workflow orchestration

Human → final publication authority

Context ≠ Policy

Input context may tell the system which content is being evaluated, but origin-specific information must not silently become downstream behavioral policy.

Critical workflow rules, guardrails, quality requirements, execution conventions, and publication authority remain explicit policy owned by the appropriate deterministic/workflow layer.

Known Limitation

Target Content Input v0.1 does not establish guaranteed LinkedIn-native retrieval.

A supplied LinkedIn URL may still be unreadable through the current public HTTP Reader because LinkedIn or another source may require authentication, JavaScript rendering, or anti-bot/browser capabilities.

The capability currently guarantees a controlled input contract and workflow boundary, not universal LinkedIn page accessibility.

Current WIP

The current working tree intentionally contains the Target Content Input increment and project documentation assets.

Functional WIP:

app/inputs/target_content.py

tests/test_target_content.py

tests/test_target_content_workflow.py

Documentation / visual assets:

docs/images/art-architecture-overview.png

docs/images/art-end-to-end-agentic-solution-flow.png

This PROJECT_CONTEXT.md is being refreshed before checkpoint commits.

The visual assets are relevant project documentation and should be checkpointed separately from the functional Target Content Input implementation so Git history preserves semantic separation.

Current Development Status

Target Content Input v0.1:

IMPLEMENTED

WORKFLOW-INTEGRATED

TESTED

255 PASSING TESTS

AUDITED

CHECKPOINT COMMIT PENDING

The current repository state should now be closed without adding unrelated capabilities.

Immediate Checkpoint Closure

After replacing docs/context/PROJECT_CONTEXT.md with this updated file:

run the full regression suite:

python -m pytest -q

run:

python app/scripts/project_audit.py

validate snapshot integrity and context consistency;

review git status;

commit the functional Target Content Input increment together with this context update;

commit the two visual documentation assets separately;

push both commits so origin/main and the local repository are synchronized.

Next Planned Capability

After checkpoint closure, execute the first controlled real target-content validation using a deliberately chosen known LinkedIn opportunity.

The validation objective is:

Known LinkedIn URL
↓
Target Content Loader
↓
PostCandidate
↓
Opportunity Evaluation
↓
Research, when classification permits
↓
Writer
↓
Quality Evaluator
↓
Human Review

The known target should be used as a controlled experiment, not as evidence that Scout discovered it autonomously.

The first planned real target is the previously selected professional discussion about understanding/redesigning processes before automating.

The controlled run should observe:

whether the target URL can be read through the current bounded reader;

the resulting PostCandidate;

Opportunity Evaluation signals, score, guardrails, and classification;

Research behavior and token usage if the opportunity is HIGH;

ResearchBrief evidence quality;

Writer output;

Quality Evaluator decision;

final Human / END boundary.

If direct LinkedIn reading fails, that failure should be treated as evidence about the LinkedIn-native acquisition limitation rather than bypassed by weakening the existing web-security or provenance contracts.

No autonomous publication is introduced.