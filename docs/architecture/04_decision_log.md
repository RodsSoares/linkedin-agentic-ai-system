Architecture Decision Log

This document records architectural decisions that are sufficiently established to constrain future implementation.

It is not a development diary and does not attempt to capture every implementation detail.

Status vocabulary:

Accepted = current architectural rule
Superseded = replaced by a later ADR
Proposed = under explicit consideration, not yet binding

ADR-001 --- Component-specific inputs instead of full orchestration state

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

ADR-002 --- Human publication authority is mandatory

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

ADR-003 --- Separate semantic reasoning from deterministic operational control

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

ADR-004 --- Agent autonomy must be bounded

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

ADR-005 --- Opportunity is contribution potential, not popularity

Status: Accepted
Date: 2026-09

Context

A highly popular post may have little strategic value for the user, while a less popular discussion may offer a strong opportunity for differentiated professional contribution.

The current product decision defines Opportunity as strategic contribution potential rather than simple popularity.

Decision

Opportunity Evaluation must consider multiple dimensions.

Current weights are:

Contribution Potential 30%
Positioning Fit 25%
Topic Relevance 20%
Engagement Potential 15%
Research Efficiency 10%

Contribution Potential receives the highest current weight.

Engagement is a signal, not the definition of opportunity.

Rationale

The system is intended to build useful professional interaction rather than optimize mechanically for attention.

Consequences

popularity alone cannot produce a HIGH opportunity;

reliable engagement metadata should improve the signal when available;

weights and thresholds remain calibration hypotheses rather than immutable product truths.

ADR-006 --- Final Opportunity classification is deterministic

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

HIGH -\> ACCEPTED_FOR_RESEARCH -\> Research
MEDIUM -\> QUEUED -\> END
LOW -\> END

The current routing contract is documented in the project context.

Rationale

This separates subjective semantic assessment from operational resource allocation.

Consequences

prompts cannot silently redefine routing thresholds;

guardrail behavior is directly testable;

calibration can evolve independently from semantic prompting.

ADR-007 --- Typed structured outputs at AI component boundaries

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

ADR-008 --- Research evidence must preserve explicit provenance

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

ADR-009 --- ResearchBrief is the typed Research → Writer boundary

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

ADR-010 --- Writer revision does not automatically rerun Research

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

ADR-011 --- Web tools use provider-neutral contracts with fake and real modes

Status: Accepted
Date: 2026-09-08

Context

Scout and Research were initially validated with deterministic fake web tools.

Real web access was then required without coupling agent logic to one search provider or reader implementation.

The current increment implements SearchTool, ReadTool, Brave Search, HTTP Reader, and WEB_TOOL_MODE = fake \| real.

Decision

Agent-facing web capabilities use provider-neutral functional contracts:

SearchTool:
query -\> list\[SearchResult\]

ReadTool:
url -\> str

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

ADR-012 --- Agent-accessible web reading is a security boundary

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

ADR-013 --- External content must be prepared under explicit token budgets

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
\<= 1800 tokens

Research per-read context
\<= 2500 tokens

Research cumulative stored read context
\<= 8000 tokens

Context preparation records whether truncation occurred.

Rationale

Context is computational infrastructure, not a free unlimited input channel.

Consequences

raw oversized pages must not bypass the preparation boundary;

token budgets can evolve independently by component;

future cost-aware orchestration can build on explicit context accounting.

ADR-014 --- Main-content extraction precedes LLM context preparation

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

ADR-015 --- Expected web infrastructure failures are recoverable agent observations

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

ADR-016 --- Fake infrastructure remains first-class for automated tests

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

At the time of this decision, the automated suite used deterministic external dependencies while real Scout and Research smoke validation were performed separately. The current project-wide regression baseline has since reached 437 passing tests.

Rationale

Deterministic testing and real integration validation solve different problems.

Consequences

pytest should not require live web/OpenAI access unless a test is explicitly designed as an external integration test;

real smoke results must not be confused with automated regression coverage;

the next planned increment can validate the full real path while preserving deterministic unit/integration tests.

Open Decisions --- Not Yet ADRs

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

ADR-022 --- Persistence backend selection is explicit

Status: Accepted
Date: 2026-09-30

Context

Cloud persistence introduced a subtle test-isolation problem.

DATABASE_URL may legitimately exist in a developer environment even when local execution and automated tests should continue using isolated local persistence.

During PostgreSQL checkpoint validation, a workflow integration test that reused a fixed thread_id recovered durable state from a previous execution. The behavior demonstrated that using database credentials alone as an implicit backend selector would couple local/test semantics to persistent cloud state.

Decision

Persistence technology is selected explicitly through PERSISTENCE_BACKEND.

