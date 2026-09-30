System Overview
Purpose
The LinkedIn Agentic AI System is a controlled, human-centered
agentic AI system for discovering strategically relevant professional
conversations, deciding whether they are worth pursuing, researching the
evidence required for a defensible contribution, expanding that evidence
into multiple intellectual directions, helping the human choose what is
worth saying, materializing the selected direction into a draft,
evaluating its quality, and preserving human authority over publication.
The system is not designed as an autonomous social-media bot.
The final MVP experience layer makes the same architecture usable as an
interactive product. Editable Theme / Intent, explicit Content Mode Selection,
Final Human Refinement, and on-demand Portuguese translation are now
implemented and validated end-to-end. Run History / Product Memory is
implemented and validated with navigable persistence. The local MVP experience
layer is closed, and the same product is now deployed on Render with durable
PostgreSQL/Supabase persistence for cloud execution.
Its purpose is to reduce the manual effort required to move from:
"Where should I contribute?"
to:
"What are the defensible directions here, which one do I want to own,
and how should it be expressed?"
The system therefore separates semantic reasoning, deterministic
governance, workflow orchestration, and human judgment.
Core Product Principle
AI expands. Human converges. AI materializes. Human owns.
AI is used where machine intelligence provides leverage:
discovery;
filtering;
research;
evidence retrieval;
synthesis;
tension mapping;
perspective generation;
drafting;
evaluation.
Human judgment remains authoritative for:
intellectual direction;
perspective selection, rejection, or combination;
personal context;
contextual nuance;
final editorial judgment;
publication.
Human-in-the-Loop is therefore not merely a safety gate. It is part of
the cognitive architecture of the product.
A second established principle remains:
Opportunity != Popularity
A post is not valuable merely because it has high engagement. A useful
opportunity depends on whether Rodrigo can make a relevant,
differentiated, professionally valuable, and defensible contribution.
Frozen MVP Target
MVP Human-Centered Conversation Intelligence = a system capable of
finding or receiving an opportunity, qualifying it, researching it,
transforming evidence into an ArgumentBrief, generating multiple
defensible perspectives, asking the human for the desired intellectual
direction, and only then producing and evaluating the final content. The
final experience-layer increment extends this target without changing the
core human-centered reasoning principle. Editable Theme / Intent, Content Mode
Selection, Final Human Refinement, and optional Portuguese translation are
implemented and validated. Run History / Product Memory is also implemented
and validated. The complete MVP experience layer is closed, and cloud deployment
has been validated without reopening the core reasoning architecture.
The MVP is intentionally narrower than the broader long-term product
vision.
Performance Analytics, Feedback Learning, adaptive policy calibration,
advanced UX, autonomous publication, and other post-MVP capabilities are
not required to close this MVP.
Target MVP Architecture
Human Intent / Editable Theme
\|
v
Discovery / Scout
\|
v
Target Qualification
\|
v
Opportunity Evaluation
\|
+-- LOW -----------------------------\> END
\|
+-- MEDIUM --\> QUEUED --------------\> END
\|
+-- HIGH
\|
v
Research
\|
v
ResearchBrief
\|
v
Argument Intelligence
\|
v
ArgumentBrief
\|
v
Perspective Generation
\|
v
PerspectiveSet
\|
v
Human Perspective Selection
\|
v
SelectedPerspective
\|
v
Human Content Mode Selection
(LinkedIn Post / LinkedIn Reply / Article)
\|
v
Rodrigo Voice / Writer
\|
v
Quality Evaluator
\|
+-- PASS ----------------------------\> Human Final Review
\|
+-- REVISE --\> Writer --\> Evaluator
\|
+-- REJECT --------------------------\> END
\|
v
Manual Publication
Publication remains outside autonomous execution.
The core Human-Centered Conversation Intelligence flow is integrated in
the LangGraph workflow. The MVP Experience Layer now includes Editable Theme /
Intent, Content Mode Selection, Final Human Refinement, on-demand Portuguese
translation, and Run History / Product Memory. All five capabilities are implemented and validated through the real Streamlit
workflow. Run History is implemented, navigable, and validated both locally and
through the deployed PostgreSQL/Supabase persistence path.
Responsibility Layers
LLM --- Semantic Intelligence
The LLM handles tasks where interpretation matters, including:
search strategy;
source selection;
topic relevance;
contribution potential;
evidence interpretation;
synthesis;
tension identification;
perspective generation;
writing;
semantic quality assessment.
The LLM may expand the intellectual decision space, but it must not
silently replace the human-selected intellectual direction.
Python --- Deterministic Governance
Python owns:
validation;
scoring;
thresholds;
guardrails;
action authorization;
provenance enforcement;
counters;
operational limits;
context budgets;
factual state mutation;
validation of explicit human selections.
Semantic proposals do not automatically become authoritative operational
state.
LangGraph --- Workflow Orchestration
LangGraph coordinates:
shared workflow state;
node transitions;
deterministic routing;
bounded revision paths;
Human-in-the-Loop transitions;
termination.
LangGraph orchestrates specialist components; it should not absorb their
business logic.
Human --- Intellectual and Publication Authority
The human owns two distinct decision boundaries.
Intellectual convergence
AI researches
-\> AI builds argument space
-\> AI generates defensible perspectives
-\> HUMAN SELECTS / REJECTS / COMBINES / GUIDES
Final ownership
AI materializes selected direction
-\> AI evaluates quality
-\> HUMAN REVIEWS
-\> HUMAN DECIDES WHETHER TO PUBLISH
Autonomous LinkedIn publication and commenting remain explicit
non-goals.
Discovery / Scout
Scout is the bounded discovery agent.
Its action vocabulary is:
SEARCH
READ
SELECT
FINISH
Its loop is:
ScoutState
\|
v
LLM chooses allowed action
\|
v
Structured ScoutAction
\|
v
Python authorization
\|
v
Tool execution
\|
v
Observation -\> State -\> next bounded decision
The model decides semantically what it wants to do. Python decides
whether the action is legal.
Web Tool Layer
Scout and Research use provider-neutral contracts:
SearchTool(query) -\> list(SearchResult)
ReadTool(url) -\> str
Two execution modes are supported:
FAKE MODE -\> deterministic tools for isolated tests
REAL MODE -\> Brave Search + bounded HTTP reader
The real reader validates network access and includes controls for URL
scheme, DNS resolution, localhost/private destinations, redirects,
timeouts, content type, response size, and controlled external failures.
Content Preparation
External pages pass through explicit preparation boundaries:
HTTP response
\|
v
Main Content Extraction
\|
+-\> prefer article/main
+-\> density fallback for section/div
\|
v
Editorial text
\|
v
Context Preparation
\|
+-\> normalize
+-\> remove exact duplicate lines
+-\> count tokens
+-\> enforce component budget
\|
v
PreparedContext
\|
v
LLM-facing input
This prevents arbitrary raw webpages from being treated as clean,
unlimited model context.
Current principal budgets:
Scout read context \<= 1800 tokens
Research per-read context \<= 2500 tokens
Research cumulative read context \<= 8000 tokens
Opportunity Evaluation
Opportunity Evaluation answers:
"Is this opportunity worth pursuing?"
Current weighted dimensions:
Dimension Weight
Contribution Potential 30%
Positioning Fit 25%
Topic Relevance 20%
Engagement Potential 15%
Research Efficiency 10%
The LLM produces semantic signals. Python calculates the weighted score,
applies mandatory guardrails, and produces the operational
classification.
HIGH -\> ACCEPTED_FOR_RESEARCH -\> Research
MEDIUM -\> QUEUED -\> END
LOW -\> END
Opportunity Evaluation is a strategic resource-allocation gate. It does
not determine Rodrigo's final intellectual position.
Research
Research transforms an accepted opportunity into the minimum evidence
package needed for a factual and defensible contribution.
Actions:
SEARCH
READ
EXTRACT
FINISH
Provenance chain:
SearchResult
\|
v
Authorized URL
\|
v
ReadSource
\|
v
EvidenceItem
\|
v
ResearchBrief
A search result is not automatically evidence. A read page is not
automatically evidence. Evidence must be explicitly extracted and
preserve provenance.
Current principal runtime limits:
max steps 10
max decisions 12
max searches 3
max reads 5
max evidence items 6
Research may terminate as SUFFICIENT, INSUFFICIENT, or
LIMIT_REACHED.
Research should remain independent from the final editorial direction
whenever practical so that multiple perspectives can reuse the same
evidence base.
Argument Intelligence
Argument Intelligence sits between Research and final content
generation.
Its responsibility is not to write the final LinkedIn contribution.
It transforms a ResearchBrief into an ArgumentBrief: a compact
intellectual decision artifact that can expose, where supported by the
evidence:
the original thesis;
relevant context;
strongest evidence;
counterevidence;
tensions and trade-offs;
uncertainty;
possible contribution areas;
source references.
Conceptually:
ResearchBrief
\|
v
Argument Intelligence
\|
v
ArgumentBrief
This boundary separates researching what is supported from
deciding what is worth saying.
Perspective Generation
Perspective Generation deliberately preserves divergence before human
convergence.
Instead of immediately producing one supposedly "best" answer, the
system generates a small set of materially distinct and defensible
intellectual directions grounded in the same ArgumentBrief and
evidence base.
Conceptually:
ArgumentBrief
\|
v
Perspective Generation
\|
v
PerspectiveSet
A perspective represents what could be worth saying.
It is not merely a change in tone, style, or wording.
Artificial disagreement should not be created solely to produce multiple
options.
Human Perspective Selection
Human Perspective Selection is the central convergence boundary of the
MVP.
The human may:
select a perspective;
reject a proposed direction;
combine ideas where the contract supports it;
add guidance or personal context;
modify the intended direction;
request another direction through the interaction layer.
The selected intellectual direction is represented explicitly through
SelectedPerspective.
Conceptually:
PerspectiveSet
\|
v
Human decision
\|
v
SelectedPerspective
Only after this convergence should the system materialize the complete
final contribution.
The human selection is authoritative context. Downstream generation must
not silently substitute another argument.
Perspective Is Not Expression
The architecture explicitly separates:
Perspective
What should be said.
from:
Expression
How the selected idea should be communicated.
A technical perspective can be expressed conversationally. An
organizational perspective can be expressed humorously. These dimensions
must not be collapsed into one variable.
MVP Experience Layer
The final MVP increment adds a product experience layer without reopening
the validated core reasoning architecture. Its purpose is to expose the
existing agentic capabilities through a more flexible and navigable human
workflow.
The current capabilities and status are:
Editable Theme / Intent --- IMPLEMENTED AND VALIDATED
The human can define the topic to explore instead of relying on a fixed
Scout objective. The application converts the human theme into the bounded
Scout objective while preserving the existing discovery guardrails.
Real Streamlit runs have validated this behavior across different themes,
demonstrating that the architecture is not hard-coded to a single
professional domain.
Content Mode Selection --- IMPLEMENTED AND VALIDATED
After selecting the intellectual perspective, the human chooses how the
idea should be materialized. Initial MVP modes are:
LinkedIn Post;
LinkedIn Reply / Comment;
Article.
Content mode is an expression decision, not an intellectual-position
decision. The same SelectedPerspective may therefore be materialized in
different formats without rerunning Research, Argument Intelligence, or
Perspective Generation. Writer and Quality Evaluator are content-mode-aware,
and legacy paths default to linkedin_reply for compatibility. Real Streamlit
E2E has validated both sequential HITL boundaries through Human Final Review.
Final Human Refinement --- IMPLEMENTED AND VALIDATED
After a generated draft passes quality evaluation, the human can provide
additional editorial guidance for final adjustment, such as tone, emphasis,
length, framing, or closing. This refinement must preserve the selected
intellectual direction unless the human explicitly changes it.
Bilingual Presentation --- IMPLEMENTED AND VALIDATED
The MVP remains English-first internally. Final generated content can be
presented in English and translated to Portuguese on demand through a
Translate interaction. Translation is treated as a presentation layer so
that it does not duplicate the complete reasoning pipeline or increase cost
unnecessarily.
Run History / Product Memory --- IMPLEMENTED AND VALIDATED
The application exposes navigable history for workflow runs so that
the intellectual work produced by the system does not disappear when a new
workflow starts. A history entry should preserve, at minimum:
human theme / intent;
selected supporting source and link;
selected perspective;
content mode;
final generated response;
translated response when requested;
relevant run metadata required to reconstruct the user-facing result.
This product-facing run history is distinct from Interaction Memory.
Interaction Memory primarily supports agent behavior such as URL
canonicalization, novelty, and avoiding repeated content. Run History
exists so the human can revisit prior intellectual work and generated
artifacts. Both may use persistent storage, but they have different
responsibilities.
The intended experience is therefore:
Editable Theme
-\> Discovery / Qualification / Research
-\> Argument Intelligence
-\> Perspective Generation
-\> Human Perspective Selection
-\> Human Content Mode Selection
-\> Writer / Quality Evaluation
-\> Human Final Refinement
-\> Optional Translation
-\> Persistent Run History
-\> Manual Publication
The core Scout, Opportunity Evaluation, Research, Argument Intelligence,
Perspective Generation, and scoring behavior should remain frozen during
this experience-layer increment except where a genuine defect requires a
change.
Rodrigo Voice
Rodrigo Voice is a personalization layer, not a simulator of Rodrigo's
beliefs.
Its responsibility is narrower:
"Given this specific human-selected perspective, how might Rodrigo
naturally express it?"
Rodrigo Voice must not independently infer which intellectual position
Rodrigo should adopt.
This keeps personalization downstream from human intellectual
convergence.
Writer
The Writer materializes the human-selected direction into a professional
contribution draft using the available evidence and personalization
context.
Its role is therefore:
SelectedPerspective
+
ContentMode
+
ResearchBrief / evidence context
+
Rodrigo Voice
\|
v
Writer
\|
v
Draft
Writer does not own:
discovery;
opportunity classification;
unrestricted research;
perspective selection;
human belief inference;
quality routing;
publication.
The orchestration layer supplies component-specific input instead of
exposing the entire global state indiscriminately.
Quality Evaluator
Opportunity Evaluation and Quality Evaluation solve different problems:
Opportunity Evaluation -\> "Should we invest effort in this conversation?"
Quality Evaluation -\> "Is the generated contribution good enough?"
Quality routing:
PASS -\> Human Final Review
REVISE -\> Writer -\> Quality Evaluator
REJECT -\> END
Revision is bounded and does not automatically rerun Research.
A quality PASS does not authorize publication.
Structured Contracts
Representative typed contracts include:
PostCandidate
OpportunitySignals
OpportunityEvaluation
ScoutAction
ScoutSelection
ScoutState
SearchResult
SearchTool
ReadTool
ResearchObjective
ResearchAction
ReadSource
EvidenceItem
ResearchState
ResearchBriefSynthesis
ResearchBrief
ArgumentBrief
Perspective
PerspectiveSet
SelectedPerspective
Writer contracts
Quality Evaluation contracts
LinkedInAgentState
Pydantic is preferred at machine-to-machine AI boundaries where
practical.
The new argument contracts create an explicit data boundary between
evidence, intellectual alternatives, human convergence, and final
expression.
Failure Model
The architecture distinguishes:
semantic failure
operational limit
external infrastructure failure
programming failure
A recoverable web failure can become agent state and permit another
bounded decision.
A programming failure should not be silently transformed into
plausible-looking data.
A human rejection or request for another intellectual direction is not
necessarily a system failure; it is a legitimate product outcome.
Capability Map
DISCOVERY
├── bounded Scout loop
├── structured actions
├── deterministic authorization
├── fake and real web tools
└── bounded failure recovery
WEB INFRASTRUCTURE
├── provider-neutral contracts
├── Brave Search adapter
├── bounded HTTP reader
├── network / SSRF guardrails
├── main-content extraction
└── content-density fallback
CONTEXT
├── normalization
├── duplicate-line removal
├── token counting
├── per-component truncation
└── cumulative Research read budget
OPPORTUNITY
├── semantic signal evaluation
├── deterministic weighted scoring
├── mandatory guardrails
├── HIGH / MEDIUM / LOW
└── deterministic routing
RESEARCH
├── bounded semantic loop
├── SEARCH / READ / EXTRACT / FINISH
├── source authorization
├── evidence provenance
└── ResearchBrief
CONVERSATION INTELLIGENCE
├── ArgumentBrief contracts
├── Argument Intelligence
├── Perspective / PerspectiveSet contracts
├── Perspective Generation
├── SelectedPerspective contract
└── Human Perspective Selection boundary
GENERATION & QUALITY
├── selected-perspective-aware Writer
├── content-mode-aware materialization
├── Rodrigo Voice personalization
├── Quality Evaluator
├── bounded revision loop
└── final human refinement
EXPERIENCE & MEMORY
├── editable human theme / intent (IMPLEMENTED)
├── LinkedIn Post / Reply / Article modes (IMPLEMENTED)
├── final human refinement (IMPLEMENTED)
├── on-demand Portuguese translation (IMPLEMENTED)
├── navigable run history (IMPLEMENTED)
└── separation of product history from Interaction Memory
ORCHESTRATION & GOVERNANCE
├── LangGraph workflow
├── explicit shared state
├── deterministic routing
├── structured contracts
├── Human-in-the-Loop boundaries
└── human publication authority
The core Conversation Intelligence flow and the complete MVP Experience Layer
are integrated. Editable Theme, Content Mode Selection, Final Human Refinement,
on-demand Portuguese translation, and navigable Run History are implemented and
validated. This capability map must therefore be read together with
02_current_architecture.md for the exact implemented topology and runtime details.
Validation State
The project has extensive automated unit and integration coverage,
deterministic fake-tool validation, and real-tool smoke validation.
Real-tool smoke validation has demonstrated important infrastructure
boundaries including:
Scout
OpenAI reasoning
- real search
- real reading
- content extraction
- bounded context
Research
OpenAI reasoning
- real search
- real reading
- evidence extraction
- provenance
- ResearchBrief
Automated test counts are development snapshots rather than
architectural invariants and should be recorded in the current
implementation/audit context rather than treated as a permanent design
property of this document.
Current MVP validation snapshot:
437 automated tests passing;
Editable Theme / Intent validated in real Streamlit execution;
LOW Opportunity routing validated in real Streamlit execution;
HIGH path validated through Research, Argument Intelligence, Perspective
Generation, Human Perspective Selection, Human Content Mode Selection,
mode-aware Writer, mode-aware Quality Evaluator, and Human Final Review;
both sequential LangGraph HITL interrupt/resume boundaries validated;
publication remains manual.
Current frontend hardening:
visual state/phase can lag the backend worker;
transient Scout / Opportunity text can flicker during automatic Streamlit
reruns.
These are presentation-layer defects and must not reopen the validated core
reasoning architecture.
Roadmap to MVP
Increment Delivery Architectural
Impact
1 Argument ArgumentBrief, Perspective, PerspectiveSet, Creates the
Contracts v0.1 SelectedPerspective formal language
of the new
architecture
2 Argument ResearchBrief -\> ArgumentBrief Separates
Intelligence v0.1 research from
positioning
3 Perspective ArgumentBrief -\> 2--4 defensible perspectives Implements AI
Generation v0.1 expands
4 Human Perspective Human selects / rejects / combines / guides Implements
Selection v0.1 perspective Human
converges
5 Writer / Voice SelectedPerspective -\> Rodrigo Voice -\> Writer Implements AI
Integration v0.1 materializes
6 LangGraph Complete new flow + HITL + routing Transforms
Integration components into
an integrated
system
7 MVP Experience Editable theme, content mode, final human Converts the
Layer v1.0 refinement, on-demand translation, run history validated agentic
workflow into a
navigable product
experience
The roadmap is sequential at the architectural level, even when
implementation work overlaps between adjacent increments.
Current resume point:
7.1 Editable Theme / Intent is complete and validated.
7.2 Content Mode Selection is complete and validated.
7.3 Final Human Refinement is complete and E2E validated.
7.4 Bilingual Presentation is complete and E2E validated.
7.5 Run History / Product Memory is complete and validated.
Current automated regression baseline: 437 passing tests.
Cloud deployment is implemented and smoke validated on Render, with
Supabase PostgreSQL providing durable cloud persistence.
Cloud Deployment and Durable Persistence
The local-first architecture has now been extended into a validated cloud
runtime without changing the core responsibility model.
Current deployed topology:
Browser
\|
v
Render Free Web Service
\|
+--\> Streamlit frontend
+--\> LangGraph orchestration
+--\> Python deterministic governance
+--\> OpenAI model access
+--\> Brave Search / bounded HTTP reader
\|
v
Supabase PostgreSQL
The cloud deployment preserves the same separation between semantic
intelligence, deterministic governance, orchestration, persistence, and human
authority that exists in local execution.
Render is the current application runtime.
Supabase PostgreSQL is the current durable cloud persistence platform.
The deployment deliberately remains a single application unit because the
validated MVP does not require distributed microservices, a broker, or a
container-orchestration platform.
Persistence Responsibilities
The deployed system preserves three conceptually distinct persistence domains.
LangGraph Checkpoint / HITL State
Purpose:
preserve authoritative workflow execution state required by LangGraph
interrupt/resume semantics.
Local backend:
InMemorySaver
Cloud backend:
PostgresSaver
Interaction Memory
Purpose:
support agent behavior such as canonical URL memory, novelty, visited-content
tracking, agentic drafts, human-final content, and interaction status.
Local backend:
SQLiteInteractionMemoryRepository
Cloud backend:
PostgresInteractionMemoryRepository
Run History / Product Memory
Purpose:
preserve navigable user-facing workflow history and intellectual artifacts
independently from LangGraph execution checkpoints and Interaction Memory.
Local backend:
SQLiteRunHistoryRepository
Cloud backend:
PostgresRunHistoryRepository
The three responsibilities currently share one Supabase PostgreSQL service in
cloud execution, but they must not be collapsed into one conceptual state model.
Explicit Backend Selection
Cloud persistence is selected explicitly through environment configuration.
DATABASE_URL
provides PostgreSQL connection information.
PERSISTENCE_BACKEND
selects persistence behavior.
Current rule:
PERSISTENCE_BACKEND=postgres
+
DATABASE_URL configured
-\>
PostgreSQL persistence enabled
Otherwise:
local persistence remains active.
This separation is deliberate. Possessing cloud database credentials must not
silently change local development or automated-test semantics.
The explicit selector was introduced after persistent checkpoint state exposed a
test-isolation problem when a fixed thread_id recovered state from a previous
PostgreSQL-backed execution. The resulting architecture keeps local/test
execution isolated by default while allowing the deployed environment to opt in
to durable PostgreSQL state.
Cloud Validation
The cloud deployment has been validated incrementally rather than inferred from
a successful build.
Validated runtime behavior includes:
Render repository build;
dependency installation;
Streamlit startup;
repository-root package imports through PYTHONPATH;
public application access;
OpenAI-backed workflow execution;
Brave Search real mode;
Supabase PostgreSQL connectivity;
deployed Run History navigation.
Validated LangGraph persistence includes:
PostgresSaver initialization;
creation of LangGraph checkpoint tables;
workflow execution with a known thread_id;
creation of a new workflow instance;
recovery of the persisted workflow state using the same thread_id.
Validated Interaction Memory persistence includes:
PostgreSQL repository selection;
record creation;
has_seen behavior;
agentic draft persistence;
human-final persistence;
status evolution;
recent-history retrieval.
Validated Run History persistence includes:
PostgreSQL repository selection;
table initialization;
run creation;
get by run_id;
recent-list retrieval;
UPSERT of an existing run;
updated field recovery;
deployed History retrieval;
survival of Render process restart.
The current automated regression baseline remains:
437 passing tests.
HITL Durability Boundary
The backend checkpoint foundation is durable, but durable backend state does not
by itself reconstruct a lost Streamlit browser/session state.
A deliberate Render restart test was performed while the workflow was waiting at
Human Perspective Selection.
Observed behavior:
PostgresSaver checkpoint -\> survived restart
Run History -\> survived restart
Streamlit session_state -\> did not survive restart
The checkpoint itself therefore remains recoverable when the same thread_id is
supplied. The current frontend does not yet reconstruct the active thread_id and
interrupt UI after process/session loss.
This is not treated as a PostgresSaver failure.
It is a frontend/product-resilience capability.
Resume HITL After Session Loss --- BACKLOG
A future product increment should distinguish terminal historical runs from
resumable interrupted runs.
Target behavior:
History
\|
+--\> terminal run
\| \|
\| +--\> Open / Inspect
\|
+--\> resumable HITL run
\|
+--\> Resume
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
This capability is explicitly post-MVP backlog and does not reopen the completed
cloud-deployment milestone.
Cloud Runtime Configuration
The deployed Render service currently uses environment-driven configuration,
including:
OPENAI_API_KEY
BRAVE_SEARCH_API_KEY
WEB_TOOL_MODE=real
DATABASE_URL
PERSISTENCE_BACKEND=postgres
Secrets remain external to Git.
Current Render runtime configuration uses:
Build:
pip install -r requirements.txt
Start:
PYTHONPATH=. streamlit run app/frontend/main.py --server.address 0.0.0.0 --server.port \$PORT
The explicit PYTHONPATH keeps the repository root importable when Streamlit
executes app/frontend/main.py.
The Render filesystem must not be treated as the durable cloud system of record.
Free-tier process sleep/restart is acceptable because durable application state
belongs in Supabase PostgreSQL.
Cloud Deployment Scope
The current deployment should be described as:
implemented;
publicly reachable;
smoke validated;
durably persisted for the three current persistence responsibilities;
appropriate for the current portfolio/MVP scope.
It should not be described as a fully hardened multi-user production platform.
Post-MVP production hardening still includes concerns such as:
authentication and authorization;
production-grade observability;
formal retention and deletion policy;
backup/recovery policy;
schema migration discipline;
advanced cost and latency telemetry;
multi-user concurrency hardening;
automatic Resume Run UX after frontend session loss;
LinkedIn-native authenticated integration.
None of these changes the core product rule:
AI expands. Human converges. AI materializes. Human owns.

Current Architectural Boundaries
Still intentionally incomplete or unresolved outside the MVP closure
path:
production LinkedIn-specific discovery;
reliable LinkedIn engagement metadata;
objective Engagement Potential calculation;
multiple-candidate orchestration;
production-grade observability;
production-grade deployment hardening beyond the current Render/Supabase MVP;
long-term model routing and cost telemetry;
real-world scoring calibration;
advanced Human-in-the-Loop UX beyond the MVP Experience Layer;
Performance Analytics and Feedback Learning;
adaptive policy calibration;
autonomous publication.
These items are post-MVP hardening or expansion concerns and must not be
confused with the now-closed frozen MVP scope.
Architectural Direction
The system is evolving toward:
semantic intelligence
-
deterministic governance
+
bounded tools
+
explicit state
+
evidence provenance
+
argument intelligence
+
human intellectual convergence
+
personalized materialization
+
quality evaluation
+
human ownership
The architecture is not optimized for maximum autonomy.
It is optimized for useful autonomy under explicit human control,
with AI expanding the decision space and the human retaining authority
over both intellectual direction and publication.
