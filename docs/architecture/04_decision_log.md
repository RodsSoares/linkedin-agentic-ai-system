Architecture Decision Log

This document records architectural decisions that are sufficiently established to constrain future implementation.

It is not a development diary and does not attempt to capture every implementation detail.

Status vocabulary:

Accepted    = current architectural rule
Superseded  = replaced by a later ADR
Proposed    = under explicit consideration, not yet binding

ADR-001 — Component-specific inputs instead of full orchestration state

Status: Accepted
Date: 2026-09-04

Context

The orchestration layer maintains a shared LinkedInAgentState containing information required across the complete agentic workflow.

Passing the entire state directly to specialized components such as the Writer would unnecessarily expose data that may not be relevant to their responsibility.

This coupling would increase as the global state grows.

Decision

The orchestration layer will maintain the global LinkedInAgentState, while specialized components will receive dedicated input contracts containing only the information required for their responsibility.

Example:

LinkedInAgentState
↓
writer_node
↓
WriterInput
↓
Writer

Rationale

This approach:

reduces coupling between components and the global state;

makes component dependencies explicit;

limits unnecessary data exposure;

improves testability;

allows the global state to evolve without forcing changes to unrelated components.

Consequences

The orchestration layer becomes responsible for mapping the global state into component-specific inputs.

This introduces a small amount of additional code in exchange for clearer component boundaries and better maintainability.

ADR-002 — Human publication authority is mandatory

Status: Accepted
Date: 2026-09

Context

The system can discover opportunities, research evidence, generate drafts, and evaluate quality.

Allowing the same autonomous workflow to publish directly would combine recommendation, generation, evaluation, and irreversible external action under one automated authority.

The product goal is strategic professional assistance, not autonomous social-media engagement. Human publication authority is explicitly established in the current project context.

Decision

No component may autonomously publish a LinkedIn contribution.

The terminal product boundary is:

AI prepares
AI evaluates
Human decides

A quality PASS means the contribution may reach the human decision boundary.

It does not authorize publication.

Rationale

Publication represents the user's professional identity and external communication.

Human approval therefore remains a product and governance boundary rather than merely an implementation detail.

Consequences

autonomous publication is an explicit non-goal;

autonomous commenting is an explicit non-goal;

future LinkedIn integrations must preserve human authority;

a future approval interface may make the boundary easier to operate, but must not silently remove it.

ADR-003 — Separate semantic reasoning from deterministic operational control

Status: Accepted
Date: 2026-09

Context

Agentic systems require semantic judgment but also require reliable operational constraints.

If an LLM owns both interpretation and deterministic runtime authority, scoring thresholds, routing, tool authorization, limits, and factual state can become probabilistic.

The established architecture explicitly separates semantic reasoning, deterministic governance, workflow orchestration, and human authority.

Decision

Responsibilities are divided as follows:

LLM
semantic interpretation
semantic action selection
evidence interpretation
synthesis
generation

Python
validation
scoring
guardrails
action authorization
provenance enforcement
counters
context/tool limits
factual state mutation

LangGraph
workflow state
node transitions
deterministic routing
controlled orchestration

Human
publication authority

The architectural rule is:

LLM interprets and decides semantically; Python governs execution and limits; LangGraph governs workflow; the human retains publication authority.

Rationale

This allows the system to use LLMs where semantic intelligence adds value without turning probabilistic output into unrestricted operational authority.

Consequences

LLM outputs that cause actions should cross structured validation boundaries;

deterministic rules should not be reimplemented as prompt instructions when application code can enforce them reliably;

graph nodes should orchestrate rather than absorb specialist business logic.

ADR-004 — Agent autonomy must be bounded

Status: Accepted
Date: 2026-09

Context

Scout and Research require genuine semantic exploration.

A fixed hardcoded sequence would not provide useful agent autonomy, while unrestricted browsing and unbounded loops would create unpredictable cost, latency, and failure behavior.

The project defines an agent as more than an LLM: semantic reasoning is combined with objective, state, actions, tools, a decision loop, and guardrails.

Decision

Agentic loops must operate inside explicit action vocabularies and deterministic limits.

Current examples:

Scout
SEARCH
READ
SELECT
FINISH

Research
SEARCH
READ
EXTRACT
FINISH