DATABASE_URL provides connection information but does not independently enable PostgreSQL behavior.

Current rule:

PERSISTENCE_BACKEND=postgres
+
DATABASE_URL configured
-\>
PostgreSQL enabled

Otherwise:
local persistence remains active.

Rationale

Credentials and runtime behavior are different concerns.

An explicit selector preserves deterministic local/test execution while allowing the deployed environment to opt into durable PostgreSQL state.

Consequences

local development remains local by default;

automated tests do not bind to Supabase merely because DATABASE_URL exists;

Render must explicitly configure PERSISTENCE_BACKEND=postgres;

fixed thread identifiers remain a test-isolation concern when PostgreSQL is intentionally enabled;

database configuration becomes a deterministic application boundary.

ADR-023 --- Cloud persistence uses PostgreSQL while preserving three logical persistence domains

Status: Accepted
Date: 2026-09-30

Context

The deployed application must survive process sleep, restart, and replacement on Render.

The system already has three materially different persistence responsibilities:

LangGraph execution/checkpoint state;

Interaction Memory used by agent behavior;

Run History / Product Memory used by the human-facing product.

Using one cloud database can reduce infrastructure cost, but sharing infrastructure must not erase the conceptual boundaries between those responsibilities.

Decision

Supabase PostgreSQL is the current cloud persistence platform.

The three logical domains remain separate:

LangGraph checkpoint / HITL state
- local: InMemorySaver
- cloud: PostgresSaver

Interaction Memory
- local: SQLiteInteractionMemoryRepository
- cloud: PostgresInteractionMemoryRepository

Run History / Product Memory
- local: SQLiteRunHistoryRepository
- cloud: PostgresRunHistoryRepository

Rationale

One PostgreSQL service is sufficient for the current MVP scale and cost target.

Separate application abstractions preserve different ownership, lifecycle, and consumer semantics without requiring three separate infrastructure products.

Consequences

checkpoint state must not be treated as product history;

Interaction Memory must not be treated as Run History;

repositories can evolve independently;

the Render filesystem is not the durable cloud system of record;

Redis, Kafka, and additional stateful infrastructure are not required by the current validated scope.

ADR-024 --- Initial cloud runtime is Render plus Supabase PostgreSQL

Status: Accepted
Date: 2026-09-30

Context

The current MVP is a Python/Streamlit application with LangGraph orchestration, bounded web access, explicit HITL decisions, and modest portfolio-scale traffic.

The deployment goal prioritizes:

zero or very low infrastructure cost;

learning value;

minimal operational complexity;

preservation of the existing single-application architecture.

Decision

The initial cloud topology is:

Render Free Web Service
- Python runtime
- Streamlit frontend
- LangGraph orchestration

Supabase Free PostgreSQL
- LangGraph checkpoints
- Interaction Memory
- Run History / Product Memory

External services remain:

OpenAI API

Brave Search API

bounded HTTP reader

The Render service uses the repository main branch.

Current build command:

pip install -r requirements.txt

Current start command:

PYTHONPATH=. streamlit run app/frontend/main.py --server.address 0.0.0.0 --server.port \$PORT

Secrets and environment-specific configuration remain external to Git.

Rationale

The topology is sufficient for the validated MVP and avoids premature distributed infrastructure.

It preserves the same component boundaries already validated locally.

Consequences

Render Free may sleep and introduce cold-start latency;

the application process and local filesystem are ephemeral;

durable state belongs in PostgreSQL;

deployment configuration is partly external to the repository and must remain documented;

a successful Git commit alone does not fully describe the deployed runtime configuration;

production-grade authentication, observability, and distributed scaling remain separate hardening concerns.

ADR-025 --- Durable LangGraph checkpoints do not imply automatic frontend session recovery

Status: Accepted
Date: 2026-09-30

Context

PostgresSaver was validated by recovering workflow state from a new workflow instance using the same thread_id.

A later production-runtime test intentionally left a deployed workflow waiting at Human Perspective Selection and restarted the Render service.

After restart:

the PostgreSQL checkpoint survived;

Run History survived;

Streamlit st.session_state did not survive;

the frontend returned to its ready state instead of reconstructing the interrupted HITL screen.

The backend state was therefore durable, but the frontend no longer held the active thread_id required to reopen it automatically.

Decision

Automatic recovery of an interrupted HITL run after Streamlit session/process loss is not part of the closed MVP/cloud-deployment milestone.

It is moved to backlog as an explicit Resume Run capability.

Target future behavior:

History
\|
+--\> resumable run
\|
v
Resume
\|
v
recover thread_id
\|
v
PostgresSaver checkpoint
\|
v
reconstruct interrupt/UI
\|
v
continue human decision

Rationale

The persistence foundation is working as designed.