Python authorizes requested actions and enforces operational budgets.

Rationale

Useful autonomy requires freedom to make semantic choices inside a controlled execution space.

Consequences

unbounded agent loops are prohibited;

action requests are proposals until authorized;

max-step, decision, search, read, evidence, retry, and context limits may be independently enforced;

reaching a limit is an expected runtime outcome, not necessarily a software defect.

ADR-005 — Opportunity is contribution potential, not popularity

Status: Accepted
Date: 2026-09

Context

A highly popular post may have little strategic value for the user, while a less popular discussion may offer a strong opportunity for differentiated professional contribution.

The current product decision defines Opportunity as strategic contribution potential rather than simple popularity.

Decision

Opportunity Evaluation must consider multiple dimensions.

Current weights are:

Contribution Potential  30%
Positioning Fit          25%
Topic Relevance          20%
Engagement Potential     15%
Research Efficiency      10%

Contribution Potential receives the highest current weight.

Engagement is a signal, not the definition of opportunity.

Rationale

The system is intended to build useful professional interaction rather than optimize mechanically for attention.

Consequences

popularity alone cannot produce a HIGH opportunity;

reliable engagement metadata should improve the signal when available;

weights and thresholds remain calibration hypotheses rather than immutable product truths.

ADR-006 — Final Opportunity classification is deterministic

Status: Accepted
Date: 2026-09

Context

Semantic dimensions such as positioning fit and contribution potential benefit from LLM interpretation.

Final operational routing, however, should be reproducible and testable.

The established project decision assigns Research Efficiency, weighted score, mandatory guardrails, and final classification to Python.

Decision

The LLM produces semantic OpportunitySignals.

Python owns:

Research Efficiency
weighted Opportunity Score
mandatory guardrails
HIGH / MEDIUM / LOW classification

Current routing is deterministic:

HIGH   -> ACCEPTED_FOR_RESEARCH -> Research
MEDIUM -> QUEUED -> END
LOW    -> END

The current routing contract is documented in the project context.

Rationale

This separates subjective semantic assessment from operational resource allocation.

Consequences

prompts cannot silently redefine routing thresholds;

guardrail behavior is directly testable;

calibration can evolve independently from semantic prompting.

ADR-007 — Typed structured outputs at AI component boundaries

Status: Accepted
Date: 2026-09

Context

Free-form text between machine components makes downstream parsing fragile and allows semantic output to blur into operational state.

The project already uses typed contracts for Scout, Opportunity Evaluation, Research, Writer, Quality Evaluation, and shared state.

The current project decision explicitly prefers Pydantic contracts for machine-to-machine AI communication.

Decision

LLM-facing component boundaries should use structured outputs and typed contracts where practical.

Representative examples include:

ScoutAction
ScoutSelection
OpportunitySignals
ResearchAction
ResearchBriefSynthesis
Writer structured output
Quality Evaluation structured output

Rationale

Typed outputs:

constrain the action space;

make validation explicit;

improve testability;

reduce parsing ambiguity;

make component contracts inspectable.

Consequences

Schema changes are architectural changes when they alter component responsibilities or workflow behavior.

ADR-008 — Research evidence must preserve explicit provenance

Status: Accepted
Date: 2026-09

Context

Search results, snippets, read pages, and extracted factual evidence have different trust levels.

Allowing discovered or merely read text to become Writer-facing factual support without an explicit evidence boundary would weaken factual reliability.

The implemented Research capability separates real source reading from extracted evidence and has been smoke validated while preserving provenance.

Decision

Research uses an explicit evidence chain:

SEARCH
↓
SearchResult
↓
READ
↓
ReadSource
↓
EXTRACT
↓
EvidenceItem
↓
ResearchBrief

Only explicitly extracted evidence may support Writer-facing factual findings.

Rationale

This prevents the system from treating:

discovered == verified
read == supported
snippet == evidence

Consequences

source lineage is part of the data model;

Research state must preserve authorization and provenance;

Writer does not independently reinterpret arbitrary Research tool history as evidence;

unresolved questions and counterpoints may remain explicit rather than being converted into unsupported claims.

ADR-009 — ResearchBrief is the typed Research → Writer boundary

Status: Accepted
Date: 2026-09

Context

Writer requires useful research context but should not depend on the complete internal Research runtime state.

Passing generic dictionaries or raw tool history would couple Writer to Research implementation details.

Decision

ResearchBrief is the principal Writer-facing Research artifact.

Conceptually:

Research execution
↓
ResearchState
↓
evidence + synthesis
↓
ResearchBrief
↓
WriterInput
↓
Writer

Rationale

This preserves the specialist boundary:

Research gathers and validates evidence.
Writer turns the approved evidence package into communication.

Consequences

Writer does not become a second Research agent;

internal Research mechanics can evolve while preserving the Writer contract;

revisions to Writer do not automatically require Research re-execution.

ADR-010 — Writer revision does not automatically rerun Research

Status: Accepted
Date: 2026-09

Context

The Quality Evaluator may determine that a draft needs revision.

A writing-quality revision and an evidence deficiency are not necessarily the same problem.

Automatically rerunning Research for every REVISE would increase cost and introduce unnecessary state changes.

Decision

The current revision path is:

Writer
↓
Quality Evaluator
↓
REVISE
↓
Writer

Research is not automatically repeated during this loop.

The current architecture explicitly preserves this behavior.

Rationale

Research and writing are separate capabilities with separate responsibilities.

Consequences

Writer revisions reuse the established ResearchBrief;

the revision loop remains bounded;

if future evaluation can identify an actual evidence gap, a distinct Research-reentry decision may be designed explicitly rather than inferred from generic REVISE.

ADR-011 — Web tools use provider-neutral contracts with fake and real modes

Status: Accepted
Date: 2026-09-08

Context

Scout and Research were initially validated with deterministic fake web tools.

Real web access was then required without coupling agent logic to one search provider or reader implementation.

The current increment implements SearchTool, ReadTool, Brave Search, HTTP Reader, and WEB_TOOL_MODE = fake | real.

Decision

Agent-facing web capabilities use provider-neutral functional contracts:

SearchTool:
query -> list[SearchResult]

ReadTool:
url -> str

Runtime tool selection supports:

fake
deterministic test tools

real
Brave Search + bounded HTTP Reader

Rationale

This separates:

agent capability

from:

infrastructure provider

and keeps automated tests deterministic.

Consequences

Scout and Research do not depend directly on Brave-specific response models;

future providers can implement the same contract;

fake tooling remains the default isolated test environment;

real infrastructure is validated separately through explicit smoke/end-to-end runs.

ADR-012 — Agent-accessible web reading is a security boundary

Status: Accepted
Date: 2026-09-08

Context

A READ action originates from semantic agent behavior and may target URLs discovered externally.

Treating those URLs as trusted would expose the runtime to unsafe network destinations, redirect chains, oversized responses, unsupported content, and uncontrolled waits.

The implemented real infrastructure includes URL validation, DNS resolution, private/non-global IP rejection, redirect revalidation, timeouts, and content-size bounds.

Decision

Real web reading must remain bounded and validate network destinations before content becomes agent-visible.

The current reader boundary includes:

HTTP/HTTPS validation
localhost rejection
DNS resolution
private/non-global IP rejection
redirect limits
redirect-target revalidation
timeouts
content-type checks
response-size bounds
controlled infrastructure failures

Rationale

Tool access expands the authority of an agent beyond pure text generation.

The tool boundary must therefore be treated as application security infrastructure.

Consequences

unrestricted arbitrary URL fetching is not permitted;

supported infrastructure failures use WebToolError;

a future browser-rendered reader must preserve equivalent or stronger controls.

ADR-013 — External content must be prepared under explicit token budgets

Status: Accepted
Date: 2026-09-08

Context

Real webpages can contain far more text than a component needs.

Passing complete external pages directly into LLM context creates uncontrolled token cost, latency, prompt pollution, and potentially unpredictable behavior.

The current increment introduces bounded context preparation with per-read and cumulative Research budgets.

Decision

External read content must pass through deterministic context preparation before becoming LLM-facing input.

Current principal budgets:

Scout read context
<= 1800 tokens

Research per-read context
<= 2500 tokens

Research cumulative stored read context
<= 8000 tokens

Context preparation records whether truncation occurred.

Rationale

Context is computational infrastructure, not a free unlimited input channel.