The missing behavior is product-level reconstruction of session identity and UI state, not a failure of PostgreSQL or LangGraph checkpoint durability.

Consequences

cloud deployment remains closed for the current MVP scope;

interrupted backend state remains recoverable when thread_id is known;

History currently remains primarily a product-memory / inspection surface;

future History UX should distinguish terminal runs from resumable HITL runs;

Resume Run should not require collapsing Run History and checkpoint persistence into one data model.

ADR-026 --- Cloud deployment does not change human publication authority

Status: Accepted
Date: 2026-09-30

Context

Moving the application from local execution to a publicly reachable cloud runtime increases operational availability but does not change the product's authority model.

A hosted agentic application could otherwise create pressure to equate workflow completion with autonomous external action.

Decision

Cloud deployment does not authorize autonomous LinkedIn publication.

The governing principle remains:

AI expands.
Human converges.
AI materializes.
Human owns.

Quality PASS, Final Human Refinement, durable persistence, and public hosting do not grant the application publication authority.

Publication remains manual and outside autonomous execution.

Rationale

Hosting topology is an infrastructure decision.

Publication authority is a product-governance decision.

The two must remain independent.

Consequences

future LinkedIn-native integration must preserve an explicit human publication boundary;

cloud automation must not silently convert COMPLETE into publish;

persistence and deployment work do not reopen the human-authority architecture established by ADR-017 and ADR-019.

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

ADR-017 --- Human-Centered Conversation Intelligence is the canonical product architecture

Status: Accepted
Date: 2026-09-24

Context

The original workflow moved directly from Research into Writer and relied on the Writer to perform several intellectual tasks at once:

infer a useful position;

choose an argument;

reproduce Rodrigo's voice;

write the final contribution.

Real editorial use and architecture review exposed a limitation in that assumption.

The hardest part of a valuable professional contribution is often not producing fluent text. It is deciding what is worth saying.

Human interpretation can depend on professional experience, accumulated knowledge, current objectives, personal associations, values, intuition, and context that should not be simulated through an ever-growing set of prompts, scores, and editorial variables.

A separate Human-Centered Conversation Intelligence proposal was created to explore a different product architecture. The implementation has since progressed naturally in that direction through Argument Contracts, Argument Intelligence, Perspective Generation, Human Perspective Selection, and SelectedPerspective-aware Writer / Voice integration.

Maintaining the same architecture as a separate "PROPOSED --- NOT CANONICAL" document would now conflict with the actual direction of the system.

Decision

The canonical product principle is:

AI expands. Human converges. AI materializes. Human owns.

The canonical MVP flow is:

Human Intent / Theme
→ Discovery / Scout
→ Target Qualification
→ Opportunity Evaluation
→ Research
→ ResearchBrief
→ Argument Intelligence
→ ArgumentBrief
→ Perspective Generation
→ PerspectiveSet
→ Human Perspective Selection
→ SelectedPerspective
→ Rodrigo Voice / Writer
→ Quality Evaluator
→ Human Final Review
→ Manual Publication

The human owns two distinct authority boundaries:

Intellectual authority --- selection, rejection, combination, guidance, or modification of the direction to be expressed.

Publication authority --- final review and the decision whether to publish externally.

AI may generate multiple defensible intellectual directions, but it must not silently infer or replace the human's selected final position.

Rationale

The architecture uses AI for intellectual expansion where machine capabilities provide leverage:

discovery;

reading;

research;

synthesis;

comparison;

tension mapping;

perspective generation;

drafting;

evaluation.

It preserves human judgment where irreducible personal context matters:

interpretation;

intellectual direction;

personal experience;

contextual nuance;

final editorial judgment;

publication.

Human-in-the-Loop is therefore part of the cognitive architecture, not merely a safety gate.

Consequences

Research must remain reusable and as independent as practical from the final editorial direction.

A new Argument Intelligence boundary separates evidence synthesis from final positioning.

Perspective Generation must produce materially distinct and defensible intellectual directions rather than stylistic variants.

Human Perspective Selection becomes an explicit workflow boundary.

The Writer no longer owns independent selection of Rodrigo's intellectual position when a SelectedPerspective is available.

Rodrigo Voice becomes an expression/personalization layer:

"Given this selected perspective, how might Rodrigo naturally express it?"

rather than:

"What does Rodrigo believe and which argument should he choose?"

LangGraph must eventually orchestrate the complete new flow and preserve the HITL perspective-selection boundary.

Autonomous publication remains prohibited.

The former standalone ADR-PROPOSED-human-centered-conversation-intelligence.md is superseded as a separate proposal artifact by this accepted decision plus the canonical architecture in 01_system_overview.md.

MVP Boundary

The frozen MVP is a system capable of finding or receiving an opportunity, qualifying it, researching it, transforming evidence into an ArgumentBrief, generating multiple defensible perspectives, requesting the human's desired intellectual direction, and only then producing and evaluating the final content.

The implementation roadmap is:

Argument Contracts v0.1

Argument Intelligence v0.1

Perspective Generation v0.1

Human Perspective Selection v0.1

Writer / Voice Integration v0.1

LangGraph Integration

MVP Validation & Release

Performance Analytics, Feedback Learning, adaptive policy calibration, advanced UX, and autonomous publication are outside the frozen MVP.

ADR-019 --- Final Human Refinement is a separate human authority boundary

Status: Accepted
Date: 2026-09-28

Context

Quality Evaluator PASS indicates that a draft satisfies the automated quality
contract.

It does not mean that the human has completed editorial ownership of the
content.

The human may still want a bounded adjustment to tone, emphasis, length,
framing, or closing without reopening the upstream intellectual reasoning
pipeline.

Decision

After Quality Evaluator PASS, the workflow will enter an explicit Final Human
Refinement HITL boundary.

The human may choose:

ACCEPT
terminate with the current approved draft

REFINE
provide bounded final editorial guidance and return once to Writer

A REFINE action does not create another automated Quality Evaluator loop.

SelectedPerspective, ContentMode, and factual/evidentiary grounding remain
authoritative during final refinement.

Rationale

The automated evaluator and the human perform different functions.

Quality Evaluator answers whether the draft satisfies the machine quality
contract.

Final Human Refinement allows the human to exercise editorial ownership over
how an already-approved intellectual direction is expressed.

Consequences

final_refinement_action and final_refinement_guidance become explicit
orchestration-state concepts;

Final Human Refinement is implemented as a LangGraph HITL node rather than a
frontend-only edit;

machine REVISE and human REFINE remain separate control paths;

publication remains outside autonomous execution;

the final human refinement path must remain bounded and must not silently
change the selected intellectual direction.

ADR-020 --- Translation is presentation, not reasoning

Status: Accepted
Date: 2026-09-28

Context

The internal reasoning pipeline is English-first, while the user may need to
consume generated artifacts in Brazilian Portuguese.

Rerunning the reasoning pipeline in another language would duplicate cost and
could introduce unnecessary semantic divergence between canonical artifacts.

Decision

On-demand Portuguese translation will be implemented as a presentation-layer
capability.

The canonical reasoning artifact remains the English version.

Translation must preserve meaning, structure, technical terminology, numbers,
URLs, evidence, uncertainty, and tone.

Translation does not own workflow routing and does not rerun Scout, Research,
Argument Intelligence, Perspective Generation, Writer, or Quality Evaluator.

Rationale

Language presentation and intellectual reasoning are different
responsibilities.

Separating them reduces cost, preserves one canonical reasoning path, and
makes bilingual UX available without duplicating the agentic workflow.

Consequences

translated content is not a replacement for the canonical workflow artifact;

translation can be requested selectively by the human;

translation caching may be treated as a presentation concern;

future multilingual presentation should preserve the same separation unless a
different reasoning-language requirement is explicitly introduced.

ADR-021 --- Product Run History is separate from execution state and Interaction Memory

Status: Accepted
Date: 2026-09-28

Context

The system now produces valuable intellectual artifacts across multiple
workflow stages.

LangGraph execution state exists to orchestrate a run and support HITL
interrupt/resume behavior.

Interaction Memory exists for operational agent behavior such as URL
canonicalization, novelty, and repeated-content avoidance.

Neither responsibility is equivalent to the user's need to revisit completed
or terminated product runs.

Decision

The product will maintain a separate Run History / Product Memory persistence
boundary.

Its purpose is to preserve enough information to reconstruct prior user-facing
executions and their important artifacts.

The current MVP implementation uses a dedicated local SQLite database:

data/history/run_history.db

History records use stable run identifiers and idempotent persistence.

Terminal persistence should prefer authoritative workflow state over a stale
frontend projection.

A later incomplete rerun must not overwrite a richer completed record.

Rationale

Execution state, behavioral memory, and user-facing product history have
different lifecycles and responsibilities.

Keeping them separate prevents checkpoint implementation details from becoming
the product-history contract and prevents Interaction Memory from becoming an
unstructured archive of workflow results.

Consequences

Run History can evolve independently from Interaction Memory;

the Streamlit product can expose recent-run and run-detail navigation without
changing agent reasoning;

the local SQLite implementation is an MVP persistence mechanism, not a
commitment to the final production database;

cloud deployment must explicitly decide durable execution checkpointing and
durable product-history persistence;

production retention, migration, concurrency, and system-of-record decisions
remain open.