Consequences

raw oversized pages must not bypass the preparation boundary;

token budgets can evolve independently by component;

future cost-aware orchestration can build on explicit context accounting.

ADR-014 — Main-content extraction precedes LLM context preparation

Status: Accepted
Date: 2026-09-08

Context

Webpages contain navigation, cookie notices, sidebars, related links, promotional elements, scripts, and other material that is not useful editorial content.

Token truncation alone can waste the available budget on boilerplate.

The current implementation prioritizes semantic article/main containers and uses deterministic content-density fallback for section/div pages.

Decision

HTML reading must attempt to isolate useful page content before token-budget preparation.

Current precedence:

non-empty article
↓ otherwise
non-empty main
↓ otherwise
density-scored section/div
↓ otherwise
cleaned fallback text

Rationale

The best bounded context is not merely shorter text; it is more relevant text.

Consequences

semantic containers can remain authoritative even when short;

density thresholds are fallback heuristics rather than universal content rules;

the extractor remains deterministic and dependency-light;

a future browser/DOM extraction capability may complement rather than silently replace this contract.

ADR-015 — Expected web infrastructure failures are recoverable agent observations

Status: Accepted
Date: 2026-09-08

Context

Real search/read infrastructure can fail because of timeouts, HTTP errors, blocked pages, or network conditions.

Crashing the entire agent on every expected infrastructure failure would make bounded semantic recovery impossible.

Catching arbitrary exceptions, however, could hide programming defects behind plausible agent observations.

Decision

Expected external-tool failures are represented through a dedicated WebToolError.

Scout and Research may catch that error at their tool boundary, record the failure in state, consume the appropriate operational budget, and allow another bounded semantic decision.

Arbitrary programming failures must not be silently converted into recoverable web observations.

Rationale

The system needs both resilience and debuggability.

Consequences

The runtime distinguishes:

expected external failure
!=
programming defect

This distinction should be preserved as new tools are added.

ADR-016 — Fake infrastructure remains first-class for automated tests

Status: Accepted
Date: 2026-09-08

Context

Automated tests must be reproducible and should not depend on live search providers, network availability, API quotas, or changing public webpages.

At the same time, fake infrastructure alone is insufficient evidence that real integration works.

Decision

The project uses two complementary validation layers:

Automated suite
deterministic fake/mocked external dependencies

Real validation
explicit smoke and end-to-end runs

The complete current automated suite passes 189 tests, while real Scout and Research smoke validation have separately passed.

Rationale

Deterministic testing and real integration validation solve different problems.

Consequences

pytest should not require live web/OpenAI access unless a test is explicitly designed as an external integration test;

real smoke results must not be confused with automated regression coverage;

the next planned increment can validate the full real path while preserving deterministic unit/integration tests.

Open Decisions — Not Yet ADRs

The following remain intentionally unresolved and must not be silently encoded as permanent architecture.

Current open questions include:

reliable LinkedIn-native candidate access and metadata
reaction/comment/author-reach availability
Engagement Potential normalization
handling of missing engagement metadata
queued MEDIUM lifecycle
Research status-specific routing
long-term search provider strategy
browser-rendered reading for JavaScript-heavy pages
source authority / credibility modeling
model selection per component
Opportunity Evaluation calibration
measured token/tool cost in Research Cost
author relevance as a separate dimension
Scout as a possible future LangGraph subgraph
complete chronological Scout action history
multiple-candidate ranking and orchestration
production observability and cost telemetry
real LinkedIn integration while preserving human authority

These open areas are also explicitly tracked in the current project context.

When one becomes established, it should receive a new ADR rather than being retroactively hidden inside implementation.

ADR Maintenance Rule

Create or update an ADR when a decision:

constrains multiple components;

changes responsibility ownership;

changes a trust or security boundary;

changes an agent autonomy boundary;

changes human authority;

changes an important data contract;

introduces a durable infrastructure abstraction;

would be expensive or confusing to reverse without understanding why it was chosen.

Do not create ADRs for routine refactors, isolated bug fixes, formatting, or implementation details that do not establish an architectural rule.

Existing accepted ADRs should not be rewritten to pretend the original context never existed.

If a decision changes materially, add a new ADR and mark the previous one Superseded.